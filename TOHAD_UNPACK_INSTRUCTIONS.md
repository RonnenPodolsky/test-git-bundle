# Tohad Environment - Bundle Unpack Instructions

**For Claude Code on Tohad Computer**

This guide provides step-by-step instructions to unpack BullzAI release bundles and deploy to Tohad repositories.

---

## 📋 Prerequisites

**Windows System:**
- Git for Windows installed (includes Git Bash)
- 7-Zip installed (download from https://www.7-zip.org/)
- GitHub access (for pushing to Tohad repos)
- GitHub token or SSH keys configured

**Installation Commands (Windows):**
```powershell
# Install 7-Zip via winget (Windows 10/11)
winget install 7zip.7zip

# Or download from https://www.7-zip.org/download.html
```

**Verify 7-Zip is installed:**
```bash
# In Git Bash or PowerShell
7z --help
```

---

## 🚀 First Release (v1.0.0) - Initial Setup

### Step 1: Locate the Package

You should have received a `.7z` file from USB. Example: `v1.0.0.7z`

**Windows - Using File Explorer:**
1. Insert USB drive
2. Copy `v1.0.0.7z` to `C:\Tohad\Releases\` (or your preferred location)
3. Open Git Bash (right-click in folder → "Git Bash Here")

**Windows - Using Git Bash:**
```bash
# Navigate to where the package was copied
cd /c/Tohad/Releases  # Windows path in Git Bash format
ls -lh v1.0.0.7z
```

### Step 2: Verify Package Integrity (REQUIRED)

**⚠️ IMPORTANT: Do NOT skip this step! Verify checksums before extraction.**

**Using Git Bash:**
```bash
# Verify the package hasn't been corrupted or tampered with
sha256sum -c CHECKSUMS.sha256
```

**Expected output:**
```
v1.0.0.7z: OK
```

**If you see "FAILED":**
- ❌ DO NOT extract the package
- ❌ DO NOT use the corrupted file
- ✅ Contact Byon team for a new package

---

### Step 3: Extract the Package

**Using 7-Zip (Windows):**

**Option A - File Explorer (GUI):**
1. Right-click on `v1.0.0.7z`
2. Choose "7-Zip" → "Extract Here"
3. Open Git Bash in the extracted folder

**Option B - Git Bash (Command Line):**
```bash
# Extract using 7z command
7z x v1.0.0.7z
cd v1.0.0
```

**Verify extraction:**
```bash
ls -la
# Should show: bundles/ manifest.yaml RELEASE_NOTES.md
```

### Step 4: Verify Package Contents

```bash
ls -la
# You should see:
# - bundles/              (git bundle files)
# - manifest.yaml         (release metadata)
# - RELEASE_NOTES.md      (changelog and deployment info)
```

Check the manifest:
```bash
cat manifest.yaml
```

Expected output:
```yaml
version: v1.0.0
git_refs:
  mock-app: v1.0.0
  mock-data: v1.0.0
bundles:
  mock-app:
    type: full
    size: 226809
    from_tag: null
  mock-data:
    type: full
    size: 160361
    from_tag: null
```

Check the release notes:
```bash
cat RELEASE_NOTES.md
# Contains deployment instructions and changelog
```

### Step 5: Create Tohad Workspace

**Windows - Git Bash:**
```bash
# Create a workspace directory for Tohad repos
mkdir -p /c/Tohad/workspace
cd /c/Tohad/workspace
```

**Windows - PowerShell (alternative):**
```powershell
# Create workspace
New-Item -ItemType Directory -Path "C:\Tohad\workspace" -Force
cd C:\Tohad\workspace
```

**For this guide, we'll use Git Bash commands (works on Windows with Git for Windows installed).**

### Step 6: Clone from Bundles

**Clone mock-app:**
```bash
# Windows Git Bash - use Windows-style paths
git clone /c/Tohad/Releases/v1.0.0/bundles/mock-app.bundle mock-app-tohad
cd mock-app-tohad
git log --oneline  # Verify all commits are present
cd ..
```

**Clone mock-data:**
```bash
git clone /c/Tohad/Releases/v1.0.0/bundles/mock-data.bundle mock-data-tohad
cd mock-data-tohad
git log --oneline  # Verify all commits are present
cd ..
```

**Note:** Git Bash on Windows uses Unix-style paths. `C:\Tohad\Releases` becomes `/c/Tohad/Releases`

### Step 7: Push to Tohad GitHub Repositories

**First, create the repositories on GitHub:**
- Go to https://github.com/RonnenPodolsky
- Create new repository: `mock-app-tohad` (public or private)
- Create new repository: `mock-data-tohad` (public or private)
- Do NOT initialize with README, .gitignore, or license

**Push mock-app-tohad:**
```bash
cd /c/Tohad/workspace/mock-app-tohad

# Set the remote to your Tohad repo
git remote remove origin  # Remove bundle origin
git remote add origin https://github.com/RonnenPodolsky/mock-app-tohad.git

# Push everything
git push -u origin main
git push origin --tags
```

**Push mock-data-tohad:**
```bash
cd /c/Tohad/workspace/mock-data-tohad

# Set the remote to your Tohad repo
git remote remove origin
git remote add origin https://github.com/RonnenPodolsky/mock-data-tohad.git

# Push everything
git push -u origin main
git push origin --tags
```

### Step 8: Add Tohad-Specific Customizations

Now add files that exist ONLY at Tohad (to test preservation in future updates):

```bash
cd /c/Tohad/workspace/mock-app-tohad

# Create Tohad-specific overlay directory
mkdir -p docker/overlays/tohad

# Create a Tohad-specific Dockerfile
cat > docker/overlays/tohad/backend.Dockerfile <<'EOF'
# Tohad-specific backend Dockerfile
ARG TAG=latest
FROM bullzai/backend:${TAG}

# OpenShift compatibility: create non-root user
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -m -s /bin/bash appuser

RUN mkdir -p /var/log/bullzai && \
    chown -R 1000:1000 /opt/backend /var/log/bullzai

USER 1000

# Tohad-specific environment
ENV TOHAD_DEPLOYMENT=true
ENV OPENSHIFT_BUILD=true
EOF

# Commit Tohad customizations
git add docker/overlays/tohad/
git commit -m "Add Tohad-specific Dockerfiles for OpenShift compatibility"
git push origin main
```

**✅ First release deployment complete!**

---

## 🔄 Subsequent Releases (v2.0.0+) - Incremental Updates

### Step 1: Locate the New Package

**Windows:**
```bash
# Copy v2.0.0.7z from USB to releases folder
cd /c/Tohad/Releases
ls -lh v2.0.0.7z
```

### Step 2: Extract the Package

**Using 7-Zip:**
```bash
# Extract the new release
7z x v2.0.0.7z
cd v2.0.0
```

### Step 3: Check Manifest (Important!)

```bash
cat manifest.yaml
```

Expected output for incremental:
```yaml
version: v2.0.0
git_refs:
  mock-app: v2.0.0
  mock-data: v2.0.0
bundles:
  mock-app:
    type: incremental
    size: 1117
    from_tag: v1.0.0
  mock-data:
    type: incremental
    size: 816
    from_tag: v1.0.0
```

**Also check the release notes:**
```bash
cat RELEASE_NOTES.md
# Shows what changed since v1.0.0
```

Note: `type: incremental` means this bundle only contains new commits since v1.0.0.

### Step 4: Update Tohad Repositories

**Update mock-app-tohad:**
```bash
cd /c/Tohad/workspace/mock-app-tohad

# Verify you're on main branch
git status

# Fetch new commits from the bundle
git fetch /c/Tohad/Releases/v2.0.0/bundles/mock-app.bundle refs/heads/main

# Merge the updates
git merge FETCH_HEAD -m "Merge v2.0.0 from Byon bundle"

# Verify Tohad-specific files are still there
ls docker/overlays/tohad/backend.Dockerfile
# ✅ File should still exist!

# Check git log
git log --oneline | head -10

# Push to GitHub
git push origin main
git push origin --tags
```

**Update mock-data-tohad:**
```bash
cd /c/Tohad/workspace/mock-data-tohad

# Fetch new commits from the bundle
git fetch /c/Tohad/Releases/v2.0.0/bundles/mock-data.bundle refs/heads/main

# Merge the updates
git merge FETCH_HEAD -m "Merge v2.0.0 from Byon bundle"

# Push to GitHub
git push origin main
git push origin --tags
```

### Step 5: Verify Tohad Customizations Preserved

```bash
cd /c/Tohad/workspace/mock-app-tohad

# Check that Tohad file still exists
cat docker/overlays/tohad/backend.Dockerfile

# It should contain the Tohad-specific content with:
# - OpenShift user setup
# - TOHAD_DEPLOYMENT=true
# - etc.

# If the file is missing or changed, something went wrong!
```

**✅ Incremental update complete!**

---

## 📊 Verification Checklist

After each deployment, verify:

### First Release (v1.0.0)
- [ ] Both bundles cloned successfully
- [ ] Both repos pushed to GitHub (mock-app-tohad, mock-data-tohad)
- [ ] Tohad-specific files created and committed
- [ ] Git log shows all original commits

### Incremental Release (v2.0.0+)
- [ ] Bundle type is "incremental" in manifest.json
- [ ] Bundle size is much smaller than v1.0.0
- [ ] Fetch and merge completed without errors
- [ ] Tohad-specific files still exist (docker/overlays/tohad/)
- [ ] New commits from Byon are present in git log
- [ ] No unexpected merge conflicts

---

## 🚨 Troubleshooting

### Issue: "fatal: not a git repository"

**Solution:**
```bash
# Make sure you're in the correct directory
cd ~/tohad-workspace/mock-app-tohad
git status
```

### Issue: "fatal: refusing to merge unrelated histories"

**Solution:**
This happens if the bundle and local repo don't share history. For incremental bundles, make sure:
1. You have the previous release loaded
2. The bundle's `from_tag` matches your local tag

```bash
# Check local tags
git tag

# Should include v1.0.0 if you're loading v2.0.0
```

### Issue: Merge Conflicts

**Solution:**
If Tohad modified the same files as Byon:
```bash
# View conflicts
git status

# Edit conflicted files manually
vim <conflicted-file>

# Mark as resolved
git add <conflicted-file>

# Complete the merge
git commit -m "Merge v2.0.0 from Byon (resolved conflicts)"
git push origin main
```

### Issue: Tohad Files Missing After Merge

**This should NOT happen!** If it does:
```bash
# Check if file was deleted
git log --follow -- docker/overlays/tohad/backend.Dockerfile

# If deleted, restore it
git checkout HEAD~1 -- docker/overlays/tohad/backend.Dockerfile
git commit -m "Restore Tohad-specific files"
git push origin main
```

---

## 📝 Size Comparison Reference

Expected bundle sizes:

| Release | Type | mock-app | mock-data | Total |
|---------|------|----------|-----------|-------|
| v1.0.0 | Full | ~220 KB | ~160 KB | ~380 KB |
| v2.0.0 | Incremental | ~1 KB | ~1 KB | ~2 KB |

**Savings: ~99% for incremental releases!**

After 7z compression, expect additional ~40% size reduction.

---

## 🎯 Next Steps

After successful deployment:

1. **Test the application** at Tohad with the new code
2. **Report any issues** back to Byon team
3. **Keep the bundle packages** as backup (in case you need to re-deploy)
4. **Document any Tohad-specific changes** you made

---

## 📞 Support

If you encounter issues not covered in this guide:

1. Check git status: `git status`
2. Check git log: `git log --oneline`
3. Check bundle verification: `git bundle verify <bundle-file>`
4. Contact Byon team with error messages

---

**End of Instructions**
