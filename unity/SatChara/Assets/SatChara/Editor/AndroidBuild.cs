using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace SatChara.Editor
{
    public static class AndroidBuild
    {
        private const string ScenePath = "Assets/SatChara/Scenes/Foundation.unity";

        [MenuItem("Sat Chara/Prepare Foundation Scene")]
        public static void PrepareFoundation()
        {
            Directory.CreateDirectory("Assets/SatChara/Scenes");
            Directory.CreateDirectory("Assets/SatChara/Art/Materials");
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var camera = new GameObject("Main Camera").AddComponent<Camera>();
            camera.tag = "MainCamera";
            camera.transform.position = new Vector3(10, 13, -15);
            camera.transform.LookAt(new Vector3(0, 0.7f, 0));
            camera.backgroundColor = new Color(0.48f, 0.65f, 0.75f);
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.gameObject.AddComponent<AudioListener>();
            var light = new GameObject("Afternoon Sun").AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.3f;
            light.transform.rotation = Quaternion.Euler(45, -35, 0);
            RenderSettings.ambientLight = new Color(0.55f, 0.55f, 0.5f);
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Graybox Courtyard";
            ground.transform.localScale = new Vector3(3, 1, 3);
            ground.GetComponent<Renderer>().sharedMaterial = Material("Earth", new Color(0.43f, 0.33f, 0.21f));
            var stoneMaterial = Material("Stone", new Color(0.56f, 0.54f, 0.49f));
            for (int i = 0; i < 7; i++)
            {
                var stone = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                stone.name = "Stone " + (i + 1);
                float radius = 1.05f - i * 0.11f;
                stone.transform.position = new Vector3(0, 0.12f + i * 0.23f, 0);
                stone.transform.localScale = new Vector3(radius, 0.11f, radius);
                stone.GetComponent<Renderer>().sharedMaterial = stoneMaterial;
            }
            new GameObject("Foundation Status").AddComponent<FoundationStatus>();
            EditorSceneManager.SaveScene(scene, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            PlayerSettings.companyName = "SatChara";
            PlayerSettings.productName = "Sat Chara Foundation";
            PlayerSettings.bundleVersion = "0.0.1";
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, "com.shanto3050.satchara.dev");
            PlayerSettings.Android.bundleVersionCode = 1;
            PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel26;
            PlayerSettings.Android.targetSdkVersion = AndroidSdkVersions.AndroidApiLevelAuto;
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.OpenGLES3 });
            AssetDatabase.SaveAssets();
            Debug.Log("SAT_CHARA_FOUNDATION_READY: scene and Android development settings saved.");
        }

        [MenuItem("Sat Chara/Build Android Development APK")]
        public static void BuildDevelopment()
        {
            PrepareFoundation();
            string output = Environment.GetEnvironmentVariable("SAT_CHARA_APK");
            if (string.IsNullOrEmpty(output)) output = "Builds/Android/SatChara-Foundation.apk";
            Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(output)));
            EditorUserBuildSettings.buildAppBundle = false;
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                locationPathName = output,
                target = BuildTarget.Android,
                options = BuildOptions.Development
            });
            if (report.summary.result != BuildResult.Succeeded)
                throw new Exception("Android build failed: " + report.summary.result);
            Debug.Log($"SAT_CHARA_APK_BUILT: {output}; bytes={report.summary.totalSize}");
        }

        private static Material Material(string name, Color color)
        {
            string path = "Assets/SatChara/Art/Materials/" + name + ".mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                AssetDatabase.CreateAsset(material, path);
            }
            material.color = color;
            return material;
        }
    }
}
