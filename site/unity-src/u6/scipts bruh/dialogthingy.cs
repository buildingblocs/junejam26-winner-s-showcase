using System;
using System.Collections;
using TMPro;
using UnityEngine;

public class dialogthingy : MonoBehaviour
{
    public TMP_Text dialogText;

    public float typingSpeed = 0.03f;

    public float displayTime = 2f;
    public float fadeDuration = 1f;

    [Header("Typing Sound")]
    public AudioSource audioSource;
    public AudioClip tickSound;
    public GameObject dialogueBackground;

    public event Action OnTextFullyDisplayed;

    private Coroutine typingCoroutine;

    public void ShowDialogue(string text)
    {
        dialogueBackground.SetActive(true);
        if (typingCoroutine != null)
            StopCoroutine(typingCoroutine);

        typingCoroutine = StartCoroutine(TypeText(text));
    }

    IEnumerator TypeText(string text)
    {
        // Reset alpha
        Color color = dialogText.color;
        color.a = 1f;
        dialogText.color = color;

        dialogText.text = "";

        // Type text
        foreach (char letter in text)
        {
            dialogText.text += letter;

            // Play tick sound (skip spaces if desired)
            if (letter != ' ' && tickSound != null && audioSource != null)
            {
                audioSource.PlayOneShot(tickSound);
            }

            yield return new WaitForSeconds(typingSpeed);
        }

        OnTextFullyDisplayed?.Invoke();

        // Keep text visible
        yield return new WaitForSeconds(displayTime);

        // Fade out
        float timer = 0f;

        while (timer < fadeDuration)
        {
            timer += Time.deltaTime;

            color.a = Mathf.Lerp(1f, 0f, timer / fadeDuration);
            dialogText.color = color;

            yield return null;
        }

        color.a = 0f;
        dialogText.color = color;

        dialogText.text = "";
        dialogueBackground.SetActive(false);
    }
}