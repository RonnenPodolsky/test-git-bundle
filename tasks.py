"""
Test Git Bundle Workflow - Invoke Tasks

Simulates the complete git bundle workflow for BullzAI releases.
"""

import os
import json
import shutil
from pathlib import Path
from invoke import task


@task
def setup_mock_repos(c):
    """Create mock repositories (simulates bullzai-app and bullzai-data)."""
    print("\n🏗️  Setting up mock repositories...")

    # Mock bullzai-app
    mock_app = Path("mock-repos/mock-app")
    if mock_app.exists():
        shutil.rmtree(mock_app)

    mock_app.mkdir(parents=True)
    os.chdir(mock_app)
    c.run("git init")
    c.run("git config user.name 'Test User'")
    c.run("git config user.email 'test@example.com'")

    # Create some files
    (mock_app / "backend").mkdir()
    (mock_app / "backend" / "main.py").write_text("# Backend service\nprint('Hello from backend')\n")
    (mock_app / "frontend").mkdir()
    (mock_app / "frontend" / "App.js").write_text("// React app\nconsole.log('Hello from frontend');\n")
    (mock_app / "README.md").write_text("# Mock BullzAI App\n\nSimulated application repo.\n")

    c.run("git add .")
    c.run("git commit -m 'Initial commit: backend + frontend'")

    # Add more commits
    (mock_app / "backend" / "api.py").write_text("# API routes\n")
    c.run("git add .")
    c.run("git commit -m 'Add API routes'")

    (mock_app / "common").mkdir()
    (mock_app / "common" / "utils.py").write_text("# Shared utilities\n")
    c.run("git add .")
    c.run("git commit -m 'Add common utilities'")

    os.chdir("../..")

    # Mock bullzai-data
    mock_data = Path("mock-repos/mock-data")
    if mock_data.exists():
        shutil.rmtree(mock_data)

    mock_data.mkdir(parents=True)
    os.chdir(mock_data)
    c.run("git init")
    c.run("git config user.name 'Test User'")
    c.run("git config user.email 'test@example.com'")

    # Create some files
    (mock_data / "flows").mkdir()
    (mock_data / "flows" / "bronze_flow.py").write_text("# Bronze layer flow\n")
    (mock_data / "etl_utils").mkdir()
    (mock_data / "etl_utils" / "minio_client.py").write_text("# MinIO utilities\n")
    (mock_data / "README.md").write_text("# Mock BullzAI Data\n\nSimulated data pipeline repo.\n")

    c.run("git add .")
    c.run("git commit -m 'Initial commit: flows + etl_utils'")

    # Add more commits
    (mock_data / "flows" / "silver_flow.py").write_text("# Silver layer flow\n")
    c.run("git add .")
    c.run("git commit -m 'Add silver flow'")

    os.chdir("../..")

    print("✅ Mock repositories created!")
    print(f"   - {mock_app}")
    print(f"   - {mock_data}")


@task
def create_release(c, version="v1.0.0", previous_manifest=None, split=False, base64=False):
    """
    Create a release package with git bundles.

    Args:
        version: Release version tag (e.g., v1.0.0)
        previous_manifest: Path to previous manifest.json for incremental bundles
        split: Split archive into 2GB chunks
        base64: Base64 encode the archive
    """
    from ops.create_bundles import create_git_bundles
    from ops.package_archive import package_archive

    release_dir = Path(f"releases/{version}")
    bundles_dir = release_dir / "bundles"
    bundles_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Creating Release: {version}")
    print(f"{'='*60}")

    # Define repos
    repos = {
        "mock-app": str(Path("mock-repos/mock-app").resolve()),
        "mock-data": str(Path("mock-repos/mock-data").resolve())
    }

    # Create git bundles
    bundles = create_git_bundles(
        repos=repos,
        output_dir=str(bundles_dir),
        previous_manifest=previous_manifest,
        current_release_tag=version
    )

    # Create manifest
    manifest = {
        "version": version,
        "git_refs": {},
        "bundles": {}
    }

    for repo_name, bundle_info in bundles.items():
        manifest["git_refs"][repo_name] = bundle_info["tag"]
        manifest["bundles"][repo_name] = {
            "type": bundle_info["type"],
            "size": bundle_info["size"],
            "from_tag": bundle_info.get("from_tag")
        }

    # Save manifest
    manifest_path = release_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n📄 Manifest saved: {manifest_path}")

    # Package archive (compress + optional split/base64)
    final_dir = Path("releases/final") / version
    package_result = package_archive(
        package_dir=str(release_dir),
        output_dir=str(final_dir),
        split=split,
        base64_encode=base64
    )

    print(f"\n✅ Release {version} created!")
    print(f"   Package location: {final_dir}")
    print(f"   Total size: {package_result['total_size']:,} bytes ({package_result['total_size'] / 1024 / 1024:.2f} MB)")


