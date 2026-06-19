using UnityEngine;

[ExecuteInEditMode]
public class PixelBlit : MonoBehaviour
{
    public RenderTexture pixelTexture;

    void OnRenderImage(RenderTexture source, RenderTexture destination)
    {
        if (pixelTexture != null)
        {
            Graphics.Blit(pixelTexture, destination);
        }
        else
        {
            Graphics.Blit(source, destination);
        }
    }
}
