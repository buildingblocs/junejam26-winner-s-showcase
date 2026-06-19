using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }
    public string PreviousScene { get; private set; }

    private void Awake()
    {
        // Ensure only one instance exists and it persists between scene loads
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    public void TriggerGameOver()
    {
        // Save the name of the scene that is currently active
        PreviousScene = SceneManager.GetActiveScene().name;
        
        // Load your Game Over scene
        SceneManager.LoadScene("GameOverScene"); 
    }
}
