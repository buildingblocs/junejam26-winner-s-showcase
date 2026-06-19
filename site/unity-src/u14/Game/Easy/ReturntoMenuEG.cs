using UnityEngine;
using UnityEngine.SceneManagement;

public class ReturntoMenuEG : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    void ReturnMenu()
    {
        SceneManager.LoadScene("MainMenu");
        Debug.Log("Returned to Main Menu");
    }
}
