using UnityEngine;
using UnityEngine.SceneManagement;

public class ReturnMenuCred : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    public void ReturnMenuCredits()
    {
        SceneManager.LoadScene("MainMenu");
        Debug.Log("Main Menu Loaded");

    }
}
