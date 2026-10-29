using System;
using UnityEngine;

namespace SatChara
{
    // Direction-space retargeting of recorded CMU ASF/AMC motion. Root travel is
    // owned by gameplay; stride phase is driven by measured travel distance.
    [Serializable]
    public sealed class CapturedLocomotion
    {
        [Serializable] public sealed class Frame
        {
            public Vector3[] directions;
            public float pelvis, roll;
            public bool leftContact, rightContact;
        }
        [Serializable] public sealed class Clip
        { public string name; public float duration,stride; public Frame[] frames; }
        public string[] bones, children;
        public Clip[] clips;
        public float Stride(float jog) => Mathf.Lerp(clips[0].stride,clips[1].stride,jog);
        public static CapturedLocomotion Load(TextAsset source)
        {
            if (!source) throw new InvalidOperationException("Captured locomotion asset is missing");
            var data=JsonUtility.FromJson<CapturedLocomotion>(source.text);
            if (data.bones==null || data.children.Length!=data.bones.Length || data.clips.Length!=2)
                throw new InvalidOperationException("Invalid captured locomotion schema");
            foreach(var clip in data.clips)
            {
                if(clip.frames.Length<4 || clip.stride<=0) throw new InvalidOperationException("Invalid captured stride");
                foreach(var frame in clip.frames) if(frame.directions.Length!=data.bones.Length)
                    throw new InvalidOperationException("Captured frame has inconsistent bone count");
            }
            return data;
        }
        private static void Indices(Clip clip,float phase,out int a,out int b,out float t)
        {
            float frame=Mathf.Repeat(phase,1)*(clip.frames.Length-1);
            a=Mathf.FloorToInt(frame);b=Mathf.Min(a+1,clip.frames.Length-1);t=frame-a;
        }
        public void Sample(float phase,float jog,Vector3[] directions,out float bob,out float roll,out bool left,out bool right)
        {
            Indices(clips[0],phase,out int wa,out int wb,out float wt);
            Indices(clips[1],phase,out int ra,out int rb,out float rt);
            var w0=clips[0].frames[wa];var w1=clips[0].frames[wb];
            var r0=clips[1].frames[ra];var r1=clips[1].frames[rb];
            for(int i=0;i<directions.Length;i++)
                directions[i]=Vector3.Slerp(Vector3.Slerp(w0.directions[i],w1.directions[i],wt),Vector3.Slerp(r0.directions[i],r1.directions[i],rt),jog);
            bob=Mathf.Lerp(Mathf.Lerp(w0.pelvis,w1.pelvis,wt),Mathf.Lerp(r0.pelvis,r1.pelvis,rt),jog);
            roll=Mathf.Lerp(Mathf.Lerp(w0.roll,w1.roll,wt),Mathf.Lerp(r0.roll,r1.roll,rt),jog);
            var contact=jog<.5f?(wt<.5f?w0:w1):(rt<.5f?r0:r1);
            left=contact.leftContact;right=contact.rightContact;
        }
    }
}
