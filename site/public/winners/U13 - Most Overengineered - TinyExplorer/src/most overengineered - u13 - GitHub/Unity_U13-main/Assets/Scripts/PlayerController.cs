// using System.Numerics;
using Unity.Mathematics;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Processors;
using UnityEngine.Scripting.APIUpdating;
using System;

using sVector2=System.Numerics.Vector2;
using sVector3=System.Numerics.Vector3;

public class playerController : MonoBehaviour
{
    // ensure that the player cam has tag "MainCamera" ensure that water has tag "Water" and player has tag "Player"
    public Camera cam;
    private float camVertAngle=0;
    InputAction look,jump,move;
    Rigidbody rb;
    // private float sensitivity=1f;
    public float dist=10f;
    private float jumpforce=3f;
    private int jumpCount = 0;
    public int maxJump = 1;
    // bool touchGround = false;
    public static event Action playerDie;


    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        GameObject camera = GameObject.FindWithTag("MainCamera");

        look = InputSystem.actions.FindAction("Look");
        move = InputSystem.actions.FindAction("Move");
        jump = InputSystem.actions.FindAction("Jump");
        cam = camera.GetComponent<Camera>();
        rb= GetComponent<Rigidbody>();
        Cursor.lockState=CursorLockMode.Locked;
    
    }

    // Update is called once per frame
    void Update()
    {
        RotateCam();
        Move();
        Attention();
    }

    void Move()
    {
        Vector2 moveValue = move.ReadValue<Vector2>();
//  && (jumpCount<maxJump
        if (jump.WasPressedThisFrame()) 
        {
            rb.AddForce(Vector3.up*jumpforce,ForceMode.Impulse);
            jumpCount++;
        } 

        Vector3 motion = new Vector3(moveValue.x,0,moveValue.y);
        if (motion.magnitude > 1) motion=motion.normalized;
        transform.Translate(motion*Time.deltaTime*dist);
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("Water"))
        {
            Debug.Log("player_died");
            playerDie?.Invoke();
        }
    } 
    
    void RotateCam()
    {
        Vector2 rotation=look.ReadValue<Vector2>();

        transform.Rotate(Vector3.up*rotation.x);
        camVertAngle += rotation.y;
        camVertAngle=Mathf.Clamp(camVertAngle,-89f,89f);
        cam.transform.localEulerAngles=new Vector3(-camVertAngle,0,0);
    }

    void Attention()
    {
        if (Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame)
        {Cursor.lockState=CursorLockMode.Locked;}

        if (Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame)
        {Cursor.lockState=CursorLockMode.None;}
    }

    public static void PlayerDie()
    {
        playerDie?.Invoke();
    }
}
// add to the fall reset
    // void OnEnable()
    // {
    //     playerController.playerDie += RestartGame();
    // }