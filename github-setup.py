#!/usr/bin/env python3
"""GitHub deployment helper for EcoSat Monitor."""

import subprocess
import sys
from pathlib import Path


def run_cmd(cmd: str, description: str = "") -> bool:
    """Run a shell command and print a compact status line."""
    if description:
        print(f"[*] {description}...")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    except Exception as exc:
        print(f"[x] {description or 'Command failed'}: {exc}")
        return False

    if result.returncode == 0:
        print(f"[ok] {description or 'Done'}")
        return True

    print(f"[x] {description or 'Command failed'}")
    if result.stderr:
        print(result.stderr.strip())
    return False


def check_prerequisites() -> bool:
    """Check required local tools."""
    print("\nChecking prerequisites...\n")
    return run_cmd("git --version", "Checking Git")


def setup_git() -> bool:
    """Initialize and commit the repository."""
    print("\nSetting up local Git repository...\n")

    if not Path(".git").exists() and not run_cmd("git init", "Initializing Git"):
        return False

    user_name = subprocess.run(
        "git config user.name",
        shell=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    if not user_name:
        print("\nGit user is not configured.")
        name = input("Enter your name: ").strip()
        email = input("Enter your email: ").strip()
        if not name or not email:
            print("[x] Git name and email are required.")
            return False
        if not run_cmd(f'git config --global user.name "{name}"', "Setting Git name"):
            return False
        if not run_cmd(f'git config --global user.email "{email}"', "Setting Git email"):
            return False

    if not run_cmd("git add .", "Adding files"):
        return False

    status = subprocess.run(
        "git status --short",
        shell=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    if not status:
        print("[ok] No new changes to commit")
        return True

    return run_cmd(
        'git commit -m "Initial commit: EcoSat Monitor"',
        "Creating commit",
    )


def setup_remote() -> bool:
    """Configure GitHub remote and push main branch."""
    print("\nSetting up GitHub remote...\n")

    username = input("GitHub username: ").strip()
    repo = input("Repository name (default: ecosat-monitor): ").strip() or "ecosat-monitor"

    if not username:
        print("[x] GitHub username is required.")
        return False

    remote_url = f"https://github.com/{username}/{repo}.git"
    print(f"\nRemote URL: {remote_url}\n")

    subprocess.run("git remote remove origin", shell=True, capture_output=True)

    if not run_cmd(f'git remote add origin "{remote_url}"', "Adding origin remote"):
        return False

    if not run_cmd("git branch -M main", "Renaming branch to main"):
        return False

    print("\nPushing to GitHub. Git may ask you to authenticate.\n")
    if not run_cmd("git push -u origin main", "Pushing main branch"):
        print("\nPush failed. Make sure the GitHub repository exists and your login is authenticated.")
        return False

    print("\nRepository pushed successfully.")
    print(f"Repository: https://github.com/{username}/{repo}")
    print(f"Pages settings: https://github.com/{username}/{repo}/settings/pages")
    print("Next: deploy backend with RENDER-DEPLOY.md")
    return True


def main() -> int:
    """Run setup."""
    print("=" * 60)
    print("EcoSat Monitor - GitHub Deployment Setup")
    print("=" * 60)

    if not check_prerequisites():
        return 1
    if not setup_git():
        return 1
    if not setup_remote():
        return 1

    print("\nDone. Read GITHUB-DEPLOYMENT.md and RENDER-DEPLOY.md for cloud setup.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        raise SystemExit(1)
