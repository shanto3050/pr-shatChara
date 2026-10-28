#if SAT_CHARA_VISUAL_SLICE_WIP
// Incomplete editor authoring tool. See docs/visual-slice-status.md before enabling.
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace SatChara.Editor
{
    public static partial class VillageBuild
    {
        private static GameObject CharacterPrefab()
        {
            string source=Art+"Characters/VillagePlayer.fbx";
            var importer=(ModelImporter)AssetImporter.GetAtPath(source);
            importer.importAnimation=false; importer.animationType=ModelImporterAnimationType.Generic;
            importer.optimizeGameObjects=false; importer.SaveAndReimport();
            var root=new GameObject("Village Character");
            var model=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(source));
            model.transform.SetParent(root.transform,false);
            var bones=model.GetComponentsInChildren<Transform>();
            var toe=bones.First(t=>t.name=="ball_l");var foot=bones.First(t=>t.name=="foot_l");
            Vector3 forward=toe.position-foot.position;forward.y=0;
            if(forward.sqrMagnitude>.001f) model.transform.rotation=Quaternion.FromToRotation(forward.normalized,Vector3.forward)*model.transform.rotation;
            Fit(model,1.7f);
            foreach(var animator in model.GetComponentsInChildren<Animator>()) animator.enabled=false;
            foreach(var renderer in model.GetComponentsInChildren<Renderer>())
            {
                var materials=renderer.sharedMaterials;
                for(int i=0;i<materials.Length;i++)
                {
                    string name=materials[i] ? materials[i].name.ToLowerInvariant() : "body";
                    if(name.Contains("male_casual"))
                    {
                        materials[i]=Surface("Striped Cotton", "Characters/Textures/male_casualsuit03_diffuse.png",Color.white,0,.12f);
                        materials[i].SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Art+"Characters/Textures/male_casualsuit03_normal.png"));
                        materials[i].SetFloat("_BumpScale",.4f);materials[i].EnableKeyword("_NORMALMAP");
                    }
                    else if(name.Contains("eyebrow")) materials[i]=Surface("Eyebrows","Characters/Textures/eyebrow001.png",Color.white,0,.1f,true);
                    else if(name.Contains("short01")) materials[i]=Surface("Black Hair","Characters/Textures/short01_diffuse.png",new Color(.5f,.45f,.4f),0,.16f,true);
                    else if(name.Contains("low-poly")) materials[i]=Surface("Brown Eyes","Characters/Textures/brown_eye.png",Color.white,0,.45f);
                    else materials[i]=Surface("Warm Brown Skin","Characters/Textures/young_lightskinned_male_diffuse3.png",new Color(.86f,.72f,.6f),0,.2f);
                }
                renderer.sharedMaterials=materials;renderer.shadowCastingMode=ShadowCastingMode.On;
                if(renderer is SkinnedMeshRenderer skin) skin.updateWhenOffscreen=false;
            }
            root.AddComponent<VillageAvatar>();
            var prefab=PrefabUtility.SaveAsPrefabAsset(root,Art+"Characters/VillageCharacter.prefab");
            Debug.Log("VILLAGE_CHARACTER_BOUNDS: "+BoundsOf(model));
            UnityEngine.Object.DestroyImmediate(root);return prefab;
        }

        private static GameObject EnvironmentPrefab(string name,float height)
        {
            string source=Art+"Environment/"+name+".fbx";
            var root=new GameObject(name);
            var model=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(source));
            model.transform.SetParent(root.transform,false);Fit(model,height);
            foreach(var renderer in model.GetComponentsInChildren<Renderer>())
            {
                var materials=renderer.sharedMaterials;
                for(int i=0;i<materials.Length;i++)
                {
                    string label=materials[i] ? materials[i].name.ToLowerInvariant() : name;
                    if(name=="barrel_03") materials[i]=Surface("Blue Steel Drum","Environment/Textures/barrel_03_diff_1k.jpg",Color.white,.5f,.23f);
                    else if(label.Contains("leaves")) materials[i]=Surface("Tree Leaves","Environment/Textures/island_tree_01_leaves_diff_1k.png",new Color(.8f,.9f,.66f),0,.08f,true);
                    else if(label.Contains("branches")) materials[i]=Surface("Tree Branches","Environment/Textures/island_tree_01_branches_diff_1k.png",Color.white,0,.08f,true);
                    else materials[i]=Surface("Tree Bark","Environment/Textures/island_tree_01_diff_1k.jpg",Color.white,0,.08f);
                }
                renderer.sharedMaterials=materials;
            }
            var prefab=PrefabUtility.SaveAsPrefabAsset(root,Art+"Environment/"+name+".prefab");
            UnityEngine.Object.DestroyImmediate(root);return prefab;
        }
        private static Bounds BoundsOf(GameObject model)
        {
            var renderers=model.GetComponentsInChildren<Renderer>();
            var bounds=renderers[0].bounds;
            foreach(var renderer in renderers) bounds.Encapsulate(renderer.bounds);
            return bounds;
        }
        private static void Fit(GameObject model,float height)
        {
            var bounds=BoundsOf(model);model.transform.localScale*=height/Mathf.Max(.01f,bounds.size.y);
            bounds=BoundsOf(model);
            model.transform.position-=new Vector3(bounds.center.x,bounds.min.y,bounds.center.z);
        }
    }
}
#endif
