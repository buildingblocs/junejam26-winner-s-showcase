using UnityEngine;

public class ObjectiveManager : MonoBehaviour
{
    // Number of batteries collected
    public static int batteriesCollected = 0;

    void Update()
    {
        // Check win condition
        if (batteriesCollected >= 3)
        {
            Debug.Log("YOU WIN!");
        }
    }
}
