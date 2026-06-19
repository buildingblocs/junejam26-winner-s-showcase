using UnityEngine;
// 1. Add this namespace at the very top so the script can see the new Input System
using UnityEngine.InputSystem; 

public class MenuController : MonoBehaviour
{
    [Header("UI Panels")]
    public GameObject optionsMenuPanel;

    private void Start()
    {
        if (optionsMenuPanel != null)
        {
            optionsMenuPanel.SetActive(false);
        }
    }

    private void Update()
    {
        // 2. Use the new Input System's keyboard check for the M key
        if (Keyboard.current != null && Keyboard.current.mKey.wasPressedThisFrame)
        {
            ToggleMenu();
        }
    }

    public void ToggleMenu()
    {
        if (optionsMenuPanel != null)
        {
            bool isMenuActive = !optionsMenuPanel.activeSelf;
            optionsMenuPanel.SetActive(isMenuActive);

            if (isMenuActive)
            {
                Time.timeScale = 0f;
            }
            else
            {
                Time.timeScale = 1f;
            }
        }
    }
}