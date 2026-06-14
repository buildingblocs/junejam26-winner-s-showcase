export type GameEntry = {
  slug: string;
  title: string;
  teamCode: string;
  track: "Pygame" | "Unity";
  category: "ranked" | "special";
  awards: string[];
  team: string;
  summary: string;
  cover: string;
  writeup: string;
  links: Array<{ label: string; href: string }>;
  playNote: string;
};

const w = "/winners";

export const games: GameEntry[] = [
  {
    slug: "p6",
    title: "ALARM CLOCK: Tick's Timebomb",
    teamCode: "P6",
    track: "Pygame",
    category: "ranked",
    awards: ["Pygame Winner"],
    team: "Gan Xuan En Claire, Peh Hng Hao Lucas, Yong Tian Ci Braden",
    summary:
      "A psychological horror adventure where an alarm clock comes to life, grows stranger over ten days, and changes its ending through player choices.",
    cover: "/assets/images/p6-cover.png",
    writeup:
      "The team brainstormed everyday routines and objects before centering their game on an alarm clock and its functions. ALARM CLOCK: Tick's Timebomb turns the unsettling feeling of waking up to an alarm into a psychological horror adventure, with the clock becoming more frightening each day before the player unexpectedly develops feelings for it. Choices made across the story affect the boss fight and ending. Their main challenge was balancing story and comedy, which they handled by planning dialogue carefully so the game stayed fun, strange, and engaging.",
    links: [
      {
        label: "Slides PDF",
        href: `${w}/P6 - Pygame Winner - ALARM CLOCK Ticks Timebomb/slides/pygame second - p15 - Canva/GAME JAM BUILDINGBLOCS 2026.pdf`,
      },
      {
        label: "Slides PPTX",
        href: `${w}/P6 - Pygame Winner - ALARM CLOCK Ticks Timebomb/slides/pygame second - p15 - Canva/GAME JAM BUILDINGBLOCS 2026.pptx`,
      },
      {
        label: "Source ZIP",
        href: `${w}/P6 - Pygame Winner - ALARM CLOCK Ticks Timebomb/src/pygame second - p15 - GitHub.zip`,
      },
    ],
    playNote:
      "This is downloaded Pygame source. A browser export, for example through pygbag, is needed before it can run inside this page.",
  },
  {
    slug: "p15",
    title: "Finding Way Home",
    teamCode: "P15",
    track: "Pygame",
    category: "ranked",
    awards: ["Pygame Runner-up"],
    team: "Liew Jia Yan Anne, Su Myat Thiri, Jonas Phua Yong Bin, Isaac Thian Junjie",
    summary:
      "A visual novel concept about memory loss, wayfinding, and how an ordinary walk home can become emotionally difficult.",
    cover: "/assets/images/p15-cover.svg",
    writeup:
      "The idea came from a real experience where the team encountered an elderly woman who was lost at an HDB void deck. A wrist tag helped them contact her husband, and they waited with her until he arrived. The moment stayed with them because it showed how a simple journey home can become a real struggle for people living with memory loss. Time limits and unfamiliarity with visual novel workflows in Pygame became major obstacles, so the team used AI as a prototyping aid and learned how important clear prompting is when turning an idea into a playable prototype quickly.",
    links: [
      {
        label: "Submission note",
        href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/README.md`,
      },
    ],
    playNote:
      "The matching P15 source and slides were not identifiable in the downloaded files after the label corrections, so no playable build is available yet.",
  },
  {
    slug: "p26",
    title: "Homebound",
    teamCode: "P26",
    track: "Pygame",
    category: "ranked",
    awards: ["Pygame Second Runner-up"],
    team: "Cyrus Tng Jia Zhe, Chye Kai Ru Jolin, Lee Jia Hui",
    summary:
      "A running and fighting game where household problems become interactive enemies and relatable daily obstacles.",
    cover: "/assets/images/p26-cover.png",
    writeup:
      "Homebound started from a broad team brainstorm, with ideas voted on and combined into one concept. The team wanted an interactive game rather than a passive screen, so they made the player and enemies represent ordinary challenges such as ants appearing when rice falls on the floor. Their first maze-style design failed because enemies could walk through walls. Instead of patching a weak foundation, they changed direction into a running and fighting game, using lessons from the failed prototype to improve the final version.",
    links: [
      {
        label: "Slides PPTX",
        href: `${w}/P26 - Pygame Second Runner-up - Homebound/slides/pygame 3rd - p26.pptx`,
      },
      {
        label: "Writeup DOCX",
        href: `${w}/P26 - Pygame Second Runner-up - Homebound/slides/Writeup.docx`,
      },
      {
        label: "Source ZIP",
        href: `${w}/P26 - Pygame Second Runner-up - Homebound/src/Pygame_26.zip`,
      },
    ],
    playNote:
      "This is downloaded Pygame source. A browser export is needed before it can be embedded here.",
  },
  {
    slug: "u8",
    title: "The Trash Won't Take Itself Out!",
    teamCode: "U8",
    track: "Unity",
    category: "ranked",
    awards: ["Unity Winner"],
    team: "Ng Wei Le Dylan, Chelsea Diane Balane Paquibot, Ian Then Kai Xiang, Jose Matthew Abram Mendoza",
    summary:
      "A Unity game about taking out the trash, scoped around clear mechanics, compact level design, and a new perspective on routine.",
    cover: "/assets/images/u8-cover.png",
    writeup:
      "The team found the theme broad, so they brainstormed routines and objects, filtered ideas by fun and feasibility, and eventually chose a trash bag over a book because it could become a complete game within the jam timeline. Their largest design challenge was building a level that introduced mechanics with good pacing and flow. A larger living-room-and-yard map was cut down to a tighter layout. They also debugged both code problems and Unity setup mistakes, using console errors, the debugger, Debug.Log(), and careful checks of object orientation and scene assumptions.",
    links: [
      {
        label: "Slides PDF",
        href: `${w}/U8 - Unity Winner - The Trash Wont Take Itself Out/slides/unity 1st - u8 - Canva/JuneJam U8.pdf`,
      },
      {
        label: "Slides PPTX",
        href: `${w}/U8 - Unity Winner - The Trash Wont Take Itself Out/slides/unity 1st - u8 - Canva/JuneJam U8.pptx`,
      },
      {
        label: "Source ZIP",
        href: `${w}/U8 - Unity Winner - The Trash Wont Take Itself Out/src/unity 1st - u8 - GitHub.zip`,
      },
    ],
    playNote:
      "This Unity project is downloaded as source. It needs a Unity WebGL export before it can run inside this page.",
  },
  {
    slug: "u4",
    title: "5 More Minutes",
    teamCode: "U4",
    track: "Unity",
    category: "ranked",
    awards: ["Unity Runner-up"],
team: "Pan Yinchen, Elliott Huang, Lian Shengzhe, Ricardo Delario",
    summary:
      "A walking simulator about the student commute, using narration and player choice to turn a mundane journey into comedy.",
    cover: "/assets/images/u4-cover.png",
    writeup:
      "The team looked at games they loved and focused on The Stanley Parable, which turns a boring office into something funny and thought-provoking through narration and choice. They applied the same approach to the student commute to a BuildingBloCS workshop. With only two days, they chose a walking simulator because the core mechanics were simple enough to let them spend most of their time writing narrator lines and building the world. The main challenge was resisting scope creep, so they locked the feature list at the end of day one.",
    links: [
      {
        label: "Slides PPTX",
        href: `${w}/U4 - Unity Runner-up - 5 More Minutes/slides/unity second - u4.pptx`,
      },
      {
        label: "Source ZIP",
        href: `${w}/U4 - Unity Runner-up - 5 More Minutes/src/unity second - u4 - GitHub.zip`,
      },
    ],
    playNote:
      "This Unity project needs a WebGL export before it can be played inside the website.",
  },
  {
    slug: "u2",
    title: "Taking OUT the Trash",
    teamCode: "U2",
    track: "Unity",
    category: "ranked",
    awards: ["Unity Second Runner-up", "Best Art"],
    team: "Chew Keng Kai Enson, Fang Xinzhuo, Kouta Alexander Ono-Wong, Jayden Tan Yu Zhe",
    summary:
      "A roguelike-inspired Unity game that asks players to think twice before throwing something away.",
    cover: "/assets/images/u2-cover.png",
    writeup:
      "Taking OUT the Trash puts players in the perspective of an item that might otherwise be discarded. The team drew from Brotato and the roguelike genre because it gave them a concept that could expand naturally. They added obstacles, walls, simple pathfinding, and a time-based wave system that rewards skilled players while staying accessible. Time constraints forced cuts to maps, boss fights, weapons, and upgrades, so they leaned into object-oriented structure, tilemaps, layered tiles, and denser pathfinding cells to make the game easier to improve later.",
    links: [
      {
        label: "Ranked slides PPTX",
        href: `${w}/U2 - Unity Second Runner-up + Best Art - Taking OUT the Trash/slides/unity third - u2.pptx`,
      },
      {
        label: "Best Art slides PPTX",
        href: `${w}/U2 - Unity Second Runner-up + Best Art - Taking OUT the Trash/slides/best art - u2.pptx`,
      },
      {
        label: "Source ZIP",
        href: `${w}/U2 - Unity Second Runner-up + Best Art - Taking OUT the Trash/src/unity third - u2 - GitHub.zip`,
      },
    ],
    playNote:
      "This Unity project includes source and desktop-oriented assets, but not a WebGL build. Export it from Unity as WebGL to make it playable here.",
  },
  {
    slug: "p17",
    title: "BREACH",
    teamCode: "P17",
    track: "Pygame",
    category: "special",
    awards: ["CSIT Prize"],
    team: "Khambhati Moiz Huzefa, Kendrick Slamat, Jerome Loke, Agne Rudhresh Ravichandran",
    summary:
      "A cybersecurity social-deduction game where attackers and defenders race to save or destroy a compromised research lab.",
    cover: "/assets/images/p17-cover.png",
    writeup:
      "BREACH came from asking why the social deduction structure of Among Us had not been used to teach cybersecurity. Attackers and defenders become the equivalent of imposters and crewmates, racing against the clock around a compromised research lab. The team had to learn cybersecurity concepts outside their Applied AI background, design useful beginner questions, and validate ideas with friends studying cybersecurity. They also had to learn multiplayer Pygame, with WebSocket real-time sync becoming one of the most difficult parts of the prototype.",
    links: [
      {
        label: "Slides PDF",
        href: `${w}/P17 - CSIT Prize - BREACH/slides/csit prize - p17 - Canva/Breach.pdf`,
      },
      {
        label: "Slides PPTX",
        href: `${w}/P17 - CSIT Prize - BREACH/slides/csit prize - p17 - Canva/Breach.pptx`,
      },
      {
        label: "Source ZIP",
        href: `${w}/P17 - CSIT Prize - BREACH/src/csit prize - p17 - GitHub.zip`,
      },
    ],
    playNote:
      "This Pygame multiplayer project needs a browser build and server deployment before it can run inside this page.",
  },
  {
    slug: "u16",
    title: "A Day in the Life of a Blind Person",
    teamCode: "U16",
    track: "Unity",
    category: "special",
    awards: ["Most Original Concept"],
    team: "Mao Yuxi, Sara Tan Jia Ning, Maddula Geethika, Cheng Ruitao",
    summary:
      "A 2D platformer RPG about navigating ordinary life from the perspective of someone who is blind.",
    cover: "/assets/images/u16-cover.png",
    writeup:
      "The team began with many ideas at different levels of complexity, but as the workshops progressed they realized several concepts were not feasible for beginners in the time available. They landed on a 2D platformer RPG inspired by the demo, with mechanics meant to convey parts of everyday life for someone who is blind. The project involved simplifying hard ideas, learning quickly, and taking small steps through technical and time constraints. Even though the final game changed from the original vision, the team saw it as evidence of how far they had come.",
    links: [
      {
        label: "Slides PPTX",
        href: `${w}/U16 - Most Original Concept - A Day in Life of a Blind Person/slides/most original concept - u16.pptx`,
      },
      {
        label: "Source ZIP",
        href: `${w}/U16 - Most Original Concept - A Day in Life of a Blind Person/src/GamesJamU16.zip`,
      },
    ],
    playNote:
      "This Unity project needs a WebGL export before it can be embedded and played here.",
  },
  {
    slug: "p14",
    title: "Daily Life Reimagined",
    teamCode: "P14",
    track: "Pygame",
    category: "special",
    awards: ["Most Lines of Code"],
    team: "Va Ramaswami, Mohammad Adnan Khilji, Ng Yek Tiek, Li Chang Wei Eben",
    summary:
      "A collection of minigames that turns waking up, brushing teeth, eating, homework, and sleeping into playful challenges.",
    cover: "/assets/images/p14-cover.png",
    writeup:
      "Daily Life Reimagined came from thinking about how everyday tasks can sometimes be hard. The team turned a normal day into levels about waking up, brushing teeth, eating lunch, doing homework, and going back to bed, each with a twist such as toothpaste monsters or scary things in the dark. Their main challenge was making each level play differently while keeping one story intact, with timers, keyboard controls, scoring systems, and difficulty balancing. They built the game step by step, tested each level, fixed bugs, and improved it together.",
    links: [
      {
        label: "Slides PDF",
href: `${w}/P14 - Most Lines of Code - Daily Life Reimagined/slides/most lines of code - p14 - Canva/Building Blocs Game Presentation slides.pdf`,
      },
      {
        label: "Slides PPTX",
        href: `${w}/P14 - Most Lines of Code - Daily Life Reimagined/slides/most lines of code - p14 - Canva/Building Blocs Game Presentation slides.pptx`,
      },
      {
        label: "Source ZIP",
href: `${w}/P14 - Most Lines of Code - Daily Life Reimagined/src/most lines of code - p14 - GitHub.zip`,
      },
    ],
    playNote:
      "This is downloaded Pygame source. A browser export is needed before it can be played here.",
  },
  {
    slug: "p1",
    title: "School Subway Surfers",
    teamCode: "P1",
    track: "Pygame",
    category: "special",
    awards: ["Sensory Overload"],
    team: "Aditya Jain, Tsai Rui Jie, Nguyen Ngoc Minh Khang Hamilton, Krish Vishwa Muthia",
    summary:
      "A student-teacher endless runner inspired by Subway Surfers and Mario, changing as the player survives longer.",
    cover: "/assets/images/p1-cover.png",
    writeup:
      "The team wanted to take the addictive loop of games like Subway Surfers and Mario Bros and turn it into a funny student-teacher chase that changes as the player survives longer. Their biggest challenges were understanding the code patterns taught during the jam and identifying where bugs were coming from. AI helped them debug, though they had to work through explanations several times before the ideas clicked. The final process was difficult but rewarding.",
    links: [
      {
        label: "Slides PDF",
        href: `${w}/P1 - Sensory Overload - School Subway Surfers/slides/sensory overload - p1 - Canva/Our Pygame Journey with Krish, Hamilton, Rui Jie, and Aditya.pdf`,
      },
      {
        label: "Slides PPTX",
        href: `${w}/P1 - Sensory Overload - School Subway Surfers/slides/sensory overload - p1 - Canva/Our Pygame Journey with Krish, Hamilton, Rui Jie, and Aditya.pptx`,
      },
      {
        label: "Source README",
        href: `${w}/P1 - Sensory Overload - School Subway Surfers/src/sensory overload - p1 - Drive/README FILE.md`,
      },
    ],
    playNote:
      "This is downloaded Pygame source. A browser build is needed before it can be embedded here.",
  },
  {
    slug: "p8",
    title: "Bleach Rush",
    teamCode: "P8",
    track: "Pygame",
    category: "special",
    awards: ["Most Silly"],
    team: "Guo Renjun, Kee Heng Jun, Salman Farsi, Hayyan",
    summary:
      "A deliberately unexpected Pygame entry shaped by task ownership, deadlines, and remote coordination.",
    cover: "/assets/images/p8-cover.png",
    writeup:
      "The team came up with the idea through a discussion about something unexpected. Communication was their biggest challenge because one teammate joined the Discord late and the group was not always online at the same time. They handled this by assigning specific tasks to each member and setting internal deadlines for each milestone. That let them work independently and keep progress moving even without constant real-time coordination.",
    links: [
      {
        label: "Slides PDF",
        href: `${w}/P8 - Most Silly - Bleach Rush/slides/most silly - p8 - Canva/Pygame_P8.pdf`,
      },
      {
        label: "Slides PPTX",
        href: `${w}/P8 - Most Silly - Bleach Rush/slides/most silly - p8 - Canva/Pygame_P8.pptx`,
      },
      {
        label: "Source ZIP",
        href: `${w}/P8 - Most Silly - Bleach Rush/src/most silly - p8 - Drive/buildingblocs-2026-p8.zip`,
      },
    ],
    playNote:
      "This is downloaded Pygame source. A browser build is needed before it can be embedded here.",
  },
  {
    slug: "u13",
    title: "TinyExplorer",
    teamCode: "U13",
    track: "Unity",
    category: "special",
    awards: ["Most Overengineered"],
    team: "Chong Sin Yan, Cheah Kai Qian Lucius, Quick Rui Ern, Khoo Hui Ning",
    summary:
      "A plushie-scale Unity adventure through a giant house, inspired by toys coming to life.",
    cover: "/assets/images/u13-cover.png",
    writeup:
      "Inspired by Toy Story, TinyExplorer puts the player in the perspective of a tiny animated plushie navigating giant furniture and obstacles on the way out of the house. The team faced limited programming experience, code bugs, and availability problems during crucial moments. They learned Unity, GitHub version control, and debugging through repeated testing, online resources, instructor help, and teammate support. The result is a game built around critical thinking, observation, and escape.",
    links: [
      {
        label: "Slides PPTX",
        href: `${w}/U13 - Most Overengineered - TinyExplorer/slides/most overengineered - u13.pptx`,
      },
      {
        label: "Source ZIP",
        href: `${w}/U13 - Most Overengineered - TinyExplorer/src/most overengineered - u13 - GitHub.zip`,
      },
    ],
    playNote:
      "This Unity project needs a WebGL export before it can be played inside the website.",
  },
];

export const rankedGames = games.filter((game) => game.category === "ranked");
export const specialGames = games.filter((game) => game.category === "special");
