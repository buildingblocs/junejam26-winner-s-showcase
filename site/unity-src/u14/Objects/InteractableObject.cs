using UnityEngine;

public class InteractableObject : MonoBehaviour
{
    public enum ItemType
    {
        Food,
        Trash,
        TaskItem
    }
    public ItemType itemType = ItemType.TaskItem;

    public string itemName = "Pot";
    public bool canPickup = true;
    public bool Consumable = true;

    // Start is called once before the first execution of Update after the MonoBehaviour is created


    // Template for all objects so only variables needs to be changed
    public void PickedUp()
    {
        if(canPickup == true)
        {
            Debug.Log($"{itemName} successfully picked up");
        }
    }

    public void Consumed()
    {
        if(Consumable == true)
        {
            Debug.Log($"{itemName} consumed");
        }
    }

    public void SubmitTaskItem()       //Might remove as added to another script
    {
        Debug.Log($"{itemName} submitted successfully");
        Destroy(gameObject);
    }
}
