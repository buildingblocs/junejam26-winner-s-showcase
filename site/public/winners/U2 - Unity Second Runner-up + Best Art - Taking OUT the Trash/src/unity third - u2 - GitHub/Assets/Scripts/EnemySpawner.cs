using UnityEngine;

public class EnemySpawner : MonoBehaviour
{
    float timer = 0f;
    public GameObject enemyPrefab;
    public float cooldown;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        timer += Time.deltaTime;
        if (timer >= cooldown)
        {
            timer -= cooldown;
            Instantiate(enemyPrefab, transform.position, transform.rotation);
        }
    }
}
