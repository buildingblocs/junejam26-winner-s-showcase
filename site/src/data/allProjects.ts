// All other June Jam 2026 entries (everything that isn't in the playable
// showcase in games.ts). This powers the lower half of the /all-projects page:
// a directory of every team with their slides and source/download links.
//
// The 12 showcased award winners are NOT repeated here — the page pulls those
// from games.ts and renders them at the top with their award tags.

export type DirectoryEntry = {
  id: string;            // unique key (team codes can repeat, e.g. U15)
  code: string;          // team code badge, exactly as submitted
  track: "Pygame" | "Unity";
  title: string;         // game name where one was given, else "" (blurb leads)
  team: string;
  blurb: string;         // one-line description drawn from the write-up
  writeup?: string;      // fuller description for the detail page (winner-style)
  slides?: string;       // slides / presentation link
  source?: string;       // source code or download link
  doc?: string;          // separate write-up document, where one was submitted
  playSlug?: string;     // when a browser build exists, its /play/<slug>/ folder
};

// Pygame entries (excluding showcased P1, P6, P8, P14, P15, P17, P26).
const pygame: DirectoryEntry[] = [
  {
    id: "p3",
    code: "P3",
    track: "Pygame",
    title: "Sticking Out",
    team: "Ashton Lim En Xun, Teo Kai Xiang, Oh Yi Chen, Li Wenjie Owen",
    blurb: "A Hollow Knight–inspired street fighter built around a pen weapon.",
    writeup:
      "The team took inspiration from Hollow Knight and a classmate's pen 'gun' to build a fighting game. They originally aimed for a platformer, but their wall-collision code would not come together in time, so they pivoted to a focused street-fighter-style duel. Getting gravity and collisions stable was their hardest problem, and the one place they leaned on AI for help.",
    slides: "https://docs.google.com/presentation/d/1yIwy3addzJ42DcvafPojfsHZIBkzhcZhPlH9ukvY5ao/edit?usp=sharing",
    source: "https://github.com/five8Nf/Sticking-Out",
    playSlug: "p3",
  },
  {
    id: "p4",
    code: "P4",
    track: "Pygame",
    title: "Fractured Light",
    team: "Arffa Ariff, Braden Foo, Tyler Wang, Koay Ger Rome",
    blurb: "Aim lasers through mirrors to trigger sensors.",
    writeup:
      "The idea came from playing with a cat, a laser, and a mirror, which became a puzzle game where you bounce lasers off mirrors to trigger sensors. The team split the work evenly to survive the time crunch and watched a lot of tutorials as Python beginners, ironing out a long list of bugs along the way.",
    slides: "https://canva.link/u9ttjtb5jt7zlpn",
    source: "https://drive.google.com/drive/folders/1_KN3epJm67Mj-AFUfUSd1sOjoaTJzYHA?usp=sharing",
  },
  {
    id: "p5",
    code: "P5",
    track: "Pygame",
    title: "Math Garden",
    team: "Harsheet Tummala, Loh An Kai John, Phoebe Ng Xin Yan, Hansini Madhan Raj",
    blurb: "Answer math questions to grow a colourful virtual garden.",
    writeup:
      "Math Garden turns repetitive math practice into a magical garden that grows with every correct answer, aimed at making revision feel rewarding for younger learners. The team's challenge was writing questions that were approachable yet still engaging, and building the buttons, timers, and scoring in Pygame as beginners.",
    slides: "https://canva.link/68152ngqpgta5fh",
    source: "https://drive.google.com/drive/u/1/folders/1NhRVPMhYZxIgCa3sFOi3mLId2-xyjK8D?q=sharedwith:public%20parent:1NhRVPMhYZxIgCa3sFOi3mLId2-xyjK8D",
    playSlug: "p5",
  },
  {
    id: "p9",
    code: "P9",
    track: "Pygame",
    title: "Sock Frenzy",
    team: "Natesh Thejas, Chandrasekaran Raghav, Sudhakar Kavin Amalan, Syed Muhammad Saheer",
    blurb: "A fast, beginner-friendly laundry-sorting mini-game.",
    writeup:
      "Sock Frenzy turns the chore of sorting laundry into a quick, beginner-friendly catching game. After a sudden change of teammates the group re-planned everything, leaning on Pygame's built-in collision handling and Piskel pixel art, and tuning difficulty by adjusting spawn rates.",
    slides: "https://docs.google.com/presentation/d/1OiUvG-CvmmnrxZTHtv7tLvIIsdKRvemvyI7bX5sBXdg/edit?usp=sharing",
    source: "https://drive.google.com/drive/folders/15_J2_XPQpXbcSpnAJdLFJLWVvLg_Mq1W?usp=sharing",
    playSlug: "p9",
  },
  {
    id: "p10",
    code: "P10",
    track: "Pygame",
    title: "Traffic Crosser",
    team: "Lau Zi Yu",
    blurb: "A Crossy Road–style game about the dangers of jaywalking.",
    writeup:
      "Inspired by Crossy Road, Traffic Crosser is an arcade game about the dangers of jaywalking, with unpredictable traffic to dodge. The team balanced fairness against difficulty using traffic lights, spawn timers, and spacing checks, and used interpolation to keep player movement and the camera smooth.",
    slides: "https://1drv.ms/p/c/ca4d6a21190140e7/IQA8kfbA89FVQ671Otv43N5uAUpS4951atgufT6CwgIS0rg?e=CMBA70",
    source: "https://github.com/Eng-Kai-Yang/PyGame_P10",
    playSlug: "p10",
  },
  {
    id: "p12",
    code: "P12",
    track: "Pygame",
    title: "Tabletop Madness",
    team: "Wong Jia Kai, Purin Sadiphan, Wang En Yi, Keren Siaw Yee Lei",
    blurb: "Overcooked-style post-meal cleanup against the clock.",
    writeup:
      "Drawing on Overcooked and the chaos of post-meal cleanup, Tabletop Madness is a time-pressured washing-up game meant to spark gratitude for everyday acts of care. A last-minute team change left them one day to work together, and they fixed a tricky baby-hand grabbing bug by giving it its own move() method in the main loop.",
    slides: "https://canva.link/ztamrdw310wbxhm",
    source: "https://github.com/90winner09-dotcom/Pygame_P12/tree/main",
    playSlug: "p12",
  },
  {
    id: "p13",
    code: "P13",
    track: "Pygame",
    title: "",
    team: "Asked Reno, Lakksh Vishal, Mikhail Bin Yusof, Wilbur Ong",
    blurb: "A world reclaimed by animals and nature once humans are gone.",
    writeup:
      "The team imagined a world without humans, where the animals and nature they displaced reclaim the land and flourish. Coding was a steep learning curve and Blender was a struggle, but resources like BlenderKit helped them bring the idea to life.",
    slides: "https://docs.google.com/presentation/d/1_HY52FX9kMA4PmQtQT-7u81MxvduYLMv/edit?usp=sharing&ouid=110445985428380708878&rtpof=true&sd=true",
  },
  {
    id: "p16",
    code: "P16",
    track: "Pygame",
    title: "School Day Adventure",
    team: "Dhillshan Surendra Kumar, Thaluri Kaushik Reddy, Aditi Athipattu Balaji, Jaris Ahamed",
    blurb: "Math and science quizzes feeding a turn-based combat grid.",
    writeup:
      "School Day Adventure tackles low engagement in revision by wrapping Math and Science quizzes around a turn-based 'Grid Wars' combat engine, with a shop in between. Almost everything (screens, grid coordinate conversion, pathfinding, and timing states) was hand-coded in Pygame; AI was used only to build a clean text-wrapping utility for the question UI.",
    slides: "https://docs.google.com/presentation/d/1C02zTeSt6O4hFY5dY9nfhjVnCH9vqFi_mVLXjto7pzc/edit?usp=sharing",
    source: "https://github.com/superkingdsk-ux/Pygame_P16",
    playSlug: "p16",
  },
  {
    id: "p19",
    code: "P19",
    track: "Pygame",
    title: "",
    team: "Averine Goh Xuan Ying, Tay Yu Zhen, Wang SiQi, Sreeja Sathia Narayanan",
    blurb: "Hunt and defeat stationery monsters loose in your bedroom.",
    writeup:
      "Set in a normal bedroom where everyday stationery turns into monsters, the player hunts and defeats pencils, rulers, erasers and staplers. Tight deadlines forced the team to simplify their battle system and use simple shapes instead of detailed sprites, testing each feature step by step.",
    slides: "https://canva.link/z1yrph23fl5vg7d",
    source: "https://drive.google.com/drive/folders/1SLWxuBHVRm7AuNI32-pzX793uZyBnNx5?usp=sharing",
    playSlug: "p19",
  },
  {
    id: "p20",
    code: "P20",
    track: "Pygame",
    title: "",
    team: "Lee Kah Han",
    blurb: "Shrunk down to collect materials and craft your way out, top-down.",
    writeup:
      "After being shrunk down, the player collects materials and crafts inventions in a top-down world. Originally planned as a small metroidvania, the solo developer cut it to the crafting core when teammates went unreachable, rebuilding the game from scratch on the final day.",
    slides: "https://docs.google.com/presentation/d/1u_TWuNltT0e359ZXWxKnU6uv70OoZQmjyJJczQPybvA/edit",
    source: "https://github.com/leekahhan-del/BuildingBloCS-gamejam-26",
    playSlug: "p20",
  },
  {
    id: "p22",
    code: "P22",
    track: "Pygame",
    title: "Adaptation",
    team: "Momin Khan, Savin Himsara Fernando, Perry, Jullius Lai",
    blurb: "A Blooket-inspired game for learning Python basics.",
    writeup:
      "Inspired by Blooket, Adaptation integrates questions into levelling up and upgrades so players learn Python basics while they play. With only two days and core workshops to attend, the team split the work to finish planning, coding, and slides before the deadline.",
    slides: "https://canva.link/mg6p9cntarwx52w",
    source: "https://github.com/q5hwth/JuneJam-P22",
    playSlug: "p22",
  },
  {
    id: "p23",
    code: "P23",
    track: "Pygame",
    title: "Kavin's Quest",
    team: "Tanmay Sharma, Kavin Sakthivel, Putra Rayyan, Caleb Ling",
    blurb: "A team-built quest with hand-written code and music.",
    writeup:
      "Named after the teammate who powered through its code, Kavin's Quest is a quest game the group built by dividing roles across code, debugging, slides, and music. Debugging and time management were their biggest hurdles, solved by clear roles and steady communication.",
    slides: "https://docs.google.com/presentation/d/1DD9ybYNsmNy1wAdUdknpz5wfZUvYy1X35q5npOoEBfQ/edit",
    source: "https://github.com/kavinsakthivel8661/P23-PYGAME-Project",
    playSlug: "p23",
  },
  {
    id: "p24",
    code: "P24",
    track: "Pygame",
    title: "",
    team: "Diana Tkalich, Annis Guee Ling Xuan, Ng Chyng Yi, Nguyen Ngoc Khanh Duy",
    blurb: "A multi-genre visual novel inspired by Ace Attorney and Papers, Please.",
    writeup:
      "A multi-genre visual novel inspired by Ace Attorney and Papers, Please, drawing on real-world politics and cyber threats where the weapons shift from artillery to computers. With only three days, the team maximised efficiency by delegating to each member's strengths.",
    slides: "https://canva.link/ccfnzcneuiwm5xz",
    source: "https://drive.google.com/drive/folders/1Dq3hu5zoKj41LNhtRxF-YkFW-9RImMcz?usp=sharing",
  },
  {
    id: "p25",
    code: "P25",
    track: "Pygame",
    title: "",
    team: "Li Qiaoling, Wong Jing Xiong, Tham Yuan Jun, Yeow Min Shan",
    blurb: "Keep a blooming, withering flower alive under time pressure.",
    writeup:
      "The team initially chased the CSIT prize before realising none of them knew cybersecurity, then settled on a plant-tending game where a flower blooms and withers under time pressure. Drawing and scaling the flower's many states was a last-day scramble, and adding a single class often broke other game logic.",
    slides: "https://canva.link/prx28c3a8ynum3z",
    source: "https://drive.google.com/drive/folders/1xb51HjC0_TyZ_sKerwYQOZDPEVs4LVUg?usp=sharing",
  },
  {
    id: "p27",
    code: "P27",
    track: "Pygame",
    title: "The Exam",
    team: "Liew Yu Lin, William Zheng Zhi Chen",
    blurb: "Turns the shared experience of exams into a game.",
    writeup:
      "The Exam turns the universally shared experience of sitting an exam into a game. The team considered an ambitious time-travel storyline before scoping it down, and pushed through tight deadlines, limited manpower and skill gaps with open communication and compromise.",
    slides: "https://www.canva.com/design/DAHMPjSh3vw/0KJj6xDkLpoL6OlB-lQ0ag/edit?ui=e30",
    source: "https://drive.google.com/drive/folders/1zTv1i_2Uyf4UfR9yTgjPNsYtvBBXo_jb",
  },
  {
    id: "p28",
    code: "P28",
    track: "Pygame",
    title: "",
    team: "Belicia Koh Xin Yu, Syesha Arora, Mavis Lee Xuan Ying, Radhakrishnan Shriraam",
    blurb: "Bond with an eraser that comes to life over a week.",
    writeup:
      "Bored students fidgeting with stationery inspired a game where an eraser comes to life and bonds with you over a week. As first-time game makers, the team kept the scope tight (one scene, simple sprites) and learned from friends, tutorials, and the workshop sample code through long nights of coding.",
    slides: "https://docs.google.com/presentation/d/1VXXa7BcpAQHdgZ06VM35Bph4w9mhBvB_/edit?usp=sharing&ouid=108415034079040757144&rtpof=true&sd=true",
    source: "https://drive.google.com/drive/folders/1YaoeRkAuDcogX57acRVwB5hqHJ3T77Ky?usp=sharing",
  },
  {
    id: "p29",
    code: "P29",
    track: "Pygame",
    title: "Ninten's Grand Adventure",
    team: "Syed Muhammad Ammad, Muhammad Zayd Mohaideen, Adam Umar Farooq Bin Mohamed Irshad, Syed Nauman",
    blurb: "A Mario-inspired platformer with a boss fight.",
    writeup:
      "A Mario-inspired platformer born from the team's love of Nintendo, complete with a boss that attacks at randomised intervals. They wrestled with background colours, swapping character images, and boss movement, tweaking the code repeatedly until it behaved.",
    slides: "https://docs.google.com/presentation/d/1dM4M1ckJARxakXu1xfqArjZptKXbFD5JbpcgE30h_lc/edit?usp=sharing",
    source: "https://github.com/syedammad22011-cloud/Ninten-s-grand-Adventure",
    playSlug: "p29",
  },
  {
    id: "p31",
    code: "P31",
    track: "Pygame",
    title: "",
    team: "Elijah Wang Jia Jie, Srikeshav Sriman Kidambi, Amelia Boo Yi Chen, Jessica",
    blurb: "An awareness game about depression, ADHD and self-esteem.",
    writeup:
      "Built to raise awareness of depression and ADHD, the game represents how negative thoughts chip away at self-esteem. Along the way the team solved the everyday frustration of hard-coded positioning by figuring out how to centre elements against Pygame's coordinate system.",
    slides: "https://canva.link/fwqxa809dtzeekf",
    source: "https://drive.google.com/drive/folders/1v5nUatxa_W8ZSBTw9mUrnMD4-QtQGgI5",
  },
  {
    id: "p32",
    code: "P32",
    track: "Pygame",
    title: "",
    team: "Triston Ng Jun Kai, Yap Xin Yi Kim, Lau Yu Kang, Elyssa Koo Hui Minn",
    blurb: "Dodge obstacles to chase down a departing bus.",
    writeup:
      "Many Singaporeans have sprinted for a departing bus, and this game turns that into an obstacle course to the bus stop. The team narrowed ideas against clear criteria, learned physics and gravity from YouTube and Google, and are proud to have built it without AI.",
    slides: "https://www.canva.com/design/DAHMKnHHKpw/CfQN6gRiK7RymcU7EWeW2A/view",
    source: "https://drive.google.com/drive/folders/1TQ3FmtX1QT_tRIkTK2FmZx0MALk-e48Y?usp=drive_link",
  },
  {
    id: "p33",
    code: "P33",
    track: "Pygame",
    title: "FootBottle",
    team: "Jagadev Sivaraj, Arun Roshan, Vijayan Devi Hari",
    blurb: "A two-player bottle-kick soccer game.",
    writeup:
      "FootBottle is a two-player bottle-kick soccer game. The team divided the work across code, error-fixing, slides, and music, motivated by a teammate who pushed through all of the coding.",
    slides: "https://canva.link/51mvoy72hevlofw",
    source: "https://github.com/vdhari-programmer/Pygame_P33",
    doc: "https://docs.google.com/document/d/1u-6Hm-mZFgSKjxYLIsjYEbLW_H5sNGkbODdOT4veHPc/edit?usp=sharing",
    playSlug: "p33",
  },
];

