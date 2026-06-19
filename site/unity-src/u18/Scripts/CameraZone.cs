using UnityEngine;

[RequireComponent(typeof(Collider2D))]
public class CameraZone : MonoBehaviour
{
    private Collider2D zoneCollider;

    void Awake()
    {
        zoneCollider = GetComponent<Collider2D>();
        
        if (!zoneCollider.isTrigger)
        {
            zoneCollider.isTrigger = true;
        }
    }

    public Collider2D GetZoneCollider()
    {
        return zoneCollider;
    }
}