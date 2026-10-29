using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace SatChara.Editor
{
    public static partial class VillageBuild
    {
        private const string Art = "Assets/SatChara/Art/";
        private const string ScenePath = "Assets/SatChara/Scenes/VillageMatch.unity";
        private static Material earth, plaster, tin, wood, grass, stem;

        [MenuItem("Sat Chara/Prepare Village Visual Slice")]
        public static void Prepare()
        {
            Directory.CreateDirectory(Art + "VillageMaterials");
            Directory.CreateDirectory(Art + "VillageMeshes");
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            ConfigureTextures();
            GrayboxBuild.Prepare();
            var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(Art + "VillagePipeline.asset");
            if (!pipeline)
            {
                pipeline = UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>("Assets/Settings/Mobile_RPAsset.asset"));
                AssetDatabase.CreateAsset(pipeline, Art + "VillagePipeline.asset");
            }
            var serialized = new SerializedObject(pipeline);
            serialized.FindProperty("m_SoftShadowsSupported").boolValue = true;
            serialized.FindProperty("m_MainLightShadowmapResolution").intValue = 2048;
            serialized.FindProperty("m_ShadowDistance").floatValue = 55;
            serialized.FindProperty("m_RenderScale").floatValue = .9f;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            GraphicsSettings.defaultRenderPipeline = pipeline;
            for (int i = 0; i < QualitySettings.names.Length; i++)
            { QualitySettings.SetQualityLevel(i); QualitySettings.renderPipeline = pipeline; }
            QualitySettings.SetQualityLevel(0);
            QualitySettings.vSyncCount = 0;
            earth = Surface("Village Earth", "Textures/village-earth.png", new Color(.82f,.76f,.64f), 0, .08f);
            earth.mainTextureScale = new Vector2(36,36);
            plaster = Surface("Lime Plaster", "Environment/Textures/clay_plaster_diff_1k.jpg", new Color(.92f,.85f,.67f), 0, .08f);
            tin = Surface("Weathered Tin", "Environment/Textures/worn_corrugated_iron_diff_1k.jpg", Color.white, .65f, .24f);
            wood = Surface("Old Timber", "Environment/Textures/wooden_rough_planks_diff_1k.jpg", new Color(.7f,.64f,.53f), 0, .1f);
            grass = Surface("Grass", null, new Color(.2f,.29f,.07f), 0, .08f);
            stem = Surface("Banana Stem", null, new Color(.38f,.42f,.17f), 0, .06f);
            var character = CharacterPrefab();
            var tree = EnvironmentPrefab("island_tree_01", 6.5f);
            var barrel = EnvironmentPrefab("barrel_03", .95f);
            BuildCourtyard(tree, barrel);
            var game = UnityEngine.Object.FindFirstObjectByType<GrayboxMatch>();
            game.SetVillageArt(character, earth, StoneMesh());
            game.gameObject.AddComponent<MobileVisualQuality>();
            var light = UnityEngine.Object.FindFirstObjectByType<Light>();
            light.color = new Color(1,.88f,.71f); light.intensity = 1.2f;
            light.transform.rotation = Quaternion.Euler(35,-40,0); light.shadows = LightShadows.Soft;
            light.shadowBias = .025f; light.shadowNormalBias = .2f;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.48f,.59f,.7f);
            RenderSettings.ambientEquatorColor = new Color(.49f,.47f,.4f);
            RenderSettings.ambientGroundColor = new Color(.25f,.24f,.18f);
            RenderSettings.fog = true; RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(.65f,.69f,.72f); RenderSettings.fogStartDistance = 60; RenderSettings.fogEndDistance = 150;
            var sky = AssetDatabase.LoadAssetAtPath<Material>(Art+"VillageMaterials/Evening Sky.mat");
            if (!sky) { sky = new Material(Shader.Find("Skybox/Procedural")); AssetDatabase.CreateAsset(sky,Art+"VillageMaterials/Evening Sky.mat"); }
            sky.shader = Shader.Find("Skybox/Procedural");
            sky.SetColor("_SkyTint",new Color(.5f,.5f,.5f));
            sky.SetColor("_GroundColor",new Color(.4f,.39f,.36f));
            sky.SetFloat("_AtmosphereThickness",1);sky.SetFloat("_Exposure",1);
            sky.SetFloat("_SunSize",.025f); EditorUtility.SetDirty(sky);
            RenderSettings.skybox = sky; RenderSettings.sun = light;
            Camera.main.clearFlags = CameraClearFlags.Skybox; Camera.main.allowHDR = false;
            EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(), ScenePath);
            EditorBuildSettings.scenes = new[] {new EditorBuildSettingsScene(ScenePath,true)};
            PlayerSettings.productName = "Sat Chara Village"; PlayerSettings.bundleVersion = "0.2.4"; PlayerSettings.Android.bundleVersionCode = 7;
            AssetDatabase.SaveAssets();
            Debug.Log("SAT_CHARA_VILLAGE_READY: real skinned character, textured environment and perspective camera");
        }

        public static void Build()
        {
            Prepare();
            AndroidBuild.BuildScene(ScenePath, "Builds/Android/SatChara-Village.apk");
        }

        public static void Validate()
        {
            Prepare();
            var game = UnityEngine.Object.FindFirstObjectByType<GrayboxMatch>();
            game.AutomatedPlayer = true; game.Initialize();
            for (int tick = 0; tick < 60000 && game.State.Phase != SatChara.Rules.MatchPhase.MatchOver; tick++) game.Simulate(.02f);
            string summary = $"rounds={game.CompletedRounds}, topples={game.Topples}, placements={game.Placements}, hits={game.Hits}, score={game.State.Score(0)}-{game.State.Score(1)}, phase={game.State.Phase}";
            if (game.Topples < 2 || game.Placements < 7 || game.Hits < 1 || game.State.Phase != SatChara.Rules.MatchPhase.MatchOver)
                throw new Exception("Village simulation failed: " + summary);
            Debug.Log("SAT_CHARA_VILLAGE_SIMULATION_PASS: " + summary);
        }

        public static void VerifyAndBuild()
        {
            Validate();
            Capture();
            Build();
        }

        // A real URP camera render for look development; it is not a device capture.
        public static void Capture()
        {
            Prepare();
            var game = UnityEngine.Object.FindFirstObjectByType<GrayboxMatch>();
            game.Initialize(); game.Simulate(.02f); game.SendMessage("UpdatePresentation");
            foreach(var label in UnityEngine.Object.FindObjectsByType<TextMesh>(FindObjectsSortMode.None)) label.gameObject.SetActive(false);
            var camera = Camera.main;
            camera.transform.position = new Vector3(8, 5, -12);
            camera.transform.LookAt(new Vector3(0, 1, 1)); camera.orthographic = false; camera.fieldOfView = 55;
            CaptureCamera(camera, "village-courtyard-editor.png");
            camera.transform.position = new Vector3(2, 2.1f, -13.8f);
            camera.transform.LookAt(new Vector3(0, .95f, -10)); camera.fieldOfView = 40;
            CaptureCamera(camera, "village-character-editor.png");
        }
        private static void CaptureCamera(Camera camera, string filename)
        {
            string folder = Path.GetFullPath("../../.verification/village"); Directory.CreateDirectory(folder);
            var target = new RenderTexture(1600, 900, 24);
            camera.targetTexture = target; camera.Render(); camera.Render(); RenderTexture.active = target;
            var image = new Texture2D(1600,900,TextureFormat.RGB24,false);
            image.ReadPixels(new Rect(0,0,1600,900),0,0); image.Apply();
            File.WriteAllBytes(Path.Combine(folder,filename),image.EncodeToPNG());
            camera.targetTexture = null; RenderTexture.active = null;
            UnityEngine.Object.DestroyImmediate(image); UnityEngine.Object.DestroyImmediate(target);
            Debug.Log("SAT_CHARA_EDITOR_CAPTURE: " + Path.Combine(folder,filename));
        }

        private static void ConfigureTextures()
        {
            foreach (string file in Directory.GetFiles(Art,"*.*",SearchOption.AllDirectories).Where(p => p.EndsWith(".png") || p.EndsWith(".jpg")))
            {
                var importer = AssetImporter.GetAtPath(file.Replace('\\','/')) as TextureImporter;
                if (!importer) continue;
                bool normal = file.Contains("normal") || file.Contains("nor_gl") || file.Contains("skin_pores");
                var type = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                if (importer.maxTextureSize == 1024 && importer.textureType == type && importer.textureShape == TextureImporterShape.Texture2D) continue;
                importer.maxTextureSize = 1024; importer.textureType = type; importer.textureShape = TextureImporterShape.Texture2D;
                importer.textureCompression = TextureImporterCompression.Compressed;
                importer.alphaIsTransparency = !normal; importer.SaveAndReimport();
            }
        }

        private static Material Surface(string name, string texture, Color color, float metallic, float smoothness, bool cutout=false)
        {
            string path=Art+"VillageMaterials/"+name+".mat";
            var material=AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!material) {material=new Material(Shader.Find("Universal Render Pipeline/Lit"));AssetDatabase.CreateAsset(material,path);}
            material.color=color; material.SetFloat("_Metallic",metallic);material.SetFloat("_Smoothness",smoothness);
            material.enableInstancing=true;
            if (texture != null) material.SetTexture("_BaseMap",AssetDatabase.LoadAssetAtPath<Texture2D>(Art+texture));
            if (cutout) {material.SetFloat("_AlphaClip",1);material.SetFloat("_Cutoff",.35f);material.SetFloat("_Cull",0);material.EnableKeyword("_ALPHATEST_ON");material.renderQueue=2450;}
            EditorUtility.SetDirty(material);return material;
        }
    }
}
