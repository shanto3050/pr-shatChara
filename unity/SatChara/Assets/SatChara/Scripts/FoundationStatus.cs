using SatChara.Rules;
using UnityEngine;

namespace SatChara
{
    // Temporary installation/simulation smoke screen; replaced by gameplay at M1.
    public sealed class FoundationStatus : MonoBehaviour
    {
        private MatchState match = new MatchState();
        private GUIStyle title;
        private GUIStyle body;

        private void Awake()
        {
            Application.targetFrameRate = 30;
            Screen.sleepTimeout = SleepTimeout.NeverSleep;
        }

        private void OnGUI()
        {
            float scale = Mathf.Max(0.5f, Mathf.Min(Screen.width / 960f, Screen.height / 540f));
            GUI.matrix = Matrix4x4.TRS(Vector3.zero, Quaternion.identity, Vector3.one * scale);
            title ??= new GUIStyle(GUI.skin.label) { fontSize = 30, fontStyle = FontStyle.Bold };
            body ??= new GUIStyle(GUI.skin.label) { fontSize = 19, wordWrap = true };
            GUI.Box(new Rect(18, 18, 530, 260), GUIContent.none);
            GUI.Label(new Rect(34, 30, 500, 44), "SAT CHARA", title);
            GUI.Label(new Rect(34, 80, 490, 70), "Android foundation build\nInstallation test — gameplay comes next.", body);
            GUI.Label(new Rect(34, 156, 490, 36), $"Rules check: {match.Score(0)} – {match.Score(1)}", body);
            if (GUI.Button(new Rect(34, 204, 225, 46), "Test seven-stone rebuild"))
            {
                match = new MatchState();
                match.ToppleTower();
                for (int i = 0; i < 7; i++) { match.PickUpStone(0, i); match.PlaceStone(0); }
                Debug.Log($"SAT_CHARA_RULE_SMOKE: score={match.Score(0)}, result={match.LastResult}");
            }
            if (GUI.Button(new Rect(278, 204, 225, 46), "Reset")) match = new MatchState();
        }

        private void OnApplicationPause(bool paused)
        {
            Screen.sleepTimeout = paused ? SleepTimeout.SystemSetting : SleepTimeout.NeverSleep;
        }
    }
}
