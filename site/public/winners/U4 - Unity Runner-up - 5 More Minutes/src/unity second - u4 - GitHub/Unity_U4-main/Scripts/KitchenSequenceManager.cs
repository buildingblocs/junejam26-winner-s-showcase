using System.Collections;
using UnityEngine;

public class KitchenSequenceManager : MonoBehaviour
{
    [Header("Bedroom Objects")]
    [SerializeField] private GameObject pillowObject;
    [SerializeField] private GameObject baguetteUnderPillow;

    [Header("Kitchen Objects")]
    [SerializeField] private GameObject baguetteInToaster;
    [SerializeField] private GameObject fireRoot;
    [SerializeField] private AudioSource fireAudio;

    [Header("Timing")]
    [SerializeField] private float delayBeforeFire = 0.5f;

    [Header("Scene Transition")]
    [SerializeField] private string nextSceneName = "Foyer";

    [Header("Narration")]
    [SerializeField] private NarratorLine toasterFirstLine;
    [SerializeField] private NarratorLine pillowTooEarlyLine;
    [SerializeField] private NarratorLine pillowMovedLine;
    [SerializeField] private NarratorLine baguettePickedUpLine;
    [SerializeField] private NarratorLine toasterNeedsBreadLine;

    [Header("Toaster Cooking Narration")]
    [SerializeField] private NarratorLine[] toasterCookingLines;

    [Header("Toaster Fire Narration")]
    [SerializeField] private NarratorLine[] toasterPanicLines;

    [Header("Front Door Narration")]
    [SerializeField] private NarratorLine frontDoorLockedLine;

    private bool toasterInspected;
    private bool pillowMoved;
    private bool hasBaguette;
    private bool isCooking;
    private bool toasterBurning;

    private void Awake()
    {
        if (baguetteUnderPillow != null)
        {
            baguetteUnderPillow.SetActive(false);
        }

        if (baguetteInToaster != null)
        {
            baguetteInToaster.SetActive(false);
        }

        if (fireRoot != null)
        {
            fireRoot.SetActive(false);
        }

        if (fireAudio != null)
        {
            fireAudio.Stop();
        }
    }

    public string GetPrompt(
        KitchenInteractionType interactionType)
    {
        switch (interactionType)
        {
            case KitchenInteractionType.Pillow:
                return toasterInspected
                    ? "Move pillow"
                    : "Examine pillow";

            case KitchenInteractionType.Baguette:
                return "Pick up baguette";

            case KitchenInteractionType.Toaster:
                if (!toasterInspected)
                {
                    return "Examine toaster";
                }

                if (isCooking)
                {
                    return "Wait for baguette";
                }

                if (!hasBaguette)
                {
                    return "Use toaster";
                }

                return "Put baguette in toaster";

            case KitchenInteractionType.FrontDoor:
                return toasterBurning
                    ? "Leave the apartment"
                    : "Open front door";

            default:
                return "Interact";
        }
    }

    public bool CanInteract(
        KitchenInteractionType interactionType)
    {
        switch (interactionType)
        {
            case KitchenInteractionType.Pillow:
                return !pillowMoved;

            case KitchenInteractionType.Baguette:
                return pillowMoved && !hasBaguette;

            case KitchenInteractionType.Toaster:
                return !isCooking && !toasterBurning;

            case KitchenInteractionType.FrontDoor:
                return true;

            default:
                return false;
        }
    }

    public void PerformInteraction(
        KitchenInteractionType interactionType)
    {
        if (NarratorManager.Instance != null &&
            NarratorManager.Instance.IsSpeaking)
        {
            return;
        }

        switch (interactionType)
        {
            case KitchenInteractionType.Pillow:
                InteractWithPillow();
                break;

            case KitchenInteractionType.Baguette:
                PickUpBaguette();
                break;

            case KitchenInteractionType.Toaster:
                InteractWithToaster();
                break;

            case KitchenInteractionType.FrontDoor:
                InteractWithFrontDoor();
                break;
        }
    }

    private void InteractWithPillow()
    {
        if (!toasterInspected)
        {
            PlayLine(pillowTooEarlyLine);
            return;
        }

        pillowMoved = true;

        if (pillowObject != null)
        {
            pillowObject.SetActive(false);
        }

        if (baguetteUnderPillow != null)
        {
            baguetteUnderPillow.SetActive(true);
        }

        PlayLine(pillowMovedLine);
    }

    private void PickUpBaguette()
    {
        if (!pillowMoved || hasBaguette)
        {
            return;
        }

        hasBaguette = true;

        if (baguetteUnderPillow != null)
        {
            baguetteUnderPillow.SetActive(false);
        }

        PlayLine(baguettePickedUpLine);
    }

    private void InteractWithToaster()
    {
        if (!toasterInspected)
        {
            toasterInspected = true;
            PlayLine(toasterFirstLine);
            return;
        }

        if (!hasBaguette)
        {
            PlayLine(toasterNeedsBreadLine);
            return;
        }

        StartCooking();
    }

    private void StartCooking()
    {
        if (isCooking || toasterBurning)
        {
            return;
        }

        isCooking = true;
        hasBaguette = false;

        // Show the baguette sticking out of the toaster.
        if (baguetteInToaster != null)
        {
            baguetteInToaster.SetActive(true);
        }

        StartCoroutine(CookingSequenceRoutine());
    }

    private IEnumerator CookingSequenceRoutine()
    {
        // The Narrator talks while the baguette cooks.
        yield return PlaySequenceAndWait(
            toasterCookingLines
        );

        // Small awkward pause before everything goes wrong.
        if (delayBeforeFire > 0f)
        {
            yield return new WaitForSeconds(
                delayBeforeFire
            );
        }

        StartFire();

        // The Narrator reacts after the fire starts.
        yield return PlaySequenceAndWait(
            toasterPanicLines
        );
    }

    private void StartFire()
    {
        toasterBurning = true;
        isCooking = false;

        if (fireRoot != null)
        {
            fireRoot.SetActive(true);
        }

        if (fireAudio != null)
        {
            fireAudio.loop = true;
            fireAudio.Play();
        }
    }

    private IEnumerator PlaySequenceAndWait(
        NarratorLine[] lines)
    {
        if (NarratorManager.Instance == null ||
            lines == null ||
            lines.Length == 0)
        {
            yield break;
        }

        bool started =
            NarratorManager.Instance.PlaySequence(lines);

        if (!started)
        {
            yield break;
        }

        while (NarratorManager.Instance.IsSpeaking)
        {
            yield return null;
        }
    }

    private void InteractWithFrontDoor()
    {
        if (!toasterBurning)
        {
            PlayLine(frontDoorLockedLine);
            return;
        }

        if (SceneLoader.Instance == null)
        {
            Debug.LogError(
                "There is no SceneLoader in the scene."
            );

            return;
        }

        SceneLoader.Instance.LoadScene(
            nextSceneName
        );
    }

    private void PlayLine(NarratorLine line)
    {
        if (line == null ||
            string.IsNullOrWhiteSpace(line.subtitle) ||
            NarratorManager.Instance == null)
        {
            return;
        }

        NarratorManager.Instance.PlayLine(line);
    }
}