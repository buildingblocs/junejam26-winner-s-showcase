using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class DialogueManager : MonoBehaviour
{
    // A clean data container structure that Unity can draw fields for in the Inspector
    [System.Serializable]
    public struct DialogueData
    {
        public string interactionKey; // e.g., "Intro_FilingCabinet"
        public string speakerName;    // e.g., "Player"
        [TextArea(2, 5)]
        public string[] sentences;    // Your conversation array lines
    }

    [Header("UI Component Hookups")]
    public TextMeshProUGUI nameText;
    public TextMeshProUGUI dialogueText;
    public GameObject dialoguePanel; 

    [Header("Dialogue Content Settings")]
    [Tooltip("Add and manage all game text entries right here instead of changing C# code fields!")]
    public DialogueData[] dialogueDatabase;

    private Queue<string> sentences;
    private PlayerMovement playerMovement;
    private bool dialogueStartedThisFrame = false;

    void Awake()
    {
        sentences = new Queue<string>();
        playerMovement = FindObjectOfType<PlayerMovement>();
        
        if (playerMovement == null)
        {
            Debug.LogWarning("[DialogueManager] PlayerMovement script not found in scene. Dialogue wont be able to freeze player.");
        }

        if (nameText == null) Debug.LogError("[DialogueManager] Inspector Field Missing: 'Name Text' is unassigned!");
        if (dialogueText == null) Debug.LogError("[DialogueManager] Inspector Field Missing: 'Dialogue Text' is unassigned!");
        if (dialoguePanel == null) Debug.LogError("[DialogueManager] Inspector Field Missing: 'Dialogue Panel' is unassigned!");

        if (dialoguePanel != null)
        {
            dialoguePanel.SetActive(false);
            Debug.Log("[DialogueManager] Initialized successfully. Dialogue Panel hidden by default.");
        }
    }

    void Update()
    {
        if (playerMovement != null && playerMovement.currentState == PlayerMovement.PlayerState.Talking)
        {
            if (Input.GetKeyUp(KeyCode.Space) || Input.GetKeyUp(KeyCode.E) || Input.GetMouseButtonUp(0))
            {
                if (dialogueStartedThisFrame)
                {
                    dialogueStartedThisFrame = false;
                    return;
                }

                Debug.Log("[DialogueManager] Advance input detected. Requesting next line.");
                DisplayNextSentence();
            }
        }
    }

    // --- switch case case case case case case case case case case case case---
    public void ProcessInteraction(string objectName)
    {
        Debug.Log($"[DialogueManager] ProcessInteraction looking up data key: '{objectName}'");
        
        // Edit the thing in unity's inspector. 
        foreach (DialogueData item in dialogueDatabase)
        {
            if (item.interactionKey == objectName)
            {
                Debug.Log($"[DialogueManager] Match found for key: '{objectName}'. Passing payload.");
                StartDialogue(item.speakerName, item.sentences);
                return;
            }
        }
        // KNOWN ERROR: if interractable object is not meant to have a dialogue entry, will print this error anyway.
        Debug.LogWarning($"[DialogueManager] Failsafe hit. Dialogue key '{objectName}' not found in Inspector Database configurations");
        StartDialogue("???", new string[] { $"[Missing text entry string data asset for: {objectName}]" });
    }

    private void StartDialogue(string characterName, string[] npcSentences)
    {
        if (playerMovement != null)
        {
            playerMovement.currentState = PlayerMovement.PlayerState.Talking;
        }
        
        if (dialoguePanel != null) dialoguePanel.SetActive(true);
        
        nameText.text = characterName;
        sentences.Clear();

        foreach (string sentence in npcSentences)
        {
            sentences.Enqueue(sentence);
        }

        dialogueStartedThisFrame = true;
        DisplayNextSentence();
    }

    public void DisplayNextSentence()
    {
        if (sentences.Count == 0)
        {
            EndDialogue();
            return;
        }

        string currentSentence = sentences.Dequeue();
        dialogueText.text = currentSentence;
        dialogueText.ForceMeshUpdate(); 
    }

    void EndDialogue()
    {
        Debug.Log("[DialogueManager] Closing dialogue sequence panel.");
        if (dialoguePanel != null) dialoguePanel.SetActive(false);
        
        PuzzleManager puzzleManager = FindObjectOfType<PuzzleManager>();
        
        // --- SLEEK ARCHITECTURE CLEANUP UP ---
        // Ask the PuzzleManager directly if it's currently holding any windows open
        bool aPuzzleIsCurrentlyOpen = (puzzleManager != null && puzzleManager.IsAnyPuzzlePanelOpen());
        
        if (aPuzzleIsCurrentlyOpen)
        {
            Debug.Log("[DialogueManager] Dialogue ended, keeping player frozen for puzzle display visibility.");
        }
        else
        {
            if (playerMovement != null)
            {
                playerMovement.currentState = PlayerMovement.PlayerState.Free;
            }
        }
    }
}