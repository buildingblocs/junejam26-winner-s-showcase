using Unity.Cinemachine;
using UnityEngine;
using UnityEngine.InputSystem;

public class CameraZoom : MonoBehaviour
{
    public float zoomSpeed = 8f;
    public float minDistance = 4f;
    public float maxDistance = 22f;

    CinemachinePositionComposer composer;

    void Awake()
    {
        composer = GetComponent<CinemachinePositionComposer>();
    }

    void Update()
    {
        Keyboard kb = Keyboard.current;
        if (kb == null || composer == null)
        {
            return;
        }

        float dir = 0f;
        if (kb.iKey.isPressed) dir -= 1f;
        if (kb.oKey.isPressed) dir += 1f;
        if (dir != 0f)
        {
            composer.CameraDistance = Mathf.Clamp(
                composer.CameraDistance + dir * zoomSpeed * Time.deltaTime,
                minDistance, maxDistance);
        }
    }
}
