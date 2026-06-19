using UnityEngine;

public class BuffItem : MonoBehaviour, IInteractable 
{
    private SpriteRenderer sr;
    private Color originalcolor;

    [Header("Item Settings")]
    public ItemType itemType; // Select this in the Unity Inspector dropdown
    public float amount = 1f;  // How much this specific item modifies the stat

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

    private void UseItem()
    {
        GameObject player = GameObject.FindGameObjectWithTag("Player");

        if (player != null)
        {
            PlayerStats stats = player.GetComponent<PlayerStats>();

            if (stats != null)
            {
                ApplyStackableBuff(stats, player);
            }
        }

        Destroy(gameObject);
    }

    private void ApplyStackableBuff(PlayerStats stats, GameObject player)
    {
        switch (itemType)
        {
            case ItemType.Heal:
                stats.Heal(amount);
                Debug.Log($"[Item] Healed player by {amount}. Current Health: {stats.currentHealth}");
                break;

            case ItemType.MaxHealth:
                stats.IncreaseMaxHealth(amount);
                Debug.Log($"[Item] Increased Max Health by {amount}. New Max: {stats.maxHealth}");
                break;

            case ItemType.Damage:
                stats.IncreaseDamage(amount);
                Debug.Log($"[Item] Increased Damage by {amount}. New Damage: {stats.attackDamage}");
                break;

            case ItemType.AttackSpeed:
                stats.IncreaseAttackSpeed(amount);
                
                // Syncs the player's animator speed with their new attack speed
                if (player.TryGetComponent<Animator>(out Animator anim)) 
                {
                    anim.speed = stats.attackSpeed;
                }
                Debug.Log($"[Item] Increased Attack Speed by {amount}. New Speed: {stats.attackSpeed}");
                break;

            case ItemType.MoveSpeed:
                stats.IncreaseMoveSpeed(amount);
                Debug.Log($"[Item] Increased Move Speed by {amount}. New Speed: {stats.moveSpeed}");
                break;

            case ItemType.Regen:
                stats.IncreaseRegen(amount);
                Debug.Log($"[Item] Increased Regen by {amount}. New Regen: {stats.regenPerSecond}");
                break;

            case ItemType.DamageReduction:
                stats.IncreaseDamageReduction(amount);
                Debug.Log($"[Item] Increased Damage Reduction by {amount}. New DR: {stats.damageReduction}");
                break;
        }
    }
}