using UnityEngine;

public class InteractionPrompt : MonoBehaviour
{
    // Player object
    public Transform player;

    // UI text object
    public GameObject interactText;

    // Lamp renderer (used to change colour)
    private Renderer lampRenderer;

    // Distance required before interaction prompt appears
    public float interactDistance = 3f;

    void Start()
    {
        // Get renderer from lamp
        lampRenderer = GetComponent<Renderer>();

        // Hide interaction text when game starts
        if (interactText != null)
        {
            interactText.SetActive(false);
        }
    }

    void Update()
    {
        // Safety check
        // Stop script if Player or Renderer is missing
        if (player == null || lampRenderer == null)
        {
            return;
        }

        // Calculate distance between player and lamp
        float distance = Vector3.Distance(
            player.position,
            transform.position
        );

        // If player is close enough
        if (distance < interactDistance)
        {
            // Show interaction text
            if (interactText != null)
            {
                interactText.SetActive(true);
            }

            // Highlight lamp
            // lampRenderer.material.color = Color.white;

            // Debug message
            Debug.Log("Player is close to lamp");
        }
        else
        {
            // Hide interaction text
            if (interactText != null)
            {
                interactText.SetActive(false);
            }

            // Return lamp to normal colour
            // lampRenderer.material.color = Color.gray;
        }
    }
}