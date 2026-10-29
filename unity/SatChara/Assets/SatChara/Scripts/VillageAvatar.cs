using System.Collections.Generic;
using UnityEngine;

namespace SatChara
{
    // Captured walk/jog retargeting with temporary authored action overlays.
    public sealed class VillageAvatar : MonoBehaviour
    {
        [SerializeField] private TextAsset capturedMotion;
        private static TextAsset cachedSource;
        private static CapturedLocomotion cachedMotion;
        private CapturedLocomotion motion;
        private readonly Dictionary<string,Transform> bones=new Dictionary<string,Transform>();
        private readonly Dictionary<Transform,Quaternion> rest=new Dictionary<Transform,Quaternion>();
        private Transform[] driven,ends;
        private Vector3[] directions,bindDirections,referenceDirections;
        private readonly bool[] planted=new bool[2];
        private readonly Vector3[] anchors=new Vector3[2];
        private static readonly string[] Sides={"l","r"};
        private Vector3 previousPosition;
        private float cycle,speed,visualTime,throwTime=-10,legLength,ankleHeight,groundOffset;
        private bool ready;
        public Vector3 HandPosition => bones.TryGetValue("hand_r",out var hand)?hand.position:transform.position+Vector3.up;
        public bool LeftPlanted => planted[0];
        public bool RightPlanted => planted[1];
        public Vector3 LeftFoot => bones["foot_l"].position;
        public Vector3 RightFoot => bones["foot_r"].position;
        public float PlantError { get; private set; }
        public void SetMotion(TextAsset source) => capturedMotion=source;
        private void Initialize()
        {
            if(ready)return;
            foreach(var bone in GetComponentsInChildren<Transform>()) { bones[bone.name]=bone;rest[bone]=bone.localRotation; }
            if(cachedSource!=capturedMotion || cachedMotion==null) { cachedMotion=CapturedLocomotion.Load(capturedMotion);cachedSource=capturedMotion; }
            motion=cachedMotion;directions=new Vector3[motion.bones.Length];driven=new Transform[directions.Length];ends=new Transform[directions.Length];
            bindDirections=new Vector3[driven.Length];referenceDirections=new Vector3[driven.Length];
            for(int i=0;i<driven.Length;i++)
            {
                driven[i]=bones[motion.bones[i]];ends[i]=bones[motion.children[i]];
                bindDirections[i]=transform.InverseTransformDirection((ends[i].position-driven[i].position).normalized);
                foreach(var frame in motion.clips[0].frames) referenceDirections[i]+=frame.directions[i];
                referenceDirections[i].Normalize();
            }
            legLength=Vector3.Distance(bones["thigh_l"].position,bones["calf_l"].position)+Vector3.Distance(bones["calf_l"].position,bones["foot_l"].position);
            ankleHeight=Mathf.Max(.05f,(bones["foot_l"].position.y+bones["foot_r"].position.y)*.5f-transform.parent.position.y+.9f);
            previousPosition=transform.parent.position;ready=true;
        }
        public void Throw() => throwTime=visualTime;
        public void Drive(Vector3 facing,bool holdingBall,bool carryingStone,bool ducking,float charge=0,bool freeze=false,float frameDelta=-1)
        {
            Initialize();
            float dt=frameDelta>=0?frameDelta:Time.deltaTime;
            Vector3 delta=transform.parent.position-previousPosition;delta.y=0;previousPosition=transform.parent.position;
            if(delta.magnitude>2) { delta=Vector3.zero;planted[0]=planted[1]=false;speed=0;groundOffset=0; }
            if(freeze) return;
            visualTime+=dt;
            speed=Mathf.Lerp(speed,delta.magnitude/Mathf.Max(.001f,dt),1-Mathf.Exp(-10*dt));
            float jog=Mathf.InverseLerp(1.5f,3.5f,speed);
            cycle=Mathf.Repeat(cycle+delta.magnitude/Mathf.Max(.1f,motion.Stride(jog)*legLength),1);
            if(delta.sqrMagnitude>.00001f && !holdingBall) facing=delta;
            if(facing.sqrMagnitude>.01f) transform.rotation=Quaternion.Slerp(transform.rotation,Quaternion.LookRotation(facing),1-Mathf.Exp(-12*dt));
            ApplyPose(jog,Mathf.Clamp01(speed/.6f),holdingBall,carryingStone,ducking,charge,true);
        }
        // Deterministic editor pose inspection; this does not animate gameplay roots.
        public void PreviewMotion(float phase,float metersPerSecond)
        {
            Initialize();cycle=Mathf.Repeat(phase,1);speed=metersPerSecond;planted[0]=planted[1]=false;
            ApplyPose(Mathf.InverseLerp(1.5f,3.5f,speed),1,false,false,false,0,false);
        }
        private void ApplyPose(float jog,float moving,bool holding,bool carrying,bool ducking,float charge,bool lockFeet)
        {
            foreach(var pair in rest) if(pair.Key!=transform) pair.Key.localRotation=pair.Value;
            motion.Sample(cycle,jog,directions,out float bob,out float roll,out bool left,out bool right);
            transform.localPosition=new Vector3(0,-.9f+groundOffset+bob*legLength*moving-(ducking?.3f:0),0);
            if(bones.TryGetValue("pelvis",out var pelvis)) pelvis.rotation=Quaternion.AngleAxis(roll*moving,transform.forward)*pelvis.rotation;
            for(int i=0;i<driven.Length;i++)
            {
                string name=motion.bones[i];
                Vector3 idle=name.StartsWith("spine")||name.StartsWith("neck")?Vector3.up:
                    name.StartsWith("foot")?new Vector3(0,-.06f,1):new Vector3(name.EndsWith("_l")?-.06f:.06f,-1,.06f);
                bool torso=name.StartsWith("spine")||name.StartsWith("neck");
                if(torso) idle=bindDirections[i];
                Vector3 captured=torso?Quaternion.FromToRotation(referenceDirections[i],directions[i])*bindDirections[i]:directions[i];
                Vector3 desired=Vector3.Slerp(idle,captured,moving);
                if(ducking && name.StartsWith("thigh")) desired=new Vector3(desired.x,-.7f,.7f);
                if(ducking && name.StartsWith("calf")) desired=new Vector3(desired.x,-.65f,-.75f);
                Aim(driven[i],ends[i],desired);
            }
            if(holding||carrying||visualTime-throwTime<.42f) { Arm("l",holding,carrying,charge);Arm("r",holding,carrying,charge); }
            float lowest=Mathf.Min(bones["foot_l"].position.y,bones["ball_l"].position.y,bones["foot_r"].position.y,bones["ball_r"].position.y)-.04f;
            if(left||right||moving<.2f||ducking||lowest<.015f)
            { float correction=.015f-lowest;groundOffset+=correction;transform.position+=Vector3.up*correction; }
            PlantError=0;
            for(int side=0;side<2;side++)
            {
                bool contact=side==0?left:right;
                string suffix=Sides[side];var foot=bones["foot_"+suffix];
                bool plant=lockFeet&&contact&&moving>.5f&&!ducking;
                if(plant && !planted[side]) { anchors[side]=foot.position;anchors[side].y=ankleHeight; }
                if(plant) anchors[side].y=Mathf.Max(ankleHeight,.055f-(bones["ball_"+suffix].position.y-foot.position.y));
                planted[side]=plant;
                if(plant)
                {
                    var thigh=bones["thigh_"+suffix];var calf=bones["calf_"+suffix];
                    if(Vector3.Distance(thigh.position,anchors[side])>legLength*.99f) { planted[side]=false;continue; }
                    SolveLeg(thigh,calf,foot,anchors[side]);PlantError=Mathf.Max(PlantError,Vector3.Distance(foot.position,anchors[side]));
                }
            }
        }
        private void Arm(string side,bool holding,bool carrying,float charge)
        {
            var upper=bones["upperarm_"+side];var lower=bones["lowerarm_"+side];var hand=bones["hand_"+side];
            float lateral=side=="l"?-1:1;
            Vector3 a=new Vector3(lateral*.14f,-.94f,.05f),b=new Vector3(lateral*.05f,-.95f,.12f);
            if(carrying) { a=new Vector3(lateral*.22f,-.7f,.5f);b=new Vector3(-lateral*.15f,.1f,1); }
            if(side=="r"&&holding)
            {
                float t=Mathf.SmoothStep(0,1,charge);
                a=Vector3.Lerp(new Vector3(lateral*.25f,-.85f,.15f),new Vector3(lateral*.35f,.15f,-.8f),t);
                b=Vector3.Lerp(new Vector3(0,.15f,1),new Vector3(0,1,.15f),t);
            }
            float follow=(visualTime-throwTime)/.42f;
            if(side=="r"&&follow>=0&&follow<1) { a=new Vector3(lateral*.12f,.7f-follow*1.2f,1);b=new Vector3(0,.25f-follow*.6f,1); }
            Aim(upper,lower,a);Aim(lower,hand,b);
        }
        private void SolveLeg(Transform hip,Transform knee,Transform ankle,Vector3 target)
        {
            Quaternion footRotation=ankle.rotation;Vector3 start=hip.position,offset=target-start;
            float a=Vector3.Distance(start,knee.position),b=Vector3.Distance(knee.position,ankle.position);
            float distance=Mathf.Clamp(offset.magnitude,Mathf.Abs(a-b)+.0001f,a+b-.0001f);
            Vector3 axis=offset.normalized,bend=Vector3.ProjectOnPlane(transform.forward,axis).normalized;
            float cosine=Mathf.Clamp((a*a+distance*distance-b*b)/(2*a*distance),-1,1);
            Vector3 desiredKnee=start+axis*(a*cosine)+bend*(a*Mathf.Sqrt(1-cosine*cosine));
            hip.rotation=Quaternion.FromToRotation(knee.position-start,desiredKnee-start)*hip.rotation;
            knee.rotation=Quaternion.FromToRotation(ankle.position-knee.position,target-knee.position)*knee.rotation;
            ankle.rotation=footRotation;
        }
        private void Aim(Transform bone,Transform child,Vector3 desired)
        {
            Vector3 current=child.position-bone.position;
            if(current.sqrMagnitude>.000001f) bone.rotation=Quaternion.FromToRotation(current,transform.TransformDirection(desired.normalized))*bone.rotation;
        }
    }
}
