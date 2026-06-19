using UnityEngine;

public class HealthSystem : MonoBehaviour
{
    // Starting HP
    public int health = 900;


void Start()
    {
        Debug.Log("Starting HP: " + health);
    }

    public void TakeDamage(int damage)
    {
        health -= damage;

        Debug.Log("Current HP: " + health);

        if (health <= 0)
        {
            health = 0;

            Debug.Log("GAME OVER");

            // Freeze game
            Time.timeScale = 0f;
        }
    }

    void Update()
    {
        // Testing only
        if (Input.GetKeyDown(KeyCode.H))
        {
            TakeDamage(90);
        }
    }

}
