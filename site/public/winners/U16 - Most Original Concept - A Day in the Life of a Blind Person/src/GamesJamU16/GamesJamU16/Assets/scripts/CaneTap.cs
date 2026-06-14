using System.Collections;
using UnityEngine;
using UnityEngine.Rendering.Universal;
using UnityEngine.InputSystem;



public class CaneTap : MonoBehaviour
{
    [Header("References")]
    public Light2D caneLight;

    [Header("Reveal")]
    public float tapCooldown     = 1.2f;
    public float revealDuration  = 0.5f;
    public float maxRadius        = 4.5f;
    public float maxIntensity     = 1.0f;

    [Header("Audio")]
    public AudioSource audioSource;
    public AudioClip   tapSound;

    private bool _canTap = true;

    void Update()
    {
        
        if (Keyboard.current.spaceKey.wasPressedThisFrame && _canTap)
        {
            StartCoroutine(TapReveal());
        }
            
    }

    IEnumerator TapReveal()
    {
        _canTap = false;

        // Play tap sound
        if (audioSource && tapSound)
            audioSource.PlayOneShot(tapSound);

        // Animate the light reveal
        float t = 0f;
        while (t < revealDuration)
        {
            t += Time.deltaTime;
            float p = t / revealDuration;

            // Sine curve: blooms open, fades out
            float curve = Mathf.Sin(p * Mathf.PI);

            caneLight.pointLightOuterRadius = curve * maxRadius;
            caneLight.pointLightInnerRadius = curve * maxRadius * 0.4f;
            caneLight.intensity             = Mathf.Lerp(maxIntensity, 0f, p);

            yield return null;
        }

        // Reset light fully
        caneLight.intensity             = 0f;
        caneLight.pointLightOuterRadius = 0f;

        // Wait out the rest of the cooldown
        yield return new WaitForSeconds(tapCooldown - revealDuration);
        _canTap = true;
    }
}