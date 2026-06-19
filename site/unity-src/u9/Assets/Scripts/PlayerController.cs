using UnityEngine;
using UnityEngine.InputSystem;

public class PlayerController : MonoBehaviour
{
    public float speed = 3.5f;


    public InputAction MoveAction;
    private Rigidbody2D myRigidbody;
    private Vector2 moveInput;


    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        MoveAction.Enable();
        myRigidbody = GetComponent<Rigidbody2D>();
    }

    // Update is called once per frame
    void Update()
    {
        moveInput = MoveAction.ReadValue<Vector2>();
        Debug.Log(moveInput);
    }

    // FixedUpdate is called once per set time
    void FixedUpdate()
    {
        myRigidbody.MovePosition(speed * Time.deltaTime * moveInput.normalized + myRigidbody.position);
    }
}
