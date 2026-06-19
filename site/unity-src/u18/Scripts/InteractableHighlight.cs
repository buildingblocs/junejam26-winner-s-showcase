using UnityEngine;

public class InteractableHighlight : MonoBehaviour
{
    [Header("Visual Feedback Hook")]
    [Tooltip("Drag a child 'Border' GameObject here, or leave blank to use basic color shifting!")]
    public GameObject visualBorder;

    private SpriteRenderer sRenderer;
    private Color originalColor;

    void Awake()
    {
        sRenderer = GetComponent<SpriteRenderer>();
        if (sRenderer != null) originalColor = sRenderer.color;
        
        // Ensure the visual border is hidden on startup execution
        SetHighlight(false);
    }

    public void SetHighlight(bool shouldHighlight)
    {
        // Option A: If you dragged an explicit border outline object, toggle its visibility
        if (visualBorder != null)
        {
            visualBorder.SetActive(shouldHighlight);
        }
        // Option B: Failsafe fallback - if no border exists, tint the sprite color slightly so it flashes
        else if (sRenderer != null)
        {
            sRenderer.color = shouldHighlight ? new Color(1.2f, 1.2f, 1.2f, 1f) : originalColor;
        }
    }
}