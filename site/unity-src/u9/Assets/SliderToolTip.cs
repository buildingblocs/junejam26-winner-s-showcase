using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Audio; // Required for Audio Mixers
using UnityEngine.EventSystems; // Required for Hover Events
using TMPro;

public class SliderTooltip : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler
{
    [Header("Components")]
    public Slider slider;
    public TextMeshProUGUI tooltipText;
    public GameObject tooltipBubble;

    [Header("Audio Settings")]
    public AudioMixer audioMixer;
    public string exposedParameterName; // E.g., "BGMVol" or "SFXVol"

    private void Start()
    {
        if (slider == null) slider = GetComponent<Slider>();
        
        // Ensure the bubble starts hidden
        if (tooltipBubble != null) tooltipBubble.SetActive(false);

        // Link the slider event
        slider.onValueChanged.RemoveAllListeners();
        slider.onValueChanged.AddListener(OnSliderValueChanged);

        // Set the initial text and volume on startup
        OnSliderValueChanged(slider.value);
    }

    private void OnSliderValueChanged(float value)
    {
        // 1. Update the Tooltip Text to show clean percentages (0% - 100%)
        if (tooltipText != null)
        {
            tooltipText.text = Mathf.RoundToInt(value * 100f).ToString() + "%";
        }

        // 2. Update the actual Audio Mixer Volume using Logarithmic conversion
        if (audioMixer != null && !string.IsNullOrEmpty(exposedParameterName))
        {
            float dbVolume = Mathf.Log10(value) * 20f;
            audioMixer.SetFloat(exposedParameterName, dbVolume);
        }
    }

    // Triggered automatically when mouse enters the slider area
    public void OnPointerEnter(PointerEventData eventData)
    {
        if (tooltipBubble != null)
            tooltipBubble.SetActive(true);
    }

    // Triggered automatically when mouse leaves the slider area
    public void OnPointerExit(PointerEventData eventData)
    {
        if (tooltipBubble != null)
            tooltipBubble.SetActive(false);
    }

    private void OnDestroy()
    {
        if (slider != null)
            slider.onValueChanged.RemoveListener(OnSliderValueChanged);
    }
}