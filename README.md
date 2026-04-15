# Test Git Bundle Workflow

**Purpose:** Mock implementation of the git bundle workflow for BullzAI release packaging (M3 Task 3.4).

**GitHub:** https://github.com/RonnenPodolsky/test-git-bundle

---

## 🎯 What This Tests

This repository demonstrates the **complete git bundle workflow** for shipping code to air-gapped sites:

1. **Full bundles** (first release) - Contains entire git history
2. **Incremental bundles** (subsequent releases) - Only new commits
3. **Bundle compression** - 7z compression with optional split/base64
4. **Tohad workspace simulation** - Clone and merge from bundles
5. **Tohad-specific file preservation** - Verify local files aren't overwritten
6. **Real GitHub integration** - Test with actual GitHub repositories

## 🌐 GitHub Repositories

This workflow uses 4 GitHub repositories:

**Byon (Development) - Source Repos:**
- https://github.com/RonnenPodolsky/mock-app
- https://github.com/RonnenPodolsky/mock-data

**Tohad (Deployment) - Target Repos:**
- https://github.com/RonnenPodolsky/mock-app-tohad
- https://github.com/RonnenPodolsky/mock-data-tohad

---

## 📂 Repository Structure

```
test-git-bundle/
├── ops/
│   ├── create_bundles.py          # Git bundle creation (Step 6 of M3)
│   └── package_archive.py         # Compression + split + base64 (Step 11 of M3)
├── tasks.py                       # Invoke tasks (CLI commands)
├── requirements.txt               # Python dependencies
├── QUICKSTART.md                  # Step-by-step usage guide
├── GITHUB_SETUP.md                # GitHub integration guide (Byon side)
├── TOHAD_UNPACK_INSTRUCTIONS.md   # Tohad deployment guide (Tohad side)
└── README.md                      # This file

Generated during tests:
├── mock-repos/               # Simulated bullzai-app and bullzai-data (pushed to GitHub)
├── releases/                 # Created release packages
│   ├── v1.0.0/              # First release (full bundles)
│   ├── v2.0.0/              # Second release (incremental bundles)
│   └── final/               # Compressed packages for transfer
└── tohad-workspace/         # Simulated Tohad repos (local, pushed to -tohad GitHub repos)
```

---

## 🚀 Quick Start

### For Complete Workflow Guide

📚 **See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)** - Comprehensive end-to-end guide covering:
- Byon side (macOS): Setup → Create release → Transfer
- Tohad side (Windows): Verify → Extract → Deploy
- Incremental updates for both sides
- Troubleshooting and verification

### Option A: Local Testing (Fast)

**For quick local testing without GitHub:**

```bash
source .venv/bin/activate
invoke test-full-workflow
```

This runs all 8 steps locally to verify the bundle mechanism works.

### Option B: GitHub Integration (Real-World)

**For complete real-world testing with GitHub repositories:**

Follow **COMPLETE_GUIDE.md** for step-by-step instructions.

### 3. Inspect Results

```bash
# Compare bundle sizes
ls -lh releases/v1.0.0/bundles/  # Full bundles (~50 KB)
ls -lh releases/v2.0.0/bundles/  # Incremental (~5 KB - 90% smaller!)

# Check manifests
cat releases/v1.0.0/manifest.yaml  # type: "full"
cat releases/v2.0.0/manifest.yaml  # type: "incremental"

# Check release notes
cat releases/v2.0.0/RELEASE_NOTES.md  # Changelog and deployment info

# Verify Tohad workspace
cd tohad-workspace/mock-app
git log --oneline                  # Should see all commits
ls docker/overlays/tohad/          # Should see backend.Dockerfile
```

---

## 📋 Available Commands

Run `invoke --list` to see all commands:

```bash
invoke --list
```

### Core Workflow

| Command | Description |
|---------|-------------|
| `invoke test-full-workflow` | Run complete end-to-end test |
| `invoke setup-mock-repos` | Create simulated repos |
| `invoke create-release --version vX.Y.Z` | Create release package |
| `invoke load-bundles --release vX.Y.Z` | Load bundles at Tohad |
| `invoke clean` | Remove all generated files |

### Development Simulation

| Command | Description |
|---------|-------------|
| `invoke add-commits-to-repo --repo app --message "..."` | Add commits to mock-app |
| `invoke simulate-tohad-customization` | Add Tohad-specific files |

### Advanced Options

```bash
# Create release with split (2GB chunks)
invoke create-release --version v3.0.0 --split

# With base64 encoding
invoke create-release --version v3.0.0 --base64

# Both
invoke create-release --version v3.0.0 --split --base64
```

---

## 🔍 Key Implementation Details

### Incremental Bundle Strategy

**First release:**
```bash
git bundle create bullzai-app.bundle --all
# Size: ~50 MB (entire history)
```

**Subsequent releases:**
```bash
git bundle create bullzai-app.bundle v1.0.0..v2.0.0
# Size: ~5 MB (only new commits - 90% savings!)
```

### Tohad-Specific Files

