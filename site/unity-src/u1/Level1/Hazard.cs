using UnityEngine;

public class Hazard : MonoBehaviour
{
    void OnCollisionEnter(Collision collision)
    {
        TryRespawn(collision.collider);
    }

    void OnTriggerEnter(Collider other)
    {
        TryRespawn(other);
    }

    static void TryRespawn(Collider col)
    {
        PlayerScript player = col.GetComponentInParent<PlayerScript>();
        if (player != null)
        {
            player.Respawn();
        }
    }
}
