# TAC/ADW System Deployment Options

**Created:** 2025-11-05
**Purpose:** Comprehensive analysis of deployment strategies for bringing the TAC/ADW autonomous coding system to other projects

---

## 🎯 Your Goal

Deploy this system to multiple projects:
- **Components:** Slash commands, ADW workflows, webhook automation, GitHub integration
- **Use Case:** Autonomous SDLC (issue → PR) across all your projects
- **Requirements:** Easy to install, easy to update, works in Claude Code ecosystem

---

## 📊 Deployment Options Comparison

### Option 1: **Smart Installation Script** ⭐ RECOMMENDED

**What it is:** Single command that intelligently copies files and configures the project

```bash
# From any project
curl -sSL https://raw.githubusercontent.com/willfung28/agentic-coding-library/main/install.sh | bash

# Or local
/path/to/agentic-coding-library/install.sh
```

**How it works:**
1. Detects project type (Python, Node.js, etc.)
2. Copies only needed components
3. Sets up `.env` template
4. Configures GitHub webhook
5. Installs dependencies
6. Runs `/begin` to generate project context

**Pros:**
- ✅ One-command installation
- ✅ Smart detection (doesn't copy unnecessary files)
- ✅ Easy to update (re-run script)
- ✅ Works with Claude Code out of box
- ✅ Project-specific customization
- ✅ No git complexity
- ✅ Can version with `--version` flag

**Cons:**
- ❌ Need to re-run for updates (not automatic)
- ❌ Requires network access (for curl version)
- ❌ Each project has independent copy (divergence possible)

**Best for:**
- New projects starting from scratch
- Existing projects needing quick setup
- Teams that want customization per project

**Implementation effort:** 🔨 Medium (2-4 hours to build script)

---

### Option 2: **Git Submodule**

**What it is:** Link to this repo as a submodule, reference files from there

```bash
# Add submodule
cd your-project/
git submodule add https://github.com/willfung28/agentic-coding-library .tac-framework

# Symlink commands
ln -s .tac-framework/.claude/commands .claude/commands
ln -s .tac-framework/adw ./adw
```

**How it works:**
- Project contains link to external repo
- Files stay in sync with framework repo
- Updates via `git submodule update`

**Pros:**
- ✅ Easy updates (`git submodule update`)
- ✅ All projects use same version
- ✅ Changes upstream benefit all projects
- ✅ Small footprint (just references)
- ✅ Version pinning possible

**Cons:**
- ❌ Git submodules are complex (learning curve)
- ❌ Symlinks may not work on all systems (Windows)
- ❌ Can't customize commands per project easily
- ❌ Extra git commands needed
- ❌ Submodule updates can break projects

**Best for:**
- Teams comfortable with git
- Projects that want automatic sync
- When customization isn't needed

**Implementation effort:** 🔨 Low (1 hour to document)

---

### Option 3: **NPM/PyPI Package** 📦

**What it is:** Publish as installable package

```bash
# NPM
npx create-tac-project
# or
npm install -g @willfung28/tac-framework

# PyPI
pip install tac-framework
tac-framework init
```

**How it works:**
- Package contains CLI + template files
- `init` command scaffolds project
- Updates via package manager

**Pros:**
- ✅ Standard installation method
- ✅ Version management (npm/pip)
- ✅ Easy updates (`npm update`)
- ✅ Can add post-install scripts
- ✅ Distribution via package registries
- ✅ Works with existing package.json/requirements.txt

**Cons:**
- ❌ High initial effort (build + publish)
- ❌ Need to maintain in two places (GitHub + registry)
- ❌ Package approval process
- ❌ Still need manual file copying
- ❌ Not native to Claude Code ecosystem

**Best for:**
- Public distribution
- When you want official package
- Teams already using npm/pip

**Implementation effort:** 🔨🔨 High (8-16 hours for proper package)

---

### Option 4: **Claude Code Plugin System** (Your tac-core-plugin attempt)

**What it is:** Structured plugin that Claude Code could theoretically load

**Status:** ❌ **NOT OFFICIALLY SUPPORTED BY CLAUDE CODE**

**Why it didn't work:**
- Claude Code doesn't have plugin API yet
- Reads commands from `.claude/commands/` directly (flat structure)
- Your `tac-core-plugin/` organized commands in subdirectories
- Claude couldn't find them

**Current state:**
```
tac-core-plugin/commands/
├── core/          # Claude can't see these
├── planning/      # Claude can't see these
└── implementation/ # Claude can't see these

Should be:
.claude/commands/
├── begin.md       # Claude sees this
├── spec.md        # Claude sees this
└── implement.md   # Claude sees this
```

**Pros (if it worked):**
- ✅ Clean separation
- ✅ Organized structure
- ✅ Could distribute via marketplace

**Cons:**
- ❌ Claude Code doesn't support this yet
- ❌ 11 MB of unused code
- ❌ No marketplace exists
- ❌ Would need Anthropic to build plugin system

**Best for:**
- **Future** - When Claude Code adds plugin support
- Not viable today

**Recommendation:** ⛔ Don't use (wait for official plugin support)

---

### Option 5: **GitHub Template Repository**

**What it is:** Make this repo a GitHub template, users click "Use this template"

```
1. Go to your repo settings
2. Check "Template repository"
3. Users click "Use this template" button
```

**How it works:**
- Creates new repo with all your files
- User owns the copy
- No link back to original

**Pros:**
- ✅ GitHub-native feature
- ✅ Dead simple (1 click)
- ✅ Full customization per project
- ✅ No git complexity
- ✅ Clean separation

**Cons:**
- ❌ No easy updates (disconnected from source)
- ❌ Only works for NEW projects
- ❌ Can't add to existing project
- ❌ Template bloat (includes everything)
- ❌ Users get ALL files (archive/, logs/, etc.)

**Best for:**
- Starting new projects from scratch
- One-time setup
- When updates aren't important

**Implementation effort:** 🔨 Minimal (5 minutes to enable)

---

### Option 6: **Monorepo with Workspace Sharing**

**What it is:** Put all projects in one monorepo, share framework code

```
monorepo/
├── packages/
│   ├── tac-framework/  # Shared framework
│   ├── project-a/      # Your app 1
│   ├── project-b/      # Your app 2
│   └── project-c/      # Your app 3
└── pnpm-workspace.yaml
```

**How it works:**
- All projects reference shared framework
- Changes to framework affect all projects
- Managed by workspace tool (pnpm, nx, turborepo)

**Pros:**
- ✅ Share code across projects
- ✅ Single source of truth
- ✅ Easy to keep in sync
- ✅ Can have shared CI/CD
- ✅ Cross-project refactoring easy

**Cons:**
- ❌ All projects must be in same repo
- ❌ Not suitable for separate client projects
- ❌ Repo grows large
- ❌ Complex tooling setup
- ❌ Doesn't fit "autonomous per project" model

**Best for:**
- Multiple related projects (microservices)
- Company internal projects
- When you control all codebases

**Implementation effort:** 🔨🔨🔨 Very High (need monorepo setup)

---

### Option 7: **Cookiecutter / Project Template**

**What it is:** Interactive template generator

```bash
pip install cookiecutter
cookiecutter gh:willfung28/agentic-coding-library
```

**How it works:**
- Asks questions about project
- Generates customized scaffolding
- One-time generation

**Pros:**
- ✅ Interactive customization
- ✅ Project-specific setup
- ✅ No git complexity
- ✅ Industry standard tool
- ✅ Can template everything (.env, configs, etc.)

**Cons:**
- ❌ Python dependency
- ❌ No updates after generation
- ❌ Requires cookiecutter.json configuration
- ❌ Only for NEW projects
- ❌ Medium learning curve

**Best for:**
- Creating new projects with customization
- When you need interactive setup
- Python-based projects

**Implementation effort:** 🔨🔨 Medium-High (4-8 hours)

---

## 🏆 Recommended Solution

### **Hybrid Approach: Smart Script + Git Submodule Option**

Combine the best of both worlds:

**1. Primary: Smart Installation Script** (for most users)
```bash
# Easy install
curl -sSL https://raw.githubusercontent.com/willfung28/agentic-coding-library/main/install.sh | bash

# With options
./install.sh --mode=full        # Commands + ADW + Webhooks
./install.sh --mode=commands    # Commands only
./install.sh --mode=update      # Update existing installation
```

**2. Advanced: Git Submodule** (for power users)
```bash
# For users who want automatic updates
./install.sh --mode=submodule
```

**Benefits:**
- ✅ Easy for beginners (script)
- ✅ Flexible for power users (submodule)
- ✅ Both integrate with Claude Code
- ✅ Can update existing projects
- ✅ Minimal maintenance

---

## 🚀 Implementation Roadmap

### Phase 1: Smart Install Script (Week 1)
```bash
# Create install.sh with:
- Detection (Python/Node.js/etc.)
- Mode selection (full/commands/update)
- Webhook setup
- Environment configuration
- Dependency installation
```

### Phase 2: Documentation (Week 1)
- Update README with installation options
- Create video walkthrough
- Write migration guide (existing projects)

### Phase 3: Optional: Package (Month 2)
- If popular, create npm/PyPI package
- Wrapper around install script
- Published to registries

### Phase 4: Future: Plugin (When Available)
- Wait for Claude Code plugin API
- Migrate to official plugin when ready

---

## 📝 Quick Decision Matrix

| Scenario | Best Option |
|----------|-------------|
| New project from scratch | **Smart Script** or GitHub Template |
| Existing project (add TAC) | **Smart Script** |
| Multiple projects, want sync | **Git Submodule** |
| Public distribution | **NPM/PyPI Package** |
| Company internal (monorepo) | **Monorepo** |
| Interactive customization | **Cookiecutter** |
| Just starting out | **Smart Script** (simplest) |

---

## 💡 Why Plugin Approach Failed

Your `tac-core-plugin/` attempt was actually well-designed! The issue:

**Problem:**
```
Claude Code expects:
.claude/commands/begin.md     ✅ Found
.claude/commands/spec.md      ✅ Found

Your plugin had:
tac-core-plugin/commands/core/begin.md     ❌ Not found
tac-core-plugin/commands/planning/spec.md  ❌ Not found
```

**Solution:**
- Claude Code doesn't have plugin system yet
- Commands must be in `.claude/commands/` (flat)
- Your plugin would work IF Claude added plugin support

**Future-proof:**
- Keep plugin structure for documentation
- When Claude adds plugins, you're ready!
- For now, use script to flatten structure on install

---

## ✅ Recommended Action Plan

**This Week:**
1. Create `install.sh` script
2. Test on 2-3 projects
3. Document usage

**Next Week:**
1. Add to README
2. Create quick-start video
3. Share with community

**Month 2 (Optional):**
1. Create npm package if demand exists
2. Add telemetry (opt-in) to see usage
3. Build marketplace (your own)

**Future:**
1. Monitor Claude Code for plugin API
2. Migrate to official plugin when available

---

## 🎓 Key Takeaways

1. **Start simple** - Installation script is most pragmatic
2. **Plugin isn't ready** - Claude Code doesn't support it yet
3. **Updates matter** - Choose approach that allows updates
4. **Customization matters** - Per-project tweaks are common
5. **Distribution** - Script → Package → Plugin (evolution)

---

**Next step:** Create the smart install script! Would you like me to build it?
