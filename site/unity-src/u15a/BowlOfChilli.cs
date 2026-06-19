using UnityEngine;

public class BowlOfChilli : MonoBehaviour, IInteractable 
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
        UseItem();
    }

    public void OnNotTouchingPlayer()
    {
        sr.color = originalcolor;   
    }

    public void OnTouchingPlayer()
    {
        sr.color = Color.blue;
    }

    void UseItem()
    {
        GameObject player = GameObject.FindGameObjectWithTag("Player");

        if (player != null)
        {
            PlayerStats stats = player.GetComponent<PlayerStats>();

            if (stats != null)
            {
                stats.IncreaseMoveSpeed(15f);
                // Directly adjusting current health for immediate negative impact
                stats.currentHealth -= 10f;
                stats.currentHealth = Mathf.Max(stats.currentHealth, 0f); 
                
                Debug.Log($"[Chilli] Speed increased by 15. New Speed: {stats.moveSpeed}. Lost 10 HP. Current HP: {stats.currentHealth}");
                
                if (stats.currentHealth <= 0f)
                {
                    // Triggers death if the item's negative cost kills them
                    stats.TakeDamage(0f); 
                }
            }
        }

        Destroy(gameObject);
    }
}