using UnityEngine;
using Vector3 = UnityEngine.Vector3;

public class PlayerMovement : MonoBehaviour
{
    public float moveSpeed = 8f;

    private Animator animator;
    private Vector2 moveInput;

    public LayerMask interactablesLayer;

    void Start()
    {
        animator = GetComponent<Animator>();
    }

    void Update()
    {
        HandleMovement();
        HandleInteract();
    }

    void HandleMovement()
    {
        moveInput.x = Input.GetAxisRaw("Horizontal");
        moveInput.y = Input.GetAxisRaw("Vertical");

        moveInput = moveInput.normalized;

        transform.position += (Vector3)moveInput * moveSpeed * Time.deltaTime;

        // Guard the animator: the player prefab may not have one, in which case
        // the original threw a NullReferenceException every frame and broke
        // movement entirely.
        if (animator != null)
        {
            if (moveInput != Vector2.zero)
            {
                animator.SetBool("IsMoving", true);
                animator.SetFloat("moveX", moveInput.x);
                animator.SetFloat("moveY", moveInput.y);
            }
            else
            {
                animator.SetBool("IsMoving", false);
            }
        }
    }

    void HandleInteract()
    {
        if (Input.GetKeyDown(KeyCode.E))
        {
            Debug.Log("E PRESSED");
            Interact();
        }
    }

    void Interact()
{
    Debug.Log("INTERACT FUNCTION CALLED");

    Collider2D hit = Physics2D.OverlapCircle(transform.position, 1.5f);

    if (hit == null)
    {
        Debug.Log("NO NPC FOUND");
        return;
    }

    SimpleDialogue dialogue = hit.GetComponentInParent<SimpleDialogue>();

    if (dialogue == null)
    {
        Debug.Log("NO DIALOGUE SCRIPT FOUND");
        return;
    }

    dialogue.Interact();
}
}