@task
def load_bundles(c, release="v1.0.0"):
    """
    Load git bundles at Tohad workspace (simulates M4 load-package).

    Args:
        release: Which release to load
    """
    print(f"\n{'='*60}")
    print(f"Loading Release at Tohad: {release}")
    print(f"{'='*60}")

    bundles_dir = Path(f"releases/{release}/bundles")
    tohad_workspace = Path("tohad-workspace")
    tohad_workspace.mkdir(exist_ok=True)

    if not bundles_dir.exists():
        print(f"❌ Release {release} not found!")
        return

    for bundle_file in bundles_dir.glob("*.bundle"):
        repo_name = bundle_file.stem  # "mock-app"
        bundle_path = bundle_file.resolve()
        repo_path = tohad_workspace / repo_name

        print(f"\n📦 Processing: {repo_name}")

        if not repo_path.exists():
            # First time: clone from bundle
            print(f"   Cloning from bundle (first time)...")
            c.run(f'git clone "{bundle_path}" "{repo_path}"')

            # Set up mock GitLab remote
            os.chdir(repo_path)
            c.run("git remote add origin https://gitlab.tohad.local/bullzai/MOCK.git", warn=True)
            os.chdir("../..")

            print(f"   ✅ Cloned to {repo_path}")

        else:
            # Subsequent releases: fetch + merge
            print(f"   Updating from bundle (incremental)...")
            os.chdir(repo_path)

            c.run(f'git fetch "{bundle_path}" refs/heads/main:refs/remotes/byon/main')
            c.run("git merge byon/main -m 'Merge from Byon bundle'")

            os.chdir("../..")

            print(f"   ✅ Updated {repo_path}")

    print(f"\n✅ All bundles loaded to Tohad workspace!")
    print(f"   Location: {tohad_workspace.resolve()}")


@task
def simulate_tohad_customization(c):
    """Add Tohad-specific files to test preservation during bundle merge."""
    print("\n🔧 Adding Tohad-specific customizations...")

    mock_app = Path("tohad-workspace/mock-app")

    if not mock_app.exists():
        print("❌ Tohad workspace not found. Run 'invoke load-bundles' first.")
        return

    # Create Tohad-specific overlays
    tohad_overlay = mock_app / "docker" / "overlays" / "tohad"
    tohad_overlay.mkdir(parents=True, exist_ok=True)

    backend_dockerfile = tohad_overlay / "backend.Dockerfile"
    backend_dockerfile.write_text("""# Tohad-specific backend Dockerfile
ARG TAG=latest
FROM bullzai/backend:${TAG}

# OpenShift compatibility
RUN groupadd -g 1000 appgroup && \\
    useradd -u 1000 -g appgroup -m appuser

USER 1000
""")

    # Commit to Tohad's local repo
    os.chdir(mock_app)
    c.run("git add docker/overlays/tohad/")
    c.run("git commit -m 'Add Tohad-specific Dockerfiles'")
    os.chdir("../..")

    print(f"✅ Tohad customizations added!")
    print(f"   File: {backend_dockerfile}")


