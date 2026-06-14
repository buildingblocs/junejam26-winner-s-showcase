using System;
using System.Collections;
using UnityEngine;
using UnityEngine.InputSystem;



public class PlayerController : MonoBehaviour

{

    private Rigidbody rb;
    public float horizontalMove;
    public float verticalMove;
    [SerializeField] private float speed;
    [SerializeField] private float maxSpeed = 10;
    [SerializeField] private float minSpeed = 2;
    [SerializeField] private float boostDuration = 1;
    [SerializeField] private Transform camera;

    public AudioSource audioSource;
    [SerializeField] private AudioClip rollSFX;
    private bool hasPlayed = false;

    public Vector3 moveDirection;

    private Coroutine audioFadeCoroutine;

    // Start is called once before the first execution of Update after the MonoBehaviour is created

    void Start()
    {
        rb = GetComponent<Rigidbody>();
    }



    void OnMove(InputValue movementValue)
    {
        Vector2 movementVector = movementValue.Get<Vector2>();
        horizontalMove = movementVector.x;
        verticalMove = movementVector.y;
    }



    void Update()
    {

        // Camera rotation
        Vector3 camForward = camera.forward;
        Vector3 camRight = camera.right;
        camForward.y = 0;
        camRight.y = 0;
        camForward.Normalize();
        camRight.Normalize();

        moveDirection = (camForward * verticalMove + camRight * horizontalMove);
        
        bool isMoving = horizontalMove != 0 || verticalMove != 0;

        // Plays rolling sfx when moving. Stops audio if not moving
        if (isMoving)
        {
            if (audioFadeCoroutine != null)
            {
                StopCoroutine(audioFadeCoroutine);
                audioFadeCoroutine = null;
            }

            if (!audioSource.isPlaying)
            {
                audioSource.clip = rollSFX;
                audioSource.loop = true;
                audioSource.volume = 1f;
                audioSource.Play();
            }
        }
        else
        {
            if (audioSource.isPlaying && audioFadeCoroutine == null) audioFadeCoroutine = StartCoroutine(FadeOutAudio(5f)); // Fade duration
        }
    }

    // Fade out rolling sfx over time
    private IEnumerator FadeOutAudio(float duration)
    {
        float startVolume = 1f;

        while (audioSource.volume > 0)
        {
            audioSource.volume -= startVolume * (Time.deltaTime / duration);
            yield return null;
        }

        audioSource.Stop();
        audioSource.volume = startVolume; // Resets volume for next time
        audioFadeCoroutine = null;
    }

    private void FixedUpdate()
    {
        rb.AddForce(moveDirection * speed, ForceMode.Acceleration);
    }

    public void PlayerStop()
    {
        // Stops rolling sfx
        audioSource.Stop();

        // Reset input & direction
        horizontalMove = 0f;
        verticalMove = 0f;
        moveDirection = Vector3.zero;

        // Kill momentum
        Rigidbody rb = GetComponent<Rigidbody>();
        rb.linearVelocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;
    }

    public IEnumerator speedBoost(float value)
    {
        // add boost
        Debug.Log($"Added speed at {Time.time}");
        addSpeed(value);
        // wait for boost duration
        yield return StartCoroutine(boostDelay());
        resetSpeed();
        Debug.Log($"Reset speed at {Time.time}");
    }

    public IEnumerator boostDelay()
    {
        yield return new WaitForSeconds(boostDuration);
    }
    public void addSpeed(float value)
    {
        speed = Math.Min(value, maxSpeed); //set to max if value>max
        Debug.Log($"Speed set to {speed}");
    }

    public void resetSpeed()
    {
        speed = minSpeed;
    }

    public float getSpeed(){return speed;}
}