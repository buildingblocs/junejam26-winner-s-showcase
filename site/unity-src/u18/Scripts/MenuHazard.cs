using UnityEngine;
using UnityEngine.SceneManagement;

public class MenuHazard : MonoBehaviour
{
    [Header("Scene Routing")]
    [Tooltip("Type the EXACT name of your Main Menu scene asset file here!")]
    public string mainMenuSceneName = "MainMenu";

    // This triggers automatically whenever an object enters this object's 2D collider matrix
    private void OnTriggerEnter2D(Collider2D collision)
    {
        // Check if the object that bumped into this is tagged as the Player
        if (collision.CompareTag("Player"))
        {
            Debug.Log("[Hazard] Player collision detected. Force returning to Main Menu...");
            SceneManager.LoadScene(mainMenuSceneName);
        }
    }
}