using UnityEngine;

public class waterRising : MonoBehaviour
{

    bool stopMove=true;
    private float waterRiseRate=1f;
    Vector3 target = new Vector3 (-4.66f,5f,-6.7f);
    // ^^ please change this to the desired position

    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        if (stopMove==false) {
            transform.position = Vector3.MoveTowards(transform.position, target, waterRiseRate * Time.deltaTime);
            if (transform.position == target)
            {
                stopMove = true;
            }
        }
    }
    
    private void OnEnable()
    {
        // Subscribe to the event when the sprite becomes active
        sinkTrigger.waterStart += startMoving;
        playerController.playerDie += stopMoving; 
    }

    private void OnDisable()
    {
        // Always unsubscribe to prevent memory leaks!
        sinkTrigger.waterStart -= startMoving;
    }

    private void startMoving()
    {
        stopMove=false;
        Debug.Log("The other sprite detected the event!");

    }

    private void stopMoving()
    {
        Debug.Log("stopped");
        stopMove=true;
    }
}
