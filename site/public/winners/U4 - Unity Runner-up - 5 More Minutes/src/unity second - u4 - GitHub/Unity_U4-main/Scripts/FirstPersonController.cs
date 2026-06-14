using UnityEngine;
using UnityEngine.InputSystem;

[RequireComponent(typeof(CharacterController))]
public class FirstPersonController : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private Camera playerCamera;

    [Header("Movement")]
    [SerializeField] private float walkSpeed = 4f;
    [SerializeField] private float runSpeed = 6f;
    [SerializeField] private float jumpHeight = 1.1f;
    [SerializeField] private float gravity = -20f;

    [Header("Camera")]
    [SerializeField] private float mouseSensitivity = 0.12f;
    [SerializeField] private float maximumLookAngle = 85f;

    private CharacterController characterController;

    private float verticalVelocity;
    private float cameraPitch;

    private bool movementEnabled = true;
    private bool lookEnabled = true;

    public bool ControlsEnabled =>
        movementEnabled && lookEnabled;

    public bool MovementEnabled => movementEnabled;
    public bool LookEnabled => lookEnabled;

    private void Awake()
    {
        characterController =
            GetComponent<CharacterController>();

        if (playerCamera == null)
        {
            playerCamera =
                GetComponentInChildren<Camera>();
        }
    }

    private void Start()
    {
        LockCursor();
    }

    private void Update()
    {
        if (lookEnabled)
        {
            HandleCamera();
        }

        if (movementEnabled)
        {
            HandleMovement();
        }
    }

    private void HandleCamera()
    {
        if (Mouse.current == null ||
            playerCamera == null)
        {
            return;
        }

        Vector2 mouseDelta =
            Mouse.current.delta.ReadValue();

        float yaw =
            mouseDelta.x * mouseSensitivity;

        float pitchChange =
            mouseDelta.y * mouseSensitivity;

        transform.Rotate(
            Vector3.up * yaw
        );

        cameraPitch -= pitchChange;

        cameraPitch = Mathf.Clamp(
            cameraPitch,
            -maximumLookAngle,
            maximumLookAngle
        );

        playerCamera.transform.localRotation =
            Quaternion.Euler(
                cameraPitch,
                0f,
                0f
            );
    }

    private void HandleMovement()
    {
        if (Keyboard.current == null)
        {
            return;
        }

        Vector2 input = Vector2.zero;

        if (Keyboard.current.wKey.isPressed)
        {
            input.y += 1f;
        }

        if (Keyboard.current.sKey.isPressed)
        {
            input.y -= 1f;
        }

        if (Keyboard.current.dKey.isPressed)
        {
            input.x += 1f;
        }

        if (Keyboard.current.aKey.isPressed)
        {
            input.x -= 1f;
        }

        input = Vector2.ClampMagnitude(
            input,
            1f
        );

        bool isRunning =
            Keyboard.current
                .leftShiftKey
                .isPressed;

        float currentSpeed =
            isRunning
                ? runSpeed
                : walkSpeed;

        Vector3 horizontalMovement =
            transform.right * input.x +
            transform.forward * input.y;

        characterController.Move(
            horizontalMovement *
            currentSpeed *
            Time.deltaTime
        );

        if (characterController.isGrounded &&
            verticalVelocity < 0f)
        {
            verticalVelocity = -2f;
        }

        if (characterController.isGrounded &&
            Keyboard.current
                .spaceKey
                .wasPressedThisFrame)
        {
            verticalVelocity =
                Mathf.Sqrt(
                    jumpHeight *
                    -2f *
                    gravity
                );
        }

        verticalVelocity +=
            gravity * Time.deltaTime;

        characterController.Move(
            Vector3.up *
            verticalVelocity *
            Time.deltaTime
        );
    }

    public void SetControlsEnabled(
        bool enabled)
    {
        movementEnabled = enabled;
        lookEnabled = enabled;

        if (!enabled)
        {
            verticalVelocity = 0f;
        }
    }

    public void SetMovementEnabled(
        bool enabled)
    {
        movementEnabled = enabled;

        if (!enabled)
        {
            verticalVelocity = 0f;
        }
    }

    public void SetLookEnabled(
        bool enabled)
    {
        lookEnabled = enabled;
    }

    public void LockCursor()
    {
        Cursor.lockState =
            CursorLockMode.Locked;

        Cursor.visible = false;
    }

    public void UnlockCursor()
    {
        Cursor.lockState =
            CursorLockMode.None;

        Cursor.visible = true;
    }

    public void TeleportTo(
        Transform target)
    {
        if (target == null)
        {
            return;
        }

        characterController.enabled = false;

        transform.SetPositionAndRotation(
            target.position,
            target.rotation
        );

        cameraPitch = 0f;
        verticalVelocity = 0f;

        if (playerCamera != null)
        {
            playerCamera.transform
                .localRotation =
                Quaternion.identity;
        }

        characterController.enabled = true;
    }
}