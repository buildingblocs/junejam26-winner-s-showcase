using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;

public class BlockBlastGame : MonoBehaviour
{
    // Singleton
    public static BlockBlastGame Instance;
    
    // ===== SETUP IN UNITY =====
    public int gridWidth = 6;
    public int gridHeight = 6;
    public GameObject cellPrefab;
    public GameObject blockPrefab;
    public Transform gridParent;
    
    // UI Elements
    public Text healthText;
    public Text bossHealthText;
    public Text timerText;
    public Text scoreText;
    public GameObject gameOverPanel;
    public GameObject victoryPanel;
    
    // Spawn points for blocks
    public Transform spawnPoint1;
    public Transform spawnPoint2;
    public Transform spawnPoint3;
    
    // ===== GAME STATE =====
    private GameObject[,] grid;
    private int playerHealth = 30;
    private int bossHealth = 50;
    private float bossTimer = 3f;
    private int score = 0;
    private bool isGameActive = true;
    private List<GameObject> availableBlocks = new List<GameObject>();
    
    // ===== BLOCK SHAPES =====
    private List<BlockShape> shapes = new List<BlockShape>();
    
    void Awake()
    {
        Instance = this;
        grid = new GameObject[gridWidth, gridHeight];
    }
    
    void Start()
    {
        CreateShapes();
        CreateGrid();
        SpawnBlocks();
        UpdateUI();
        StartCoroutine(BossTimer());
    }
    
    void CreateShapes()
    {
        shapes.Add(new BlockShape(new bool[,] { { true } }, Color.cyan));
        shapes.Add(new BlockShape(new bool[,] { { true, true }, { true, true } }, Color.yellow));
        shapes.Add(new BlockShape(new bool[,] { { true, true, true } }, Color.magenta));
        shapes.Add(new BlockShape(new bool[,] { { true }, { true }, { true } }, Color.green));
        shapes.Add(new BlockShape(new bool[,] { { true, false }, { true, false }, { true, true } }, new Color(1, 0.5f, 0)));
        shapes.Add(new BlockShape(new bool[,] { { false, true, false }, { true, true, true } }, Color.red));
        shapes.Add(new BlockShape(new bool[,] { { true, true, false }, { false, true, true } }, new Color(0, 1, 0.5f)));
    }
    
    void CreateGrid()
    {
        if (cellPrefab == null)
        {
            // Create cell dynamically if no prefab
            for (int x = 0; x < gridWidth; x++)
            {
                for (int y = 0; y < gridHeight; y++)
                {
                    GameObject cell = new GameObject("Cell_" + x + "_" + y);
                    cell.transform.parent = gridParent;
                    cell.transform.position = new Vector3(x - gridWidth/2f + 0.5f, y - gridHeight/2f + 0.5f, 0);
                    SpriteRenderer sr = cell.AddComponent<SpriteRenderer>();
                    sr.color = new Color(0.2f, 0.2f, 0.2f, 0.5f);
                    
                    Texture2D tex = new Texture2D(1, 1);
                    tex.SetPixel(0, 0, Color.white);
                    tex.Apply();
                    sr.sprite = Sprite.Create(tex, new Rect(0, 0, 1, 1), new Vector2(0.5f, 0.5f));
                    sr.drawMode = SpriteDrawMode.Sliced;
                    sr.size = new Vector2(0.9f, 0.9f);
                }
            }
        }
    }
    
    IEnumerator BossTimer()
    {
        while (isGameActive)
        {
            if (bossTimer > 0)
            {
                bossTimer -= Time.deltaTime;
                if (timerText != null)
                    timerText.text = "⏱️ " + Mathf.RoundToInt(bossTimer);
            }
            else
            {
                playerHealth -= 5;
                UpdateUI();
                Camera.main.backgroundColor = Color.red;
                yield return new WaitForSeconds(0.2f);
                Camera.main.backgroundColor = new Color(0.1f, 0.1f, 0.2f);
                bossTimer = 3f;
                
                if (playerHealth <= 0)
                {
                    isGameActive = false;
                    if (gameOverPanel != null) gameOverPanel.SetActive(true);
                }
            }
            yield return null;
        }
    }
    
    void SpawnBlocks()
    {
        // Clear existing blocks
        foreach (GameObject block in availableBlocks)
        {
            if (block != null) Destroy(block);
        }
        availableBlocks.Clear();
        
        // Spawn 3 random blocks
        if (spawnPoint1 != null) CreateBlockAt(spawnPoint1.position, GetRandomShape());
        if (spawnPoint2 != null) CreateBlockAt(spawnPoint2.position, GetRandomShape());
        if (spawnPoint3 != null) CreateBlockAt(spawnPoint3.position, GetRandomShape());
    }
    
