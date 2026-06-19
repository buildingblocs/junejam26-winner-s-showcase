using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.InputSystem;

[RequireComponent(typeof(Rigidbody))]
public class Player_Controller : MonoBehaviour
{
    public float speed = 5f;
    public float maxForce = 10f;
    public float sprint = 15f;
    public float maxForceSprint = 20f;
    public float jumpForce = 5f;
    public float sens = 2f;

    public Rigidbody rb;

    private Vector2 move;
    public float checkRadius = 0.2f;
    public bool isGrounded;
    private bool sprinting = false;

    private void Awake()
    {
        if (rb == null) rb = GetComponent<Rigidbody>();
    }

    public void OnMove(InputValue value)
    {
        move = value.Get<Vector2>();
    }

    [System.Obsolete]
    public void OnJump(InputValue value)
    {
        if (value.isPressed && isGrounded)
        {
            Vector3 velo = rb.velocity;
            velo.y = 0f;
            rb.velocity = velo;

            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        }
    }

    [System.Obsolete]
    private void FixedUpdate()
    {
        Vector3 currentVelo = rb.velocity;

        Transform cam = Camera.main.transform;

        Vector3 camForward = cam.forward;
        Vector3 camRight = cam.right;

        camForward.y = 0f;
        camRight.y = 0f;

        camForward.Normalize();
        camRight.Normalize();

        Vector3 moveDir = camRight * move.x + camForward * move.y;

        Vector3 targetVelocity = moveDir * ((sprinting)? sprint:speed);

        Vector3 veloChange = targetVelocity - currentVelo;
        veloChange.y = 0f;
        if (sprinting)
        {
            veloChange = Vector3.ClampMagnitude(veloChange, maxForceSprint);
        }else{
            veloChange = Vector3.ClampMagnitude(veloChange, maxForce);
        }
        rb.AddForce(veloChange, ForceMode.VelocityChange);
    }

    [System.Obsolete]
    private void Update()
    {
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;

        if (transform.position.y < -1000)
        {
            transform.position = new Vector3(0, 10, 0);
            rb.velocity = Vector3.zero;
            rb.angularVelocity = Vector3.zero;
        }
    }

    private void OnCollisionStay(Collision collision)
    {
        foreach (ContactPoint contact in collision.contacts)
        {
            if (contact.normal.y > 0.6f)
            {
                isGrounded = true;
                return;
            }
        }
        isGrounded = false;
    }

    private void OnCollisionExit(Collision collision)
    {
        isGrounded = false;
    }
    public void OnSprint(InputValue value) => sprinting = value.isPressed;
}
