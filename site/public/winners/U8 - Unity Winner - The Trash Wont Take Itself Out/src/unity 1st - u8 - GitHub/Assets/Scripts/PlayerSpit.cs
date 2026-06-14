using UnityEngine;
using UnityEngine.InputSystem;
using TMPro;
public class PlayerSpit : MonoBehaviour
{
    public int spitStrength;
    public float minSize =0.5f;
    public int maxSpits = 5;
    public float maxSize =1f; // set to what the player is originally on start
    private float sizeDelta;
    private InputAction spitAction;
    public GameObject trashObject;
    private ThrowableTrash currTrash;
    public Transform spawnPoint;

    public float currentMass;

    public TextMeshProUGUI massUI;

    public AudioSource audioSource;
    public AudioClip spitSFX;
    public AudioClip eatSFX;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        currentMass = transform.localScale.x;
        spitAction = InputSystem.actions.FindAction("Spit");
        sizeDelta = (maxSize - minSize) / (maxSpits);
        UpdateUI(transform.localScale.x * 10);
        spitAction.started += context =>
        {
            if (currentMass <= minSize) { return; } // Don't spit if at min size
            //Transform playerTransform = GetComponent<Transform>();
            //currentMass = playerTransform.localScale.x;
            spitTrash();
            currentMass = Mathf.Max(minSize, currentMass - sizeDelta);
            transform.localScale = new Vector3(currentMass, currentMass, currentMass);
            UpdateUI(Mathf.RoundToInt(currentMass * 10));
            Debug.Log("Trash was spit");
        };
    }

    // Update is called once per frame
    void Update()
    {

    }

    private void spitTrash()
    {
        // Spawn trash
        GameObject spawnedTrash = Instantiate(trashObject, spawnPoint.position, Quaternion.identity);
        currTrash = spawnedTrash.GetComponent<ThrowableTrash>();

        //Play Spit SFX
        audioSource.PlayOneShot(spitSFX, 1f);
        // Throw trash
        currTrash.Throw(spawnPoint.up, spitStrength);
        Destroy(spawnedTrash, 3);
    }

    private void eatTrash(GameObject trash)
    {
        currentMass = transform.localScale.x; //store current size of trashbag

        //Transform playerTransform = GetComponent<Transform>(); //access transform component

        if (currentMass >= maxSize) { Destroy(trash);} //stops code if current size is equals to maxSize

        //Play Spit SFX
        audioSource.PlayOneShot(eatSFX, 0.4f);
        currentMass = Mathf.Min(maxSize, currentMass + sizeDelta);
        transform.localScale = new Vector3(currentMass, currentMass, currentMass);
        UpdateUI(Mathf.RoundToInt(currentMass * 10));

        Destroy(trash);
    }

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("trash"))
        {
            Debug.Log("Yum");
            eatTrash(other.gameObject);
        }
    }

    private void UpdateUI(float currentSize)
    {
        if (massUI != null)
        {
            massUI.text = "Mass: " + currentSize.ToString() + " KG";
        }
    }
}