    BlockShape GetRandomShape()
    {
        return shapes[Random.Range(0, shapes.Count)];
    }
    
    void CreateBlockAt(Vector3 position, BlockShape shape)
    {
        GameObject blockObj = new GameObject("DraggableBlock");
        blockObj.transform.position = position;
        
        SpriteRenderer sr = blockObj.AddComponent<SpriteRenderer>();
        BoxCollider2D col = blockObj.AddComponent<BoxCollider2D>();
        
        // Create visual for the shape
        int shapeWidth = shape.shape.GetLength(0);
        int shapeHeight = shape.shape.GetLength(1);
        
        for (int x = 0; x < shapeWidth; x++)
        {
            for (int y = 0; y < shapeHeight; y++)
            {
                if (shape.shape[x, y])
                {
                    GameObject part = new GameObject("Part");
                    part.transform.parent = blockObj.transform;
                    part.transform.localPosition = new Vector3(x - shapeWidth/2f + 0.5f, y - shapeHeight/2f + 0.5f, 0);
                    SpriteRenderer partSr = part.AddComponent<SpriteRenderer>();
                    
                    Texture2D tex = new Texture2D(32, 32);
                    for (int i = 0; i < 32 * 32; i++) tex.SetPixel(i % 32, i / 32, Color.white);
                    tex.Apply();
                    partSr.sprite = Sprite.Create(tex, new Rect(0, 0, 32, 32), new Vector2(0.5f, 0.5f));
                    partSr.color = shape.color;
                    partSr.drawMode = SpriteDrawMode.Sliced;
                    partSr.size = new Vector2(0.85f, 0.85f);
                }
            }
        }
        
        // Set collider size
        col.size = new Vector2(shapeWidth * 0.9f, shapeHeight * 0.9f);
        
        // Add drag script
        BlockDrag drag = blockObj.AddComponent<BlockDrag>();
        drag.shape = shape.shape;
        drag.blockColor = shape.color;
        drag.shapeWidth = shapeWidth;
        drag.shapeHeight = shapeHeight;
        
        availableBlocks.Add(blockObj);
    }
    
    public void OnBlockPlaced()
    {
        SpawnBlocks();
    }
    
    public bool CanPlaceBlock(int startX, int startY, bool[,] shape)
    {
        for (int x = 0; x < shape.GetLength(0); x++)
        {
            for (int y = 0; y < shape.GetLength(1); y++)
            {
                if (shape[x, y])
                {
                    int gridX = startX + x;
                    int gridY = startY + y;
                    if (gridX < 0 || gridX >= gridWidth || gridY < 0 || gridY >= gridHeight)
                        return false;
                    if (grid[gridX, gridY] != null)
                        return false;
                }
            }
        }
        return true;
    }
    
    public void PlaceBlock(int startX, int startY, bool[,] shape, Color color)
    {
        for (int x = 0; x < shape.GetLength(0); x++)
        {
            for (int y = 0; y < shape.GetLength(1); y++)
            {
                if (shape[x, y])
                {
                    int gridX = startX + x;
                    int gridY = startY + y;
                    if (gridX >= 0 && gridX < gridWidth && gridY >= 0 && gridY < gridHeight)
                    {
                        GameObject block = new GameObject("PlacedBlock");
                        block.transform.parent = gridParent;
                        block.transform.position = new Vector3(gridX - gridWidth/2f + 0.5f, gridY - gridHeight/2f + 0.5f, 0);
                        SpriteRenderer sr = block.AddComponent<SpriteRenderer>();
                        
                        Texture2D tex = new Texture2D(1, 1);
                        tex.SetPixel(0, 0, Color.white);
                        tex.Apply();
                        sr.sprite = Sprite.Create(tex, new Rect(0, 0, 1, 1), new Vector2(0.5f, 0.5f));
                        sr.color = color;
                        sr.drawMode = SpriteDrawMode.Sliced;
                        sr.size = new Vector2(0.9f, 0.9f);
                        
                        grid[gridX, gridY] = block;
                    }
                }
            }
        }
        
        CheckAndClearLines();
    }
    
