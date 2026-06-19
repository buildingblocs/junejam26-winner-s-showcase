using UnityEngine;

public class PlayerSpriteSwapper : MonoBehaviour
{
    private SpriteRenderer spriteRenderer;

    public Sprite forwardSprite;
    public Sprite backwardSprite;
    public Sprite leftSprite;
    public Sprite rightSprite;


    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
