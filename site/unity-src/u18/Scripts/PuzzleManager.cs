using UnityEngine;
using TMPro;
using System.Text.RegularExpressions;

public class PuzzleManager : MonoBehaviour
{
    [Header("Puzzle State Tracking")]
    // Remembers if a puzzle type string has been triggered before during this play session
    private System.Collections.Generic.HashSet<string> triggeredPuzzles = new System.Collections.Generic.HashSet<string>();

    [Header("Clean UI Infrastructure Layout")]
    [Tooltip("Drag ALL your puzzle panel GameObjects into this list container in the Inspector!")]
    public GameObject[] allPuzzlePanels;

    [Header("Player Tracking")]
    public PlayerMovement playerMovement;

    [Header("Puzzle 1 Panels")]
    public GameObject stickyNotePanel;
    public GameObject combinationLockPanel;

    [Header("Puzzle 2 (OSINT) Panels")]
    public GameObject mailScreenPanel;  // Mial
    public GameObject linkedinScreenPanel;  // LinkedIn
    public GameObject targetLoginPanel; //Login

    [Header("Puzzle 1 Settings")]
    public int targetCombination = 127; // Password for lockbox puzzle 1. Dont update value here, do it in the inspector
    public TMP_Text[] digitDisplays;    
    public GameObject zoneBDoorObstacle; // To do: update sprite for door

    [Header("Puzzle 2 Settings")]
    public TMP_InputField passwordInput;
    public TMP_Text loginErrorText;

    [Header("Puzzle 3 (Wordlist) Settings")]
    public GameObject puzzle3Panel;
    public Transform fileGridContainer;    
    public GameObject fileButtonPrefab;  
    public TextAsset wordlistTextFile;     
    public string exactCorrectPath = "vault_credentials.cfg"; 

    [Header("Final Escape Terminal Settings")]
    public GameObject finalTerminalPanel;
    public TMP_InputField finalUsernameInput;
    public TMP_InputField finalPasswordInput;
    public TMP_Text finalTerminalErrorText;
    public GameObject finalEscapeDoorObstacle; // The door out of the level
    public GameObject gameWinScreenOverlay;   // The screen that stops gameplay
    
    
    [Header("Global Unlock Flags")]
    public bool hasFileSorter = false;  // dirb, use to make puzzle 3 easy

    private int[] currentDigits = new int[3] { 0, 0, 0 };
    private bool isPuzzleActive = false;

    void Start()
    {
        // Clean automation sweep setup sequence on startup
        if (allPuzzlePanels != null)
        {
            foreach (GameObject panel in allPuzzlePanels)
            {
                if (panel != null) panel.SetActive(false);
            }
        }

        if (loginErrorText != null) loginErrorText.text = "";
    }

    void Update()
    {
        // TODO: Lock movement. Ts dont work bro. 
        if (isPuzzleActive && Input.GetKeyDown(KeyCode.Escape))
        {
            CloseCurrentPuzzle();
        }
    }

    public bool IsAnyPuzzlePanelOpen()
    {
        if (allPuzzlePanels == null) return false;
        
        foreach (GameObject panel in allPuzzlePanels)
        {
            if (panel != null && panel.activeInHierarchy)
            {
                return true; // Found an open panel instantly, tell whoever asked
            }
        }
        return false;
    }

