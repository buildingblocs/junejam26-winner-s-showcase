using UnityEngine;
using UnityEngine.Video;
using System.Collections;

public class VideoController : MonoBehaviour
{
    private VideoPlayer videoPlayer;
    public GameObject videoOverlay;

    void Awake()
    {
        // Automatically finds the Video Player on this same GameObject
        videoPlayer = GetComponent<VideoPlayer>();
        
        // Prevent the video from rushing to play on startup
        if (videoPlayer != null)
            videoPlayer.playOnAwake = false;

        if (videoOverlay != null)
            videoOverlay.SetActive(false);
    }

    public void PlayVideoOverlay()
    {
        if (videoOverlay != null)
            videoOverlay.SetActive(true);

        if (videoPlayer == null)
            return;

        StartCoroutine(PrepareAndPlayVideo());
    }

    IEnumerator PrepareAndPlayVideo()
    {
        if (videoPlayer.isPrepared)
        {
            videoPlayer.Play();
            yield break;
        }

        // Load the video data into memory first
        videoPlayer.Prepare();

        // Wait here until the audio and video buffers are ready
        while (!videoPlayer.isPrepared)
        {
            yield return null;
        }

        // Buffer is safely filled, now play without overflowing
        videoPlayer.Play();
        Debug.Log("Video started smoothly!");
    }
}