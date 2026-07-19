# How to Use NIA: GUI Automation & Sovereign Commands

---

## 🚀 Getting Started

### Step 1: Launch NIA
Open the application. You will see the **Sovereign Portal** — the glowing 3D orb. Click **[ENTER NIA]** to proceed to the Hub.

### Step 2: The Sovereign Hub
The Hub is your command center:
- **Left (Vision Stream):** Live log of NIA's perception.
- **Center (NIA Presence):** The pulsing node represents NIA's active state.
- **Right (Sovereign Memory):** Memory allocation visualizer.
- **Bottom (Command Bar):** Issue commands or interact via voice.

---

## 🖥️ GUI Automation: How NIA Controls Your Screen

NIA uses a **Pixels-to-Actions** pipeline. It does not rely on APIs from other apps.

```
┌──────────────────────────────────────┐
│   SCREEN CAPTURE (60fps, local)      │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  VISION MODEL (local, ~2GB VRAM)     │
│  Detects: buttons, text, UI elements │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  REASONING ENGINE (NIA Brain)        │
│  Plans: "Click 'File' → 'Save As'"   │
└────────────────┬─────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│  ACTION EXECUTOR                     │
│  Moves cursor, types, clicks         │
└──────────────────────────────────────┘
```

### Example Commands

| Command | What NIA Does |
|---|---|
| "Open my resume in Word and add today's date" | Opens File Explorer, finds resume, opens Word, edits document |
| "Book a meeting for next Monday 3PM" | Opens Calendar app, creates event with details |
| "Summarize this email and reply politely" | Reads email client via screen, drafts reply |
| "Vibe-code a Python script to rename these files" | Writes, tests, and runs the script autonomously |

---

## 🎙️ Voice Commands

1. Say **"NIA"** to wake NIA from ambient listening.
2. Speak your command naturally: *"NIA, download those files and organize them by date."*
3. NIA will confirm the action and execute.

Toggle **Voice Interruption** in the Command Bar to allow NIA to be interrupted mid-task.

---

## ⚙️ Vibe Coding Mode

Enable **Vibe Mode** in the Command Bar (purple `<>` button). In this mode:
- Describe what you want to build in natural language.
- NIA will write, test, and deploy code for you.
- All code changes are shown in the Vision Stream before execution.

---

## 🔒 Safety & Sovereign Mode

- Actions in sensitive apps (banking, admin panels) require a confirmation prompt.
- You can say **"NIA, pause"** at any time to halt execution.
- Full audit logs are available in Settings > Action History.
