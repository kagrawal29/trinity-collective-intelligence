#!/bin/bash

# Trinity LangGraph Integration Setup Script
# This script sets up Trinity in your project with proper directory structure

set -e  # Exit on error

echo "🌟 Trinity LangGraph Integration Setup"
echo "======================================"

# Check if we're in a git repository or project directory
if [ ! -d ".git" ] && [ -z "$(ls -A 2>/dev/null)" ]; then
    echo "⚠️  Warning: Current directory appears empty. Are you in your project root?"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Set variables
TRINITY_BRANCH="trinity-langgraph-integration"
TRINITY_REPO="https://github.com/kagrawal29/trinity-collective-intelligence.git"
TRINITY_DIR="trinity"

# Step 1: Download Trinity
echo "📦 Downloading Trinity..."
if [ -d "$TRINITY_DIR" ]; then
    echo "  ⚠️  Trinity directory already exists. Backing up to trinity.backup..."
    mv "$TRINITY_DIR" "trinity.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Clone the specific branch
git clone -b "$TRINITY_BRANCH" --single-branch "$TRINITY_REPO" "$TRINITY_DIR" 2>/dev/null || {
    echo "  Using fallback download method..."
    curl -L "https://github.com/kagrawal29/trinity-collective-intelligence/archive/refs/heads/${TRINITY_BRANCH}.zip" -o trinity.zip
    unzip -q trinity.zip
    mv "trinity-collective-intelligence-${TRINITY_BRANCH}" "$TRINITY_DIR"
    rm trinity.zip
}

# Step 2: Move Guide's configuration to project root
echo "🔧 Configuring Guide for project root..."

# Move CLAUDE.md to project root (for Guide)
if [ -f "CLAUDE.md" ]; then
    echo "  ⚠️  CLAUDE.md already exists in project root. Backing up..."
    mv "CLAUDE.md" "CLAUDE.md.backup.$(date +%Y%m%d_%H%M%S)"
fi
cp "$TRINITY_DIR/CLAUDE.md" "CLAUDE.md"

# Move .claude/agents to project root (Guide's sub-agents)
if [ -d ".claude/agents" ]; then
    echo "  ⚠️  .claude/agents already exists. Backing up..."
    mv ".claude/agents" ".claude/agents.backup.$(date +%Y%m%d_%H%M%S)"
fi
mkdir -p .claude
cp -r "$TRINITY_DIR/.claude/agents" ".claude/"

# Step 3: Update paths in CLAUDE.md files
echo "📝 Updating agent configurations..."

# Update Guide's CLAUDE.md to reference trinity subdirectory
sed -i.bak 's|/trinity/|/|g' CLAUDE.md
sed -i.bak 's|agents/send_message\.py|trinity/agents/send_message.py|g' CLAUDE.md
sed -i.bak 's|agents/check_messages\.py|trinity/agents/check_messages.py|g' CLAUDE.md
sed -i.bak 's|agents/archive_comm\.py|trinity/agents/archive_comm.py|g' CLAUDE.md
sed -i.bak 's|agents/comm\.json|trinity/agents/comm.json|g' CLAUDE.md
rm CLAUDE.md.bak

# Update Tyler and Dev paths to reference project root
if [ -f "$TRINITY_DIR/agents/e2e-Tester/CLAUDE.md" ]; then
    sed -i.bak 's|"\.\./\.\./|"../../../|g' "$TRINITY_DIR/agents/e2e-Tester/CLAUDE.md"
    rm "$TRINITY_DIR/agents/e2e-Tester/CLAUDE.md.bak"
fi

if [ -f "$TRINITY_DIR/agents/dev/CLAUDE.md" ]; then
    sed -i.bak 's|"\.\./\.\./|"../../../|g' "$TRINITY_DIR/agents/dev/CLAUDE.md"
    rm "$TRINITY_DIR/agents/dev/CLAUDE.md.bak"
fi

# Step 4: Update .gitignore
echo "📄 Updating .gitignore..."
if [ ! -f ".gitignore" ]; then
    touch .gitignore
fi

# Add Trinity dynamic file ignores (but keep Trinity itself in git)
if ! grep -q "trinity/agents/comm.json" .gitignore 2>/dev/null; then
    cat >> .gitignore << 'EOL'

# Trinity Dynamic Files (Trinity itself should be committed)
trinity/agents/comm.json
trinity/agents/comm_backup*.json
trinity/agents/.cycle_*.json
trinity/agents/cycles/
trinity/.cycle_*.json

# Trinity Setup Backups
.claude/agents.backup.*
CLAUDE.md.backup.*
trinity.backup.*
EOL
fi

# Step 5: Initialize git if needed
if [ ! -d ".git" ]; then
    echo "🎯 Initializing git repository..."
    git init
    git add .
    git commit -m "feat: Initialize project with Trinity LangGraph integration"
fi

# Step 6: Create startup script
echo "🚀 Creating startup script..."
cat > start-trinity.sh << 'EOL'
#!/bin/bash

echo "🌟 Starting Trinity Multi-Agent System"
echo "======================================"
echo ""
echo "Open 3 terminals and run:"
echo ""
echo "Terminal 1 - Guide (Project Root):"
echo "  claude"
echo ""
echo "Terminal 2 - Tyler (Chaos Testing):"
echo "  cd trinity/agents/e2e-Tester && claude"
echo ""
echo "Terminal 3 - Dev (Architecture):"
echo "  cd trinity/agents/dev && claude"
echo ""
echo "Then in Guide terminal, start with:"
echo '  "Lets start working on [your task]"'
EOL
chmod +x start-trinity.sh

# Step 7: Final summary
echo ""
echo "✅ Trinity Setup Complete!"
echo "=========================="
echo ""
echo "📁 New Structure:"
echo "  your-project/"
echo "  ├── CLAUDE.md              (Guide runs from here)"
echo "  ├── .claude/agents/        (Guide's sub-agents)"
echo "  └── trinity/"
echo "      └── agents/"
echo "          ├── e2e-Tester/   (Tyler runs from here)"
echo "          └── dev/          (Dev runs from here)"
echo ""
echo "🎯 Next Steps:"
echo "  1. Run: ./start-trinity.sh for instructions"
echo "  2. Open 3 terminals as instructed"
echo "  3. Start your first sprint!"
echo ""
echo "📚 Documentation:"
echo "  - README: trinity/README.md"
echo "  - LangGraph Guide: trinity/LANGGRAPH_INTEGRATION.md"
echo "  - Architecture: trinity/PROJECT_INDEX.md"
echo ""
echo "Happy coding with Trinity! 🚀"