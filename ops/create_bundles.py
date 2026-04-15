#!/usr/bin/env python3
"""
Git Bundle Creation - Implementation for M3 Task 3.4

Creates incremental or full git bundles for repository distribution.
"""

import os
import subprocess
import json
import yaml
from pathlib import Path


def run_cmd(cmd, cwd=None, check=True):
    """Run shell command and return output."""
    print(f"  → {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True
    )
    return result


def get_previous_tag(manifest_path, repo_name):
    """Extract the git tag from the previous release manifest."""
    if not manifest_path or not os.path.exists(manifest_path):
        return None

    with open(manifest_path) as f:
        # Support both JSON and YAML manifests
        if manifest_path.endswith('.json'):
            manifest = json.load(f)
        else:
            manifest = yaml.safe_load(f)

    git_refs = manifest.get("git_refs", {})
    previous_tag = git_refs.get(repo_name)

    print(f"  Previous tag for {repo_name}: {previous_tag or 'None (first release)'}")
    return previous_tag


def create_bundle(repo_path, output_path, previous_tag=None, current_tag=None):
    """
    Create git bundle - incremental if possible, full as fallback.

    Returns: tuple (bundle_type, bundle_size)
    """
    repo_path = Path(repo_path).resolve()
    output_path = Path(output_path).resolve()

    print(f"\n📦 Creating bundle for {repo_path.name}")
    print(f"   Output: {output_path}")

    bundle_type = None

    if previous_tag and current_tag:
        # Try incremental first
        try:
            print(f"   Attempting incremental bundle: {previous_tag}..{current_tag}")

            # Include the main branch ref along with the commit range
            result = run_cmd([
                "git", "bundle", "create", str(output_path),
                f"{previous_tag}..{current_tag}",
                "main"
            ], cwd=repo_path)

            # Verify the bundle
            run_cmd(["git", "bundle", "verify", str(output_path)], cwd=repo_path)

            bundle_type = "incremental"
            print(f"   ✅ Incremental bundle created")

        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Incremental bundle failed: {e}")
            print(f"   Falling back to full bundle...")
            previous_tag = None  # Trigger full bundle

    if bundle_type is None:
        # Full bundle (first release or fallback)
        print(f"   Creating full bundle (--all)")

        run_cmd([
            "git", "bundle", "create", str(output_path), "--all"
        ], cwd=repo_path)

        # Verify
        run_cmd(["git", "bundle", "verify", str(output_path)], cwd=repo_path)

        bundle_type = "full"
        print(f"   ✅ Full bundle created")

    # Get bundle size
    bundle_size = os.path.getsize(output_path)
    print(f"   Size: {bundle_size:,} bytes ({bundle_size / 1024 / 1024:.2f} MB)")

    return bundle_type, bundle_size


def tag_release(repo_path, tag):
    """Tag the current HEAD with the release version."""
    repo_path = Path(repo_path).resolve()

    print(f"\n🏷️  Tagging {repo_path.name} as {tag}")

    try:
        # Create annotated tag
        run_cmd([
            "git", "tag", "-a", tag,
            "-m", f"Release {tag}"
        ], cwd=repo_path)

        print(f"   ✅ Tagged successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  Tag already exists or failed: {e}")
        return False


def create_git_bundles(repos, output_dir, previous_manifest=None, current_release_tag=None):
    """
    Create git bundles for all repos.

    Args:
        repos: dict of {repo_name: repo_path}
        output_dir: where to save bundles
        previous_manifest: path to previous manifest.json (optional)
        current_release_tag: tag for current release (e.g., "v2.1.0")

    Returns:
        dict with bundle metadata
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    bundles = {}

    for repo_name, repo_path in repos.items():
        print(f"\n{'='*60}")
        print(f"Processing: {repo_name}")
        print(f"{'='*60}")

        # Get previous tag from manifest (if exists)
        previous_tag = get_previous_tag(previous_manifest, repo_name)

        # Tag current release
        tag_release(repo_path, current_release_tag)

        # Create bundle
        bundle_filename = f"{repo_name}.bundle"
        bundle_path = output_dir / bundle_filename

        bundle_type, bundle_size = create_bundle(
            repo_path=repo_path,
            output_path=bundle_path,
            previous_tag=previous_tag,
            current_tag=current_release_tag
        )

        # Record metadata
        bundles[repo_name] = {
            "type": bundle_type,
            "size": bundle_size,
            "path": str(bundle_path),
            "tag": current_release_tag,
            "from_tag": previous_tag if bundle_type == "incremental" else None
        }

    print(f"\n{'='*60}")
    print(f"✅ Bundle creation complete!")
    print(f"{'='*60}")

    return bundles


if __name__ == "__main__":
    # Test locally
    repos = {
        "mock-app": "../mock-repos/mock-app",
        "mock-data": "../mock-repos/mock-data"
    }

    bundles = create_git_bundles(
        repos=repos,
        output_dir="../releases/v1.0.0/bundles",
        current_release_tag="v1.0.0"
    )

    print("\n📊 Bundle Summary:")
    for repo, info in bundles.items():
        print(f"  {repo}: {info['type']} ({info['size']:,} bytes)")
