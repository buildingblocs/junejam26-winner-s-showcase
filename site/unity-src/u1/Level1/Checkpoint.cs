using UnityEngine;

public class Checkpoint : MonoBehaviour
{
    [SerializeField] Material activatedMaterial;
    private bool activated;

    void OnTriggerEnter(Collider other)
    {
        if (activated) return;
        PlayerScript player = other.GetComponentInParent<PlayerScript>();
        if (player == null) return;

        player.SetCheckpoint(transform.position + Vector3.up * 0.5f);
        activated = true;
        if (activatedMaterial != null)
            GetComponent<Renderer>().sharedMaterial = activatedMaterial;
    }
}
