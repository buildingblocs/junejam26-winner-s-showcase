using UnityEngine;
using UnityEngine.InputSystem;
using System.Collections.Generic;
using System;
using UnityEngine.Tilemaps;
using Unity.VisualScripting;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using System.Linq;
using TMPro;
using NUnit.Framework;

public class PlayerController : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    InputAction moveAction;
    public float moveSpeed = 8;
    float timer = 0f;
    float timer2 = 0f;
    public Tilemap tilemap;
    private int [,] visited = new int[Navigation.mapx,Navigation.mapy];
    public int maxhealth;
    private int health = 100;
    private GameObject activeWeaponGameObject;
    private IWeapon activeWeapon;
    public GameObject[] weaponPrefabs;
    private int curHotbarSlot = 0;
    private int[] hotbarWeapons = new int[3];
    public int weaponCount = 1;
    public int[] prevWeapon;
    public bool[] hasWeapon;
    public int coins;

    public InputAction AttackAction;
    public InputAction[] Hotbar;
    public Slider healthBar;
    public Image[] weaponSprites;
    public TextMeshProUGUI[] weaponDesc;
    public TextMeshProUGUI[] weaponNames;
    public GameObject UI;
    public GameObject Shop;
    public TextMeshProUGUI coinAmount;
    public int totalWaves = 5;
    public int waves = 1;
    public GameObject[] wave1spawners;
    public GameObject[] wave2spawners;
    public GameObject[] wave3spawners;
    public GameObject[] wave4spawners;
    public GameObject[] wave5spawners;
    public GameObject[][] waveSpawners;
    public TextMeshProUGUI waveCounter;
    public TextMeshProUGUI timeCounter;
    public TextMeshProUGUI UIcoinAmount;
    public Image[] hotbarSprites;
    public Image[] hotbarWeaponSprites;
    public Sprite unselectedHotbar;
    public Sprite selectedHotbar;
    private void OnEnable()
    {
        AttackAction.Enable();
        AttackAction.performed += OnAttackPressed;
        Hotbar[0].Enable();
        Hotbar[1].Enable();
        Hotbar[2].Enable();
        Hotbar[0].performed += SwitchHotbar0;
        Hotbar[1].performed += SwitchHotbar1;
        Hotbar[2].performed += SwitchHotbar2;
    }
    private void OnDisable()
    {
        AttackAction.performed -= OnAttackPressed;
        AttackAction.Disable();
        Hotbar[0].Disable();
        Hotbar[1].Disable();
        Hotbar[2].Disable();
        Hotbar[0].performed -= SwitchHotbar0;
        Hotbar[1].performed -= SwitchHotbar1;
        Hotbar[2].performed -= SwitchHotbar2;
    }
    private void OnAttackPressed(InputAction.CallbackContext context)
    {
        activeWeapon.Attack();
    }

    void Start()
    {
        waveSpawners = new GameObject[][] {wave1spawners, wave2spawners, wave3spawners, wave4spawners, wave5spawners};
        Navigation.Map = new();
        UI.SetActive(true);
        Shop.SetActive(false);
        health = maxhealth;
        healthBar.maxValue = maxhealth;
        healthBar.value = maxhealth;
        hotbarWeapons[0] = 0;
        hasWeapon[0] = true;
        activeWeaponGameObject = Instantiate(weaponPrefabs[0], gameObject.GetComponent<Transform>());
        activeWeapon = activeWeaponGameObject.GetComponent<IWeapon>();
        Navigation.player = this;
        moveAction = InputSystem.actions.FindAction("Move");
        BoundsInt bounds = tilemap.cellBounds;
        foreach(Vector3Int cellPosition in bounds.allPositionsWithin)
        {
            if (tilemap.HasTile(cellPosition))
            {
                int rX = cellPosition.x*2;
                int rY = cellPosition.y*2;
                visited[rX,rY]=1;
                visited[rX+1,rY]=1;
                visited[rX,rY+1]=1;
                visited[rX+1,rY+1]=1;
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
        UIcoinAmount.text = coins.ToString();
        Vector2 moveValue = moveAction.ReadValue<Vector2>().normalized;
        transform.Translate(moveValue * moveSpeed * Time.deltaTime);
        timer += Time.deltaTime;
        timer2 += Time.deltaTime;
        if (timer > 0.1f)
        {
            timer -= 0.1f;
            Queue<Vector2Int> queue = new Queue<Vector2Int>();
            int [,] directions = new int[Navigation.mapx,Navigation.mapy];
            int [,] cloneVisited = (int[,])visited.Clone();
            directions[(int)Math.Floor(transform.position.x/Navigation.tilesize),(int)Math.Floor(transform.position.y/Navigation.tilesize)] = 0;
            cloneVisited[(int)Math.Floor(transform.position.x/Navigation.tilesize),(int)Math.Floor(transform.position.y/Navigation.tilesize)] = 1;
            queue.Enqueue(new Vector2Int((int)Math.Floor(transform.position.x/Navigation.tilesize), (int)Math.Floor(transform.position.y/Navigation.tilesize)));
            while(queue.Count > 0)
            {
                Vector2Int t = queue.Peek();
                queue.Dequeue();
                for(int i = 0; i < 4; i++)
                {
                    int a = Navigation.diri[i].x;
                    int b = Navigation.diri[i].y;
                    if (!(t.x + a >= 0 && t.x + a <= Navigation.mapx-1 && t.y + b >= 0 && t.y + b <= Navigation.mapy-1)) continue;
                    if (cloneVisited[t.x+a,t.y+b] == 1) continue;
                    cloneVisited[t.x+a,t.y+b] = 1;
                    directions[t.x+a,t.y+b] = i+1;
                    queue.Enqueue(new Vector2Int(t.x+a,t.y+b));
                }

            }
            Navigation.directions = directions;
        }
        timeCounter.text = "Time: " + Mathf.Round(timer2).ToString();
        if (timer2 >= Navigation.waveLength)
        {
            timer2 -= Navigation.waveLength;
            waves++;
            if (waves > totalWaves)
            {
                SceneManager.LoadScene(3);
            }
            openShop();
        }
    }
    public void dealDamage(int damage)
    {
        health -= damage;
        healthBar.value = health;
        if (health <= 0) {
        AudioManager.instance.Play("Die");
        SceneManager.LoadScene(2);
        }
        else AudioManager.instance.Play("Hurt");
    }
    public void openShop()
    {
        UI.SetActive(false);
        Shop.SetActive(true);
        Time.timeScale = 0f;
        initShop();
    }
    public void closeShop()
    {
        health = maxhealth;
        healthBar.value = maxhealth;
        UI.SetActive(true);
        Shop.SetActive(false);
        waveCounter.text = "Wave " + waves.ToString();
        Time.timeScale = 1f;
        for(int i = 0; i < weaponCount; i++)hotbarWeaponSprites[i].sprite = weaponPrefabs[hotbarWeapons[i]].GetComponent<SpriteRenderer>().sprite;
        foreach(GameObject o in waveSpawners[waves-2])
        {
            o.SetActive(false);
        }
        foreach(GameObject o in waveSpawners[waves - 1])
        {
            o.SetActive(true);
        }
    }
    private List<int> shopWeapons = new List<int>();
    public void initShop()
    {
        coinAmount.text = coins.ToString();
        shopWeapons.Clear();
        List<int> validWeapons = new List<int>();
        for(int i = 0; i < hasWeapon.Length; i++)
        {
            if (!hasWeapon[i] && (prevWeapon[i] == -1 || hasWeapon[prevWeapon[i]]))
            {
                validWeapons.Add(i);
            }
        }
        for(int i = 0; i < 3; i++)
        {
            int randi = UnityEngine.Random.Range(0, validWeapons.Count);
            int w = validWeapons[randi];
            shopWeapons.Add(w);
            weaponDesc[i].text = weaponPrefabs[w].GetComponent<IWeapon>().getDesc();
            weaponSprites[i].sprite = weaponPrefabs[w].GetComponent<SpriteRenderer>().sprite;
            weaponNames[i].text = weaponPrefabs[w].GetComponent<IWeapon>().getName();
        }
    }
    public void buyWeapon(int index)
    {
        if (hasWeapon[shopWeapons[index]]) {AudioManager.instance.Play("Error");return;}
        if (weaponPrefabs[shopWeapons[index]].GetComponent<IWeapon>().getPrice() > coins) {AudioManager.instance.Play("Error");return;}
        if (weaponCount == 3 && prevWeapon[shopWeapons[index]] == -1) {AudioManager.instance.Play("Error");return;}
        coins -= weaponPrefabs[shopWeapons[index]].GetComponent<IWeapon>().getPrice();
        coinAmount.text = coins.ToString();
        if (prevWeapon[shopWeapons[index]] == -1) 
        {
            hotbarWeapons[weaponCount] = shopWeapons[index];
            weaponCount++;
            SwitchHotbar(weaponCount-1);
        }
        else
        {
            int hotbarSlot = Array.IndexOf(hotbarWeapons, prevWeapon[shopWeapons[index]]);
            hotbarWeapons[hotbarSlot] = shopWeapons[index];
            Destroy(activeWeaponGameObject);
            activeWeaponGameObject = Instantiate(weaponPrefabs[shopWeapons[index]], gameObject.GetComponent<Transform>());
            activeWeapon = activeWeaponGameObject.GetComponent<IWeapon>();
            curHotbarSlot = hotbarSlot;
        }
        hasWeapon[shopWeapons[index]] = true;
        AudioManager.instance.Play("Coin");
    }
    public void buyWeapon0(){buyWeapon(0);}
    public void buyWeapon1(){buyWeapon(1);}
    public void buyWeapon2(){buyWeapon(2);}
    public void SwitchHotbar(int index)
    {
        if (index == curHotbarSlot) return;
        if (index >= weaponCount) return;
        hotbarSprites[curHotbarSlot].sprite = unselectedHotbar;
        curHotbarSlot = index;
        hotbarSprites[curHotbarSlot].sprite = selectedHotbar;
        Destroy(activeWeaponGameObject);
        activeWeaponGameObject = Instantiate(weaponPrefabs[hotbarWeapons[index]], gameObject.GetComponent<Transform>());
        activeWeapon = activeWeaponGameObject.GetComponent<IWeapon>();
    }
    public void SwitchHotbar0(InputAction.CallbackContext context){SwitchHotbar(0);}
    public void SwitchHotbar1(InputAction.CallbackContext context){SwitchHotbar(1);}
    public void SwitchHotbar2(InputAction.CallbackContext context){SwitchHotbar(2);}
}