**The Problem:** Tohad has custom Dockerfiles (`docker/overlays/tohad/`) that don't exist at Byon.

**The Solution:**
- Byon's bundle doesn't include these files (they don't exist)
- Git merge at Tohad preserves local files automatically
- ✅ No risk of overwriting!

**Proof:**
```bash
invoke test-full-workflow
# Watch for: "✅ Tohad file preserved: docker/overlays/tohad/backend.Dockerfile"
```

### Compression & Splitting

**7z compression:**
```bash
7z a -t7z -mx=9 package.7z releases/v1.0.0/
# Creates: package.7z (~40% size reduction)
```

**Split for FAT32 USB:**
```bash
split -b 2000m package.7z package.7z.part
# Creates: package.7z.partaa, package.7z.partab, ...
```

**Base64 for email/security:**
```bash
base64 package.7z > package.7z.b64
# Creates: base64-encoded file (+33% overhead but passes scanners)
```

---

## 📊 Expected Results

### Bundle Size Comparison

| Release | Bundle Type | Size | Savings |
|---------|-------------|------|---------|
| v1.0.0 | Full | ~50 KB | Baseline |
| v2.0.0 | Incremental | ~5 KB | 90% smaller! |

*(Actual sizes depend on mock repo commits)*

### Manifest Comparison

**v1.0.0/manifest.yaml:**
```yaml
version: v1.0.0
git_refs:
  mock-app: v1.0.0
  mock-data: v1.0.0
bundles:
  mock-app:
    type: full
    size: 51234
    from_tag: null
  mock-data:
    type: full
    size: 48567
    from_tag: null
```

**v2.0.0/manifest.yaml:**
```yaml
version: v2.0.0
git_refs:
  mock-app: v2.0.0
  mock-data: v2.0.0
bundles:
  mock-app:
    type: incremental
    size: 5123
    from_tag: v1.0.0
  mock-data:
    type: incremental
    size: 4897
    from_tag: v1.0.0
```

---

## 🧪 Testing Checklist

After running `invoke test-full-workflow`, verify:

- [ ] Mock repos created (`mock-repos/mock-app/` and `mock-repos/mock-data/`)
- [ ] v1.0.0 bundles are type "full" (check manifest.json)
- [ ] v2.0.0 bundles are type "incremental" (check manifest.json)
- [ ] v2.0.0 bundles are smaller than v1.0.0 (check file sizes)
- [ ] Tohad workspace cloned successfully
- [ ] Tohad-specific file exists: `tohad-workspace/mock-app/docker/overlays/tohad/backend.Dockerfile`
- [ ] All commits from both releases are in Tohad workspace (`git log`)
- [ ] Compressed packages created in `releases/final/`

---

## 🔄 Integration Path

This is a **proof of concept**. To integrate into real BullzAI workflow:

### Step 1: Copy to bullzai-ops

```bash
cp ops/create_bundles.py ~/bullzai-ops/ops/airgap/
cp ops/package_archive.py ~/bullzai-ops/ops/airgap/
```

### Step 2: Update tasks.py

Add to `bullzai-ops/tasks.py`:
```python
from ops.airgap.create_bundles import create_git_bundles
from ops.airgap.package_archive import package_archive

@task
def create_release_package(c, site, release, previous_manifest=None):
    # Use create_git_bundles() and package_archive()
    ...
```

### Step 3: Test with Real Repos

```python
repos = {
    "bullzai-app": "/path/to/bullzai-app",
    "bullzai-data": "/path/to/bullzai-data"
}

bundles = create_git_bundles(
    repos=repos,
    output_dir="releases/v2026.05.01/bundles",
    previous_manifest="releases/v2026.04.01/manifest.json",
    current_release_tag="v2.1.0"
)
```

---

## 📚 References

- **Research Doc:** `.claude/work/m3-task-3.4-git-bundles-research.md` (in bullzai-ops)
- **M3 Overview:** `.claude/work/m3-overview-hld.md` (in bullzai-ops)
- **Design Plan v6:** `.claude/work/draft-design-plan-v6.md` (in bullzai-ops)
- **Quickstart:** `QUICKSTART.md` (this repo)

---

## 🎓 What You Learned

1. **Full vs Incremental Bundles**
   - Full: Entire git history (~50 MB)
   - Incremental: Only new commits (~5 MB, 90% savings!)

2. **Tohad File Preservation**
   - Files that don't exist at Byon are preserved at Tohad
   - Git merge handles this automatically ✅

3. **Compression Pipeline**
   - 7z compression (40% reduction)
   - Optional split (2GB chunks for FAT32)
   - Optional base64 (for security scanners)

4. **Manifest Structure**
   - Tracks bundle types (full/incremental)
   - Records git tags for next release
   - Enables incremental packaging

---

## 🙏 Credits

Created for **BullzAI M3: Release Packaging** (Task 3.4 - Git Bundle Creation)

**Owner:** Gal
**Date:** 2026-04-12
**Purpose:** Research, implement, and test git bundle workflow before integrating into bullzai-ops

---

**Ready to test?** Run `invoke test-full-workflow` and see the magic! ✨
