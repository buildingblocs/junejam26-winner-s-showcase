using UnityEngine;

public class PickupItem : MonoBehaviour
{
    public string itemName = "Unnamed Item";

    private PlayerInventory playerInventory;
    private Collider2D myCollider;

    private void Start()
    {
        myCollider = GetComponent<Collider2D>();
        if (myCollider == null)
        {
            Debug.LogError($"[PickupItem] {gameObject.name} has NO Collider2D component!");
            return;
        }

        if (!myCollider.isTrigger)
        {
            Debug.LogWarning($"[PickupItem] {gameObject.name} collider is NOT set to isTrigger=true");
        }

        Rigidbody2D rb = GetComponent<Rigidbody2D>();
        if (rb == null)
        {
            Debug.LogWarning($"[PickupItem] {gameObject.name} has NO Rigidbody2D - consider adding one for reliable trigger detection");
        }

        Debug.Log($"[PickupItem] '{itemName}' initialized - ready to pickup");
    }

    private void OnTriggerEnter2D(Collider2D other)
    {
        Debug.Log($"[PickupItem] OnTriggerEnter2D detected from {other.gameObject.name}");

        playerInventory = other.GetComponent<PlayerInventory>();
        if (playerInventory != null)
        {
            Debug.Log($"[PickupItem] Player nearby for '{itemName}'");
        }
        else
        {
            Debug.Log($"[PickupItem] Collision with {other.gameObject.name} but no PlayerInventory found");
        }
    }

    private void OnTriggerExit2D(Collider2D other)
    {
        if (other.GetComponent<PlayerInventory>() == playerInventory)
        {
            Debug.Log($"[PickupItem] Player left trigger for '{itemName}'");
            playerInventory = null;
        }
    }

    private void Update()
    {
        if (playerInventory == null)
            return;

        if (!Input.GetKeyDown(KeyCode.E))
            return;

        Debug.Log($"[PickupItem] E pressed - attempting to pick up '{itemName}'");
        if (playerInventory.AddItem(itemName))
        {
            Debug.Log($"[PickupItem] Successfully picked up: {itemName}");
            Destroy(gameObject);
        }
        else
        {
            Debug.Log("[PickupItem] Inventory Full!");
        }
    }
}