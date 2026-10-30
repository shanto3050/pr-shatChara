using UnityEngine;

namespace SatChara
{
    // Quality changes affect decoration only; gameplay geometry and rules are shared.
    public sealed class VillageSceneryQuality : MonoBehaviour
    {
        [SerializeField] private GameObject grassDetail;
        private LODGroup[] groups;
        public void SetDetail(GameObject value) => grassDetail=value;
        public void Apply(MobileVisualQuality.Preset preset)
        {
            if(groups==null)groups=GetComponentsInChildren<LODGroup>(true);
            foreach(var group in groups)group.ForceLOD(preset==MobileVisualQuality.Preset.Low && group.lodCount>1?1:-1);
            if(grassDetail)grassDetail.SetActive(preset!=MobileVisualQuality.Preset.Low);
            foreach(var terrain in GetComponentsInChildren<Terrain>()) { terrain.heightmapPixelError=preset==MobileVisualQuality.Preset.Low?16:preset==MobileVisualQuality.Preset.High?5:8;terrain.basemapDistance=preset==MobileVisualQuality.Preset.Low?40:preset==MobileVisualQuality.Preset.High?100:70; }
            QualitySettings.lodBias=preset==MobileVisualQuality.Preset.Low?.65f:preset==MobileVisualQuality.Preset.High?1.3f:1;
        }
    }
}
