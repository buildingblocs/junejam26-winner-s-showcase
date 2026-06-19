using UnityEngine;

public class FirstPersonInteraction : MonoBehaviour
{
    public Camera playerCamera;
    public Transform holdTransform;

    public float pickupRange = 4f; //can change this

    public float throwForce = 15f; //can change this

    public int heldItemLayer;

    private GameObject heldObject;
    private Rigidbody heldRigidbody;
    private int originalLayer;

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.E))
        {
            if (heldObject == null)
            {
                TryPickupObject();
            }
            else
            {
                DropObject();
            }
        }

        if (Input.GetMouseButtonDown(0) && heldObject != null)
        {
          ThrowObject();  
        }
    }

    void TryPickupObject()
    {
        Ray ray = playerCamera.ViewportPointToRay(new Vector3(0.5f, 0.5f, 0));
        RaycastHit hit;

        if (Physics.Raycast(ray, out hit, pickupRange))
        {
            if (hit.collider.TryGetComponent<Rigidbody>(out Rigidbody rb))
            {
                if (hit.collider.CompareTag("Pickupable"))
                {
                    Pickup(hit.collider.gameObject, rb);
                }
            }
        }
    }
    void Pickup(GameObject obj, Rigidbody rb)
    {
        heldObject = obj;
        heldRigidbody = rb;

        originalLayer = heldObject.layer;
        heldObject.layer = heldItemLayer;

        heldRigidbody.isKinematic = true;
        heldRigidbody.useGravity = false;

        heldObject.transform.SetParent(holdTransform);
        heldObject.transform.localPosition = Vector3.zero;
        heldObject.transform.localRotation = Quaternion.identity;
    }

    void DropObject()
    {
        if (heldObject == null) return;

        heldObject.transform.SetParent(null);

        heldObject.layer = originalLayer;
        heldRigidbody.isKinematic = false;
        heldRigidbody.useGravity = true;

        heldObject = null;
        heldRigidbody = null;
    }

    void ThrowObject()
    {
        Rigidbody rbToThrow = heldRigidbody;

        DropObject();

        rbToThrow.AddForce(playerCamera.transform.forward * throwForce, ForceMode.Impulse);
    }
}