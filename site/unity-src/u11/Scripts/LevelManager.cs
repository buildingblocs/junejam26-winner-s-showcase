using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UIElements;

public class LevelManager : MonoBehaviour
{
    public static LevelManager Instance;

    [Header("Levels")]
    [SerializeField] private int maxLevels = 4;

    [Header("Timer")]
    [SerializeField] private float maxTimeLeft = 60f;
    private float timeLeft;
    private bool isTimerActive = false;

    private const string LEVEL_KEY = "CurrentLevel";
    public int CurrentLevel { get; private set; }

    [Header("UI Instructions")]
    [TextArea(3, 10)]
    public string Instructions = "";
    private string[] instructionsStr;
    private int instrIndex = 0;

    private UIDocument levelUI;
    private Label instruct;
    private Label timer;

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            SplitInstructions();
            SceneManager.sceneLoaded += OnSceneLoaded;
            Debug.Log("[LevelManager] Awake completed and initialized.");
        }
        else
        {
            Debug.Log("[LevelManager] Duplicate detected and destroyed.");
            Destroy(gameObject);
            return;
        }
    }

    private void Start()
    {
        LoadLevelProgress();
    }

    private void Update()
    {
        if (!isTimerActive) return;

        timeLeft -= Time.deltaTime;

        if (timeLeft <= 0f)
        {
            Debug.Log("[LevelManager] Time is up!");
            TimeUp();
            return;
        }

        if (timer != null)
        {
            timer.text = FormatTime(timeLeft);
        }
        else
        {
            Debug.LogWarning("[LevelManager] Timer text is active but the UI Label reference is missing inside Update!");
        }
    }

    private void OnSceneLoaded(Scene scene, LoadSceneMode mode)
    {
        CancelInvoke(nameof(UpdateInstructions));
        timeLeft = maxTimeLeft;
        instrIndex = 0;
        
        FindAndBindUI();
        
        isTimerActive = true; 
        Debug.Log($"[LevelManager] Scene Loaded: {scene.name}. Timer active status: {isTimerActive}. Initial timeLeft: {timeLeft}");
        
        if (instructionsStr != null)
        {
            for (int i = 0; i < instructionsStr.Length; i++)
            {
                Invoke(nameof(UpdateInstructions), 1f * i);
            }
        }
    }

    private void FindAndBindUI()
    {
        levelUI = Object.FindFirstObjectByType<UIDocument>();
        
        if (levelUI != null && levelUI.rootVisualElement != null)
        {
            VisualElement root = levelUI.rootVisualElement;
            timer = root.Q<Label>("Timer");
            instruct = root.Q<Label>("Instruct");

            if (timer != null)
            {
                timer.text = FormatTime(timeLeft);
                Debug.Log("[LevelManager] UI 'Timer' label successfully located and bound.");
            }
            else
            {
                Debug.LogWarning("[LevelManager] Could not find a UI Label named 'Timer' in the root visual element.");
            }

            if (instruct != null)
            {
                Debug.Log("[LevelManager] UI 'Instruct' label successfully located and bound.");
            }
            else
            {
                Debug.LogWarning("[LevelManager] Could not find a UI Label named 'Instruct' in the root visual element.");
            }
        }
        else
        {
            Debug.LogError("[LevelManager] No active UIDocument found in the current scene framework.");
            timer = null;
            instruct = null;
        }
    }

    private void SplitInstructions()
    {
        if (string.IsNullOrEmpty(Instructions))
        {
            instructionsStr = new string[] { "" };
            return;
        }

        instructionsStr = Instructions.Split('\n');
    }

    private void UpdateInstructions()
    {
        if (instruct == null || instructionsStr == null) return;
        
        if (instrIndex >= 0 && instrIndex < instructionsStr.Length)
        {
            instruct.text = instructionsStr[instrIndex];
            Debug.Log($"[LevelManager] Showing Instruction Index [{instrIndex}]: '{instructionsStr[instrIndex]}'");
            instrIndex++;
        }
        else
        {
            instruct.text = "";
        }
    }

    private void TimeUp()
    {
        timeLeft = maxTimeLeft;
        LoadCurrentLevel();
    }

    public void CompleteLevel()
    {
        if (CurrentLevel < maxLevels)
        {
            CurrentLevel++;
            SaveLevelProgress(CurrentLevel);
        }
        LoadCurrentLevel();
    }

    public void ResetProgress()
    {
        CurrentLevel = 0;
        SaveLevelProgress(CurrentLevel);
        LoadCurrentLevel();
    }

    public void SaveLevelProgress(int level)
    {
        CurrentLevel = Mathf.Clamp(level, 0, maxLevels);
        PlayerPrefs.SetInt(LEVEL_KEY, CurrentLevel);
        PlayerPrefs.Save();
    }

    public void LoadLevelProgress()
    {
        CurrentLevel = PlayerPrefs.GetInt(LEVEL_KEY, 0);
    }

    public void LoadCurrentLevel()
    {
        if (CurrentLevel == 0)
        {
            SceneManager.LoadScene("Tutorial");
        }
        else
        {
            SceneManager.LoadScene("Lvl" + CurrentLevel);
        }
    }

    private void OnDestroy()
    {
        if (Instance == this)
        {
            SceneManager.sceneLoaded -= OnSceneLoaded;
            CancelInvoke(nameof(UpdateInstructions));
        }
    }

    private string FormatTime(float timeToDisplay)
    {
        if (timeToDisplay < 0) timeToDisplay = 0;
        int minutes = Mathf.FloorToInt(timeToDisplay / 60);
        int seconds = Mathf.FloorToInt(timeToDisplay % 60);
        return string.Format("{0:00}:{1:00}", minutes, seconds);
    }
}
