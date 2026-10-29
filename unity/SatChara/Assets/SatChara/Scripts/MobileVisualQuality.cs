using System;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace SatChara
{
    // Delivered-frame intervals are a smoke-test measure, not GPU timings or a
    // sustained thermal certification. Changes are limited to the visual scene.
    public sealed class MobileVisualQuality : MonoBehaviour
    {
        public enum Preset { Low, Realistic, High }
        public Preset Current { get; private set; } = Preset.Realistic;
        public string Label => Current.ToString();
        private UniversalRenderPipelineAsset pipeline;
        private RenderPipelineAsset originalQuality, originalDefault;
        private Light sun;
        private LightShadows originalSunShadows;
        private int nativeWidth, nativeHeight, count, over100;
        private readonly float[] intervals = new float[4096];
        private float warmupUntil, elapsed;
        private bool focused = true;

        private void Awake()
        {
            nativeWidth=Screen.width;nativeHeight=Screen.height;
            originalQuality=QualitySettings.renderPipeline;originalDefault=GraphicsSettings.defaultRenderPipeline;
            var source=GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
            if (!source) { Debug.LogError("SAT_CHARA_QUALITY: URP asset missing");enabled=false;return; }
            pipeline=Instantiate(source);pipeline.name="Village runtime quality";
            QualitySettings.renderPipeline=pipeline;
            sun=RenderSettings.sun; if(sun) originalSunShadows=sun.shadows;
            Apply((Preset)Mathf.Clamp(PlayerPrefs.GetInt("SatChara.VisualQuality",1),0,2));
        }
        public void Next() => Apply((Preset)(((int)Current+1)%3));
        public void Apply(Preset preset)
        {
            if (!pipeline) return;
            Current=preset;
            int height=Mathf.Min(nativeHeight,preset==Preset.Low?540:preset==Preset.High?900:720);
            int width=Mathf.RoundToInt(height*(float)nativeWidth/Mathf.Max(1,nativeHeight));
            if (!Application.isEditor) Screen.SetResolution(width,height,FullScreenMode.FullScreenWindow);
            pipeline.renderScale=1;
            pipeline.shadowDistance=preset==Preset.Low?12:preset==Preset.High?55:35;
            pipeline.msaaSampleCount=preset==Preset.High?2:1;
            pipeline.mainLightShadowmapResolution=preset==Preset.Low?512:preset==Preset.High?2048:1024;
            if(sun) sun.shadows=preset==Preset.Low?LightShadows.None:preset==Preset.High?LightShadows.Soft:LightShadows.Hard;
            Application.targetFrameRate=30;
            PlayerPrefs.SetInt("SatChara.VisualQuality",(int)preset);
            ResetSamples();
            Debug.Log($"SAT_CHARA_QUALITY: preset={Current}, requested={width}x{height}, renderScale={pipeline.renderScale}, shadows={pipeline.shadowDistance}, msaa={pipeline.msaaSampleCount}");
        }
        private void ResetSamples()
        { count=0;elapsed=0;over100=0;warmupUntil=Time.unscaledTime+5; }
        private void OnApplicationFocus(bool value) { focused=value;ResetSamples(); }
        private void OnApplicationPause(bool value) { focused=!value;ResetSamples(); }
        private void Update()
        {
            if (Application.isEditor || !focused || Time.unscaledTime<warmupUntil) return;
            float delta=Time.unscaledDeltaTime;
            if (delta<=0) return;
            intervals[count++]=delta*1000;elapsed+=delta;if(delta>.1f)over100++;
            if (elapsed<20 && count<intervals.Length) return;
            Array.Sort(intervals,0,count);
            float p50=intervals[Mathf.Clamp(Mathf.CeilToInt(count*.50f)-1,0,count-1)];
            float p95=intervals[Mathf.Clamp(Mathf.CeilToInt(count*.95f)-1,0,count-1)];
            float p99=intervals[Mathf.Clamp(Mathf.CeilToInt(count*.99f)-1,0,count-1)];
            Debug.Log($"SAT_CHARA_FRAME_SAMPLE: preset={Current}, resolution={Screen.width}x{Screen.height}, frames={count}, seconds={elapsed:F2}, fps={count/elapsed:F1}, p50ms={p50:F2}, p95ms={p95:F2}, p99ms={p99:F2}, over100ms={over100}");
            count=0;elapsed=0;over100=0;
        }
        private void OnDestroy()
        {
            if (!pipeline) return;
            QualitySettings.renderPipeline=originalQuality;GraphicsSettings.defaultRenderPipeline=originalDefault;
            if(sun) sun.shadows=originalSunShadows;
            Destroy(pipeline);
        }
    }
}
