using UnityEngine;

public class FishItem : MonoBehaviour, IInteractable 
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
                // Weapon change simulation: set damage base directly to 3
                stats.attackDamage = 3f;
                
                // Decreases attack speed to make attacks slower
                stats.attackSpeed = Mathf.Max(0.2f, stats.attackSpeed - 0.4f); 

                // Sync with Animator system
                if (player.TryGetComponent<Animator>(out Animator anim)) 
                {
                    anim.speed = stats.attackSpeed;
                }

                Debug.Log($"[Fish] Equipped Fish weapon. Damage set to: {stats.attackDamage}. Slower Attack Speed: {stats.attackSpeed}");
            }
        }

        Destroy(gameObject);
    }
}