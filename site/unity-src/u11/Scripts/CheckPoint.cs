using UnityEngine;

public class Checkpoint : MonoBehaviour
{
    private GameObject player;

    [Header("Setup")]
    [SerializeField] private string outlineLayerName = "Outline";

    [SerializeField] private Animator animator;

    private void Start()
    {
        player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogWarning("No GameObject named 'Player' found in the scene.");
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject == player)
        {
            Debug.Log("Player entered checkpoint!");

            int outlineLayer = LayerMask.NameToLayer(outlineLayerName);
            if (outlineLayer != -1)
            {
                Debug.Log("Before: " + LayerMask.LayerToName(gameObject.layer));
                gameObject.layer = outlineLayer;
                Debug.Log("After: " + LayerMask.LayerToName(gameObject.layer));
            }
            else
            {
                Debug.LogError($"Layer '{outlineLayerName}' does not exist! Please create it in Project Settings.");
            }
            animator.SetTrigger("CheckPointTrig");
            
            Invoke(nameof(LevelManager.Instance.CompleteLevel), 2.5f);
        }
    }
    private void CompleteLevel()
    {
        LevelManager.Instance.CompleteLevel();
    }
}
