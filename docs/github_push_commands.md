# GitHub push commands

Run these commands after creating an empty GitHub repository.

```bash
cd /Users/itaehwan/Desktop/ai_rookie_data/campfire-ai-security
git add .
git commit -m "Initial Campfire research package"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

Before pushing, rerun:

```bash
rg -n "hf_[A-Za-z0-9]{20,}|<server-password-fragment>|<server-ip>" .
find . -type f -size +90M -print
```
