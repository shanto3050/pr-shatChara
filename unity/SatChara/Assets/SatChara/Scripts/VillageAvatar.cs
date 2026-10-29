using System.Collections.Generic;
using UnityEngine;

namespace SatChara
{
    // First-pass skeletal poses, driven by actual gameplay displacement.
    public sealed class VillageAvatar : MonoBehaviour
    {
        private readonly Dictionary<string, Transform> bones = new Dictionary<string, Transform>();
        private readonly Dictionary<Transform, Quaternion> rest = new Dictionary<Transform, Quaternion>();
        private static readonly string[] SupportBones = { "foot_l", "ball_l", "foot_r", "ball_r" };
        private Vector3 previousPosition;
        private float phase, throwTime = -10;
        private bool ready;
        public Vector3 HandPosition => bones.TryGetValue("hand_r", out var hand) ? hand.position : transform.position + Vector3.up;
        private void Initialize()
        {
            if (ready) return;
            ready = true;
            foreach (var bone in GetComponentsInChildren<Transform>())
            { bones[bone.name] = bone; rest[bone] = bone.localRotation; }
            previousPosition = transform.parent.position;
        }
        public void Throw() => throwTime = Time.time;
        public void Drive(Vector3 facing, bool holdingBall, bool carryingStone, bool ducking)
        {
            Initialize();
            Vector3 delta = transform.parent.position - previousPosition; delta.y = 0;
            previousPosition = transform.parent.position;
            if (delta.magnitude > 2) delta = Vector3.zero;
            float speed = delta.magnitude / Mathf.Max(.001f, Time.deltaTime);
            phase += delta.magnitude * Mathf.PI * 2 / 2.2f;
            if (speed > .15f && !holdingBall) facing = delta;
            if (facing.sqrMagnitude > .01f)
                transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(facing), 1 - Mathf.Exp(-12 * Time.deltaTime));
            foreach (var pair in rest) if (pair.Key != transform) pair.Key.localRotation = pair.Value;
            float gait = Mathf.Clamp01(speed / 3.5f);
            float left = Mathf.Sin(phase), right = -left;
            transform.localPosition = new Vector3(0, -.9f + Mathf.Abs(Mathf.Sin(phase * 2)) * .025f * gait - (ducking ? .35f : 0), 0);
            Leg("l", left, gait, ducking); Leg("r", right, gait, ducking);
            Arm("l", -left, gait, holdingBall, carryingStone);
            Arm("r", -right, gait, holdingBall, carryingStone);
            // Keep the support foot on the flat gameplay ground while this temporary
            // pose controller is used. Production animation will use foot IK.
            float sole = float.PositiveInfinity;
            foreach (string key in SupportBones)
                if (bones.TryGetValue(key, out var support)) sole = Mathf.Min(sole, support.position.y - .04f);
            if (!float.IsPositiveInfinity(sole)) transform.position += Vector3.up * (.015f - sole);
        }
        private void Leg(string side, float wave, float gait, bool ducking)
        {
            float hip = wave * .65f * gait + (ducking ? .7f : 0);
            float knee = (.12f + Mathf.Max(0, wave) * .9f) * gait + (ducking ? 1.3f : 0);
            Aim("thigh_" + side, "calf_" + side, new Vector3(0, -Mathf.Cos(hip), Mathf.Sin(hip)));
            float shin = hip - knee;
            Aim("calf_" + side, "foot_" + side, new Vector3(0, -Mathf.Cos(shin), Mathf.Sin(shin)));
            Aim("foot_" + side, "ball_" + side, new Vector3(0, -.06f, 1));
        }
        private void Arm(string side, float wave, float gait, bool holding, bool carrying)
        {
            string upper = "upperarm_" + side, lower = "lowerarm_" + side, hand = "hand_" + side;
            if (!bones.TryGetValue(upper, out var arm) || !bones.TryGetValue(lower, out var elbow)) return;
            float lateral = Mathf.Sign(Vector3.Dot(elbow.position - arm.position, transform.right));
            Vector3 upperDirection = new Vector3(lateral * .14f, -.94f, wave * .5f * gait);
            Vector3 lowerDirection = new Vector3(lateral * .05f, -.95f, .12f + Mathf.Abs(wave) * .25f * gait);
            if (carrying)
            { upperDirection = new Vector3(lateral * .22f, -.7f, .5f); lowerDirection = new Vector3(-lateral * .15f, .1f, 1); }
            if (side == "r" && holding)
            { upperDirection = new Vector3(lateral * .35f, .15f, -.8f); lowerDirection = new Vector3(0, 1, .15f); }
            float follow = (Time.time - throwTime) / .42f;
            if (side == "r" && follow >= 0 && follow < 1)
            { upperDirection = new Vector3(lateral * .12f, .7f - follow * 1.2f, 1); lowerDirection = new Vector3(0, .25f - follow * .6f, 1); }
            Aim(upper, lower, upperDirection); Aim(lower, hand, lowerDirection);
        }
        private void Aim(string name, string childName, Vector3 desired)
        {
            if (!bones.TryGetValue(name, out var bone) || !bones.TryGetValue(childName, out var child)) return;
            Vector3 current = child.position - bone.position;
            if (current.sqrMagnitude < .000001f) return;
            bone.rotation = Quaternion.FromToRotation(current, transform.TransformDirection(desired.normalized)) * bone.rotation;
        }
    }
}