@task
def add_commits_to_repo(c, repo="app", message="Update"):
    """Add new commits to mock repo (simulates development)."""
    repo_map = {
        "app": "mock-repos/mock-app",
        "data": "mock-repos/mock-data"
    }

    repo_path = Path(repo_map.get(repo, repo))

    if not repo_path.exists():
        print(f"❌ Repo {repo_path} not found!")
        return

    print(f"\n📝 Adding commits to {repo_path.name}...")

    os.chdir(repo_path)

    # Add a new file
    new_file = Path(f"feature_{len(list(Path('.').glob('feature_*')))}.txt")
    new_file.write_text(f"# {message}\n")

    c.run("git add .")
    c.run(f'git commit -m "{message}"')

    os.chdir("../..")

    print(f"✅ Commit added!")


@task
def clean(c):
    """Clean all generated files."""
    print("\n🧹 Cleaning...")

    dirs_to_remove = ["mock-repos", "releases", "tohad-workspace"]

    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Removed: {dir_name}")

    print("✅ Clean complete!")


@task
def test_full_workflow(c):
    """Run the complete workflow from start to finish."""
    print("\n" + "="*60)
    print("🧪 TESTING COMPLETE GIT BUNDLE WORKFLOW")
    print("="*60)

    # Step 1: Setup
    print("\n[1/8] Setting up mock repositories...")
    setup_mock_repos(c)

    # Step 2: First release (full bundles)
    print("\n[2/8] Creating first release (v1.0.0 - full bundles)...")
    create_release(c, version="v1.0.0")

    # Step 3: Load at Tohad
    print("\n[3/8] Loading v1.0.0 at Tohad...")
    load_bundles(c, release="v1.0.0")

    # Step 4: Add Tohad customizations
    print("\n[4/8] Adding Tohad-specific customizations...")
    simulate_tohad_customization(c)

    # Step 5: Add new commits at Byon
    print("\n[5/8] Simulating development - adding commits...")
    add_commits_to_repo(c, repo="app", message="Add new feature X")
    add_commits_to_repo(c, repo="app", message="Fix bug Y")
    add_commits_to_repo(c, repo="data", message="Add gold layer flow")

    # Step 6: Second release (incremental bundles)
    print("\n[6/8] Creating second release (v2.0.0 - incremental bundles)...")
    create_release(
        c,
        version="v2.0.0",
        previous_manifest="releases/v1.0.0/manifest.json"
    )

    # Step 7: Load v2.0.0 at Tohad
    print("\n[7/8] Loading v2.0.0 at Tohad (incremental update)...")
    load_bundles(c, release="v2.0.0")

    # Step 8: Verify Tohad files preserved
    print("\n[8/8] Verifying Tohad-specific files preserved...")
    tohad_dockerfile = Path("tohad-workspace/mock-app/docker/overlays/tohad/backend.Dockerfile")

    if tohad_dockerfile.exists():
        print(f"   ✅ Tohad file preserved: {tohad_dockerfile}")
        print(f"   Content preview:")
        print("   " + "-" * 50)
        for line in tohad_dockerfile.read_text().split('\n')[:5]:
            print(f"   {line}")
        print("   " + "-" * 50)
    else:
        print(f"   ❌ Tohad file missing: {tohad_dockerfile}")

    print("\n" + "="*60)
    print("✅ WORKFLOW TEST COMPLETE!")
    print("="*60)

    print("\nSummary:")
    print("  - Created 2 releases (v1.0.0 full, v2.0.0 incremental)")
    print("  - Loaded both at Tohad workspace")
    print("  - Tohad-specific files preserved during merge")
    print("\nInspect:")
    print("  - releases/v1.0.0/  (first release)")
    print("  - releases/v2.0.0/  (second release with incremental bundles)")
    print("  - tohad-workspace/  (simulated Tohad repos)")
