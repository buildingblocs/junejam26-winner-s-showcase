using UnityEngine;

public class DialogueTrigger : MonoBehaviour
{
    public string[] dialogueLines;

    private bool triggered = false;

    [System.Obsolete]
    private void OnTriggerEnter2D(Collider2D other)
    {
        if (triggered)
            return;

        if (other.CompareTag("Player"))
        {
            Debug.Log("Player contact");
            FindObjectOfType<DialogueManager>()
                .StartDialogue(dialogueLines);

            triggered = true;
        }
    }
}