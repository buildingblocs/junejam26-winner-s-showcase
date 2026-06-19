using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    public Transform target;

    [Header("Camera Distance")]
    public float distance = 2.5f;

    [Header("Camera Height")]
    public float height = 1f;

    [Header("Mouse")]
    public float rotationSpeed = 150f;

    private float yaw = 0f;

    void Start()
    {
        Cursor.lockState =
            CursorLockMode.Locked;

        Cursor.visible = false;
    }

    void LateUpdate()
    {
        if (target == null)
            return;

        // Rotate cat
        float mouseX =
            Input.GetAxis("Mouse X");

        yaw +=
            mouseX *
            rotationSpeed *
            Time.deltaTime;

        target.rotation =
            Quaternion.Euler(
                0,
                yaw,
                0
            );

        // Camera position
        Vector3 cameraPosition =
            target.position
            - target.forward * distance
            + Vector3.up * height;

        transform.position =
            cameraPosition;

        // Look at cat
        transform.LookAt(
            target.position +
            Vector3.up * 0.5f
        );
    }
}