// Unity entries (excluding showcased U2, U4, U8, U13, U16).
const unity: DirectoryEntry[] = [
  {
    id: "u1",
    code: "U1",
    track: "Unity",
    title: "",
    team: "Tung Hong Jiang, Lee Marc Brandon, Lim Bo En Edmund",
    blurb: "A paper character transforms into a ball or plane to platform.",
    writeup:
      "The team picked paper as a household object that could transform, then built a 2D Super Mario-style platformer where a paper character morphs into a ball or plane to clear levels. They handled a non-contributing teammate by re-planning around three people and smoothed out jumping bugs by reading through the code.",
    slides: "https://www.icloud.com/keynote/0115tZWaTGrmW_BQgsFH2-eLg",
    source: "https://github.com/tunghongjiang-sys1/U1-GameJam2026-2026-06-10_10-00-36",
    playSlug: "u1",
  },
  {
    id: "u3",
    code: "U3",
    track: "Unity",
    title: "The Great Sink Escape",
    team: "Kavin Sathia Narayanan, Atharv Pandit, Aaron Tan, Seng Chun Shi",
    blurb: "A bar of soap escapes a sink as the water rises.",
    writeup:
      "The Great Sink Escape casts you as a bar of soap escaping a sink as the water, and the pressure, rises. Unable to collaborate easily in Unity, the team split the work and refined the platform layout through repeated testing and communication.",
    slides: "https://docs.google.com/presentation/d/1-Na0hsQRCeP-WuOojgN2AuKFFm2ec_WcF21qdygooNc/edit?usp=sharing",
    source: "https://drive.google.com/drive/folders/11bZ3LwfWs32gg9A4XQu3IQYl90X_UBEc",
  },
  {
    id: "u5",
    code: "U5",
    track: "Unity",
    title: "",
    team: "Yeo Ern, Lai Jian Zhang, Sam Tu Toan, Lucas Zhang Haoyu",
    blurb: "A roguelike about little creatures fighting each other.",
    writeup:
      "Inspired by a YouTube video about little creatures fighting each other, the team built a roguelike around that core loop.",
    slides: "https://canva.link/k5c1aepcmx8k90f",
  },
  {
    id: "u6",
    code: "U6",
    track: "Unity",
    title: "",
    team: "Kai Thoelke, Goh Rae Pin, Chia Yu Han Sherry, Yu Xuan Ong",
    blurb: "A magic paintbrush restores colour and hidden memories.",
    writeup:
      "Asking what the opposite of a grey, repeating routine looks like, the team landed on colour: a world that lost its colour because people stopped looking closely, restored by a magic paintbrush that reveals the memories hidden inside ordinary things. They tied the message to the mechanic, since painting an object unlocks one of the player's memories, and added a countdown to give the quiet reflection real stakes.",
    slides: "https://docs.google.com/presentation/d/1a_v-ZHaeqEhLahwTRQUccM5202tEo3fzwn7bsnstfz4/edit?usp=drivesdk",
    source: "https://drive.google.com/file/d/15hNg4ZCGsMx-MLQfz2Br8kf5dFVupUPJ/view?usp=sharing",
    playSlug: "u6",
  },
  {
    id: "u7a",
    code: "U7a",
    track: "Unity",
    title: "",
    team: "Woo You Tong, Aeric Axl Amir",
    blurb: "A block-puzzle RPG where clearing lines battles a boss.",
    writeup:
      "Exhausted and juggling exams, the team started with a casual Block Blast-style puzzle and, in a late-night spark, turned it into a roguelike RPG. A constant boss countdown makes the puzzle feel real-time: place blocks too slowly and the boss attacks, while clearing lines triggers combo counters.",
    slides: "https://docs.google.com/presentation/d/1fZOvBt5fgupj7JSgRxNYY8sx7RktNfh_ipito94A9Bk/edit?usp=sharing",
    source: "https://drive.google.com/drive/folders/1zU1B4Z4PcuRRdtk0ZeVc1emOH8hbWWUt?usp=sharing",
  },
  {
    id: "u7b",
    code: "U7b",
    track: "Unity",
    title: "Day2Day!",
    team: "Ng Chee Yong",
    blurb: "Get characters with different lives ready for the day.",
    writeup:
      "The team set out to question what 'everyday' even means, building a game where you control different characters, each with different circumstances, all working toward the shared goal of getting ready for the day. Facing a large original scope, they downsized, taking assets from itch.io and trimming redundant characters and level size.",
    slides: "https://docs.google.com/presentation/d/1Zk5Jpv2ot5BhM1t5UezZ45-yBvf_WE8_AYGCoPJM_gc/edit?usp=sharing",
    source: "https://drive.google.com/drive/u/0/folders/13yyoIY3Y8Gpatj-H-fEBljwwE8R6FGzk",
    playSlug: "u7b",
  },
  {
    id: "u9",
    code: "U9",
    track: "Unity",
    title: "",
    team: "Asmita Gowri Kallam, Ong Yun Qing, Tan Yi Cong Aidan, Ariel Joshua Lau",
    blurb: "A nostalgic action game set in a school warped by memory.",
    writeup:
      "Reframing a liminal-horror idea into a story about nostalgia, the team set the game in a school warped by the protagonist's memories, asking whether too much nostalgia can do more harm than good. The project was ambitious for three days, so they split into music, art, and coding and pushed to deliver a slower, introspective experience.",
    slides: "https://docs.google.com/presentation/d/1-idy6nY81iDYMu3mUOBw6eGnci0_hq_qd205QuxF8XY/edit?usp=sharing",
    source: "https://drive.google.com/drive/folders/1_k5EM6o0QSCyX-UDBdtgvqhVNMPgH2oN?usp=sharing",
  },
  {
    id: "u10",
    code: "U10",
    track: "Unity",
    title: "Memory Overwrite",
    team: "Lee Ying Xuan, Ashriyah Shahana",
    blurb: "A cybersecurity escape room played from the hacker's seat.",
    writeup:
      "Motivated by the CSIT prize, the team put the player in the hacker's seat of a cybersecurity escape room so they would appreciate how attackers use data, a CTF-like, story-driven experience. Working a four-person job with two people and little Unity or C# experience, they leaned on adaptive systems to cope.",
    slides: "https://docs.google.com/presentation/d/1BhsM7jW08zS-VZ_f3tNe8sKPGrLOfX5flCEdrG3TbeQ/edit?usp=sharing",
    source: "https://github.com/luckynpower/unity-memory0verwrite--u10",
    playSlug: "u10",
  },
  {
    id: "u11",
    code: "U11",
    track: "Unity",
    title: "Cup game",
    team: "Mohamed Areeq Bin Mohamed Ashraf, Poh Jun Zhe Matthew, Emerald Alin Eain, Lu Yanjun",
    blurb: "A Unity game dreamed up over a cup of Milo.",
    writeup:
      "Dreamed up over a cup of Milo, the team built their first Unity game while all of them were still learning C#. They overcame time, skill, and experience gaps by collaborating and each contributing what they could.",
    slides: "https://docs.google.com/presentation/d/12f6U52jRNBCplCPaIN8TL_l_0ZTiZ5BwQMv2lYQFGrE/edit?usp=sharing",
    source: "https://github.com/PohJunZheMatthew/June_Jam_Competition_U11",
    playSlug: "u11",
  },
  {
    id: "u12",
    code: "U12",
    track: "Unity",
    title: "",
    team: "Michael Taw Wee Meng, Janice Lee, Chua Tin Giap (Calvin), Chin Xu Biao",
    blurb: "Horror where you play a house cat that isn't home alone.",
    writeup:
      "A teammate's love of horror led to a game where you play a house cat in a lovely home, only to find it is not alone. New to coding for games, the team learned from any resource they could find to ship a tense experience in just over a day.",
    slides: "https://docs.google.com/presentation/d/1HHLNlj_hII-tlmtBJCKL8jYnG3aOESv3va81B9rMEgE/edit?usp=drive_link",
    source: "https://drive.google.com/drive/folders/1LCd2v9EsipwUKg8GIW-i7bchapwgj5x0?usp=drive_link",
  },
  {
    id: "u14",
    code: "U14",
    track: "Unity",
    title: "Jim",
    team: "Zheng Zixuan, Kate Lin Ker Tang, Chan Zaw Shine",
    blurb: "A Unity entry — see the write-up and slides.",
    writeup:
      "A Unity game that opens on a difficulty-select menu (Easy or Medium) fronted by a character named Jim. See the team's write-up and slides for the full concept.",
    slides: "https://canva.link/4ofb3zngx019zvy",
    source: "https://github.com/Kaloo930/U_14",
    playSlug: "u14",
    doc: "https://docs.google.com/document/d/1Tj0bnPwu3FuUFzSTdO71OWn0ygGoCJt0lqHp3RzXjoc/edit",
  },
  {
    id: "u15-morning",
    code: "U15",
    track: "Unity",
    title: "The Morning Routine",
    team: "Jaclyn Olivia Yip, Mohammad Riyaz, Chan Nyein, Vera Ng",
    blurb: "A Risk of Rain–style roguelike through a haunted house.",
    writeup:
      "Inspired by Risk of Rain, The Morning Routine is a roguelike where everyday household items inherit violent souls and attack the player, who fights back with a pencil and stackable buffs. The team chose to prioritise core mechanics and the map over polish, aiming to deliver a promising, properly-built prototype rather than a pretty but shallow one.",
    slides: "https://canva.link/znev4yx6641mevy",
    source: "https://github.com/ritzmonke/The-Morning-Routine/tree/main",
    playSlug: "u15a",
  },
  {
    id: "u15-cyberbound",
    code: "U15",
    track: "Unity",
    title: "Cyberbound",
    team: "Jaclyn Olivia Yip, Mohammad Riyaz",
    blurb: "A dungeon RPG teaching Python basics and reverse engineering.",
    writeup:
      "Cyberbound turns cybersecurity into a dungeon RPG where you learn Python basics and reverse engineering by exploring areas and solving logic challenges to earn access keys. Late in development much of the code broke, so the developer simplified back to a stable core loop (move, interact, complete challenges) to ship a working prototype.",
    slides: "https://canva.link/7u0cmoh0bc3ae4e",
    source: "https://github.com/royaleleaf/CyberBound",
  },
  {
    id: "u17",
    code: "U17",
    track: "Unity",
    title: "",
    team: "Kingzly Yew Min Jin, Cody Charles Carpenter, Jaron Chew Kai Xin",
    blurb: "A two-player game about avoiding malware, inspired by ROUNDS.",
    writeup:
      "Inspired by ROUNDS, the team set out to teach the public to avoid malware through a two-player, last-one-standing duel with between-round power-ups. Losing a designer and manpower late forced them to make their own graphics and scope down, but they pushed the idea as far as the time allowed.",
    slides: "https://docs.google.com/presentation/d/1mNzcUP3_2env0Blbxy3kG-tW6KZzd3XyK99WzvkcJes/edit?usp=sharing",
    source: "https://drive.google.com/drive/folders/1mfnUEDz1NzfNxdYX4tgZT5KgIbRYZ4Hb?usp=sharing",
  },
  {
    id: "u18",
    code: "U18",
    track: "Unity",
    title: "System Fault",
    team: "Leonard Tan Jun Quan",
    blurb: "A 2D escape room that teaches how an attacker thinks.",
    writeup:
      "Originally a penetration-tester simulator, the solo developer pivoted to a 2D escape room that teaches how an attacker thinks: gather info about a 'box', exploit it, and repeat until you capture the machine. Fresh from Roblox and Godot, he cut features that would not fit 48 hours and focused on scalable systems he could extend later.",
    slides: "https://1drv.ms/p/c/16AB706070C9421F/IQANp3q8YV57Srdb973w4He0AetXjDgGVYKxtTrjMTZ6AhA?e=E7gPeC",
    source: "https://drive.google.com/file/d/1zzug99FBrEFrKe4aZKWIhFak-wCO1bIP/view?usp=sharing",
    playSlug: "u18",
  },
];

export const otherProjects: DirectoryEntry[] = [...pygame, ...unity];
