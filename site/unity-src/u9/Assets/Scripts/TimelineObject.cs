using UnityEngine;

public class TimelineObject : MonoBehaviour
{
    public GameObject targetObject;
    public bool existsInPast;

    private void Update()
    {
        bool shouldBeVisible =
            WorldStateManager.Instance.isPast == existsInPast;

        targetObject.SetActive(shouldBeVisible);
    }
}