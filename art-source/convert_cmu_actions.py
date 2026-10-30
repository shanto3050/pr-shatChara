"""Convert official CMU ASF/AMC takes into one-shot game actions (throw, pick up, place, duck, dodge).
Same direction-space format as CapturedLocomotion.json, plus root travel, pelvis height and event times.
Run with Blender's Python (numpy is bundled). Sources and SHA-256 digests: motion/cmu/manifest.json.
CMU reuse terms: http://mocap.cs.cmu.edu/faqs.php
"""
import json, math, hashlib
import numpy as np
from convert_cmu_motion import ROOT, SOURCE, OUT, MAP, skeleton, frames, forward_kinematics, vector

FPS_IN, FPS_OUT = 120, 30
UP = np.array([0., 1., 0.])

def flat(v):
    v = np.array(v, float); v[1] = 0; n = np.linalg.norm(v)
    return v / n if n > 1e-9 else np.array([0., 0., 1.])

def facing(p):
    """Forward direction of the body from the hip line. In CMU data (right hip minus left hip) x up points
    backwards: checked against walk 02_01, where it is opposite to the direction of travel."""
    right = flat(p['rhipjoint'] - p['lhipjoint'])
    return flat(np.cross(UP, right))

def speed(track, i):
    a, b = max(0, i - 2), min(len(track) - 1, i + 2)
    return np.linalg.norm(track[b] - track[a]) * FPS_IN / max(1, b - a)

# name, subject, take, how to find the key moment, seconds before/after it, event name
ACTIONS = [
    ('Throw',       '124', '124_01', 'throw',  .95, .65, 'release'),   # baseball pitch: full overarm throw
    ('ThrowCasual', '111', '111_33', 'throw',  .75, .55, 'release'),   # everyday throw
    ('PickUp',      '111', '111_17', 'lowest_hand', .95, .85, 'grab'),  # bend down, feet still (64_26-30 all stepped or kicked)
    ('PickUpSquat', '111', '111_18', 'lowest_hand', .95, .9, 'grab'),   # squat right down to the ground
    ('Place',       '69',  '69_75',  'second_lowest_hand', .9, .8, 'place'),  # squat and set an object down
    ('Duck',        '139', '139_09', 'lowest_head', .55, .75, 'lowest'),
    ('DodgeRight',  '127', '127_14', 'side_step', .45, .55, 'step'),
]
# 127_13 "Run Side Step Left" barely moves sideways (0.08 leg lengths), so DodgeLeft mirrors DodgeRight.
MIRRORS = [('DodgeLeft', 'DodgeRight')]

def mirror(clip, name, bone_names):
    swap = [bone_names.index(b[:-1] + ('r' if b.endswith('l') else 'l')) if b[-2:] in ('_l', '_r') else i
            for i, b in enumerate(bone_names)]
    m = json.loads(json.dumps(clip)); m['name'] = name
    for f, src in zip(m['frames'], clip['frames']):
        f['directions'] = [dict(src['directions'][swap[i]], x=-src['directions'][swap[i]]['x']) for i in range(len(swap))]
        f['root'] = dict(src['root'], x=-src['root']['x']); f['roll'] = -src['roll']
        f['leftContact'], f['rightContact'] = src['rightContact'], src['leftContact']
    return m

def key_frame(kind, solved, roots, basis_guess):
    n = len(solved)
    if kind == 'throw':
        hand = np.array([p['rwrist'] for p, d in solved])
        sp = np.array([speed(hand, i) for i in range(n)])
        return int(np.argmax(sp[5:-5]) + 5)
    if kind in ('lowest_hand', 'second_lowest_hand'):
        low = np.array([min(p['lwrist'][1], p['rwrist'][1]) for p, d in solved])
        sm = np.convolve(low, np.ones(15) / 15, mode='same')
        first = int(np.argmin(sm[10:-10]) + 10)
        if kind == 'lowest_hand': return first
        mask = np.abs(np.arange(n) - first) > 1.5 * FPS_IN                  # the other trough: setting down
        sm2 = np.where(mask, sm, np.inf); second = int(np.argmin(sm2[10:-10]) + 10)
        return max(first, second)                                          # the later one is the set-down
    if kind == 'lowest_head':
        head = np.array([p['head'][1] for p, d in solved])
        return int(np.argmin(np.convolve(head, np.ones(9) / 9, mode='same')[10:-10]) + 10)
    if kind == 'side_step':
        lat = np.array([abs(np.dot((roots[min(i + 2, n - 1)] - roots[max(i - 2, 0)]) * [1, 0, 1], basis_guess[0]))
                        for i in range(n)])
        return int(np.argmax(lat[10:-10]) + 10)
    raise ValueError(kind)

