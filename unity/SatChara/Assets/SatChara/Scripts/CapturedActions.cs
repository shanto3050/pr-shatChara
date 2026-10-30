using System;
using UnityEngine;

namespace SatChara
{
    // One-shot recorded CMU actions (throw, pick up, place, duck, dodge) in the same direction space as
    // CapturedLocomotion: one direction per mapped bone. x is the character's anatomical right, y up,
    // z forward. Pelvis height and root travel are in leg lengths; gameplay still owns the real root
    // movement. Events (release, grab, place, lowest, step) are times in seconds from the clip start.
    // Source: art-source/convert_cmu_actions.py.
    [Serializable]
    public sealed class CapturedActions
    {
        [Serializable] public sealed class Event { public string name; public float time; }
        [Serializable] public sealed class Frame
        {
            public Vector3[] directions;
            public float pelvis, roll;
            public Vector3 root;
            public bool leftContact, rightContact;
        }
        [Serializable] public sealed class Clip
        { public string name; public float duration; public bool loop; public Event[] events; public Frame[] frames; }
        public string[] bones, children;
        public float fps;
        public Clip[] clips;

        public static CapturedActions Load(TextAsset source)
        {
            if (!source) throw new InvalidOperationException("Captured actions asset is missing");
            var data=JsonUtility.FromJson<CapturedActions>(source.text);
            if (data.bones==null || data.children==null || data.children.Length!=data.bones.Length || data.clips==null || data.clips.Length==0)
                throw new InvalidOperationException("Invalid captured actions schema");
            foreach(var clip in data.clips)
            {
                if(clip.frames==null || clip.frames.Length<2 || clip.duration<=0) throw new InvalidOperationException("Invalid captured action: "+clip.name);
                foreach(var frame in clip.frames) if(frame.directions.Length!=data.bones.Length)
                    throw new InvalidOperationException("Captured action frame has inconsistent bone count: "+clip.name);
            }
            return data;
        }

        public Clip Find(string name)
        {
            foreach(var clip in clips) if(clip.name==name) return clip;
            return null;
        }

        // Time of a named event (e.g. "release"), or -1 if the clip has none.
        public static float EventTime(Clip clip,string name)
        {
            if(clip.events!=null) foreach(var e in clip.events) if(e.name==name) return e.time;
            return -1;
        }

        // Pose at a time in seconds (clamped to the clip). Directions are written into the caller's array.
        public static void Sample(Clip clip,float time,Vector3[] directions,out float pelvis,out float roll,out Vector3 root,out bool left,out bool right)
        {
            float frame=Mathf.Clamp(time,0,clip.duration)/clip.duration*(clip.frames.Length-1);
            int a=Mathf.FloorToInt(frame),b=Mathf.Min(a+1,clip.frames.Length-1);float t=frame-a;
            var f0=clip.frames[a];var f1=clip.frames[b];
            for(int i=0;i<directions.Length;i++) directions[i]=Vector3.Slerp(f0.directions[i],f1.directions[i],t);
            pelvis=Mathf.Lerp(f0.pelvis,f1.pelvis,t);
            roll=Mathf.Lerp(f0.roll,f1.roll,t);
            root=Vector3.Lerp(f0.root,f1.root,t);
            var contact=t<.5f?f0:f1;
            left=contact.leftContact;right=contact.rightContact;
        }
    }
}
