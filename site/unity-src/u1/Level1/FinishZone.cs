using UnityEngine;
using UnityEngine.SceneManagement;

public class FinishZone : MonoBehaviour
{
    public float nextLevelDelay = 2f;

    private bool finished;
    private bool isLastLevel;

    void OnTriggerEnter(Collider other)
    {
        if (finished) return;
        if (other.GetComponentInParent<PlayerScript>() != null)
        {
            finished = true;
            int nextIndex = SceneManager.GetActiveScene().buildIndex + 1;
            isLastLevel = nextIndex >= SceneManager.sceneCountInBuildSettings;
            if (!isLastLevel)
            {
                Invoke(nameof(LoadNextLevel), nextLevelDelay);
            }
        }
    }

    void LoadNextLevel()
    {
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex + 1);
    }

    void OnGUI()
    {
        if (!finished) return;
        GUIStyle style = new GUIStyle(GUI.skin.label)
        {
            fontSize = 48,
            alignment = TextAnchor.MiddleCenter,
            fontStyle = FontStyle.Bold
        };
        style.normal.textColor = Color.white;
        string message = isLastLevel ? "You Win!" : "Level Complete!";
        GUI.Label(new Rect(0, 0, Screen.width, Screen.height), message, style);
    }
}
