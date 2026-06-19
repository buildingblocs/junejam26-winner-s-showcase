using UnityEngine;

public class LampController : MonoBehaviour
{
    // Is lamp currently on?
    private bool isOn = false;
    private Renderer lampRenderer;

    void Start()
    {
        lampRenderer = GetComponent<Renderer>();
    }

    public void Interact()
    {
        // Switch lamp state
        isOn = !isOn;

        if (isOn)
        {
            Debug.Log("Lamp ON");

            lampRenderer.material.color = Color.yellow;
        }
        else
        {
            Debug.Log("Lamp OFF");

            lampRenderer.material.color = Color.gray;
        }
    }
}
