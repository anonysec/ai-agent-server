# Push to GitHub using Windows CMD (Command Prompt)

**Repo:** anoneysec/ai-agent-server

**Instructions:**
1. Extract `ai-agent-server.zip`
2. Right-click the extracted folder → **"Open in Terminal"** (or open CMD in that folder)
3. Run the commands below **one by one**

---

## Step 1: Install GitHub CLI (only once)

Download from: https://cli.github.com/

After install, restart CMD and verify:
```cmd
gh --version
```

---

## Step 2: Login to GitHub

```cmd
gh auth login
```

- Select `GitHub.com`
- Select `HTTPS`
- Choose `Login with a web browser`
- Follow the link and code

---

## Step 3: Create Repo & Push (Run these commands)

```cmd
git init
```

```cmd
git add .
```

```cmd
git commit -m "Initial commit - AI Agent Server (full access + auto-start)"
```

```cmd
git branch -M main
```

```cmd
gh repo create anoneysec/ai-agent-server --public --source=. --remote=origin --push
```

---

## Done!

Your repo will be at:  
**https://github.com/anoneysec/ai-agent-server**

---

## After Pushing

Update the install script URLs (they already point to `anoneysec`).

### Test the installer from anywhere:

```bash
curl -fsSL https://raw.githubusercontent.com/anoneysec/ai-agent-server/main/install.sh | bash
```

With custom token:
```bash
curl -fsSL https://raw.githubusercontent.com/anoneysec/ai-agent-server/main/install.sh | bash -s -- 8847
```

---

## Alternative (if repo already exists)

```cmd
git remote add origin https://github.com/anoneysec/ai-agent-server.git
git branch -M main
git push -u origin main
```

