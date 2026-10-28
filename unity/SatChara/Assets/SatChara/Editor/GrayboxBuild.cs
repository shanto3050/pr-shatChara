using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using SatChara.Rules;

namespace SatChara.Editor
{
    public static class GrayboxBuild
    {
        private const string ScenePath = "Assets/SatChara/Scenes/GrayboxMatch.unity";
        [MenuItem("Sat Chara/Prepare Playable Graybox")]
        public static void Prepare()
        {
            // Retain the earlier foundation diagnostic scene and shared Android defaults.
            AndroidBuild.PrepareFoundation();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var camera = new GameObject("Main Camera").AddComponent<Camera>();
            camera.tag = "MainCamera";
            camera.transform.position = new Vector3(0, 29, -19); camera.transform.LookAt(Vector3.zero);
            camera.backgroundColor = new Color(.44f, .62f, .72f); camera.clearFlags = CameraClearFlags.SolidColor;
            camera.gameObject.AddComponent<AudioListener>();
            var light = new GameObject("Sun").AddComponent<Light>(); light.type = LightType.Directional;
            light.intensity = 1.4f; light.transform.rotation = Quaternion.Euler(50, -30, 0);
            RenderSettings.ambientLight = new Color(.55f, .58f, .61f);
            var game = new GameObject("Match").AddComponent<GrayboxMatch>();
            game.SetMaterial(AssetDatabase.LoadAssetAtPath<Material>("Assets/SatChara/Art/Materials/Earth.mat"));
            EditorSceneManager.SaveScene(scene, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            PlayerSettings.productName = "Sat Chara Graybox"; PlayerSettings.bundleVersion = "0.1.0";
            PlayerSettings.Android.bundleVersionCode = 2;
            AssetDatabase.SaveAssets();
            Debug.Log("SAT_CHARA_GRAYBOX_READY");
        }

        [MenuItem("Sat Chara/Build Playable Android Graybox")]
        public static void Build()
        {
            Prepare();
            string output = Environment.GetEnvironmentVariable("SAT_CHARA_APK");
            AndroidBuild.BuildScene(ScenePath, string.IsNullOrEmpty(output) ? "Builds/Android/SatChara-Graybox.apk" : output);
        }

        // Executes actual scene simulation, not a second copy of the rules or an animation.
        public static void ValidateSimulation()
        {
            float near = GrayboxMatch.SweepFraction(Vector3.zero, Vector3.forward * 10, Vector3.forward * 4, .5f);
            float far = GrayboxMatch.SweepFraction(Vector3.zero, Vector3.forward * 10, Vector3.forward * 8, .5f);
            if (Mathf.Abs(near - .35f) > .0001f || near >= far
                || !float.IsPositiveInfinity(GrayboxMatch.SweepFraction(Vector3.zero, Vector3.forward * 10, Vector3.right * 4, .5f))
                || GrayboxMatch.SweepFraction(Vector3.zero, Vector3.zero, Vector3.zero, .5f) != 0)
                throw new Exception("Swept-contact regression failed");
            Prepare();
            var game = UnityEngine.Object.FindFirstObjectByType<GrayboxMatch>();
            game.AutomatedPlayer = true;
            game.Initialize();
            for (int tick = 0; tick < 60000 && game.State.Phase != MatchPhase.MatchOver; tick++) game.Simulate(.02f);
            string summary = $"rounds={game.CompletedRounds}, topples={game.Topples}, placements={game.Placements}, hits={game.Hits}, score={game.State.Score(0)}-{game.State.Score(1)}, phase={game.State.Phase}";
            if (game.Topples < 2 || game.Placements < 7 || game.Hits < 1 || game.CompletedRounds < 2 || game.State.Phase != MatchPhase.MatchOver)
                throw new Exception("Graybox integration failed: " + summary);
            Debug.Log("SAT_CHARA_SIMULATION_PASS: " + summary);
            // Do not save the test-generated runtime objects into the authored scene.
        }

        public static void ValidateAndBuild()
        {
            ValidateSimulation();
            Build();
        }
    }
}
