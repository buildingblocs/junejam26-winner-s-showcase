using UnityEngine;

public class BarSoap : MonoBehaviour, IInteractable 
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
                stats.IncreaseAttackSpeed(1f);
                stats.IncreaseMoveSpeed(1f);

                if (player.TryGetComponent<Animator>(out Animator anim)) 
                {
                    anim.speed = stats.attackSpeed;
                }

                Debug.Log($"[Bar Soap] Increased Speed and Attack Speed by 20. MoveSpeed: {stats.moveSpeed}, AtkSpeed: {stats.attackSpeed}");
            }
        }

        Destroy(gameObject);
    }
}