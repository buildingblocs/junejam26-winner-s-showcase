using System;
using UnityEngine;
using UnityEngine.SceneManagement;

public class keyTrigger : MonoBehaviour
{

    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnTriggerEnter(Collider collision)
    {
        if (collision.gameObject.CompareTag("Key"))
        {
            SceneManager.LoadScene("");
        }
    }

}
