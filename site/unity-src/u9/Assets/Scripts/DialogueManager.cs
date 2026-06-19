using UnityEngine;
using TMPro;

public class DialogueManager : MonoBehaviour
{
    public GameObject dialogueBox;
    public TextMeshProUGUI dialogueText;

    public string[] lines;
    private int currentLine = 0;

    void Start()
    {
        dialogueBox.SetActive(false);
    }

    public void StartDialogue(string[] newLines)
    {
        if (newLines == null || newLines.Length == 0)
        {
            Debug.LogWarning("DialogueManager: No dialogue lines provided!");
            return;
        }
        
        lines = newLines;
        currentLine = 0;

        dialogueBox.SetActive(true);
        dialogueText.text = lines[currentLine];
    }

    void Update()
    {
        if (dialogueBox.activeSelf && Input.GetKeyDown(KeyCode.Space))
        {
            NextLine();
        }
    }

    void NextLine()
    {
        currentLine++;

        if (currentLine >= lines.Length)
        {
            dialogueBox.SetActive(false);
        }
        else
        {
            dialogueText.text = lines[currentLine];
        }
    }
}