    public void TriggerPuzzle(string puzzleType, PlayerMovement incomingPlayerScript)
    {
        if (isPuzzleActive) return; 

        playerMovement = incomingPlayerScript;

        bool isFirstTime = !triggeredPuzzles.Contains(puzzleType);
        if (isFirstTime)
        {
            triggeredPuzzles.Add(puzzleType);
            
            DialogueManager dialogue = FindObjectOfType<DialogueManager>();
            if (dialogue != null)
            {

                dialogue.ProcessInteraction("Intro_" + puzzleType);
            }
        }

        // KNOWN ISSUE: Should switch to unity inspector option rather than switch case statements
        switch (puzzleType)
        {
            case "StickyNote":
                OpenPanel(stickyNotePanel);
                break;
            case "Lock":
                OpenPanel(combinationLockPanel);
                UpdateLockDisplay();
                break;
            case "OSINT_Mail":
                OpenPanel(mailScreenPanel);
                break;
            case "OSINT_Linkedin":
                OpenPanel(linkedinScreenPanel);
                break;
            case "OSINT_Login":
                OpenPanel(targetLoginPanel);
                if (loginErrorText != null) loginErrorText.text = "";
                break;
            case "FilingCabinet":
                OpenFilingCabinet();
                break;
            case "Final_Terminal":
                OpenPanel(finalTerminalPanel);
                if (finalTerminalErrorText != null) finalTerminalErrorText.text = "";
                break;
            default:
                Debug.LogError($"[PuzzleManager] your string mismatch zzz -  '{puzzleType}' - ");
                break;
        }
    }

    private void OpenPanel(GameObject panel)
    {
        if (panel == null) return;
        panel.SetActive(true);
        isPuzzleActive = true;

        if (playerMovement != null)
        {
            playerMovement.currentState = PlayerMovement.PlayerState.Talking;
        }
    }

    public void CloseCurrentPuzzle()
    {
        // Safely shuts down every panel registered in your infrastructure
        if (allPuzzlePanels != null)
        {
            foreach (GameObject panel in allPuzzlePanels)
            {
                if (panel != null) panel.SetActive(false);
            }
        }
        
        isPuzzleActive = false;

        if (playerMovement != null)
        {
            playerMovement.currentState = PlayerMovement.PlayerState.Free;
        }
    }

    // --- PUZZLE 1: LOCKBOX  ---
    public void IncrementDigit(int digitIndex)
    {
        if (digitIndex < 0 || digitIndex >= currentDigits.Length) return;
        currentDigits[digitIndex] = (currentDigits[digitIndex] + 1) % 10; 
        UpdateLockDisplay();
        CheckCombination();
    }

    private void UpdateLockDisplay()
    {
        for (int i = 0; i < digitDisplays.Length; i++)
        {
            if (digitDisplays[i] != null) digitDisplays[i].text = currentDigits[i].ToString();
        }
    }

    private void CheckCombination()
    {
        int currentInGameCode = (currentDigits[0] * 100) + (currentDigits[1] * 10) + currentDigits[2];
        if (currentInGameCode == targetCombination)
        {
            if (zoneBDoorObstacle != null) Destroy(zoneBDoorObstacle); 
            CloseCurrentPuzzle();
            DialogueManager dialogue = FindObjectOfType<DialogueManager>();
            if (dialogue != null)
            {
                dialogue.ProcessInteraction("Puzzle1_Complete_Dialogue");
            }
        }
    }

    // --- PUZZLE 2: OSINT ---
    public void SubmitOSINTLogin()
    {
        if (passwordInput == null) return;

        string enteredPass = passwordInput.text.Trim();

        // Regex parameters: ^ balances start, $ balances end, RegexOptions.IgnoreCase ignores capitalization completely
        if (Regex.IsMatch(enteredPass, "^johnjohnson03$", RegexOptions.IgnoreCase)) // change password here if need, but youd also need to change the password in the assets. Not reccomended.
        {
            Debug.Log("[PUZZLE 2 SUCCESS] Swapped state. Granting File Sorter tool.");
            
            hasFileSorter = true;
            CloseCurrentPuzzle();

            DialogueManager manager = FindObjectOfType<DialogueManager>();
            if (manager != null)
            {
                manager.ProcessInteraction("FileSorterAcquired_DialogueEvent");
            }
        }
        else
        {
            if (loginErrorText != null)
            {
                loginErrorText.text = "INVALID SECURITY TOKEN PATH NOT FOUND.";
                loginErrorText.color = Color.red;
            }
        }
    }
    // --- Puzzle 3: Dir Discovery ---
    private string[] activeSessionFiles = null;

