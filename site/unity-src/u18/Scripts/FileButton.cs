using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class FileButton : MonoBehaviour
{
    public TMP_Text fileNameText;
    
    private string myPath;
    private bool isCorrectTarget;
    private PuzzleManager manager;

    public void Setup(string path, bool isCorrect, bool playerHasSorter, PuzzleManager puzzleManager)
    {
        myPath = path;
        isCorrectTarget = isCorrect;
        manager = puzzleManager;
        fileNameText.text = myPath;

        // Color Swap: If player has the tool from Puzzle 2 AND this is the winning file
        if (playerHasSorter && isCorrectTarget)
        {
            Image buttonImage = GetComponent<Image>();
            if (buttonImage != null)
            {
                buttonImage.color = Color.green; 
            }
        }

        GetComponent<Button>().onClick.AddListener(OnFileClicked);
    }

    private void OnFileClicked()
    {
        if (isCorrectTarget)
        {
            manager.ResolvePuzzle3Success();
        }
        else
        {
            DialogueManager dialogue = FindObjectOfType<DialogueManager>();
            if (dialogue != null)
            {
                dialogue.ProcessInteraction("FilingCabinet_Doubt_Dialogue");
            }
        }
    }
}