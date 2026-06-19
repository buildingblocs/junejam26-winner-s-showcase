using UnityEngine;

[CreateAssetMenu(fileName = "NewFileEntry", menuName = "Puzzles/File Entry Data")]
public class FileEntryData : ScriptableObject
{
    public string fileName;          // e.g., "/backup_2024.log"
    public bool isCorrectTarget;     // Is this the magic file containing the password?
    [TextArea(3, 5)]
    public string doubtDialogueKey;  // The dialogue event identifier to call if clicked
}