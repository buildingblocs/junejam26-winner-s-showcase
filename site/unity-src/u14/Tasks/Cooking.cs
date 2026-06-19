
/* using UnityEngine;
using UnityEngine.Playables;

// // A behaviour that is attached to a playable
// public class SimpleCookingSystem : MonoBehaviour
// {
//     // Variables to track cooking state
//     public float currentTemperature = 20.0f; // Starting room temperature in Celsius
//     public float targetDoneTemperature = 55.0f; // Target temperature for medium-rare

    private float rawTemperature = 45.0f;

    private float burntTemperature = 75.0f;
    private bool isStoveOn = false;

//     // 1. Initialization phase: Place the pan on the stove
//     private void Start()
//     {
//         Debug.Log("Prep Work: Placed the " + ingredientName + " into the pan.");
//         TurnOnStove();
//     }

//     // 2. Loop phase: Heat up the food frame by frame
//     private void Update()
//     {
//         if (isStoveOn)
//         {
//             HeatFood();
//             CheckDoneness();
//         }
//     }

//     // Custom method to turn the stove on
//     private void TurnOnStove()
//     {
//         isStoveOn = true;
//         Debug.Log("Action: Stove is turned ON. Cooking started...");
//     }

//     // Custom method to simulate heat transfer
//     private void HeatFood()
//     {
//         // Time.deltaTime ensures smooth, steady heating regardless of frame rate
//         currentTemperature += 5.0f * Time.deltaTime;
//     }

    // Custom method to check the food temperature
    private void CheckDoneness()
    {
        if (currentTemperature <= rawTemperature)
        {
            isStoveOn = false;

            Debug.Log("Failure! The " + ingredientName + " is raw at" + currentTemperature.ToString("F1") + "°C!");
        }
        else if (rawTemperature < currentTemperature < targetDoneTemperature)
        {
            isStoveOn = false; // Turn off the stove automatically
            
//             Debug.Log("The " + ingredientName + " is slightly undercooked at " + currentTemperature.ToString("F1") + "°C.");
//         }
//         else if (currentTemperature = targetDoneTemperature)
//         {
//             isStoveOn = false;

            Debug.Log("Success! The " + ingredientName + " is perfectly cooked at " + currentTemperature.ToString("F1") + "°C.");
        }
        else if (targetDoneTemperature < currentTemperature < BurntTemperature)
        {
            isStoveOn = false;

//             Debug.Log("The " + ingredientName + " is slightly overcooked at " + currentTemperature.ToString("F1") + "°C.");
//         }
//         else if (currentTemperature >= BurntTemperature)
//         {
//             isStoveOn = false;

            Debug.Log("Failure! The " + ingredientName + "is burnt at " + currentTemperature.ToString("F1") + "°C.");
        }
    }
}
*/
