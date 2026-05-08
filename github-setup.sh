#!/bin/bash
# Quick GitHub Setup Script for EcoSat Monitor

set -e

echo "🚀 EcoSat Monitor - GitHub Deployment Setup"
echo "==========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if already a git repository
if [ -d .git ]; then
    echo "✅ Git repository already initialized"
else
    echo "📝 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
fi

# Add all files
echo "📦 Adding files to staging..."
git add .
echo "✅ Files added"

# Check if any changes to commit
if git diff --cached --quiet; then
    echo "⚠️  No changes to commit"
else
    echo "💾 Creating initial commit..."
    git commit -m "Initial commit: EcoSat Monitor - Production Ready"
    echo "✅ Commit created"
fi

# Get GitHub username if not set
if [ -z "$GITHUB_USERNAME" ]; then
    echo ""
    read -p "📌 Enter your GitHub username: " GITHUB_USERNAME
fi

if [ -z "$GITHUB_REPO" ]; then
    GITHUB_REPO="ecosat-monitor"
    read -p "📌 Enter repository name (default: ecosat-monitor): " GITHUB_REPO_INPUT
    [ -n "$GITHUB_REPO_INPUT" ] && GITHUB_REPO="$GITHUB_REPO_INPUT"
fi

# Set remote URL
REMOTE_URL="https://github.com/$GITHUB_USERNAME/$GITHUB_REPO.git"
echo ""
echo "🔗 Setting remote URL: $REMOTE_URL"

# Remove existing remote if it exists
if git remote | grep -q "^origin$"; then
    git remote remove origin
fi

git remote add origin "$REMOTE_URL"
echo "✅ Remote added"

# Create main branch if needed
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    echo "🔄 Renaming branch to main..."
    git branch -M main
    echo "✅ Branch renamed"
fi

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
echo "   Note: This requires your GitHub token or SSH key"
echo "   You may be prompted to authenticate..."
echo ""

git push -u origin main

echo ""
echo "✅ SUCCESS! Repository pushed to GitHub"
echo ""
echo "📍 Repository URL: https://github.com/$GITHUB_USERNAME/$GITHUB_REPO"
echo ""
echo "🚀 Next Steps:"
echo "   1. Go to: https://github.com/$GITHUB_USERNAME/$GITHUB_REPO/settings/pages"
echo "   2. Enable GitHub Pages (deploy from gh-pages branch)"
echo "   3. Deploy backend to Render/Railway:"
echo "      → https://render.com (recommended)"
echo "      → https://railway.app"
echo "      → https://replit.com"
echo ""
echo "📖 Full deployment guide: GITHUB-DEPLOYMENT.md"
echo ""
