
using UnityEngine;
using UnityEngine.SceneManagement;

public class ReturntoMenu : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    public void ReturnMenu()
    {
        SceneManager.LoadScene("MainMenu");
        Debug.Log("Returned to Main Menu successfully");
    }
}
