# Quick Start Guide

## Setup

### 1. Activate the Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 2. Verify Installation

```bash
invoke --list
```

You should see all available tasks.

---

## Running the Complete Workflow

### Run Everything in One Command

```bash
invoke test-full-workflow
```

This will:
1. Create mock repositories (bullzai-app, bullzai-data)
2. Create first release (v1.0.0 with full bundles)
3. Load at Tohad workspace
4. Add Tohad-specific customizations
5. Add new commits (simulating development)
6. Create second release (v2.0.0 with incremental bundles)
7. Load v2.0.0 at Tohad
8. Verify Tohad files are preserved

---

## Step-by-Step Usage

### Step 1: Setup Mock Repositories

```bash
invoke setup-mock-repos
```

This creates:
- `mock-repos/mock-app/` - Simulated bullzai-app
- `mock-repos/mock-data/` - Simulated bullzai-data

### Step 2: Create First Release (Full Bundles)

```bash
invoke create-release --version v1.0.0
```

Creates:
- `releases/v1.0.0/bundles/` - Git bundles
- `releases/v1.0.0/manifest.json` - Release manifest
- `releases/final/v1.0.0/` - Compressed package

### Step 3: Load at Tohad

```bash
invoke load-bundles --release v1.0.0
```

Clones bundles to `tohad-workspace/`

### Step 4: Add Tohad Customizations

```bash
invoke simulate-tohad-customization
```

Adds `docker/overlays/tohad/backend.Dockerfile` to simulate Tohad-specific files.

### Step 5: Simulate Development

```bash
invoke add-commits-to-repo --repo app --message "Add feature X"
invoke add-commits-to-repo --repo data --message "Add gold flow"
```

### Step 6: Create Second Release (Incremental Bundles)

```bash
invoke create-release --version v2.0.0 --previous-manifest releases/v1.0.0/manifest.json
```

Creates incremental bundles (only new commits since v1.0.0).

### Step 7: Load v2.0.0 at Tohad

```bash
invoke load-bundles --release v2.0.0
```

Fetches and merges new commits. **Tohad-specific files are preserved!**

---

## Advanced Options

### Create Release with Compression Options

```bash
# With split (2GB chunks)
invoke create-release --version v3.0.0 --split

# With base64 encoding
invoke create-release --version v3.0.0 --base64

# Both
invoke create-release --version v3.0.0 --split --base64
```

### Clean Everything

```bash
invoke clean
```

Removes all generated files (mock-repos, releases, tohad-workspace).

---

## What to Inspect

After running the workflow:

### 1. Bundle Sizes

```bash
ls -lh releases/v1.0.0/bundles/
ls -lh releases/v2.0.0/bundles/
```

Compare full bundles (v1.0.0) vs incremental bundles (v2.0.0).

### 2. Manifests

```bash
cat releases/v1.0.0/manifest.json
cat releases/v2.0.0/manifest.json
```

Check bundle types: "full" vs "incremental".

### 3. Tohad Workspace

```bash
cd tohad-workspace/mock-app
git log --oneline
ls docker/overlays/tohad/
```

Verify:
- All commits from both releases are present
- Tohad-specific files still exist

### 4. Compressed Packages

```bash
ls -lh releases/final/v1.0.0/
ls -lh releases/final/v2.0.0/
```

See the final packages ready for USB transfer.

---

## Expected Results

### First Release (v1.0.0)
- **Bundle type:** full
- **Bundle size:** ~10-50 KB (small test repos)
- **Includes:** All git history

### Second Release (v2.0.0)
- **Bundle type:** incremental
- **Bundle size:** ~2-5 KB (only new commits)
- **Includes:** Only commits since v1.0.0

### Tohad Files
- ✅ `docker/overlays/tohad/backend.Dockerfile` preserved after merge
- ✅ All new commits from v2.0.0 applied
- ✅ No conflicts

---

## Troubleshooting

### "invoke: command not found"

Make sure virtual environment is activated:
```bash
source .venv/bin/activate
```

### Git user not configured

If you see git errors about user.name/user.email:
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### Permission denied on scripts

Make Python scripts executable:
```bash
chmod +x ops/*.py
```

---

## Next Steps

Once you understand the workflow:

1. **Integrate into bullzai-ops**
   - Copy `ops/create_bundles.py` to `bullzai-ops/ops/airgap/`
   - Copy `ops/package_archive.py` to `bullzai-ops/ops/airgap/`
   - Add tasks to `bullzai-ops/tasks.py`

2. **Test with real repos**
   - Point to actual bullzai-app and bullzai-data repos
   - Test with real Harbor registry
   - Create actual release packages

3. **Implement M4 (load-package)**
   - Use `load_bundles()` logic as starting point
   - Add image loading, wheels, DuckDB extensions
   - Add updates.yaml merging

---

## References

- Research document: `.claude/work/m3-task-3.4-git-bundles-research.md`
- M3 Overview: `.claude/work/m3-overview-hld.md`
- Design Plan: `bullzai-ops/.claude/work/draft-design-plan-v6.md`
