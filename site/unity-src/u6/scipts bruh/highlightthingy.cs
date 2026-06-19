using UnityEngine;
using UnityEngine.InputSystem;
using TMPro;

public class HoverOutline : MonoBehaviour
{
    public TMP_Text hoverTextUI;
    public VideoController videoController;

    private Outline currentOutline;
    public dialogthingy dialogthingy;

    public Key interactKey = Key.E;

    void Update()
{
    if (currentOutline != null)
    {
        currentOutline.enabled = false;
        currentOutline = null;
    }

    hoverTextUI.text = "";

    Vector2 mousePos = Mouse.current.position.ReadValue();
    Ray ray = Camera.main.ScreenPointToRay(mousePos);

    if (Physics.Raycast(ray, out RaycastHit hit))
    {
        Outline outline = hit.collider.GetComponent<Outline>();

        if (outline != null)
        {
            outline.enabled = true;
            currentOutline = outline;
        }

        Interactable interactable = hit.collider.GetComponent<Interactable>();

        if (interactable != null)
        {
            hoverTextUI.text = interactable.hoverText;

            if (Keyboard.current[interactKey].wasPressedThisFrame)
            {
                if (dialogthingy != null)
                {
                    dialogthingy.OnTextFullyDisplayed -= OnDialogueTextFullyDisplayed;
                    dialogthingy.OnTextFullyDisplayed += OnDialogueTextFullyDisplayed;
                    dialogthingy.ShowDialogue(interactable.dialogueText);
                }
            }
        }
    }
}

    private void OnDialogueTextFullyDisplayed()
    {
        if (videoController != null)
        {
            videoController.PlayVideoOverlay();
        }

        if (dialogthingy != null)
        {
            dialogthingy.OnTextFullyDisplayed -= OnDialogueTextFullyDisplayed;
        }
    }
}
