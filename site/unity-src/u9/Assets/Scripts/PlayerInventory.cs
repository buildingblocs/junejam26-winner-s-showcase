using System.Collections.Generic;
using UnityEngine;

public class PlayerInventory : MonoBehaviour
{
    public int maxItems = 3;

    public List<string> items = new List<string>();

    public bool IsFull()
    {
        return items.Count >= maxItems;
    }

    public bool AddItem(string itemName)
    {
        if (IsFull())
            return false;

        items.Add(itemName);
        return true;
    }
}