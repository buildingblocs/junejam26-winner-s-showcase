using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenuController : MonoBehaviour
{
    [Header("Scene Configuration")]
    [Tooltip("Type the EXACT name of your main gameplay scene asset file here!")]
    public string gameplaySceneName = "MainLevel"; 

    public void PlayGame()
    {
        Debug.Log("[MainMenu] Play button pressed. Loading gameplay scene...");
        SceneManager.LoadScene(gameplaySceneName);
    }

    public void QuitGame()
    {
        Debug.Log("[MainMenu] Quit button pressed. Closing application.");
        Application.Quit();
    }
}