# 🛸 Save the World with Ben 10: Hand-Controlled Alien Defense 🦸‍♂️

**Fight aliens with your bare hands using your webcam!** This gesture-controlled game leverages computer vision to turn your hand movements into actions. No controllers, no keyboards—just **Python, OpenCV, and MediaPipe magic**!

[![GitHub Release](https://img.shields.io/github/v/release/Raghulskr12/Save_the_world_with_ben?include_prereleases&style=for-the-badge)](https://github.com/Raghulskr12/Save_the_world_with_ben/releases)
[![Medium Blog](https://img.shields.io/badge/Read-Blog-FF6F00?style=for-the-badge&logo=medium)](https://medium.com/@kalairaghul70/how-i-built-a-hand-controlled-game-and-survived-the-debugging-chaos-2bff299373e3)

---

## 🚀 DownThe game is packaged as a **standalone .exe file**—no installations or dependencies required!  
🔗 **Download the latest release here:**  
👉 [**Download from GitHub Releases**](https://github.com/Raghulskr12/Save_the_world_with_ben/releases/download/v1.0.0/Save_the_world.zip) 👈

**How to Play:**
1. Download and extract the .zip file from the Releases section.
2. Run `Save_the_world_raghul.exe`.
3. Enable your webcam and follow the on-screen instructions.
4. **Use your hands to fight aliens—become Ben 10!**

---

## 🛠️ Tech Stack

- **Python** 🐍: Core game logic and integration.
- **OpenCV** 👀: Real-time webcam feed processing.
- **MediaPipe** ✋: Hand tracking and gesture recognition.
- **Pygame** 🎮: Game engine for rendering and audio.
- **PyInstaller** 📦: Packaging the game into a standalone .exe.

---

## 🎮 How It Works

1. **Hand Tracking**: MediaPipe detects your hand landmarks via your webcam.
2. **Gesture Recognition**: Custom logic translates hand movements into in-game actions (e.g., punching, blocking).
3. **Alien Combat**: Defend against waves of aliens using timed gestures.
4. **Score System**: Earn points for defeating aliens and unlock power-ups!

---

## 📖 Development Journey

I documented the entire process—**debugging chaos, wins, and lessons learned**—in my Medium blog:  
🔗 [**"How I Built a Hand-Controlled Game and Survived the Debugging Chaos"**](https://medium.com/@kalairaghul70/how-i-built-a-hand-controlled-game-and-survived-the-debugging-chaos-2bff299373e3)

---

## 💻 For Developers: Run the Code

### Prerequisites
- Python 3.8+
- Webcam
- Windows OS (for .exe compatibility)

### Installation
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt
