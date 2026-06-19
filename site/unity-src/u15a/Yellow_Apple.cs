using UnityEngine;

public class YellowApple : MonoBehaviour, IInteractable 
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
                stats.IncreaseDamage(10f);
                stats.currentHealth -= 15f;
                stats.currentHealth = Mathf.Max(stats.currentHealth, 0f);

                Debug.Log($"[Yellow Apple] Attack increased by 10. New Damage: {stats.attackDamage}. Lost 15 HP. Current HP: {stats.currentHealth}");

                if (stats.currentHealth <= 0f)
                {
                    stats.TakeDamage(0f);
                }
            }
        }

        Destroy(gameObject);
    }
}