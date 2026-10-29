using UnityEditor;

namespace SatChara.Editor
{
    // Use standard material slots as names only. VillageBuild assigns explicit URP
    // materials; importing Blender's offline node graphs produces invalid cube maps.
    public sealed class VillageModelImport : AssetPostprocessor
    {
        private void OnPreprocessModel()
        {
            if (!assetPath.StartsWith("Assets/SatChara/Art/")) return;
            var importer = (ModelImporter)assetImporter;
            importer.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
        }
    }
}
