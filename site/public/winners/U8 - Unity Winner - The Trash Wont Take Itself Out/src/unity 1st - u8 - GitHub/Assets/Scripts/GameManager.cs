using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    [SerializeField] private PlayerController playerController;

    public bool gameStart = false;

    private void Awake()
    {
        // Ensures players cannot move when in main menu scene.
        playerController.enabled = false;
    }

    void Start()
    {
        Time.timeScale = 1.0f;
    }

    public void StartGame()
    {
        playerController.enabled = true;

        gameStart = true;

        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    public void RestartGame()
    {
        var currentScene = SceneManager.GetActiveScene();
        SceneManager.LoadScene(currentScene.name);
    }
}
