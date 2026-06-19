using UnityEngine;
using UnityEngine.UIElements;

public class UiScript : MonoBehaviour
{
    private UIDocument _uiDocument;

    [Header("UXML Source Assets")]
    [SerializeField] private VisualTreeAsset mainMenuAsset;
    [SerializeField] private VisualTreeAsset settingsMenuAsset;
    private Button continueBtn;
    private Button newGameBtn;
    void Start()
    {
        if (transform.parent != null)
        {
            _uiDocument = transform.parent.GetComponent<UIDocument>();
        }
        else
        {
            _uiDocument = GetComponent<UIDocument>();
        }
        
        if (_uiDocument == null)
        {
            Debug.LogError("UiScript Error: No UIDocument component found!");
            return;
        }

        BindMainMenu();
    }

    private void BindMainMenu()
    {
        _uiDocument.visualTreeAsset = mainMenuAsset;
        VisualElement root = _uiDocument.rootVisualElement;

        if (root == null) return;

        Button settingsButton = root.Q<Button>("Settings");
        newGameBtn = root.Q<Button>("NewGameBtn");
        continueBtn = root.Q<Button>("ContinueBtn");
        newGameBtn.clicked += () =>
        {
            LevelManager.Instance.SaveLevelProgress(0);
            LevelManager.Instance.LoadCurrentLevel();
        };
        continueBtn.clicked += () =>
        {
            LevelManager.Instance.LoadCurrentLevel();
        };
        if (settingsButton != null)
        {
            settingsButton.clicked += showSettings;
        }
        else
        {
            Debug.LogError("UiScript Error: Could not find 'Settings' button in Main Menu.");
        }
        Button quit = root.Q<Button>("QuitGameBtn");
        quit.clicked+=quitGame;
    }

    private void BindSettingsMenu()
    {
        _uiDocument.visualTreeAsset = settingsMenuAsset;
        VisualElement root = _uiDocument.rootVisualElement;

        if (root == null) return;

        // Match your UXML hierarchy name "Backbtn"
        Button backSettingsButton = root.Q<Button>("Backbtn");
        if (backSettingsButton != null)
        {
            backSettingsButton.clicked += showMainMenu;
        }
        else
        {
            Debug.LogError("UiScript Error: Could not find 'Backbtn' button in Settings Menu.");
        }
    }

    private void showSettings()
    {
        BindSettingsMenu();
    }

    private void showMainMenu()
    {
        BindMainMenu();
    }
    
    private void quitGame()
    {
        Application.Quit();

        #if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
        #else
            Application.Quit(); 
        #endif
    }
}
