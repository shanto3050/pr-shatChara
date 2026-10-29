using System;
using UnityEditor;
using UnityEngine;

namespace SatChara.Editor
{
    public static partial class VillageBuild
    {
        public static void ValidateAnimation()
        {
            Prepare();
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(Art+"Characters/VillageCharacter.prefab");
            var driver=new GameObject("Animation validation driver");driver.transform.position=Vector3.up*.9f;
            var avatar=UnityEngine.Object.Instantiate(prefab,driver.transform).GetComponent<VillageAvatar>();
            avatar.transform.localPosition=Vector3.down*.9f;
            var camera=Camera.main;camera.orthographic=false;camera.fieldOfView=40;
            camera.transform.position=new Vector3(4,1.3f,-.3f);camera.transform.LookAt(new Vector3(0,.85f,0));
            for(int warm=0;warm<60;warm++) avatar.PreviewMotion(warm/60f,3.5f);
            for(int i=0;i<4;i++)
            {
                avatar.PreviewMotion(i*.25f,3.5f);
                CaptureSkinnedPose(avatar,camera,"animation-jog-"+i+".png");
            }
            UnityEngine.Object.DestroyImmediate(driver);
            foreach(float speed in new[]{1.3f,3.5f})
            {
                driver=new GameObject("Animation validation driver");driver.transform.position=Vector3.up*.9f;
                avatar=UnityEngine.Object.Instantiate(prefab,driver.transform).GetComponent<VillageAvatar>();
                avatar.transform.localPosition=Vector3.down*.9f;
                float maxError=0,maxSlip=0,minSole=float.PositiveInfinity;int plants=0,continuations=0;
                bool lastLeft=false,lastRight=false;Vector3 left=Vector3.zero,right=Vector3.zero;
                for(int tick=0;tick<360;tick++)
                {
                    Vector3 heading=tick<180?Vector3.forward:Vector3.right;
                    driver.transform.position+=heading*(speed*.02f);Vector3 position=driver.transform.position;
                    avatar.Drive(heading,false,false,false,frameDelta:.02f);
                    if(driver.transform.position!=position) throw new Exception("Animation moved authoritative gameplay root");
                    if(avatar.LeftPlanted)plants++;if(avatar.RightPlanted)plants++;
                    if(avatar.LeftPlanted&&lastLeft) { maxSlip=Mathf.Max(maxSlip,Horizontal(avatar.LeftFoot-left));continuations++; }
                    if(avatar.RightPlanted&&lastRight) { maxSlip=Mathf.Max(maxSlip,Horizontal(avatar.RightFoot-right));continuations++; }
                    left=avatar.LeftFoot;right=avatar.RightFoot;lastLeft=avatar.LeftPlanted;lastRight=avatar.RightPlanted;
                    maxError=Mathf.Max(maxError,avatar.PlantError);minSole=Mathf.Min(minSole,left.y-.04f,right.y-.04f);
                    if(float.IsNaN(left.x)||float.IsNaN(right.x)) throw new Exception("Non-finite retargeted foot");
                }
                Vector3 pausedFoot=avatar.LeftFoot;
                avatar.Drive(Vector3.forward,false,false,false,freeze:true,frameDelta:1);
                if(Vector3.Distance(pausedFoot,avatar.LeftFoot)>.0001f) throw new Exception("Paused animation advanced");
                if(plants<60 || continuations<40 || maxError>.025f || maxSlip>.025f || minSole<-.01f)
                    throw new Exception($"Animation contact failed: speed={speed}, plants={plants}, continued={continuations}, error={maxError}, slip={maxSlip}, sole={minSole}");
                Debug.Log($"SAT_CHARA_ANIMATION_PASS: speed={speed}, plants={plants}, continued={continuations}, maxPlantError={maxError:F5}, maxHorizontalSlip={maxSlip:F5}, minSole={minSole:F5}, pause=held, root=unchanged");
                UnityEngine.Object.DestroyImmediate(driver);
            }
        }
        private static void CaptureSkinnedPose(VillageAvatar avatar,Camera camera,string filename)
        {
            var skins=avatar.GetComponentsInChildren<SkinnedMeshRenderer>();
            var snapshots=new System.Collections.Generic.List<GameObject>();
            try
            {
                foreach(var skin in skins)
                {
                    var mesh=new Mesh();skin.BakeMesh(mesh);
                    var ob=new GameObject("Pose snapshot",typeof(MeshFilter),typeof(MeshRenderer));ob.transform.SetParent(skin.transform,false);
                    ob.GetComponent<MeshFilter>().sharedMesh=mesh;ob.GetComponent<MeshRenderer>().sharedMaterials=skin.sharedMaterials;
                    skin.enabled=false;snapshots.Add(ob);
                }
                CaptureCamera(camera,filename);
            }
            finally
            {
                foreach(var ob in snapshots) { UnityEngine.Object.DestroyImmediate(ob.GetComponent<MeshFilter>().sharedMesh);UnityEngine.Object.DestroyImmediate(ob); }
                foreach(var skin in skins)skin.enabled=true;
            }
        }
        // Offline URP preview, explicitly separate from actual-device playback.
        public static void CaptureMotionPreview()
        {
            Prepare();
            System.IO.Directory.CreateDirectory(System.IO.Path.GetFullPath("../../.verification/village/motion-preview"));
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(Art+"Characters/VillageCharacter.prefab");
            var camera=Camera.main;camera.orthographic=false;camera.fieldOfView=40;
            foreach(float speed in new[]{1.3f,3.5f})
            {
                string label=speed<2?"walk":"jog";
                var driver=new GameObject("Motion preview driver");driver.transform.position=Vector3.up*.9f;
                var avatar=UnityEngine.Object.Instantiate(prefab,driver.transform).GetComponent<VillageAvatar>();avatar.transform.localPosition=Vector3.down*.9f;
                for(int frame=-30;frame<60;frame++)
                {
                    driver.transform.position+=Vector3.forward*(speed/30);
                    avatar.Drive(Vector3.forward,false,false,false,frameDelta:1f/30);
                    camera.transform.position=driver.transform.position+new Vector3(4,.4f,-.3f);camera.transform.LookAt(driver.transform.position);
                    if(frame>=0)CaptureSkinnedPose(avatar,camera,"motion-preview/"+label+"-"+frame.ToString("D3")+".png");
                }
                UnityEngine.Object.DestroyImmediate(driver);
            }
            Debug.Log("SAT_CHARA_MOTION_PREVIEW_READY: offline 60-frame walk and jog sequences");
        }
        private static float Horizontal(Vector3 delta) { delta.y=0;return delta.magnitude; }
        public static void VerifyAnimationAndBuild() { ValidateAnimation();VerifyAndBuild(); }
    }
}
