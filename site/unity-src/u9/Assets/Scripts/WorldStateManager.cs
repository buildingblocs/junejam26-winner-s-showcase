using UnityEngine;

public class WorldStateManager : MonoBehaviour
{
    public static WorldStateManager Instance;

    public bool isPast = false;

    private void Awake()
    {
        Instance = this;
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Q))
        {
            isPast = !isPast;
        }
    }
}