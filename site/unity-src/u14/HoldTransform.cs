using UnityEngine;


public class ItemSwatAndBob: MonoBehaviour
{
    public float swayAmount = 0.05f;
    public float maxSwayAmount = 0.1f;
    public float swaySmoothness = 6f;

    public float bobSpeed = 10f;
    public float bobAmount = 0.03f;

    private Vector3 originalPosition;
    private float bobTimer = 0f;

    void Start()
    {
        originalPosition = transform.localPosition;
    }

    void Update()
    {
        float mouseX = -Input.GetAxis("Mouse X") * swayAmount;
        float mouseY = -Input.GetAxis("Mouse Y") * swayAmount;

        mouseX = Mathf.Clamp(mouseX, -maxSwayAmount, maxSwayAmount);
        mouseY = Mathf.Clamp(mouseY, -maxSwayAmount, maxSwayAmount);

        Vector3 targetPosition = new Vector3(mouseX, mouseY, 0);

        transform.localPosition = Vector3.Lerp(transform.localPosition, originalPosition + targetPosition, Time.deltaTime * swaySmoothness);
    }

    void CalculateBobbing()
    {
        float movementInput = new Vector2(Input.GetAxis("Horizontal"), Input.GetAxis("Vertical")).magnitude;

        if (movementInput > 0.1f)
        {
            bobTimer += Time.deltaTime * bobSpeed;

            float newY = originalPosition.y + Mathf.Sin(bobTimer) * bobAmount;
            float newX = originalPosition.x + Mathf.Cos(bobTimer/2) * bobAmount;

            transform.localPosition = new Vector3(transform.localPosition.x + (newX - originalPosition.x), newY, transform.localPosition.z);
        }

        else
        {
            bobTimer = 0;
        }
    }
}
