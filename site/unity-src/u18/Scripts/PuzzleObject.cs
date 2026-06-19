using UnityEngine;

// Slap this onto the PHYSICAL object tied to the puzzle piece.
public class PuzzleObject : MonoBehaviour
{
    [Header("Puzzle Configuration")]
    [Tooltip("The exact name identifier of the puzzle type (e.g., StickyNote, Lock, Terminal)")]
    public string puzzleType;
}