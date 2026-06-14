export type SourcePreview = {
  label: string;
  href: string;
  language: "python" | "csharp";
};

export type ShowcaseAsset = {
  slidePdf?: string;
  playUrl?: string;
  keyboardMode?: "wasd" | "full";
  sourceFiles: SourcePreview[];
};

const w = "/winners";

export const showcaseAssets: Record<string, ShowcaseAsset> = {
  p6: {
    slidePdf: `${w}/P6 - Pygame Winner - ALARM CLOCK Ticks Timebomb/slides/pygame second - p15 - Canva/GAME JAM BUILDINGBLOCS 2026.pdf`,
    playUrl: "/play/p6/index.html",
    keyboardMode: "full",
    sourceFiles: [
      {
        label: "alarm_clock.py",
        href: `${w}/P6 - Pygame Winner - ALARM CLOCK Ticks Timebomb/src/pygame second - p15 - GitHub/Pygame_P6-main/alarm_clock.py`,
        language: "python",
      },
    ],
  },
  p15: {
    slidePdf: `${w}/P15 - Pygame Runner-up - Finding the Way Home/slides/p15 - Canva/P15 Game Jam Where The Path Used to Be.pdf`,
    sourceFiles: [
      { label: "main.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/main.py`, language: "python" },
      { label: "settings.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/settings.py`, language: "python" },
      { label: "core/asset_manager.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/core/asset_manager.py`, language: "python" },
      { label: "core/game_manager.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/core/game_manager.py`, language: "python" },
      { label: "scenes/base_scene.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/scenes/base_scene.py`, language: "python" },
      { label: "scenes/menu.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/scenes/menu.py`, language: "python" },
      { label: "scenes/prologue.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/scenes/prologue.py`, language: "python" },
      { label: "scenes/chapter1.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/scenes/chapter1.py`, language: "python" },
      { label: "scenes/chapter2.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/scenes/chapter2.py`, language: "python" },
      { label: "scenes/chapter3.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/scenes/chapter3.py`, language: "python" },
      { label: "scenes/chapter4.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/scenes/chapter4.py`, language: "python" },
      { label: "systems/audio.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/systems/audio.py`, language: "python" },
      { label: "systems/glitch.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/systems/glitch.py`, language: "python" },
      { label: "systems/transition.py", href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/src/p15 - Drive/systems/transition.py`, language: "python" },
    ],
  },
  p26: {
    playUrl: "/play/p26/index.html",
    keyboardMode: "wasd",
    sourceFiles: [
      {
        label: "homebound.py",
        href: `${w}/P26 - Pygame Second Runner-up - Homebound/src/Pygame_26/Pygame_26-main/homebound.py`,
        language: "python",
      },
    ],
  },
  u8: {
    slidePdf: `${w}/U8 - Unity Winner - The Trash Wont Take Itself Out/slides/unity 1st - u8 - Canva/JuneJam U8.pdf`,
    sourceFiles: [
      { label: "PlayerController.cs", href: `${w}/U8 - Unity Winner - The Trash Wont Take Itself Out/src/unity 1st - u8 - GitHub/Assets/Scripts/PlayerController.cs`, language: "csharp" },
      { label: "PlayerSpit.cs", href: `${w}/U8 - Unity Winner - The Trash Wont Take Itself Out/src/unity 1st - u8 - GitHub/Assets/Scripts/PlayerSpit.cs`, language: "csharp" },
      { label: "GameManager.cs", href: `${w}/U8 - Unity Winner - The Trash Wont Take Itself Out/src/unity 1st - u8 - GitHub/Assets/Scripts/GameManager.cs`, language: "csharp" },
    ],
  },
  u4: {
    sourceFiles: [
      { label: "FirstPersonController.cs", href: `${w}/U4 - Unity Runner-up - 5 More Minutes/src/unity second - u4 - GitHub/Unity_U4-main/Scripts/FirstPersonController.cs`, language: "csharp" },
      { label: "NarratorManager.cs", href: `${w}/U4 - Unity Runner-up - 5 More Minutes/src/unity second - u4 - GitHub/Unity_U4-main/Scripts/NarratorManager.cs`, language: "csharp" },
      { label: "KitchenSequenceManager.cs", href: `${w}/U4 - Unity Runner-up - 5 More Minutes/src/unity second - u4 - GitHub/Unity_U4-main/Scripts/KitchenSequenceManager.cs`, language: "csharp" },
    ],
  },
  u2: {
    sourceFiles: [
      { label: "PlayerController.cs", href: `${w}/U2 - Unity Second Runner-up + Best Art - Taking OUT the Trash/src/unity third - u2 - GitHub/Assets/Scripts/PlayerController.cs`, language: "csharp" },
      { label: "EnemySpawner.cs", href: `${w}/U2 - Unity Second Runner-up + Best Art - Taking OUT the Trash/src/unity third - u2 - GitHub/Assets/Scripts/EnemySpawner.cs`, language: "csharp" },
      { label: "Navigation.cs", href: `${w}/U2 - Unity Second Runner-up + Best Art - Taking OUT the Trash/src/unity third - u2 - GitHub/Assets/Scripts/Navigation.cs`, language: "csharp" },
    ],
  },
  p17: {
    slidePdf: `${w}/P17 - CSIT Prize - BREACH/slides/csit prize - p17 - Canva/Breach.pdf`,
    sourceFiles: [
      { label: "client.py", href: `${w}/P17 - CSIT Prize - BREACH/src/csit prize - p17 - GitHub/Pygame_P17-main/breach_mvp/client.py`, language: "python" },
      { label: "server.py", href: `${w}/P17 - CSIT Prize - BREACH/src/csit prize - p17 - GitHub/Pygame_P17-main/breach_mvp/server.py`, language: "python" },
      { label: "game_rules.py", href: `${w}/P17 - CSIT Prize - BREACH/src/csit prize - p17 - GitHub/Pygame_P17-main/breach_mvp/game_rules.py`, language: "python" },
    ],
  },
  u16: {
    sourceFiles: [
      { label: "PlayerController.cs", href: `${w}/U16 - Most Original Concept - A Day in the Life of a Blind Person/src/GamesJamU16/GamesJamU16/Assets/scripts/PlayerController.cs`, language: "csharp" },
      { label: "CaneTap.cs", href: `${w}/U16 - Most Original Concept - A Day in the Life of a Blind Person/src/GamesJamU16/GamesJamU16/Assets/scripts/CaneTap.cs`, language: "csharp" },
      { label: "QuestManager.cs", href: `${w}/U16 - Most Original Concept - A Day in the Life of a Blind Person/src/GamesJamU16/GamesJamU16/Assets/scripts/QuestManager.cs`, language: "csharp" },
    ],
  },
  p14: {
    slidePdf: `${w}/P14 - Most Lines of Code - Daily Life Reimagined/slides/most lines of code - p14 - Canva/Building Blocs Game Presentation slides.pdf`,
    playUrl: "/play/p14/index.html",
    keyboardMode: "full",
    sourceFiles: [
      {
        label: "FinalGame.py",
        href: `${w}/P14 - Most Lines of Code - Daily Life Reimagined/src/most lines of code - p14 - GitHub/Pygame_14-main/FinalGame.py`,
        language: "python",
      },
    ],
  },
  p1: {
    slidePdf: `${w}/P1 - Sensory Overload - School Subway Surfers/slides/sensory overload - p1 - Canva/Our Pygame Journey with Krish, Hamilton, Rui Jie, and Aditya.pdf`,
    playUrl: "/play/p1/index.html",
    keyboardMode: "full",
    sourceFiles: [
      {
        label: "Schools Subway Surfers.py",
        href: `${w}/P1 - Sensory Overload - School Subway Surfers/src/sensory overload - p1 - Drive/Schools Subway Surfers.py`,
        language: "python",
      },
    ],
  },
  p8: {
    slidePdf: `${w}/P8 - Most Silly - Bleach Rush/slides/most silly - p8 - Canva/Pygame_P8.pdf`,
    playUrl: "/play/p8/index.html",
    keyboardMode: "wasd",
    sourceFiles: [
      {
        label: "bleach_rush.py",
        href: `${w}/P8 - Most Silly - Bleach Rush/src/most silly - p8 - Drive/buildingblocs-2026-p8/buildingblocs-2026-p8/coding stuff/bleach_rush.py`,
        language: "python",
      },
    ],
  },
  u13: {
    sourceFiles: [
      { label: "PlayerController.cs", href: `${w}/U13 - Most Overengineered - TinyExplorer/src/most overengineered - u13 - GitHub/Unity_U13-main/Assets/Scripts/PlayerController.cs`, language: "csharp" },
      { label: "waterRIsing.cs", href: `${w}/U13 - Most Overengineered - TinyExplorer/src/most overengineered - u13 - GitHub/Unity_U13-main/Assets/Scripts/waterRIsing.cs`, language: "csharp" },
      { label: "keyTrigger.cs", href: `${w}/U13 - Most Overengineered - TinyExplorer/src/most overengineered - u13 - GitHub/Unity_U13-main/Assets/Scripts/keyTrigger.cs`, language: "csharp" },
    ],
  },
};
