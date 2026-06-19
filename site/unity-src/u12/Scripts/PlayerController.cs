using UnityEngine;

public class PlayerController : MonoBehaviour
{
    public CharacterController controller;

    [Header("Movement")]
    public float walkSpeed = 5f;
    public float sprintSpeed = 8f;

    [Header("Jump")]
    public float gravity = -9.81f;
    public float jumpHeight = 1.5f;

    private Vector3 velocity;

    void Start()
    {
        controller = GetComponent<CharacterController>();
    }

    void Update()
    {
        bool isGrounded = controller.isGrounded;

        if (isGrounded && velocity.y < 0)
        {
            velocity.y = -2f;
        }

        float x = Input.GetAxis("Horizontal");
        float z = Input.GetAxis("Vertical");

        Vector3 move =
            transform.right * x +
            transform.forward * z;

        float currentSpeed = walkSpeed;

        if (Input.GetKey(KeyCode.LeftShift))
        {
            currentSpeed = sprintSpeed;
        }

        controller.Move(
            move *
            currentSpeed *
            Time.deltaTime
        );

        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            velocity.y =
                Mathf.Sqrt(
                    jumpHeight * -2f * gravity
                );
        }

        velocity.y += gravity * Time.deltaTime;

        controller.Move(
            velocity *
            Time.deltaTime
        );

        // Lamp interaction
        if (Input.GetKeyDown(KeyCode.F))
        {
            GameObject lamp =
                GameObject.Find("Lamp");

            if (lamp != null)
            {
                float distance =
                    Vector3.Distance(
                        transform.position,
                        lamp.transform.position
                    );

                if (distance < 3f)
                {
                    Interactable interactable =
                        lamp.GetComponent<Interactable>();

                    if (interactable != null)
                    {
                        interactable.Interact();
                    }
                }
            }
        }
    }
}