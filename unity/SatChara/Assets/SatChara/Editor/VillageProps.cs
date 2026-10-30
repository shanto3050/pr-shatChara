using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace SatChara.Editor
{
    public static partial class VillageBuild
    {
        private const string Props = Art+"Environment/Village/";
        [Serializable] private class PropMaterials { public PropMaterial[] materials; }
        [Serializable] private class PropMaterial
        {
            public string name,texture,normal,roughness;
            public float[] color;
            public float metallic,smoothness;
            public bool cutout,twoSided;
        }
        private static readonly Dictionary<string,Material> propMaterials=new Dictionary<string,Material>();
        private static readonly Dictionary<string,GameObject> propPrefabs=new Dictionary<string,GameObject>();

        private static void PreparePropMaterials()
        {
            foreach(string folder in new[]{"RuntimeMaterials","RuntimeMeshes","RuntimePrefabs"}) Directory.CreateDirectory(Props+folder);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            propMaterials.Clear();propPrefabs.Clear();
            var manifest=JsonUtility.FromJson<PropMaterials>(File.ReadAllText("../../art-source/village-unity-materials.json"));
            foreach(var entry in manifest.materials)
            {
                string path=Props+"RuntimeMaterials/"+entry.name+".mat";
                var material=AssetDatabase.LoadAssetAtPath<Material>(path);
                if(!material) { material=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(material,path); }
                material.shader=Shader.Find("Universal Render Pipeline/Lit");
                material.SetColor("_BaseColor",new Color(entry.color[0],entry.color[1],entry.color[2],entry.color[3]));
                material.SetTexture("_BaseMap",PropTexture(entry.texture,false));
                var normal=PropTexture(entry.normal,true);material.SetTexture("_BumpMap",normal);
                if(normal)material.EnableKeyword("_NORMALMAP");else material.DisableKeyword("_NORMALMAP");
                material.SetFloat("_BumpScale",.7f);material.SetFloat("_Metallic",entry.metallic);
                material.SetFloat("_Smoothness",entry.smoothness);
                if(!string.IsNullOrEmpty(entry.roughness))
                {
                    material.SetTexture("_MetallicGlossMap",PackRoughness(entry));
                    material.SetFloat("_Smoothness",1);material.EnableKeyword("_METALLICSPECGLOSSMAP");
                }
                else { material.SetTexture("_MetallicGlossMap",null);material.DisableKeyword("_METALLICSPECGLOSSMAP"); }
                material.SetFloat("_AlphaClip",entry.cutout?1:0);material.SetFloat("_Cutoff",.4f);
                material.SetFloat("_Cull",entry.twoSided?0:2);
                if(entry.cutout)material.EnableKeyword("_ALPHATEST_ON");else material.DisableKeyword("_ALPHATEST_ON");
                material.SetOverrideTag("RenderType",entry.cutout?"TransparentCutout":"Opaque");
                material.renderQueue=entry.cutout?2450:2000;material.enableInstancing=true;
                EditorUtility.SetDirty(material);propMaterials.Add(entry.name,material);
            }
        }
        private static Texture2D PropTexture(string file,bool normal)
        {
            if(string.IsNullOrEmpty(file))return null;
            string path=Props+"Textures/"+file;
            var importer=AssetImporter.GetAtPath(path) as TextureImporter;
            if(!importer)throw new Exception("Missing village texture: "+path);
            var type=normal?TextureImporterType.NormalMap:TextureImporterType.Default;
            if(importer.textureType!=type || importer.maxTextureSize!=1024 || importer.wrapMode!=TextureWrapMode.Repeat)
            { importer.textureType=type;importer.maxTextureSize=1024;importer.wrapMode=TextureWrapMode.Repeat;importer.SaveAndReimport(); }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }
        private static Texture2D PackRoughness(PropMaterial entry)
        {
            var source=new Texture2D(2,2,TextureFormat.RGBA32,false,true);
            source.LoadImage(File.ReadAllBytes(Props+"Textures/"+entry.roughness));
            var pixels=source.GetPixels32();byte metal=(byte)Mathf.RoundToInt(entry.metallic*255);
            for(int i=0;i<pixels.Length;i++)pixels[i]=new Color32(metal,0,0,(byte)(255-pixels[i].r));
            source.Reinitialize(source.width,source.height,TextureFormat.RGBA32,false);
            source.SetPixels32(pixels);source.Apply();
            string path=Props+"RuntimeMaterials/"+entry.name+"-metal-smooth.png";
            byte[] bytes=source.EncodeToPNG();UnityEngine.Object.DestroyImmediate(source);
            if(!File.Exists(path) || !File.ReadAllBytes(path).SequenceEqual(bytes))
            { File.WriteAllBytes(path,bytes);AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport); }
            var importer=(TextureImporter)AssetImporter.GetAtPath(path);
            if(importer.sRGBTexture || importer.maxTextureSize!=1024 || importer.alphaIsTransparency)
            { importer.sRGBTexture=false;importer.maxTextureSize=1024;importer.alphaIsTransparency=false;importer.SaveAndReimport(); }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }
        private static GameObject PropPrefab(string name)
        {
            if(propPrefabs.TryGetValue(name,out var existing))return existing;
            var root=new GameObject(name+" mobile prop");
            bool reduced=File.Exists(Props+"LODs/"+name+"LOD1.fbx");
            var levels=new List<LOD>();
            for(int level=0;level<(reduced?2:1);level++)
            {
                string sourcePath=Props+(level==0?name:"LODs/"+name+"LOD1")+".fbx";
                var importer=(ModelImporter)AssetImporter.GetAtPath(sourcePath);
                if(!importer.isReadable || importer.importAnimation)
                { importer.isReadable=true;importer.importAnimation=false;importer.SaveAndReimport(); }
                var source=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(sourcePath));
                Debug.Log($"SAT_CHARA_PROP_IMPORT: {name}, rootPosition={source.transform.position}, rootRotation={source.transform.eulerAngles}, rootScale={source.transform.localScale}");
                var batches=new Dictionary<string,List<CombineInstance>>();
                foreach(var filter in source.GetComponentsInChildren<MeshFilter>())
                {
                    var renderer=filter.GetComponent<MeshRenderer>();if(!renderer)continue;
                    for(int sub=0;sub<filter.sharedMesh.subMeshCount;sub++)
                    {
                        string label=renderer.sharedMaterials[sub].name.Split('.')[0];
                        if(!propMaterials.ContainsKey(label))throw new Exception("Unmapped village material: "+label);
                        if(!batches.TryGetValue(label,out var list)) { list=new List<CombineInstance>();batches.Add(label,list); }
                        list.Add(new CombineInstance{mesh=filter.sharedMesh,subMeshIndex=sub,transform=filter.transform.localToWorldMatrix});
                    }
                }
                var renderers=new List<Renderer>();
                foreach(var batch in batches)
                {
                    var mesh=new Mesh{name=name+" LOD"+level+" "+batch.Key,indexFormat=IndexFormat.UInt32};
                    mesh.CombineMeshes(batch.Value.ToArray(),true,true);mesh.RecalculateBounds();
                    string path=Props+"RuntimeMeshes/"+name+"-"+level+"-"+batch.Key+".asset";
                    var saved=AssetDatabase.LoadAssetAtPath<Mesh>(path);
                    if(saved) { EditorUtility.CopySerialized(mesh,saved);UnityEngine.Object.DestroyImmediate(mesh);mesh=saved; }
                    else AssetDatabase.CreateAsset(mesh,path);
                    EditorUtility.SetDirty(mesh);AssetDatabase.SaveAssetIfDirty(mesh);
                    var part=new GameObject(batch.Key,typeof(MeshFilter),typeof(MeshRenderer));part.transform.SetParent(root.transform,false);
                    part.GetComponent<MeshFilter>().sharedMesh=mesh;var renderer=part.GetComponent<MeshRenderer>();
                    renderer.sharedMaterial=propMaterials[batch.Key];renderer.shadowCastingMode=batch.Key=="GrassCards"||batch.Key=="StrawCards"||batch.Key=="PondWater"?ShadowCastingMode.Off:ShadowCastingMode.On;
                    renderers.Add(renderer);part.isStatic=true;
                }
                var expectedBounds=BoundsOf(source);var combinedBounds=renderers[0].bounds;
                foreach(var renderer in renderers)combinedBounds.Encapsulate(renderer.bounds);
                if(Vector3.Distance(expectedBounds.center,combinedBounds.center)>.01f || Vector3.Distance(expectedBounds.size,combinedBounds.size)>.01f)throw new Exception($"Prop transform changed: {name}, source={expectedBounds}, combined={combinedBounds}");
                Debug.Log($"SAT_CHARA_PROP_BOUNDS_PASS: {name}, level={level}, bounds={combinedBounds}");
                UnityEngine.Object.DestroyImmediate(source);
                levels.Add(new LOD(level==0&&reduced?.12f:.006f,renderers.ToArray()));
            }
            var group=root.AddComponent<LODGroup>();group.SetLODs(levels.ToArray());group.RecalculateBounds();
            root.isStatic=true;
            var prefab=PrefabUtility.SaveAsPrefabAsset(root,Props+"RuntimePrefabs/"+name+".prefab");
            UnityEngine.Object.DestroyImmediate(root);propPrefabs.Add(name,prefab);return prefab;
        }
        private static GameObject PlaceVillageProp(string name,Vector3 at,float yaw=0,float scale=1)
        {
            var ob=(GameObject)PrefabUtility.InstantiatePrefab(PropPrefab(name));ob.transform.SetParent(scenery,false);
            ob.transform.position=at;ob.transform.rotation=Quaternion.Euler(0,yaw,0);ob.transform.localScale=Vector3.one*scale;
            return ob;
        }
        private static void CourtyardGround()
        {
            var layers=new TerrainLayer[2];
            for(int i=0;i<2;i++)
            {
                string path=Props+"RuntimeMaterials/"+(i==0?"SweptEarth":"GroundGrass")+".terrainlayer";
                var layer=AssetDatabase.LoadAssetAtPath<TerrainLayer>(path);
                if(!layer) { layer=new TerrainLayer();AssetDatabase.CreateAsset(layer,path); }
                layer.diffuseTexture=(Texture2D)(i==0?earth:propMaterials["GroundGrass"]).GetTexture("_BaseMap");
                layer.normalMapTexture=i==0?null:(Texture2D)propMaterials["GroundGrass"].GetTexture("_BumpMap");
                layer.diffuseRemapMax=i==0?new Vector4(.82f,.76f,.64f,1):new Vector4(.48f,1.05f,.48f,1);
                layer.tileSize=Vector2.one*(i==0?4:3);layer.metallic=0;layer.smoothness=.08f;layer.smoothnessSource=TerrainLayerSmoothnessSource.Constant;
                EditorUtility.SetDirty(layer);layers[i]=layer;
            }
            string terrainPath=Props+"RuntimeMeshes/CourtyardTerrain.asset";
            var data=AssetDatabase.LoadAssetAtPath<TerrainData>(terrainPath);
            if(!data) { data=new TerrainData();AssetDatabase.CreateAsset(data,terrainPath); }
            data.heightmapResolution=33;data.alphamapResolution=128;data.baseMapResolution=512;
            data.size=new Vector3(180,1,180);data.SetHeights(0,0,new float[33,33]);data.terrainLayers=layers;
            var weights=new float[128,128,2];
            for(int z=0;z<128;z++)for(int x=0;x<128;x++)
            {
                float wx=x/127f*180-90,wz=z/127f*180-90;
                float edge=Mathf.Max(Mathf.Abs(wx)-14.5f,Mathf.Abs(wz)-17);
                float variation=Mathf.Sin(wx*.71f+wz*.29f)*.7f+Mathf.Cos(wz*.59f)*.4f;
                float dirt=1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(-1,2,edge+variation));
                if(wz>14 && wz<32)dirt=Mathf.Max(dirt,1-Mathf.SmoothStep(0,1,Mathf.InverseLerp(1,2.5f,Mathf.Abs(wx))));
                weights[z,x,0]=dirt;weights[z,x,1]=1-dirt;
                if(Mathf.Abs(wx)<=11 && Mathf.Abs(wz)<=13 && dirt<.99f)throw new Exception("Grass encroached on clear play area");
            }
            data.SetAlphamaps(0,0,weights);EditorUtility.SetDirty(data);
            var ob=new GameObject("Swept courtyard and grass verges",typeof(Terrain));ob.transform.SetParent(scenery,false);ob.transform.position=new Vector3(-90,-.025f,-90);
            var terrain=ob.GetComponent<Terrain>();terrain.terrainData=data;terrain.drawInstanced=true;terrain.heightmapPixelError=8;terrain.basemapDistance=70;
            string materialPath=Props+"RuntimeMaterials/CourtyardTerrain.mat";
            var material=AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            if(!material) { material=new Material(Shader.Find("Universal Render Pipeline/Terrain/Lit"));AssetDatabase.CreateAsset(material,materialPath); }
            terrain.materialTemplate=material;terrain.shadowCastingMode=ShadowCastingMode.Off;data.SetBaseMapDirty();terrain.Flush();
        }
        private static void ImportedCourtyard()
        {
            PreparePropMaterials();scenery=new GameObject("Village surroundings").transform;
            // A grass ring surrounds the swept play area; the path to the house remains bare earth.
            CourtyardGround();
            PlaceVillageProp("MudHouse",new Vector3(-20,0,17),200,1.25f);
            PlaceVillageProp("MudHouse",new Vector3(17,0,24),165,1.15f);
            PlaceVillageProp("MudHouse",new Vector3(0,0,31),180,1.3f);
            PlaceVillageProp("Haystack",new Vector3(-14,0,21),35);
            PlaceVillageProp("TubeWell",new Vector3(13,0,17),-25,1.1f);
            PlaceVillageProp("ClayPot",new Vector3(12.2f,0,16.3f));
            PlaceVillageProp("ClayPot",new Vector3(12.6f,0,15.6f),50,.8f);
            PlaceVillageProp("JuteSack",new Vector3(-14,0,23),15);
            PlaceVillageProp("ClothesLine",new Vector3(-13,0,14),8);
            PlaceVillageProp("StrawDrying",new Vector3(-13,0,19),20);
            PlaceVillageProp("VanRickshaw",new Vector3(14,0,21),-35);
            PlaceVillageProp("Pond",new Vector3(21,-.035f,8),20,1.35f);
            for(int side=-1;side<=1;side+=2)
                for(int i=0;i<10;i++)PlaceVillageProp("BambooFence",new Vector3(side*16.5f,0,-18+i*4),90);
            for(int i=0;i<8;i++)
            {
                float side=i%2==0?-1:1;
                var at=new Vector3(side*(19+i%3),0,3+i*4.4f);
                if(Vector3.Distance(at,new Vector3(21,0,8))<6)at.x=28;
                PlaceVillageProp("BananaPlant",at,i*67,.9f+i%3*.08f);
            }
            for(int i=0;i<6;i++)PlaceVillageProp("CoconutPalm",new Vector3(i%2==0?-25:26,0,-6+i*8),i*71,.85f+i%3*.1f);
            // Reuse the existing optimized broadleaf asset, with nearer trees enclosing the homestead.
            var distantTree=EnvironmentPrefab("island_tree_01_distant",7);
            for(int i=0;i<12;i++)
            {
                var ob=(GameObject)PrefabUtility.InstantiatePrefab(distantTree);ob.transform.SetParent(scenery,false);
                ob.transform.position=new Vector3(i<4?-29:i<8?30:-30+(i-8)*20,0,i<8?-12+i%4*14:45);
                ob.transform.rotation=Quaternion.Euler(0,i*97,0);ob.transform.localScale=Vector3.one*(1+i%3*.2f);
                foreach(var renderer in ob.GetComponentsInChildren<Renderer>()) { renderer.shadowCastingMode=ShadowCastingMode.Off;renderer.gameObject.isStatic=true; }
            }
            var detail=new GameObject("Grass detail");detail.transform.SetParent(scenery,false);
            for(int i=0;i<100;i++)
            {
                float side=i%2==0?-1:1,z=-17+(i/2)*.9f;
                var ob=PlaceVillageProp("GrassClump",new Vector3(side*(15.1f+Mathf.Sin(i*2.3f)*.7f),0,z),i*137,.65f+i%4*.12f);
                ob.transform.SetParent(detail.transform,true);
            }
            var quality=scenery.gameObject.AddComponent<VillageSceneryQuality>();quality.SetDetail(detail);
            float previousBias=QualitySettings.lodBias;
            quality.Apply(MobileVisualQuality.Preset.Low);
            if(detail.activeSelf)throw new Exception("Low preset did not hide grass detail");
            quality.Apply(MobileVisualQuality.Preset.Realistic);
            if(!detail.activeSelf)throw new Exception("Realistic preset did not restore grass detail");
            QualitySettings.lodBias=previousBias;
            ValidateVillageProps();
        }
        public static void CaptureProps()
        {
            Capture();var camera=Camera.main;
            camera.transform.position=new Vector3(10,1.6f,14);camera.transform.LookAt(new Vector3(13,.55f,17));camera.fieldOfView=50;CaptureCamera(camera,"village-tube-well-unity.png");
            camera.transform.position=new Vector3(-16,1.8f,9);camera.transform.LookAt(new Vector3(-13,1.1f,16));camera.fieldOfView=55;CaptureCamera(camera,"village-clothes-unity.png");
            camera.transform.position=new Vector3(17,2,3);camera.transform.LookAt(new Vector3(21,.15f,8));camera.fieldOfView=65;CaptureCamera(camera,"village-pond-unity.png");
        }
        private static void ValidateVillageProps()
        {
            int renderers=0,triangles=0;
            foreach(var renderer in scenery.GetComponentsInChildren<MeshRenderer>())
            {
                if(!renderer.sharedMaterial || renderer.sharedMaterial.shader.name!="Universal Render Pipeline/Lit")throw new Exception("Invalid village material: "+renderer.name);
                var bounds=renderer.bounds;
                if(float.IsNaN(bounds.size.x))throw new Exception("Invalid village mesh bounds");
                renderers++;triangles+=renderer.GetComponent<MeshFilter>().sharedMesh.triangles.Length/3;
            }
            if(scenery.GetComponentsInChildren<Collider>().Length!=0)throw new Exception("Decorative scenery changed gameplay collisions");
            var terrain=scenery.GetComponentInChildren<Terrain>();
            if(!terrain || terrain.terrainData.terrainLayers.Length!=2 || terrain.terrainData.terrainLayers.Any(l=>l.smoothnessSource!=TerrainLayerSmoothnessSource.Constant))throw new Exception("Invalid dry courtyard terrain");
            Debug.Log($"SAT_CHARA_PROPS_PASS: prefabs={propPrefabs.Count}, allLevelRenderers={renderers}, allLevelTriangles={triangles}, materials={propMaterials.Count}, colliders={scenery.GetComponentsInChildren<Collider>().Length}");
        }
    }
}
