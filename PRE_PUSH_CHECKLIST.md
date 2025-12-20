# Pre-Push Checklist

Before pushing to GitHub, verify the following:

## ✅ Security Check

```bash
# Verify sensitive files are NOT tracked
git ls-files | grep -E "(token\.json|credentials\.json|\.env)"

# Should return nothing. If files appear, remove them:
git rm --cached token.json credentials.json .env
```

## ✅ Files to Verify

- [ ] `.env` file is NOT committed (should be in .gitignore)
- [ ] `token.json` is NOT committed (should be in .gitignore)
- [ ] `credentials.json` is NOT committed (should be in .gitignore)
- [ ] `credentials_template.json` IS committed (template only, safe)
- [ ] No hardcoded API keys or passwords in code
- [ ] All sensitive data uses environment variables

## ✅ Documentation

- [ ] README.md is up to date
- [ ] All documentation files are accurate
- [ ] No references to old/deleted files
- [ ] Setup instructions are clear

## ✅ Code Quality

- [ ] No debug print statements
- [ ] No commented-out code blocks
- [ ] Code is properly formatted
- [ ] Imports are organized

## ✅ Project Structure

- [ ] All files are in appropriate folders
- [ ] No duplicate files
- [ ] Scripts are in `scripts/` folder
- [ ] Documentation is organized

## ✅ Git Status

```bash
# Review what will be committed
git status

# Review changes
git diff --cached

# Verify .gitignore is working
git check-ignore -v token.json credentials.json .env
```

## ✅ Final Steps

1. Review all changes: `git diff`
2. Test locally: `python start.py`
3. Verify no errors in console
4. Commit with clear message
5. Push to GitHub

---

**Remember**: Once sensitive data is pushed to GitHub, it's exposed. Always verify before pushing!

