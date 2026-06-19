using UnityEngine;

public class Interactable : MonoBehaviour
{
    // Is lamp currently on?
    public bool isOn = false;

    private Renderer lampRenderer;
    private Light lampLight;

    // Lamp sound
    private AudioSource lampSound;

    void Start()
    {
        // Get lamp renderer
        lampRenderer = GetComponent<Renderer>();

        // Get light component
        lampLight = GetComponentInChildren<Light>();

        // Get audio source
        lampSound = GetComponent<AudioSource>();

        // Start with light OFF
        if (lampLight != null)
        {
            lampLight.enabled = false;
        }

        // Start with gray color
        lampRenderer.material.color = Color.gray;
    }

    // Called when player presses F
    public void Interact()
    {
        // Play click sound
        if (lampSound != null)
        {
            lampSound.Play();
        }

        // Toggle lamp state
        isOn = !isOn;

        if (isOn)
        {
            Debug.Log("Lamp ON");

            lampRenderer.material.color = Color.yellow;

            if (lampLight != null)
            {
                lampLight.enabled = true;
            }
        }
        else
        {
            Debug.Log("Lamp OFF");

            lampRenderer.material.color = Color.gray;

            if (lampLight != null)
            {
                lampLight.enabled = false;
            }
        }
    }
}