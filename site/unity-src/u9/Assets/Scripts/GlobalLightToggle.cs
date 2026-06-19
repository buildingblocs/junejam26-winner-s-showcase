using UnityEngine;
using UnityEngine.Rendering.Universal;

public class GlobalLightToggle : MonoBehaviour
{
    private Light2D globalLight;

    public Color presentColor = new Color32(0x78, 0xA6, 0xBE, 0xFF);
    public float presentIntensity = 1.0f;
    public Color pastColor = new Color32(0xBE, 0xB5, 0x78, 0xFF);
    public float pastIntensity = 0.05f;

    public float transitionSpeed = 1.5f;


    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        globalLight = GetComponent<Light2D>();
    }

    // Update is called once per frame
    void Update()
    {
        if (NostalgiaManager.IsPast)
        {
            globalLight.color = Color.Lerp(globalLight.color, pastColor, Time.deltaTime * transitionSpeed);
            globalLight.intensity = Mathf.Lerp(globalLight.intensity, pastIntensity, Time.deltaTime * transitionSpeed);
        }
        else
        {
            globalLight.color = Color.Lerp(globalLight.color, presentColor, Time.deltaTime * transitionSpeed);
            globalLight.intensity = Mathf.Lerp(globalLight.intensity, presentIntensity, Time.deltaTime * transitionSpeed);
        }
    }
}
