using UnityEngine;
using UnityEngine.SceneManagement;

public class QuestManager : MonoBehaviour
{
    public static QuestManager Instance { get; private set; }

    [Header("Settings")]
    public int pointsToWin = 5;

    public int CurrentPoints { get; private set; } = 0;

    public event System.Action<int> OnPointsChanged; 

    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    public void AddPoint()
    {
        CurrentPoints++;
        OnPointsChanged?.Invoke(CurrentPoints);

        if (CurrentPoints >= pointsToWin)
            TriggerWin();
    }

    private void TriggerWin()
    {
        Debug.Log("You win!");
        // swap this for your win screen scene name
        SceneManager.LoadScene("WinScreen");
    }
}
