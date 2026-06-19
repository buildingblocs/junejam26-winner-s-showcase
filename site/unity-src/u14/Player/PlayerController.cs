using UnityEngine;
using UnityEngine.InputSystem;
/*
Move - WASD
Look - Mouse
Interact - E
*/

public class PlayerController : MonoBehaviour
{
    // Player Movement
    InputAction moveAction;
    private float speed = 8f;
    private Rigidbody rb;
    

    // Player's Camera Angle
    InputAction lookAction;
    private float mouseSensitivity = 0.5f;
    private float rotX = 0f;   
    private float rotY = 0f;
    private float reachDist = 3f;

    // Player's Inventory
    private GameObject itemHeld = null;
    private InteractableObject itemScript = null;

    // Player's Task Completion
    public int completedTasks = 0;
    public int failedTasks = 0;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        moveAction = InputSystem.actions.FindAction("Move");
        lookAction = InputSystem.actions.FindAction("Look");
        Cursor.lockState = CursorLockMode.Locked;   // Locked at start
        rb = GetComponent<Rigidbody>();
        rb.freezeRotation = true;
    }

    // Update is called once per frame
    void Update()
    {
        if(PauseMenu.isPaused)
        {
            Cursor.lockState = CursorLockMode.None;
            return;
        }
        Cursor.lockState = CursorLockMode.Locked;
        Move();
        Look();
        Interact();
    }








    void Move()
    {
        // Player movement
        Vector2 moveValue = moveAction.ReadValue<Vector2>();
        Vector3 moveDirection = (moveValue.x * transform.right) + (moveValue.y * transform.forward); 
        /// Explanation for vectors logic
        /// final vector Eg. (1,0,1) 
        /// eg. 0.5 . (1,0,0) = (0.5,0,0)  where (1,0,0) is transform.right 


        if(moveDirection.magnitude > 1)
        {
            moveDirection.Normalize();     // Vector of magnitude 1
        }

        Vector3 movement = moveDirection * speed;      // Scaled with speed
        rb.linearVelocity = new Vector3(movement.x, rb.linearVelocity.y, movement.z);     // Move Character
    }

    void Look()
    {
        //Player Camera
        Vector2 lookValue = lookAction.ReadValue<Vector2>();
        float scaledX = lookValue.x * mouseSensitivity;
        float scaledY = lookValue.y * mouseSensitivity;

        rotY -= scaledY;
        rotY = Mathf.Clamp(rotY, -89f, 89f); // Prevents breaking of necks
        Camera.main.transform.localRotation = Quaternion.Euler(rotY, 0f, 0f);   // Only change in camera direction and not Player's model

        // Camera Left and right
        rotX += scaledX;
        transform.rotation = Quaternion.Euler(0f, rotX, 0f);    // Camera direction changes with Player's model

    }

    void Interact()
    {
        if(Input.GetKeyDown(KeyCode.E)){
            Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);    // Vector of ray
            if(Physics.Raycast(ray, out RaycastHit hit, reachDist))
            {
                if(hit.collider.CompareTag("interactableObject")){
                    Debug.Log("Object interacted with");
                    hit.collider.gameObject.SetActive(false);
                    PickupItem(hit.collider.gameObject, hit.collider.GetComponent<InteractableObject>());
                }

                if(hit.collider.CompareTag("questGiver")){      // Remember to link to NPC to accept quest
                    Debug.Log("Quest received");
                    questGiver person = hit.collider.GetComponent<questGiver>();
                    person.GiveQuest();
                    return;

                }
            }
        }
    }

    void PickupItem(GameObject item, InteractableObject script)
    {
        itemHeld = item;
        itemScript = script;
        Debug.Log($"Player picked up {itemHeld.name}");
        Debug.Log($"Item is for {script.itemType}");
        script.PickedUp();
        if(script.itemType == InteractableObject.ItemType.TaskItem)
        {
            questGiver person = FindAnyObjectByType<questGiver>();
            person.CompleteTask();
        }

    }
}
