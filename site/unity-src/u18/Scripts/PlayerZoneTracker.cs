using UnityEngine;
using Unity.Cinemachine;

public class PlayerZoneTracker : MonoBehaviour
{
    [Header("Cinemachine Setup")]
    public CinemachineCamera mainVirtualCamera; 
    private CinemachineConfiner2D cameraConfiner;

    void Start()
    {
        if (mainVirtualCamera == null) return;
        cameraConfiner = mainVirtualCamera.GetComponent<CinemachineConfiner2D>();
    }

    private void OnTriggerEnter2D(Collider2D other)
    {
        ProcessZoneSwap(other);
    }

    private void OnTriggerStay2D(Collider2D other)
    {
        ProcessZoneSwap(other);
    }

    private void ProcessZoneSwap(Collider2D other)
    {
        CameraZone newZone = other.GetComponent<CameraZone>();
        
        if (newZone != null && cameraConfiner != null)
        {
            Collider2D newBoundaryCollider = newZone.GetZoneCollider();
            
            if (cameraConfiner.BoundingShape2D == newBoundaryCollider) return;

            cameraConfiner.BoundingShape2D = newBoundaryCollider;
            cameraConfiner.InvalidateCache(); 
        }
    }
    // Note to self: player AND zone need to have colliderbox2d. Not just rigidbody for this to work.
    // You can also just ctrl c ctrl v the zoneB collider to create a new logical camera zone. It will respect the bounds of the new collider.
}