using UnityEngine;

[RequireComponent(typeof(AudioSource))]
public class AudioPlayer : MonoBehaviour
{
    private AudioSource audioSource;

    [Header("Audio Settings")]
    [SerializeField] private AudioClip backgroundMusic;
    [SerializeField] private bool playMusicOnAwake = true;

    void Awake()
    {
        audioSource = GetComponent<AudioSource>();
    }

    void Start()
    {
        if (playMusicOnAwake && backgroundMusic != null)
        {
            PlayBackgroundMusic(backgroundMusic);
        }
    }

    public void PlayBackgroundMusic(AudioClip clip)
    {
        audioSource.clip = clip;
        audioSource.loop = true;
        audioSource.Play();
    }

    public void PlaySFX(AudioClip clip, float volume = 1f)
    {
        audioSource.PlayOneShot(clip, volume);
    }

    public void PauseAudio() => audioSource.Pause();
    public void UnPauseAudio() => audioSource.UnPause();
    public void StopAudio() => audioSource.Stop();
}