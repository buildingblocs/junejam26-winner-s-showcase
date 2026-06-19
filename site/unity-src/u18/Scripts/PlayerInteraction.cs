using UnityEngine;

public class PlayerInteraction : MonoBehaviour
{
    public KeyCode interactKey = KeyCode.E;
    
    [Header("Detection Settings")]
    public Vector2 boxSize = new Vector2(0.8f, 0.8f);
    public float boxOffsetDistance = 0.7f;
    
    [Tooltip("Set this to an 'Interactable' layer so the player ignores cameras, floors, and triggers!")]
    public LayerMask interactionLayer;

    private PlayerMovement movementScript;
    private InteractableHighlight currentlyHighlightedTarget;

    void Start()
    {
        movementScript = GetComponent<PlayerMovement>();
        if (movementScript == null)
        {
            Debug.LogError("[PlayerInteraction] CRITICAL: PlayerMovement script NOT found on this GameObject!");
        }
    }

    void Update()
    {
        if (movementScript.currentState == PlayerMovement.PlayerState.Talking)
        {
            // Failsafe: Clear out visual highlights instantly if a text event begins
            ClearCurrentHighlight();
            return; 
        }

        // --- NEW: Dynamic real-time border target detection loop ---
        ScanForClosestInteractable();

        if (Input.GetKeyDown(interactKey))
        {
            TryInteract();
        }
    }

    private void ScanForClosestInteractable()
    {
        Vector2 lookDir = (movementScript != null) ? movementScript.GetLookDirection() : Vector2.down;
        Vector2 boxCenter = (Vector2)transform.position + (lookDir * boxOffsetDistance);

        Collider2D[] hitObjects = Physics2D.OverlapBoxAll(boxCenter, boxSize, 0f, interactionLayer);
        Collider2D closestCollider = null;
        float closestDistance = Mathf.Infinity;

        foreach (var col in hitObjects)
        {
            if (col.gameObject == this.gameObject) continue;
            float distance = Vector2.Distance(transform.position, col.transform.position);
            if (distance < closestDistance)
            {
                closestDistance = distance;
                closestCollider = col;
            }
        }

        if (closestCollider != null)
        {
            InteractableHighlight newHighlight = closestCollider.GetComponent<InteractableHighlight>();
            
            // If the closest item changed, update our targets cleanly
            if (newHighlight != currentlyHighlightedTarget)
            {
                ClearCurrentHighlight();
                currentlyHighlightedTarget = newHighlight;
                if (currentlyHighlightedTarget != null) currentlyHighlightedTarget.SetHighlight(true);
            }
        }
        else
        {
            ClearCurrentHighlight();
        }
    }

    private void ClearCurrentHighlight()
    {
        if (currentlyHighlightedTarget != null)
        {
            currentlyHighlightedTarget.SetHighlight(false);
            currentlyHighlightedTarget = null;
        }
    }

    void TryInteract()
    {
        Vector2 lookDir = (movementScript != null) ? movementScript.GetLookDirection() : Vector2.down;
        Vector2 boxCenter = (Vector2)transform.position + (lookDir * boxOffsetDistance);

        // --- FIXED: Added interactionLayer filter right into the engine physics cast ---
        Collider2D[] hitObjects = Physics2D.OverlapBoxAll(boxCenter, boxSize, 0f, interactionLayer);

        if (hitObjects.Length == 0)
        {
            return;
        }

        Collider2D closestCollider = null;
        float closestDistance = Mathf.Infinity;

        foreach (var col in hitObjects)
        {
            if (col.gameObject == this.gameObject) continue;

            float distance = Vector2.Distance(transform.position, col.transform.position);

            if (distance < closestDistance)
            {
                closestDistance = distance;
                closestCollider = col;
            }
        }

        if (closestCollider != null)
        {
            string objectName = closestCollider.gameObject.name;

            // Check if the object has a puzzle component
            PuzzleObject puzzle = closestCollider.GetComponent<PuzzleObject>();
            
            if (puzzle != null)
            {
                PuzzleManager puzzleManager = FindObjectOfType<PuzzleManager>();
                if (puzzleManager != null)
                {
                    puzzleManager.TriggerPuzzle(puzzle.puzzleType, movementScript);
                    return; 
                }
            }

            // Dialogue fallback uses the object name key safely, knowing it's an approved object
            DialogueManager manager = FindObjectOfType<DialogueManager>();
            if (manager != null)
            {
                manager.ProcessInteraction(objectName);
            }
        }
    }

    private void OnDrawGizmosSelected()
    {
        if (movementScript == null) movementScript = GetComponent<PlayerMovement>();
        Vector2 lookDir = (movementScript != null) ? movementScript.GetLookDirection() : Vector2.down;
        Vector2 boxCenter = (Vector2)transform.position + (lookDir * boxOffsetDistance);
        Gizmos.color = Color.green;
        Gizmos.DrawWireCube(boxCenter, boxSize);
    }
}