def convert(name, subject, take, kind, before, after, event):
    bones, children = skeleton(SOURCE / f'{subject}.asf')
    raw = frames(SOURCE / f'{take}.amc')
    solved = [forward_kinematics(f, bones, children) for f in raw]
    roots = np.array([p['root'] for p, d in solved])
    leg = bones['lfemur']['length'] + bones['ltibia']['length']
    # heading: throws face the direction the hand travels at release; everything else faces the hips' forward
    guess_fwd = facing(solved[len(solved) // 2][0]); guess = np.array([np.cross(UP, guess_fwd), UP, guess_fwd])
    k = key_frame(kind, solved, roots, guess)
    a, b = max(0, k - int(before * FPS_IN)), min(len(solved) - 1, k + int(after * FPS_IN))
    stride = (roots[b] - roots[a]) * [1, 0, 1]
    if kind == 'throw' and np.linalg.norm(stride) > .3 * leg:
        fwd = flat(stride)                                                     # pitchers stride toward the target
    elif kind == 'throw':
        hand = np.array([p['rwrist'] for p, d in solved])
        fwd = flat(hand[min(k + 2, len(hand) - 1)] - hand[max(k - 2, 0)])
    else:
        fwd = facing(solved[k][0])
    # x must be the subject's anatomical right (Unity: x right, y up, z forward). np.cross(UP, fwd), as used in
    # convert_cmu_motion.py, points to the subject's left in CMU data and would mirror a right-handed throw.
    right = np.cross(fwd, UP); basis = np.array([right, UP, fwd])
    stand = float(np.median(roots[a:a + 12, 1]))                              # standing pelvis height at the start
    floor = min(min(p['ltoes'][1], p['rtoes'][1]) for p, d in solved[a:b + 1])
    out = []
    for s in np.linspace(a, b, int(round((b - a) / FPS_IN * FPS_OUT)) + 1):
        i = int(round(s)); p, d = solved[i]; contacts = []
        for toe in ('ltoes', 'rtoes'):
            v = (solved[min(i + 2, len(solved) - 1)][0][toe] - solved[max(i - 2, 0)][0][toe]) * FPS_IN / 4
            contacts.append(bool(p[toe][1] < floor + leg * .09 and np.linalg.norm(v * [1, 0, 1]) < leg * .6))
        hips = basis @ (p['rhipjoint'] - p['lhipjoint'])
        travel = basis @ ((roots[i] - roots[a]) * [1, 0, 1]) / leg
        out.append({'directions': [vector(basis @ d[src]) for _, _, src in MAP],
                    'pelvis': round((roots[i, 1] - stand) / leg, 6),
                    'roll': round(math.degrees(math.atan2(hips[1], abs(hips[0]))), 5),
                    'root': vector(travel),
                    'leftContact': contacts[0], 'rightContact': contacts[1]})
    clip = {'name': name, 'duration': round((b - a) / FPS_IN, 6), 'loop': False,
            'events': [{'name': event, 'time': round((k - a) / FPS_IN, 6)}], 'frames': out}
    info = {'name': name, 'source': f'{take}.amc', 'subject': subject, 'key': kind, 'key_frame': k + 1,
            'window': [a + 1, b + 1], 'frames': len(out), 'duration': clip['duration'], 'event_time': clip['events'][0]['time'],
            'min_pelvis': round(min(f['pelvis'] for f in out), 4),
            'root_end': out[-1]['root'],
            'sha256': hashlib.sha256((SOURCE / f'{take}.amc').read_bytes()).hexdigest()}
    return clip, info

if __name__ == '__main__':
    clips, summary = [], []
    for args in ACTIONS:
        c, info = convert(*args); clips.append(c); summary.append(info)
    names = [a for a, b, c in MAP]
    for new, src in MIRRORS:
        clips.append(mirror(next(c for c in clips if c['name'] == src), new, names))
        summary.append({'name': new, 'mirror_of': src})
    data = {'bones': names, 'children': [b for a, b, c in MAP], 'fps': FPS_OUT, 'clips': clips}
    (OUT / 'CapturedActions.json').write_text(json.dumps(data, separators=(',', ':')))
    (ROOT / 'captured-actions-summary.json').write_text(json.dumps(summary, indent=2))
    print('CMU_ACTIONS', json.dumps(summary, indent=2))
