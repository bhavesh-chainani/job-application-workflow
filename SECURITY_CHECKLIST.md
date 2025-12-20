# Security Checklist for GitHub Push

## ✅ Files Already in .gitignore (Safe to Push)

- ✅ `credentials.json` - Gmail OAuth credentials
- ✅ `token.json` - Gmail OAuth tokens (contains sensitive refresh tokens)
- ✅ `.env` - Environment variables (API keys, database passwords)
- ✅ `*.csv`, `*.xlsx` - Data files
- ✅ `*.log` - Log files
- ✅ `venv/` - Virtual environment
- ✅ `__pycache__/` - Python cache

## ⚠️ CRITICAL: Verify Before Pushing

Before pushing to GitHub, run these commands to ensure sensitive files are NOT tracked:

```bash
# Check if token.json is tracked (should return nothing)
git ls-files | grep -E "(token\.json|credentials\.json|\.env)"

# Check git status to see what will be committed
git status

# If token.json or credentials.json show up, remove them:
git rm --cached token.json
git rm --cached credentials.json
git rm --cached .env
```

## ✅ Safe Files (Can be Committed)

- ✅ `credentials_template.json` - Template only, no real credentials
- ✅ `config.py` - Only reads from environment variables, no hardcoded secrets
- ✅ All `.py` files - No hardcoded API keys or passwords
- ✅ Documentation files (`.md` files)
- ✅ `requirements.txt`
- ✅ `setup_automation.sh`

## 🔒 Security Best Practices

1. **Never commit:**
   - `token.json` (contains OAuth tokens)
   - `credentials.json` (contains OAuth client secrets)
   - `.env` (contains API keys and database passwords)
   - Any files with actual credentials

2. **Always use:**
   - Environment variables for secrets
   - `.gitignore` to exclude sensitive files
   - Template files (like `credentials_template.json`) instead of real credentials

3. **If you accidentally commit sensitive data:**
   ```bash
   # Remove from git tracking (but keep local file)
   git rm --cached token.json
   git rm --cached credentials.json
   git rm --cached .env
   
   # Commit the removal
   git commit -m "Remove sensitive files from tracking"
   
   # If already pushed, you'll need to rewrite history or rotate credentials
   ```

## ✅ Pre-Push Verification

Run this before pushing:

```bash
# 1. Check what will be committed
git status

# 2. Verify sensitive files are ignored
git check-ignore -v token.json credentials.json .env

# 3. Review the diff
git diff --cached

# 4. If everything looks good, push
git push
```




