# Install mehdiagent from zero (no coding needed)

Takes about 15 minutes the first time. You only do this once.

## What you need

| | Why | Cost |
|---|---|---|
| A **Claude** plan with **Claude Code** | Claude does the editing | your Claude subscription |
| A **Fish Audio** *or* **OpenRouter** account with a few dollars of credit | turns your voice into timed captions | cents per reel |
| A Mac, or a Windows / Linux computer | the dark style looks exactly like Apple's UI on a Mac; both styles work everywhere | — |

---

## Mac

**1. Open Terminal** — press `⌘ + Space`, type `Terminal`, press Enter.

**2. Install Homebrew** (the Mac app store for developer tools) — paste this, press Enter, follow the prompts:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**3. Install the tools** (Python, ffmpeg for video, Node.js for the white style, git):

```bash
brew install python ffmpeg node git
```

**4. Install Claude Code** — follow the official guide at **claude.com/claude-code**, then sign in.

**5. Download mehdiagent and install it:**

```bash
git clone https://github.com/mehdiagentai/mehdiagent_Claude_editing.git ~/mehdiagent && cd ~/mehdiagent && ./install.sh
```

Answer **y** when it asks to install the Python packages.

---

## Windows

The tools run inside **WSL** (a small Linux built into Windows).

**1.** Open **PowerShell as administrator** and run `wsl --install`, then restart your PC.
**2.** Open **Ubuntu** from the Start menu and create a username/password when asked.
**3.** In Ubuntu, install the tools:

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv ffmpeg nodejs npm git
```

**4.** Install Claude Code inside Ubuntu (official guide: **claude.com/claude-code**) and sign in.
**5.** Download mehdiagent and install it:

```bash
git clone https://github.com/mehdiagentai/mehdiagent_Claude_editing.git ~/mehdiagent && cd ~/mehdiagent && ./install.sh
```

Your Windows files are under `/mnt/c/Users/<you>/` inside Ubuntu (e.g. a video in Downloads:
`/mnt/c/Users/<you>/Downloads/video.mp4`).

## Linux

Same as Windows step 3 and 5 (use your distribution's package manager).

---

## First run (everyone)

1. Open Claude Code (type `claude` in the terminal) and type **`/mehdiagent`**.
2. Answer the questions: dark or white style, your language, captions, transcription service, music…
3. It opens a small text file — paste your **Fish Audio** or **OpenRouter** API key there and save.
   **Never paste an API key into the chat.**
   - Fish Audio: fish.audio → sign in → API keys → create.
   - OpenRouter: openrouter.ai/keys → create key (add a few dollars of credit).
4. Send your first video: `Make a reel from ~/Downloads/my-video.mp4`

The first reel takes longer (it downloads its models once). After that, a 35-second reel takes about 10–15 minutes.

## Something's wrong?

Type **doctor** in Claude Code, or run:

```bash
python3 ~/.claude/skills/mehdiagent/scripts/doctor.py
```

It lists what is missing and the exact command to fix it.

## Update

```bash
cd ~/mehdiagent && git pull && ./install.sh
```
