using TMPro;
using UnityEngine;

public class InventoryUI : MonoBehaviour
{
    public PlayerInventory inventory;
    public TextMeshProUGUI inventoryText;
    private void Start()
    {
        if (inventory == null)
            Debug.LogError("[InventoryUI] inventory field is NOT assigned in Inspector!");
        
        if (inventoryText == null)
            Debug.LogError("[InventoryUI] inventoryText field is NOT assigned in Inspector!");
        
        if (inventory != null && inventoryText != null)
            Debug.Log("[InventoryUI] Both fields assigned - ready to display inventory");

        // Try to ensure the TextMeshProUGUI is visible at runtime and provide diagnostics
        if (inventoryText != null)
        {
            inventoryText.gameObject.SetActive(true);
            inventoryText.enabled = true;

            var col = inventoryText.color;
            col.a = 1f;
            inventoryText.color = col;

            // Bring to front in the Canvas hierarchy
            inventoryText.transform.SetAsLastSibling();

            if (inventoryText.canvas != null)
            {
                Debug.Log($"[InventoryUI] inventoryText.canvas='{inventoryText.canvas.name}' renderMode={inventoryText.canvas.renderMode} sortingOrder={inventoryText.canvas.sortingOrder}");
            }
            else
            {
                Debug.LogWarning("[InventoryUI] inventoryText has no Canvas parent (canvas is null)");
            }
        }
    }


    void Update()
    {
        if (inventory == null || inventoryText == null)
            return;

        string text =
            "Inventory (" +
            inventory.items.Count +
            "/" +
            inventory.maxItems +
            ")\n";

        foreach(string item in inventory.items)
        {
            text += "- " + item + "\n";
        }

        // Update the text
        inventoryText.text = text;

        // Extra runtime check: ensure the TMP object is active and enabled
        if (!inventoryText.gameObject.activeInHierarchy || !inventoryText.enabled)
        {
            Debug.LogWarning("[InventoryUI] inventoryText is not active or not enabled at runtime");
        }
    }
}