# Git Bundle Workflow - Complete Guide

**Version:** 1.0 | **Date:** 2026-04-15
**Purpose:** End-to-end git bundle workflow for air-gapped BullzAI deployments

---

## 🎯 Overview

This workflow enables shipping code changes to air-gapped sites (like Tohad) using git bundles with 90%+ size savings on incremental releases.

**Key Features:**
- ✅ Full bundles (first release) + Incremental bundles (updates)
- ✅ M3 compliant: `manifest.yaml` + `RELEASE_NOTES.md` + 7z compression
- ✅ Cross-platform: macOS development → Windows deployment
- ✅ Tohad customization preservation (files that don't exist at Byon are preserved)
- ✅ Real GitHub integration for testing

---

## 📦 What Gets Packaged

```
releases/v1.0.0/
├── bundles/
│   ├── mock-app.bundle       # Git bundle with full/incremental commits
│   └── mock-data.bundle
├── manifest.yaml              # Package metadata (M3 spec)
└── RELEASE_NOTES.md           # Auto-generated changelog

Compressed for transfer:
releases/final/v1.0.0/
├── v1.0.0.7z                  # Compressed package (~40% size reduction)
├── CHECKSUMS.sha256           # REQUIRED for integrity verification
└── RECONSTRUCTION_INSTRUCTIONS.txt
```

---

## 🌐 GitHub Repositories

**Byon (Development - macOS):**
- `RonnenPodolsky/mock-app` - Source application
- `RonnenPodolsky/mock-data` - Source data pipeline

**Tohad (Deployment - Windows):**
- `RonnenPodolsky/mock-app-tohad` - Deployed with Tohad customizations
- `RonnenPodolsky/mock-data-tohad` - Deployed data pipeline

---

## 🚀 Quick Start - Byon Side (macOS)

### Prerequisites
```bash
# Install 7-Zip
brew install p7zip

# Verify installation
7z --help

# Create 4 GitHub repos (see above)
```

### Step 1: Setup and Create First Release

```bash
cd /Users/ronnennpodolsky/Downloads/Dev/Byon/Platform/test-git-bundle

# Activate virtual environment
source .venv/bin/activate

# Clean previous runs
invoke clean

# Create mock repositories
invoke setup-mock-repos

# Push to GitHub
cd mock-repos/mock-app
git remote add origin https://github.com/RonnenPodolsky/mock-app.git
git push -u origin main

cd ../mock-data
git remote add origin https://github.com/RonnenPodolsky/mock-data.git
git push -u origin main

# Create v1.0.0 release on GitHub UI (both repos)
# Then fetch tags locally
cd ../mock-app && git fetch origin --tags
cd ../mock-data && git fetch origin --tags

# Generate v1.0.0 bundle package
cd ../..
invoke create-release --version v1.0.0
```

**Output:**
```
✅ Full bundles created: mock-app (220 KB), mock-data (157 KB)
✅ Compressed: v1.0.0.7z (380 KB)
✅ Files: manifest.yaml, RELEASE_NOTES.md, CHECKSUMS.sha256
```

### Step 2: Transfer to Tohad

```bash
# Copy to transfer location
cp releases/final/v1.0.0/v1.0.0.7z ~/Desktop/tohad-transfer/
cp releases/final/v1.0.0/CHECKSUMS.sha256 ~/Desktop/tohad-transfer/
cp releases/final/v1.0.0/RECONSTRUCTION_INSTRUCTIONS.txt ~/Desktop/tohad-transfer/

# Email or USB transfer to Tohad Windows machine
```

---

## 💻 Tohad Side (Windows)

**📄 For complete step-by-step Tohad deployment instructions, see:**

### [TOHAD_UNPACK_INSTRUCTIONS.md](TOHAD_UNPACK_INSTRUCTIONS.md)

This file is included in every release package and contains:
- Prerequisites (Git for Windows, 7-Zip)
- Mandatory checksum verification
- Package extraction (GUI and CLI)
- Bundle cloning
- GitHub repository setup
- Tohad customization examples
- Incremental update procedures
- Troubleshooting

**Quick summary:**
1. Verify checksums (MANDATORY): `sha256sum -c CHECKSUMS.sha256`
2. Extract: Right-click → 7-Zip → Extract Here
3. Clone bundles to local workspace
4. Push to Tohad GitHub repos
5. Add Tohad-specific customizations
6. For updates: fetch bundle + merge (preserves customizations)

---

## 🔄 Incremental Updates (v2.0.0)

### Byon Side: Create Incremental Release

```bash
cd /Users/ronnennpodolsky/Downloads/Dev/Byon/Platform/test-git-bundle

# Make changes
source .venv/bin/activate
invoke add-commits-to-repo --repo app --message "Add feature X"
invoke add-commits-to-repo --repo data --message "Add gold flow"

# Push changes
cd mock-repos/mock-app && git push origin main
cd ../mock-data && git push origin main

# Create v2.0.0 release on GitHub UI
# Fetch tags
cd ../mock-app && git fetch origin --tags
cd ../mock-data && git fetch origin --tags

# Generate INCREMENTAL bundle
cd ../..
invoke create-release --version v2.0.0 \
  --previous-manifest releases/v1.0.0/manifest.yaml
```

**Output:**
```
✅ Incremental bundles: mock-app (~1 KB), mock-data (~1 KB)
✅ Compressed: v2.0.0.7z (~2 KB)
✅ 99% smaller than v1.0.0! 🎉
```

### Tohad Side: Apply Incremental Update

**See TOHAD_UNPACK_INSTRUCTIONS.md § "Subsequent Releases"** for complete instructions.

**Quick summary:**
1. Verify checksums (MANDATORY)
2. Extract v2.0.0.7z
3. Check manifest shows `type: incremental`
4. Fetch from bundle: `git fetch <bundle> refs/heads/main`
5. Merge: `git merge FETCH_HEAD`
6. Verify Tohad files preserved
7. Push to GitHub

✅ **Key Point:** Git merge automatically preserves Tohad-specific files that don't exist in Byon bundles!

---

## 📊 Expected Results

### Bundle Sizes

| Release | Type | mock-app | mock-data | Total | vs v1.0.0 |
|---------|------|----------|-----------|-------|-----------|
| v1.0.0 | Full | 220 KB | 157 KB | 377 KB | Baseline |
| v2.0.0 | Incremental | ~1 KB | ~1 KB | ~2 KB | **99% smaller** |

### After 7z Compression

| Release | Uncompressed | 7z Compressed | Savings |
|---------|--------------|---------------|---------|
| v1.0.0 | 377 KB | 380 KB | ~0% (bundles pre-compressed) |
| v2.0.0 | ~2 KB | ~2 KB | ~0% (tiny file) |

**Overall: v2.0.0 is 99% smaller than v1.0.0 due to incremental bundles!**

---

## ✅ Verification Checklist

### After v1.0.0 Deployment
- [ ] 4 GitHub repos exist (mock-app, mock-data, mock-app-tohad, mock-data-tohad)
- [ ] Tohad repos have all commits from v1.0.0
- [ ] Tohad-specific file exists: `docker/overlays/tohad/backend.Dockerfile`
- [ ] manifest.yaml shows `type: full`

### After v2.0.0 Update
- [ ] manifest.yaml shows `type: incremental, from_tag: v1.0.0`
- [ ] Bundle size < 5% of v1.0.0
- [ ] Tohad repos have commits from BOTH v1.0.0 and v2.0.0
- [ ] **Tohad customizations PRESERVED** (backend.Dockerfile still exists)
- [ ] No merge conflicts

---

## 🛠️ Available Commands

```bash
# Setup
invoke clean                    # Remove all generated files
invoke setup-mock-repos         # Create fresh mock repos

# Release Creation
invoke create-release --version vX.Y.Z
invoke create-release --version vX.Y.Z --previous-manifest path/to/manifest.yaml

# Development
invoke add-commits-to-repo --repo app --message "Feature X"
invoke add-commits-to-repo --repo data --message "Gold flow"

# Testing
invoke test-full-workflow       # Complete local test (no GitHub)
```

---

## 🔍 Troubleshooting

### Byon Side

**"7z not found"**
```bash
brew install p7zip
```

**"Tag already exists"**
- Expected if re-running create-release
- Tags fetched from GitHub override local tags

### Tohad Side

**"sha256sum: command not found"**
- Use Git Bash (comes with Git for Windows)
- PowerShell alternative in RECONSTRUCTION_INSTRUCTIONS.txt

**"fatal: not a git repository"**
- Ensure you're in the correct directory
- Check path: `/c/Tohad/workspace/mock-app-tohad`

**Tohad file missing after merge**
- This should NEVER happen
- Files that don't exist at Byon are preserved by git merge
- If missing, check `git log --follow docker/overlays/tohad/backend.Dockerfile`

---

## 📝 M3 Compliance

| M3 Requirement | Status | Implementation |
|----------------|--------|----------------|
| `manifest.yaml` | ✅ | YAML format with bundle metadata |
| `RELEASE_NOTES.md` | ✅ | Auto-generated with changelog |
| 7z compression | ✅ | Default with tar.gz fallback |
| Incremental bundles | ✅ | Tag-based (v1.0.0..v2.0.0) |
| Integrity verification | ✅ | CHECKSUMS.sha256 (MANDATORY) |
| Windows compatibility | ✅ | Git Bash + 7-Zip instructions |

---

## 🎯 Key Concepts

### Why Git Bundles?

Git bundles package git history into a single file for offline transfer:
- **Full bundle:** Contains entire git history (first release)
- **Incremental bundle:** Only commits since previous tag (updates)
- **Verified:** `git bundle verify` ensures integrity

### How Tohad Files Stay Safe

Tohad has custom files in `docker/overlays/tohad/` that don't exist at Byon:
1. Byon's bundle doesn't include these files (they don't exist in Byon repo)
2. Git merge at Tohad preserves local files automatically
3. No risk of overwriting Tohad customizations ✅

### Manifest Structure

**v1.0.0 (full):**
```yaml
version: v1.0.0
git_refs:
  mock-app: v1.0.0
  mock-data: v1.0.0
bundles:
  mock-app:
    type: full
    size: 226033
    from_tag: null
```

**v2.0.0 (incremental):**
```yaml
version: v2.0.0
git_refs:
  mock-app: v2.0.0
  mock-data: v2.0.0
bundles:
  mock-app:
    type: incremental
    size: 1117
    from_tag: v1.0.0  # Only commits since v1.0.0
```

---

## 📚 File Reference

**Implementation:**
- `tasks.py` - Invoke commands, manifest/release notes generation
- `ops/create_bundles.py` - Git bundle creation logic
- `ops/package_archive.py` - 7z compression, checksums

**Documentation:**
- `COMPLETE_GUIDE.md` - This file (comprehensive guide)
- `RECONSTRUCTION_INSTRUCTIONS.txt` - Auto-generated extraction guide

---

## 🎓 Success Story

**Real-world test results:**
- ✅ v1.0.0: 377 KB (full bundles)
- ✅ v2.0.0: ~2 KB (incremental bundles)
- ✅ **99% size reduction** for updates
- ✅ Tohad customizations preserved across updates
- ✅ Cross-platform validated (macOS → Windows)
- ✅ M3 specification compliant

**Ready for production BullzAI deployments!**

---

**For questions or issues:** Contact Byon development team

**Last Updated:** 2026-04-15
