"""Score CMU pick-up takes for game use: foot lift and travel (want small), hand height at the lowest point
(want near the ground), pelvis drop and knee bend. Run with Blender's Python from art-source/."""
import sys; sys.path.insert(0, '.')
import numpy as np
from convert_cmu_actions import skeleton, frames, forward_kinematics, SOURCE, key_frame, UP, facing
FPS = 120
for subj, take in [('64','64_26'),('64','64_27'),('64','64_28'),('64','64_29'),('64','64_30'),('115','115_06'),('115','115_07'),('115','115_08'),('111','111_17'),('111','111_18')]:
    bones, ch = skeleton(SOURCE/f'{subj}.asf'); sol = [forward_kinematics(f, bones, ch) for f in frames(SOURCE/f'{take}.amc')]
    roots = np.array([p['root'] for p, d in sol]); leg = bones['lfemur']['length'] + bones['ltibia']['length']
    k = key_frame('lowest_hand', sol, roots, None); a, b = max(0, k - int(.95*FPS)), min(len(sol)-1, k + int(.85*FPS))
    floor = min(min(p['ltoes'][1], p['rtoes'][1]) for p, d in sol[a:b+1])
    lift = max(max(p['ltoes'][1], p['rtoes'][1]) for p, d in sol[a:b+1]) - floor
    travel = sum(np.linalg.norm((sol[b][0][t] - sol[a][0][t]) * [1,0,1]) for t in ('ltoes','rtoes'))
    hand = min(sol[k][0]['lwrist'][1], sol[k][0]['rwrist'][1]) - floor
    drop = (np.median(roots[a:a+12,1]) - roots[k,1])
    knee = np.degrees(np.arccos(np.clip(np.dot((sol[k][0]['lfemur']-sol[k][0]['lhipjoint']), (sol[k][0]['ltibia']-sol[k][0]['lfemur']))/(np.linalg.norm(sol[k][0]['lfemur']-sol[k][0]['lhipjoint'])*np.linalg.norm(sol[k][0]['ltibia']-sol[k][0]['lfemur'])),-1,1)))
    print(f'{take:7s} foot_lift {lift/leg:5.2f}  feet_travel {travel/leg:5.2f}  hand_height {hand/leg:5.2f}  pelvis_drop {drop/leg:5.2f}  knee_bend {knee:5.1f}deg')
