



using System.Security.AccessControl;
using UnityEngine;
using UnityEngine.SceneManagement;

public class PauseMenu : MonoBehaviour {
    public GameObject pauseMenuUI;
    public GameObject crosshair;
    public GameObject storyUI;
    
    

public GameObject settingsMenuUI;
    public static bool isPaused = true;

    void Update() {
        if (Input.GetKeyDown(KeyCode.Escape)) {
            if (isPaused) Resume();
            
            else Pause();
        }
    }

    public void Start()
    {
        crosshair.SetActive(false);
        isPaused = true;
        
    }

    public void Resume() {
        pauseMenuUI.SetActive(false);
        Time.timeScale = 1f; // Resumes the game
        isPaused = false;
        Debug.Log("Game Resumed");

        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;

        crosshair.SetActive(true);
        
    }

    public void Pause() {
        pauseMenuUI.SetActive(true);
        Time.timeScale = 0f; // Pauses the game
        isPaused = true;
        Debug.Log("Game Paused");

        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;

        crosshair.SetActive(false);
    }

    public void LoadMenu() {
        Time.timeScale = 1f;
        SceneManager.LoadScene("MainMenu"); // Replace with your Menu scene name
        Debug.Log("Returned to Main Menu");
        isPaused = false;
    }
    public void LoadSettings()
    {
        Time.timeScale = 0f;
        settingsMenuUI.SetActive(true);
        Debug.Log("Settings opened");
        isPaused = true;

        pauseMenuUI.SetActive(false);
    }
    public void ReturnPause()
    {
        Time.timeScale = 0f;
        settingsMenuUI.SetActive(false);
        Debug.Log("Settings closed");
        pauseMenuUI.SetActive(true);
        isPaused = true;
    }

    public void StoryLeave()
    {
        Time.timeScale = 1f;
        storyUI.SetActive(false);
        isPaused = false;
        Debug.Log("Closed Story");
        crosshair.SetActive(true);
    }

    
}
