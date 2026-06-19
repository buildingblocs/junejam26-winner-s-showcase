using UnityEngine;
using UnityEngine.InputSystem;

public class NostalgiaManager : MonoBehaviour
{
    public static bool IsPast = false;
    public float CooldownSecs = 10.0f;
    private float cooldownTimer = 0.0f;


    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (cooldownTimer >= CooldownSecs && Keyboard.current.qKey.isPressed)
        {
            IsPast = !IsPast;
            cooldownTimer = 0.0f;

            Debug.Log("IsPast is now: " + IsPast);
        }
        else
        {
            cooldownTimer += Time.deltaTime;
        }
    }
}
