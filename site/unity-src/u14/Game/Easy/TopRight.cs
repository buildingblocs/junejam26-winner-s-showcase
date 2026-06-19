using UnityEngine;
using TMPro;
using UnityEngine.SceneManagement;


public class TopRight : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI topRightText1;
    [SerializeField] private TextMeshProUGUI topRightText2;
    [SerializeField] private TaskTimer taskTimer;
    [SerializeField] private PlayerController taskRecorder;

    private float lastCheckedTime = -1f;
    private int lastCompletedTasks = -1;
    private int lastFailedTasks = -1;

    void Start()
    {
        // Null check to prevent crashes if you forget to assign it in the Inspector
        if (taskTimer == null)
        {
            topRightText1.text = "Timer: No active timer found";
            topRightText2.text = "No tasks found";
            return;
        }

        topRightText1.text = "Timer: nil";
        topRightText2.text = "Completed: 0 Failed: 0";
    }

    void Update()
    {
        if (taskTimer == null) return;

        
        float currentTime = Mathf.Ceil(taskTimer.timeLeft);

        if (currentTime != lastCheckedTime)
        {
            lastCheckedTime = currentTime;

            
            topRightText1.text = $"Timer: {currentTime}s";
        }

        if (taskRecorder == null) return;

        
        if (taskRecorder.completedTasks != lastCompletedTasks ||
            taskRecorder.failedTasks != lastFailedTasks)
        {
            lastCompletedTasks = taskRecorder.completedTasks;
            lastFailedTasks = taskRecorder.failedTasks;
            topRightText2.text = $"Completed: {lastCompletedTasks} Failed: {lastFailedTasks}";
        }
       if (taskRecorder.completedTasks >= 10) 
        {
            SceneManager.LoadScene("GoodEndingScene");
            Debug.Log("Good Ending");
        }
        else if (taskRecorder.failedTasks >= 5)
        {
            SceneManager.LoadScene("BadEndingScene");
            Debug.Log("Bad Ending");
        }



    }
}
