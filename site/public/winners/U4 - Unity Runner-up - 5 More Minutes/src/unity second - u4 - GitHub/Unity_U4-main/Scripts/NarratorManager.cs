using System.Collections;
using TMPro;
using UnityEngine;

public class NarratorManager : MonoBehaviour
{
    public static NarratorManager Instance { get; private set; }

    [Header("References")]
    [SerializeField] private AudioSource voiceSource;
    [SerializeField] private TextMeshProUGUI subtitleText;
    [SerializeField] private CanvasGroup subtitleGroup;

    public bool IsSpeaking { get; private set; }

    private Coroutine currentNarration;

    private void Awake()
    {
        Instance = this;

        if (voiceSource == null)
        {
            voiceSource = GetComponent<AudioSource>();
        }

        HideSubtitlesImmediately();
    }

    private void OnDestroy()
    {
        if (Instance == this)
        {
            Instance = null;
        }
    }

    public bool PlayLine(NarratorLine line)
    {
        if (IsSpeaking || !IsLineValid(line))
        {
            return false;
        }

        currentNarration = StartCoroutine(
            PlaySequenceRoutine(new[] { line })
        );

        return true;
    }

    public bool PlaySequence(NarratorLine[] lines)
    {
        if (IsSpeaking ||
            lines == null ||
            lines.Length == 0)
        {
            return false;
        }

        currentNarration = StartCoroutine(
            PlaySequenceRoutine(lines)
        );

        return true;
    }

    public bool PlayBeatSequence(NarratorBeat[] beats)
    {
        if (IsSpeaking ||
            beats == null ||
            beats.Length == 0)
        {
            return false;
        }

        currentNarration = StartCoroutine(
            PlayBeatSequenceRoutine(beats)
        );

        return true;
    }

    private IEnumerator PlaySequenceRoutine(
        NarratorLine[] lines)
    {
        IsSpeaking = true;

        foreach (NarratorLine line in lines)
        {
            if (IsLineValid(line))
            {
                yield return PlaySingleLineRoutine(line);
            }
        }

        FinishNarration();
    }

    private IEnumerator PlayBeatSequenceRoutine(
        NarratorBeat[] beats)
    {
        IsSpeaking = true;

        foreach (NarratorBeat beat in beats)
        {
            if (beat == null ||
                !IsLineValid(beat.line))
            {
                continue;
            }

            yield return PlaySingleLineRoutine(beat.line);

            if (beat.pauseAfter > 0f)
            {
                yield return new WaitForSecondsRealtime(
                    beat.pauseAfter
                );
            }
        }

        FinishNarration();
    }

    private IEnumerator PlaySingleLineRoutine(
        NarratorLine line)
    {
        subtitleGroup.alpha = 1f;
        subtitleText.text = line.subtitle;
        subtitleText.maxVisibleCharacters = 0;

        subtitleText.ForceMeshUpdate();

        int characterCount =
            subtitleText.textInfo.characterCount;

        if (line.audioClip != null)
        {
            voiceSource.clip = line.audioClip;
            voiceSource.Play();

            float duration = Mathf.Max(
                line.audioClip.length,
                0.01f
            );

            float elapsed = 0f;

            while (elapsed < duration)
            {
                elapsed += Time.unscaledDeltaTime;

                float progress = Mathf.Clamp01(
                    elapsed / duration
                );

                subtitleText.maxVisibleCharacters =
                    Mathf.CeilToInt(
                        progress * characterCount
                    );

                yield return null;
            }

            while (voiceSource.isPlaying)
            {
                yield return null;
            }
        }
        else
        {
            float delay =
                1f / Mathf.Max(
                    line.charactersPerSecond,
                    1f
                );

            for (int i = 0; i <= characterCount; i++)
            {
                subtitleText.maxVisibleCharacters = i;

                yield return new WaitForSecondsRealtime(
                    delay
                );
            }
        }

        subtitleText.maxVisibleCharacters =
            characterCount;

        if (line.holdAfterLine > 0f)
        {
            yield return new WaitForSecondsRealtime(
                line.holdAfterLine
            );
        }

        HideSubtitlesImmediately();
    }

    private void FinishNarration()
    {
        HideSubtitlesImmediately();

        IsSpeaking = false;
        currentNarration = null;
    }

    private static bool IsLineValid(
        NarratorLine line)
    {
        return line != null &&
               !string.IsNullOrWhiteSpace(
                   line.subtitle
               );
    }

    private void HideSubtitlesImmediately()
    {
        if (subtitleText != null)
        {
            subtitleText.text = string.Empty;
            subtitleText.maxVisibleCharacters = 0;
        }

        if (subtitleGroup != null)
        {
            subtitleGroup.alpha = 0f;
        }
    }
}