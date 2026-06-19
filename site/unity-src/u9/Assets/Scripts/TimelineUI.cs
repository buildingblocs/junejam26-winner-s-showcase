using TMPro;
using UnityEngine;

public class TimelineUI : MonoBehaviour
{
    public TextMeshProUGUI timelineText;

    private void Update()
    {
        if (WorldStateManager.Instance.isPast)
            timelineText.text = "PAST";
        else
            timelineText.text = "PRESENT";
    }
}