
using UnityEngine;
using UnityEngine.SceneManagement;

public class ReturntoMenuGE : MonoBehaviour
{
    public void ReturnMenu()
    {
        SceneManager.LoadScene("MainMenu");
        Debug.Log("Returned to Main Menu successfully");
    }
}
