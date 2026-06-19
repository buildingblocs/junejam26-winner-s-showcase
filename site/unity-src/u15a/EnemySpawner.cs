using UnityEngine;
using System.Collections;

public class EnemySpawner : MonoBehaviour
{
    [SerializeField] private GameObject swarmerPrefab;
    [SerializeField] private float swarmerInterval = 2.0f;
    [SerializeField] private int maxEnemies = 20;

    private bool playerInRoom = false;
    private bool isSpawningCoroutineRunning = false;

    private void OnTriggerEnter2D(Collider2D collision)
    {
        if (collision.CompareTag("Player"))
        {
            playerInRoom = true;
            if (!isSpawningCoroutineRunning)
            {
                StartCoroutine(SpawnRoutine());
            }
        }
    }

    private void OnTriggerExit2D(Collider2D collision)
    {
        if (collision.CompareTag("Player"))
        {
            playerInRoom = false;
        }
    }

    private IEnumerator SpawnRoutine()
    {
        isSpawningCoroutineRunning = true;

        while (playerInRoom)
        {
            int currentEnemyCount = GameObject.FindGameObjectsWithTag("Enemy").Length;

            if (currentEnemyCount < maxEnemies)
            {
                // Spawns them right near the spawner center instead of everywhere
                Vector2 spawnPosition = (Vector2)transform.position + new Vector2(Random.Range(-2f, 2f), Random.Range(-2f, 2f));
                Instantiate(swarmerPrefab, spawnPosition, Quaternion.identity);
            }

            yield return new WaitForSeconds(swarmerInterval);
        }

        isSpawningCoroutineRunning = false;
    }
}