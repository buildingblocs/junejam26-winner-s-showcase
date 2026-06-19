using UnityEngine;

public class CupDown : MonoBehaviour, IInteractable 
{
    private SpriteRenderer sr;
    private Color originalcolor;

    private void Awake()
    {
        sr = GetComponent<SpriteRenderer>();
        originalcolor = sr.color;
    }

    public void Interact()
    {
        UseCup();
    }

    public void OnNotTouchingPlayer()
    {
        sr.color = originalcolor;   
    }

    public void OnTouchingPlayer()
    {
        sr.color = Color.blue;
    }

    void UseCup()
    {
        GameObject player = GameObject.FindGameObjectWithTag("Player");

        if (player != null)
        {
            PlayerStats stats = player.GetComponent<PlayerStats>();

            if (stats != null)
            {
                // DEBUG: Print current speed BEFORE the increase
                Debug.Log($"[Cup Interaction] Current Attack Speed: {stats.attackSpeed}. Adding 1.0!");
                
                stats.IncreaseAttackSpeed(0.1f); 
                
                // DEBUG: Print current speed AFTER the increase
                Debug.Log($"[Cup Interaction] New Attack Speed: {stats.attackSpeed}!");
            }
            else
            {
                Debug.LogWarning("[Cup Interaction] Found Player, but PlayerStats component is missing!");
            }
        }
        else
        {
            Debug.LogWarning("[Cup Interaction] Could not find any GameObject with the tag 'Player'!");
        }

        Destroy(gameObject);
    }
}