    void CheckAndClearLines()
    {
        int linesCleared = 0;
        
        // Check rows
        for (int y = 0; y < gridHeight; y++)
        {
            bool full = true;
            for (int x = 0; x < gridWidth; x++)
            {
                if (grid[x, y] == null) { full = false; break; }
            }
            if (full)
            {
                for (int x = 0; x < gridWidth; x++)
                {
                    Destroy(grid[x, y]);
                    grid[x, y] = null;
                }
                linesCleared++;
            }
        }
        
        // Check columns
        for (int x = 0; x < gridWidth; x++)
        {
            bool full = true;
            for (int y = 0; y < gridHeight; y++)
            {
                if (grid[x, y] == null) { full = false; break; }
            }
            if (full)
            {
                for (int y = 0; y < gridHeight; y++)
                {
                    Destroy(grid[x, y]);
                    grid[x, y] = null;
                }
                linesCleared++;
            }
        }
        
        if (linesCleared > 0)
        {
            int damage = linesCleared * 10;
            bossHealth -= damage;
            score += damage;
            bossTimer = 3f;
            UpdateUI();
            
            Camera.main.backgroundColor = Color.green;
            StartCoroutine(ResetColor());
            
            if (bossHealth <= 0)
            {
                isGameActive = false;
                if (victoryPanel != null) victoryPanel.SetActive(true);
            }
        }
    }
    
    IEnumerator ResetColor()
    {
        yield return new WaitForSeconds(0.2f);
        Camera.main.backgroundColor = new Color(0.1f, 0.1f, 0.2f);
    }
    
    void UpdateUI()
    {
        if (healthText != null) healthText.text = "❤️ " + playerHealth;
        if (bossHealthText != null) bossHealthText.text = "👾 " + bossHealth;
        if (scoreText != null) scoreText.text = "💥 " + score;
    }
    
    public void RestartGame()
    {
        UnityEngine.SceneManagement.SceneManager.LoadScene(
            UnityEngine.SceneManagement.SceneManager.GetActiveScene().name
        );
    }
    
    // Block shape class
    public class BlockShape
    {
        public bool[,] shape;
        public Color color;
        
        public BlockShape(bool[,] shape, Color color)
        {
            this.shape = shape;
            this.color = color;
        }
    }
}

// ===== DRAG SCRIPT =====
public class BlockDrag : MonoBehaviour
{
    public bool[,] shape;
    public Color blockColor;
    public int shapeWidth;
    public int shapeHeight;
    
    private Vector3 startPos;
    private bool isDragging = false;
    private Vector3 offset;
    private Camera cam;
    private GameObject[] visualParts;
    
    void Start()
    {
        cam = Camera.main;
        startPos = transform.position;
        
        // Store visual parts
        visualParts = new GameObject[transform.childCount];
        for (int i = 0; i < transform.childCount; i++)
            visualParts[i] = transform.GetChild(i).gameObject;
    }
    
    void OnMouseDown()
    {
        isDragging = true;
        if (cam != null)
        {
            Vector3 mouse = cam.ScreenToWorldPoint(Input.mousePosition);
            mouse.z = 0;
            offset = mouse - transform.position;
        }
        
        foreach (GameObject part in visualParts)
        {
            if (part != null)
            {
                SpriteRenderer sr = part.GetComponent<SpriteRenderer>();
                if (sr != null)
                    sr.color = new Color(sr.color.r, sr.color.g, sr.color.b, 0.5f);
            }
        }
    }
    
    void OnMouseDrag()
    {
        if (isDragging && cam != null)
        {
            Vector3 mouse = cam.ScreenToWorldPoint(Input.mousePosition);
            mouse.z = 0;
            transform.position = mouse - offset;
        }
    }
    
    void OnMouseUp()
    {
        isDragging = false;
        
        foreach (GameObject part in visualParts)
        {
            if (part != null)
            {
                SpriteRenderer sr = part.GetComponent<SpriteRenderer>();
                if (sr != null)
                    sr.color = new Color(sr.color.r, sr.color.g, sr.color.b, 1f);
            }
        }
        
        if (BlockBlastGame.Instance == null)
        {
            transform.position = startPos;
            return;
        }
        
        Vector3 gridPos = transform.position;
        int gridX = Mathf.RoundToInt(gridPos.x + BlockBlastGame.Instance.gridWidth/2f - 0.5f);
        int gridY = Mathf.RoundToInt(gridPos.y + BlockBlastGame.Instance.gridHeight/2f - 0.5f);
        
        if (BlockBlastGame.Instance.CanPlaceBlock(gridX, gridY, shape))
        {
            BlockBlastGame.Instance.PlaceBlock(gridX, gridY, shape, blockColor);
            BlockBlastGame.Instance.OnBlockPlaced();
            Destroy(gameObject);
        }
        else
        {
            transform.position = startPos;
        }
    }
}