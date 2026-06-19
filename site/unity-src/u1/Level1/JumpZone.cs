using UnityEngine;

public class JumpZone : MonoBehaviour
{
    void OnTriggerEnter(Collider other)
    {
        PlayerScript player = other.GetComponentInParent<PlayerScript>();
        if (player != null)
        {
            player.EnterJumpZone();
        }
    }

    void OnTriggerExit(Collider other)
    {
        PlayerScript player = other.GetComponentInParent<PlayerScript>();
        if (player != null)
        {
            player.ExitJumpZone();
        }
    }
}
