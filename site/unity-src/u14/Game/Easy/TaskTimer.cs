using UnityEngine;

public class TaskTimer : MonoBehaviour
{
    public PlayerController playerController;
    public float easyTaskTime = 5f;
    public float timeLeft;
    public bool taskDone = false;
    public bool questStarted = false;
    public bool questEnd = false;
    
    private questGiver currentQuestGiver;
    
    public void SetCurrentQuestGiver(questGiver giver){
        currentQuestGiver = giver;
    }
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    public void StartQuest()
    {
        questStarted = true;
        timeLeft = easyTaskTime;
        questEnd = false;
        taskDone = false;
    }

    // Update is called once per frame
    void Update()
    {
        if(questStarted && !taskDone && !questEnd){
            timeLeft -= Time.deltaTime;
            if(timeLeft <= 0){
                timeLeft = 0;
                questStarted = false;
                taskDone = true;
                // FailQuest() owns the failedTasks increment — don't add it here too,
                // or every timeout would be counted as two failures.
                if(currentQuestGiver != null)
                {
                    currentQuestGiver.FailQuest();
                }
            }

            Debug.Log(timeLeft);
        }
        
    }

    public void CompleteQuest()
    {
        if(questStarted && !taskDone && !questEnd)
        {
            taskDone = true;
            questStarted = false;
            questEnd = true;
            // questGiver.CompleteTask() owns the completedTasks increment.
            // This method only stops the timer so it can't later "time out".
            Debug.Log("Quest Completed");
        }
    }
    
}
