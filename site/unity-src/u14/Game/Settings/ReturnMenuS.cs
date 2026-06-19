using UnityEngine;
using UnityEngine.SceneManagement;

public class ExitSettings : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void ToMenu()
    {
        SceneManager.LoadScene("MainMenu");
        Debug.Log("Main Menu loaded");
    }


}
