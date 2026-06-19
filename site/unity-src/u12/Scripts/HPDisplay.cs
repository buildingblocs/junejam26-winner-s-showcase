using TMPro;
using UnityEngine;

public class HPDisplay : MonoBehaviour
{
    public HealthSystem healthSystem;
    public TextMeshProUGUI hpText;

    void Update()
    {
        hpText.text = "HP: " + healthSystem.health;
    }
}