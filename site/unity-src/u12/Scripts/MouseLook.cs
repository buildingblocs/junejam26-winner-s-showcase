using UnityEngine;

public class MouseLook : MonoBehaviour
{
    public float mouseSensitivity = 100f;

    void Update()
    {
        float mouseX = Input.GetAxis("Mouse X");

        transform.Rotate(
            Vector3.up * mouseX * mouseSensitivity * Time.deltaTime
        );

        // Debug.Log(transform.eulerAngles.y);
    }
}