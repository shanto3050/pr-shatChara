#if SAT_CHARA_VISUAL_SLICE_WIP
// Incomplete editor authoring tool. See docs/visual-slice-status.md before enabling.
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
            earth.mainTextureScale = new Vector2(18,18);
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
            var light = UnityEngine.Object.FindFirstObjectByType<Light>();
            light.color = new Color(1,.88f,.71f); light.intensity = 1.65f;
            light.transform.rotation = Quaternion.Euler(35,-40,0); light.shadows = LightShadows.Soft;
            light.shadowBias = .025f; light.shadowNormalBias = .2f;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(.48f,.59f,.7f);
            RenderSettings.ambientEquatorColor = new Color(.49f,.47f,.4f);
            RenderSettings.ambientGroundColor = new Color(.25f,.24f,.18f);
            RenderSettings.fog = true; RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = new Color(.72f,.76f,.7f); RenderSettings.fogStartDistance = 32; RenderSettings.fogEndDistance = 95;
            var sky = new Material(Shader.Find("Skybox/Procedural"));
            sky.SetColor("_SkyTint",new Color(.55f,.62f,.7f)); sky.SetFloat("_AtmosphereThickness",1.1f);
            RenderSettings.skybox = sky; RenderSettings.sun = light;
            Camera.main.clearFlags = CameraClearFlags.Skybox; Camera.main.allowHDR = false;
            EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(), ScenePath);
            EditorBuildSettings.scenes = new[] {new EditorBuildSettingsScene(ScenePath,true)};
            PlayerSettings.productName = "Sat Chara Village"; PlayerSettings.bundleVersion = "0.2.0"; PlayerSettings.Android.bundleVersionCode = 3;
            AssetDatabase.SaveAssets();
            Debug.Log("SAT_CHARA_VILLAGE_READY: real skinned character, textured environment and perspective camera");
        }

        public static void Build()
        {
            Prepare();
            AndroidBuild.BuildScene(ScenePath, "Builds/Android/SatChara-Village.apk");
        }

        private static void ConfigureTextures()
        {
            foreach (string file in Directory.GetFiles(Art,"*.*",SearchOption.AllDirectories).Where(p => p.EndsWith(".png") || p.EndsWith(".jpg")))
            {
                var importer = AssetImporter.GetAtPath(file.Replace('\\','/')) as TextureImporter;
                if (!importer) continue;
                bool normal = file.Contains("normal") || file.Contains("nor_gl");
                var type = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                if (importer.maxTextureSize == 1024 && importer.textureType == type) continue;
                importer.maxTextureSize = 1024; importer.textureType = type;
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
#endif
