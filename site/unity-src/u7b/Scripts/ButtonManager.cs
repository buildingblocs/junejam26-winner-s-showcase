using UnityEngine;
using UnityEngine.SceneManagement;

public class ButtonManager : MonoBehaviour
{
    public void StartJohn(){
        SceneManager.LoadScene("LevelA-1");
    }

    public void StartCass(){
        SceneManager.LoadScene("LevelB-1");
    }

    public void StartSam(){
        SceneManager.LoadScene("LevelC-1");
    }

    public void GoCredits(){
        SceneManager.LoadScene("Credits");
    }

    public void BackMenu(){
        SceneManager.LoadScene("Menu");
    }
}
