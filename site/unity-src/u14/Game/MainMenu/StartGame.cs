

using System.Security.AccessControl;
using UnityEngine;
using UnityEngine.SceneManagement;

public class StartGame : MonoBehaviour
{
    public static bool isPaused = false;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        Cursor.lockState = CursorLockMode.None;

        Cursor.visible = true;
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void StartEasy()
    {   
        SceneManager.LoadScene("EasyScene");
        Debug.Log("Easy scene loaded");
        isPaused = false;
    }

    public void StartMedium()
    {
        SceneManager.LoadScene("MediumScene");
        Debug.Log("Medium scene loaded");
    }
    public void StartSettings()
    {
        SceneManager.LoadScene("Settings");
        Debug.Log("Settings loaded");
    }
    public void StartCredits()
    {
        SceneManager.LoadScene("CreditsScene");
        Debug.Log("Credits loaded");

    }
    
}
