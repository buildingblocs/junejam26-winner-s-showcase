using UnityEngine;

// Patched for the browser showcase: the original printed the Python-wizard
// challenge only to the console (Debug.Log), so nothing showed on screen and
// the game looked empty. This renders the dialogue on-screen with OnGUI and
// steps through the questions each time you press E next to the NPC.
public class SimpleDialogue : MonoBehaviour
{
    private bool completed = false;
    private bool showing = false;
    private int step = 0;

    private static readonly string[] lines = new string[]
    {
        "<b>Python Wizard</b>\n\nQ1:\n  x = 5\n  print(x)\n\nA) 5    B) x    C) Error\n\n→ Answer: A (5)",
        "<b>Python Wizard</b>\n\nQ2:\n  name = 'Cyber'\n  print(name)\n\nA) Cyber    B) name    C) Error\n\n→ Answer: A (Cyber)",
        "<b>Python Wizard</b>\n\nQ3:\n  if 3 > 1:\n      print('Yes')\n\nA) Yes    B) No    C) Error\n\n→ Answer: A (Yes)",
        "<b>✔ CHALLENGE COMPLETE</b>\n\n🔑 Python Access Key acquired (GREEN)!",
    };

    private GUIStyle boxStyle;
    private GUIStyle hintStyle;

    public void Interact()
    {
        if (completed && !showing)
        {
            showing = true;
            step = lines.Length - 1; // re-show the "complete" panel
            return;
        }

        if (!showing)
        {
            showing = true;
            step = 0;
            return;
        }

        // advance through the questions
        step++;
        if (step >= lines.Length)
        {
            completed = true;
            showing = false;
            step = 0;
        }
    }

    void OnGUI()
    {
        if (!showing) return;

        if (boxStyle == null)
        {
            boxStyle = new GUIStyle(GUI.skin.box)
            {
                fontSize = 20,
                alignment = TextAnchor.UpperLeft,
                wordWrap = true,
                richText = true,
                padding = new RectOffset(20, 20, 18, 18),
            };
            boxStyle.normal.textColor = Color.white;
            hintStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 15,
                alignment = TextAnchor.MiddleCenter,
            };
            hintStyle.normal.textColor = new Color(0.6f, 0.9f, 0.7f);
        }

        float w = Mathf.Min(620f, Screen.width - 40f);
        float h = 230f;
        float x = (Screen.width - w) / 2f;
        float y = Screen.height - h - 30f;

        GUI.color = new Color(0.04f, 0.05f, 0.12f, 0.92f);
        GUI.Box(new Rect(x, y, w, h), GUIContent.none);
        GUI.color = Color.white;
        GUI.Box(new Rect(x, y, w, h - 28), lines[Mathf.Clamp(step, 0, lines.Length - 1)], boxStyle);
        GUI.Label(new Rect(x, y + h - 26, w, 22), "Press E to continue", hintStyle);
    }
}
