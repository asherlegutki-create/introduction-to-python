# Python Class — GitHub Codespaces Setup Guide

## What is a Codespace?

A Codespace is a full coding environment that runs in your browser. You don't install anything — it works on Chromebooks, Windows, Mac, and Linux. When you open one, it automatically sets up Python and everything you need for class.

---

## Step 1 — Create a Free GitHub Account

1. Go to **github.com** and click **Sign up**
2. Choose a username (keep it professional — you may use this for years)
3. Select the **Free** plan
4. Verify your email address

> ✅ You only do this once. If you already have a GitHub account, skip to Step 2.

---

## Step 2 — Open the Class Repository

1. Your instructor will give you a link to the class GitHub repository
2. Click the link — it will take you to a page that looks like a file browser
3. You're now looking at the class code

---

## Step 3 — Start Your Codespace

1. On the repository page, click the green **`< > Code`** button
2. Click the **Codespaces** tab
3. Click **Create codespace on main**
4. Wait about 60–90 seconds while it sets up (you'll see a loading screen)
5. A full coding environment will open in your browser — this is VS Code

> ⚠️ The first time takes a minute or two. After that, resuming is fast.

---

## Step 4 — Run Your First Program

1. In the file panel on the left, open the `tryme` folder
2. Click on `hello.py`
3. In the top menu, click **Terminal → New Terminal**
4. In the terminal at the bottom, type:

```
python hello.py
```

5. Press **Enter** — you should see output in the terminal

---

## Step 5 — Stop Your Codespace When Done ⚠️

**This is important.** Closing the browser tab does NOT stop your Codespace — it keeps running and uses up your free hours.

**To properly stop it:**

1. Close the editor tab,

**From GitHub:**

1. Go to **github.com/codespaces**
2. Find your running Codespace
3. Click the **`...`** menu next to it
4. Click **Stop codespace**

> ✅ A stopped Codespace saves your work automatically. Next time you open it, everything will be exactly where you left it.

---

## Resuming a Codespace Next Class

You don't create a new one each time — resume the one you already have:

1. Go to **github.com/codespaces**
2. Click on your existing Codespace to reopen it

---

## Free Usage — What You Get

GitHub gives every free account a monthly allowance:

| Resource | Free Monthly Allowance |
|---|---|
| Compute time | 120 core-hours (~60 hrs on a 2-core machine) |
| Storage | 15 GB-months |

For a class meeting a few hours a week, **you will not exceed the free tier.**

To check your usage at any time: **github.com → Settings → Billing**

---

## Quick Troubleshooting

| Problem | Fix |
|---|---|
| Page is loading forever | Refresh the browser tab |
| "You've used all your free hours" | Go to github.com/codespaces and delete old unused codespaces |
| Can't find your files | Check the Explorer panel on the left (click the file icon) |
| Terminal won't open | Top menu → Terminal → New Terminal |
| Changes not saving | Press **Ctrl+S** (or **Cmd+S** on Mac) to save manually |

---

## Tips for Success

- **Save often** — press `Ctrl+S` after every change
- **Don't create multiple Codespaces** — always resume your existing one
- **Delete old Codespaces** you no longer need — they use up your storage allowance even when stopped
- **Ask for help early** — if something looks broken, tell your instructor before class, not during

---

## Saving Your Work to GitHub

Saving a file in VS Code keeps it in your Codespace, but it does **not** send it to GitHub. To permanently back up your work and let your instructor see it, you need to **commit and push**. Do this at the end of every class.

### Using the VS Code Interface (recommended)

1. Click the **Source Control icon** in the left sidebar — it looks like a branch/fork and may show a number badge if you have unsaved changes
2. You'll see a list of files you've changed
3. Click the **`+`** next to each file to stage it (or click `+` next to "Changes" to stage all)
4. Type a short message in the box at the top describing what you did — e.g. `week 1 hello world done`
5. Click the **✓ Commit** button
6. Click **Sync Changes** (or the cloud upload icon) to push to GitHub

> ✅ You'll see "0 changes" in the Source Control panel when everything is pushed successfully.

### Using the Terminal

If you prefer the terminal, type these three commands:

```bash
git add .
git commit -m "describe what you did here"
git push
```

### What a Good Commit Message Looks Like

| ✅ Good | ❌ Not helpful |
|---|---|
| `week 2 loops exercise complete` | `stuff` |
| `fixed infinite loop in exercise 3` | `aaa` |
| `added error handling to calculator` | `idk` |

### Make It a Habit

Before you leave class each day:

1. Save your files — **Ctrl+S**
2. Commit and push — **Source Control → Commit → Sync**

Think of it like handing in your work. If you don't push, your instructor can't see it and you have no backup if something goes wrong with your Codespace.

---

*Questions? Ask your instructor or visit **docs.github.com/codespaces***
