"""Convert official CMU ASF/AMC locomotion into heading-normalized joint directions.
Run with Blender's Python (numpy is bundled). Source numerical data is included under motion/cmu.
CMU reuse terms: http://mocap.cs.cmu.edu/faqs.php
"""
import pathlib, math, json, hashlib
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parent
SOURCE=ROOT/'motion/cmu'
OUT=ROOT.parent/'unity/SatChara/Assets/SatChara/Animation'
OUT.mkdir(parents=True,exist_ok=True)
manifest=json.loads((SOURCE/'manifest.json').read_text())
for item in manifest['files']:
    if hashlib.sha256((SOURCE/item['name']).read_bytes()).hexdigest()!=item['sha256']:
        raise RuntimeError('CMU source hash mismatch: '+item['name'])
MAP=[('spine_01','spine_02','lowerback'),('spine_02','spine_03','upperback'),('spine_03','neck_01','thorax'),
     ('neck_01','head','upperneck'),('thigh_l','calf_l','lfemur'),('calf_l','foot_l','ltibia'),('foot_l','ball_l','lfoot'),
     ('thigh_r','calf_r','rfemur'),('calf_r','foot_r','rtibia'),('foot_r','ball_r','rfoot'),
     ('upperarm_l','lowerarm_l','lhumerus'),('lowerarm_l','hand_l','lradius'),
     ('upperarm_r','lowerarm_r','rhumerus'),('lowerarm_r','hand_r','rradius')]
def rotation(v):
    x,y,z=np.radians(v);cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
    return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
def skeleton(path):
    text=path.read_text();bones={}
    import re
    for block in re.findall(r'\bbegin\s+(.*?)\bend\b',text.split(':bonedata')[1].split(':hierarchy')[0],re.S):
        fields={p[0]:p[1:] for line in block.splitlines() if (p:=line.split())}
        name=fields['name'][0];axis=rotation(list(map(float,fields['axis'][:3])))
        bones[name]={'direction':np.array(list(map(float,fields['direction']))),'length':float(fields['length'][0]),'axis':axis,'dof':fields.get('dof',[])}
    children={}
    for line in text.split(':hierarchy')[1].splitlines():
        p=line.split()
        if p and p[0] not in ('begin','end'):children[p[0]]=p[1:]
    return bones,children
def frames(path):
    result=[];frame=None
    for line in path.read_text().splitlines():
        p=line.split()
        if not p or p[0][0] in '#:':continue
        if p[0].isdigit():
            frame={};result.append(frame)
        else:frame[p[0]]=list(map(float,p[1:]))
    return result
def forward_kinematics(frame,bones,children):
    root=frame['root'];ends={'root':np.array(root[:3])};world={'root':rotation(root[3:6])};directions={}
    def visit(parent):
        for name in children.get(parent,[]):
            b=bones[name];angles=[0.,0.,0.]
            for channel,value in zip(b['dof'],frame.get(name,[])):angles['xyz'.index(channel[1])]=value
            world[name]=world[parent]@b['axis']@rotation(angles)@b['axis'].T
            directions[name]=world[name]@b['direction']
            ends[name]=ends[parent]+directions[name]*b['length'];visit(name)
    visit('root');return ends,directions
def vector(v):return dict(zip(('x','y','z'),[round(float(x),6) for x in v]))
def convert(name,filename,min_period):
    bones,children=skeleton(SOURCE/'02.asf');raw=frames(SOURCE/filename)
    solved=[forward_kinematics(f,bones,children) for f in raw]
    roots=np.array([p['root'] for p,d in solved]);heading=roots[-10]-roots[10];heading[1]=0;heading/=np.linalg.norm(heading)
    right=np.cross([0,1,0],heading);basis=np.array([right,[0,1,0],heading])
    leg=bones['lfemur']['length']+bones['ltibia']['length']
    ankle=np.array([basis@(p['ltibia']-p['root']) for p,d in solved])
    z=np.convolve(ankle[:,2],np.ones(9)/9,mode='same')
    candidates=[i for i in range(10,len(z)-10) if z[i]>=max(z[i-4:i+5])]
    peaks=[]
    for i in candidates:
        if peaks and i-peaks[-1]<min_period:
            if z[i]>z[peaks[-1]]:peaks[-1]=i
        else:peaks.append(i)
    if len(peaks)<2:raise RuntimeError(f'{name}: no complete stride; peaks={peaks}')
    start,end=peaks[0],peaks[1]
    floor=min(min(p['ltoes'][1],p['rtoes'][1]) for p,d in solved[start:end+1])
    speed=np.linalg.norm((roots[end]-roots[start])*[1,0,1])/((end-start)/120)
    median=float(np.median(roots[start:end,1]));output=[]
    for sample in np.linspace(start,end,round((end-start)/4)+1):
        i=int(round(sample));p,d=solved[i];contacts=[]
        for toe in ['ltoes','rtoes']:
            a=max(0,i-2);b=min(len(solved)-1,i+2)
            velocity=(solved[b][0][toe]-solved[a][0][toe])*120/(b-a)
            contacts.append(bool(p[toe][1]<floor+leg*.09 and np.linalg.norm(velocity*[1,0,1])<speed*.6))
        hips=basis@(p['rhipjoint']-p['lhipjoint'])
        output.append({'directions':[vector(basis@d[src]) for _,_,src in MAP],
            'pelvis':round((roots[i,1]-median)/leg,6),'roll':round(math.degrees(math.atan2(hips[1],abs(hips[0]))),5),
            'leftContact':contacts[0],'rightContact':contacts[1]})
    # Crossfade a small tail into the start, preserving a continuous repeating cycle.
    seam=min(4,len(output)//8)
    for k in range(seam):
        t=(k+1)/seam;dst=output[len(output)-seam+k];src=output[0]
        for j in range(len(MAP)):
            a=np.array(list(dst['directions'][j].values()));b=np.array(list(src['directions'][j].values()));v=a*(1-t)+b*t;v/=np.linalg.norm(v)
            dst['directions'][j]=vector(v)
        dst['pelvis']=dst['pelvis']*(1-t)+src['pelvis']*t;dst['roll']=dst['roll']*(1-t)+src['roll']*t
    output[-1]=dict(output[0])
    clip={'name':name,'duration':round((end-start)/120,6),'stride':round(np.linalg.norm((roots[end]-roots[start])*[1,0,1])/leg,6),'frames':output}
    info={'name':name,'source':filename,'source_fps':120,'source_frames':len(raw),'cycle_start_frame':start+1,'cycle_end_frame':end+1,
        'peaks':peaks,'frames':len(output),'stride_leg_lengths':clip['stride'],'duration':clip['duration'],
        'contact_samples':[sum(f['leftContact'] for f in output),sum(f['rightContact'] for f in output)],
        'heading':heading.tolist(),'sha256':hashlib.sha256((SOURCE/filename).read_bytes()).hexdigest()}
    return clip,info
clips=[];summary=[]
for args in [('Walk','02_01.amc',65),('Jog','02_03.amc',40)]:
    clip,info=convert(*args);clips.append(clip);summary.append(info)
(OUT/'CapturedLocomotion.json').write_text(json.dumps({'bones':[a for a,b,c in MAP],'children':[b for a,b,c in MAP],'clips':clips},separators=(',',':')))
(ROOT/'captured-motion-summary.json').write_text(json.dumps(summary,indent=2))
print('CMU_CONVERTED',json.dumps(summary,indent=2))
