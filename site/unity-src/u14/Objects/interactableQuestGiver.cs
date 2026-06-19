using UnityEngine;

public class questGiver : MonoBehaviour
{
    public string questName = "Submit Item";

    private bool questActive = false;
    private bool questCompleted = false;
    private TaskTimer taskTimer;

    private bool hasReset = false;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        taskTimer = FindAnyObjectByType<TaskTimer>();
        taskTimer.SetCurrentQuestGiver(this);
    }

    // Update is called once per frame
    void Update()
    {
        if (!questActive && questCompleted && !hasReset){    // For repeating quests and testing purposes
            questCompleted = false;
            hasReset = true;
        }
    }

    public void GiveQuest()
    {
        if(questCompleted)
        {
            Debug.Log("Quest already completed");
            return;
        }
        else if(questActive)
        {
            Debug.Log("Only 1 quest at a time");
            return;
        }

        questActive = true;
        hasReset = false;
        Debug.Log($"Quest Started: {questName}");
        taskTimer.StartQuest();
    }

    public void CompleteTask()
    {
        if(!questActive || questCompleted)
        {
            Debug.Log("No quests");
            return;
        }
        questActive = false;
        questCompleted = true;

        // Stop the running timer so it doesn't later count this finished task as a timeout/failure.
        taskTimer.CompleteQuest();

        PlayerController player = FindAnyObjectByType<PlayerController>();
        player.completedTasks += 1;
    }

    public void FailQuest()
    {
        if(!questActive || questCompleted)
        {
            return;
        }
        questActive = false;
        Debug.Log("Quest failed");

        PlayerController player = FindAnyObjectByType<PlayerController>();
        player.failedTasks += 1;
    }

    public bool getQuestActive()
    {
        return questActive && !questCompleted;
    }
    
    public bool getQuestCompleted()
    {
        return questCompleted;
    }
}
