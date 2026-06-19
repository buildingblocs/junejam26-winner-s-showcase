using UnityEngine;

public class Cookies : MonoBehaviour, IInteractable 
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
                stats.Heal(10f);
                Debug.Log($"[Cookies] Healed player by 10. Current Health: {stats.currentHealth}");
            }
        }

        Destroy(gameObject);
    }
}