    private void GeneratePuzzle3Pool()
    {
        if (wordlistTextFile == null) return;

        // Split your massive text document into a clean array
        string[] allLines = wordlistTextFile.text.Split(new[] { '\r', '\n' }, System.StringSplitOptions.RemoveEmptyEntries);
        
        if (allLines.Length == 0) return;

        // Establish the maximum size constraints safely
        int totalToPick = Mathf.Min(50, allLines.Length);
        activeSessionFiles = new string[totalToPick];

        // Create a temporary index tracking list to select distinct lines without duplication
        System.Collections.Generic.List<int> availableIndices = new System.Collections.Generic.List<int>();
        for (int i = 0; i < allLines.Length; i++) availableIndices.Add(i);

        // Populate the unique pool array
        for (int i = 0; i < totalToPick; i++)
        {
            int randomPick = Random.Range(0, availableIndices.Count);
            int selectedIndex = availableIndices[randomPick];
            
            activeSessionFiles[i] = allLines[selectedIndex].Trim();
            availableIndices.RemoveAt(randomPick);
        }

        // Select exactly one random winning option out of our newly drawn pool array
        int targetWinnerIndex = Random.Range(0, activeSessionFiles.Length);
        exactCorrectPath = activeSessionFiles[targetWinnerIndex];
        
        Debug.Log($"[PUZZLE 3 INITIALIZED] Dynamic winning file set to: {exactCorrectPath}");
    }

    private void OpenFilingCabinet()
    {
        OpenPanel(puzzle3Panel);

        // Clear previous buttons out of the layout container layout
        foreach (Transform child in fileGridContainer)
        {
            Destroy(child.gameObject);
        }

        // Lazily generate our randomized pool layout if this is the very first interaction contact
        if (activeSessionFiles == null)
        {
            GeneratePuzzle3Pool();
        }

        if (activeSessionFiles == null) return;

        // Instantiate the pre-calculated 50 files cleanly
        foreach (string line in activeSessionFiles)
        {
            if (string.IsNullOrEmpty(line)) continue;

            bool isTarget = (line == exactCorrectPath);

            GameObject newBtn = Instantiate(fileButtonPrefab, fileGridContainer);
            FileButton fileScript = newBtn.GetComponent<FileButton>();
            
            fileScript.Setup(line, isTarget, hasFileSorter, this);
        }
    }

    public void ResolvePuzzle3Success()
    {
        CloseCurrentPuzzle();
        
        DialogueManager dialogue = FindObjectOfType<DialogueManager>();
        if (dialogue != null)
        {
            dialogue.ProcessInteraction("ZoneC_Credentials_Found");
        }
    }
    // --- PUZZLE 3.1: terminal lock ---
    public void SubmitFinalSystemCredentials()
    {
        if (finalUsernameInput == null || finalPasswordInput == null) return;

        string userText = finalUsernameInput.text.Trim();
        string passText = finalPasswordInput.text.Trim();

        // Exact match checking against the credentials found in your filing system text cache
        if (userText == "admin" && passText == "admin")
        {
            Debug.Log("[ESCAPE SEQUENCE] Root authorized. Removing physical containment structures.");
            
            if (finalEscapeDoorObstacle != null) Destroy(finalEscapeDoorObstacle);
            
            CloseCurrentPuzzle();

            // Fire the narrative resolution or drop the Game Win Screen asset directly in place
            if (gameWinScreenOverlay != null)
            {
                gameWinScreenOverlay.SetActive(true);
                // Set state to freeze inputs indefinitely
                if (playerMovement != null) playerMovement.currentState = PlayerMovement.PlayerState.Talking;
            }

            DialogueManager dialogue = FindObjectOfType<DialogueManager>();
            if (dialogue != null)
            {
                dialogue.ProcessInteraction("System_Override_Win_Sequence");
            }
        }
        else
        {
            if (finalTerminalErrorText != null)
            {
                finalTerminalErrorText.text = "ACCESS DENIED: INVALID ROOT PROFILE METRICS.";
                finalTerminalErrorText.color = Color.red;
            }
        }
    }
}