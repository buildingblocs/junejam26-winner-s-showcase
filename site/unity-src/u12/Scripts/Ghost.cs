using UnityEngine;

public class Ghost : MonoBehaviour
{
    public Transform player;
    public Transform lamp;

    [Header("Movement")]
    public float speed = 2f;
    public float attackDistance = 2f;
    public float lampFearDistance = 5f;

    [Header("Damage")]
    public int damage = 10;
    public float damageCooldown = 1f;

    [Header("Sound")]
    public float maxSoundDistance = 10f;
    public float minVolume = 0.05f;
    public float maxVolume = 0.8f;

    private float damageTimer;
    private Interactable lampScript;
    private AudioSource ghostSound;

    void Start()
    {
        if (lamp != null)
        {
            lampScript = lamp.GetComponent<Interactable>();
        }

        ghostSound = GetComponent<AudioSource>();

        if (ghostSound != null)
        {
            ghostSound.loop = true;
            ghostSound.playOnAwake = false;
            ghostSound.volume = minVolume;
            ghostSound.Play();
        }
    }

    void Update()
    {
        if (player == null)
            return;

        damageTimer -= Time.deltaTime;

        float playerDistance =
            Vector3.Distance(transform.position, player.position);

        UpdateGhostSound(playerDistance);

        if (lampScript != null && lampScript.isOn && lamp != null)
        {
            float lampDistance =
                Vector3.Distance(transform.position, lamp.position);

            if (lampDistance < lampFearDistance)
            {
                Vector3 runDirection =
                    (transform.position - lamp.position).normalized;

                transform.position +=
                    runDirection * speed * Time.deltaTime;

                return;
            }
        }

        if (playerDistance > attackDistance)
        {
            transform.position =
                Vector3.MoveTowards(
                    transform.position,
                    player.position,
                    speed * Time.deltaTime
                );
        }
        else
        {
            if (damageTimer <= 0f)
            {
                HealthSystem hp =
                    player.GetComponent<HealthSystem>();

                if (hp != null)
                {
                    hp.TakeDamage(damage);
                    Debug.Log("Ghost attacked! HP: " + hp.health);
                }

                damageTimer = damageCooldown;
            }
        }
    }

    void UpdateGhostSound(float distance)
    {
        if (ghostSound == null)
            return;

        if (!ghostSound.isPlaying)
        {
            ghostSound.Play();
        }

        float closeness =
            1f - Mathf.Clamp01(distance / maxSoundDistance);

        ghostSound.volume =
            Mathf.Lerp(minVolume, maxVolume, closeness);
    }
}