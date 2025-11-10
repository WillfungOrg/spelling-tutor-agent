# Plugin vs Skill: Which is Best for TAC/ADW?

**Updated:** 2025-11-05
**Status:** ✅ Claude Code Plugins ARE Available (Public Beta)

---

## 🎉 Good News: Your Plugin Approach Was Correct!

You already have `.claude-plugin/marketplace.json` — you were on the right track!

**The Issue:** Commands need to be in flat structure for Claude to find them.

---

## Understanding the Ecosystem

### **Claude Code Plugins** (Public Beta)

**What they bundle:**
1. ✅ **Slash commands** — Your 27 commands
2. ✅ **Subagents** — Could be your ADW workflows
3. ✅ **MCP servers** — GitHub/webhook integration
4. ✅ **Hooks** — Event-driven customizations

**How to install:**
```bash
# Users install with:
/plugin marketplace add willfung28/agentic-coding-library
/plugin install tac-core
```

**Perfect for:**
- ✅ Complete development workflows
- ✅ Team/community sharing
- ✅ Bundling multiple components
- ✅ Your TAC/ADW system!

---

### **Claude Code Skills**

**What they are:**
- Specialized expertise packages
- Load automatically when needed
- Portable (works in Claude Apps, Code, API)
- Instructions + scripts + resources

**How to use:**
```bash
# Install from marketplace
/plugin marketplace add anthropics/skills
/plugin install skill-name

# Or manually
cp -r skill-folder ~/.claude/skills/
```

**Perfect for:**
- ✅ Domain-specific expertise (Excel formulas, brand guidelines)
- ✅ Reusable across multiple projects
- ✅ Auto-loading based on context
- ❌ NOT for complete SDLC systems

---

## 🎯 Recommendation: Use Plugin (Not Skill)

### Why Plugin is Better for Your Use Case

| Feature | Plugin | Skill | Winner |
|---------|--------|-------|--------|
| Slash commands | ✅ Yes | ⚠️ Can include | **Plugin** |
| Workflows (ADW) | ✅ Subagents | ❌ Limited | **Plugin** |
| GitHub integration | ✅ MCP servers | ❌ Not designed for | **Plugin** |
| Hooks | ✅ Yes | ❌ No | **Plugin** |
| Complete SDLC | ✅ Perfect | ❌ Too narrow | **Plugin** |
| Auto-load | ⚠️ Manual | ✅ Automatic | Skill |
| Marketplace | ✅ Yes | ✅ Yes | Tie |

**Verdict:** **Plugin is perfect for TAC/ADW** ⭐

---

## 🔧 Fixing Your Current Plugin

### Problem: Command Structure

**Current (doesn't work):**
```
tac-core-plugin/
├── commands/
│   ├── core/
│   │   └── begin.md        ❌ Claude can't find
│   ├── planning/
│   │   └── spec.md         ❌ Claude can't find
```

**Solution:**
```
tac-core-plugin/
├── commands/
│   ├── begin.md            ✅ Claude finds this
│   ├── spec.md             ✅ Claude finds this
```

### How to Fix

**Option A: Flatten structure** (Quick fix)
```bash
cd tac-core-plugin/commands/
mv core/* .
mv planning/* .
mv implementation/* .
# ... flatten all subdirectories
rm -rf core planning implementation
```

**Option B: Keep organized + use symlinks**
```bash
# Keep organized structure
tac-core-plugin/
├── src/
│   ├── core/
│   ├── planning/
│   └── implementation/
└── commands/          # Flat directory with symlinks
    ├── begin.md -> ../src/core/begin.md
    ├── spec.md -> ../src/planning/spec.md
```

**Option C: Build script** (Best)
```bash
# Create build script that flattens on publish
./scripts/build-plugin.sh  # Copies from src/ to commands/
```

---

## 📦 Complete Plugin Structure

```
tac-core-plugin/
├── .claude-plugin/
│   └── manifest.json       # Plugin metadata
├── commands/               # ⚠️ MUST BE FLAT
│   ├── begin.md
│   ├── spec.md
│   ├── feature.md
│   └── ... (all 27 commands)
├── subagents/             # ADW workflows as subagents
│   ├── adw_plan_iso.py
│   ├── adw_build_iso.py
│   └── ...
├── mcp/                   # MCP servers
│   └── github-webhook/
│       └── server.py
├── hooks/                 # Event hooks
│   ├── pre_tool_use.py
│   └── post_tool_use.py
├── templates/             # Templates
├── docs/                  # Documentation
└── README.md
```

---

## 🚀 Deployment Strategy: Plugin-First

### **Recommended: Publish as Claude Code Plugin**

**Step 1: Fix Structure**
```bash
# Flatten commands directory
cd tac-core-plugin/
./scripts/flatten-commands.sh
```

**Step 2: Update Manifest**
```json
{
  "name": "tac-core",
  "version": "1.0.0",
  "description": "Complete autonomous SDLC system with ADW workflows",
  "author": "willfung28",
  "components": {
    "commands": true,
    "subagents": true,
    "mcp_servers": true,
    "hooks": true
  }
}
```

**Step 3: Create Marketplace**
```json
// .claude-plugin/marketplace.json
{
  "name": "tac-autonomous-coding",
  "owner": {
    "name": "willfung28",
    "email": "willfung28@gmail.com"
  },
  "plugins": [
    {
      "name": "tac-core",
      "source": "./tac-core-plugin",
      "description": "Autonomous SDLC with ADW workflows, webhooks, and GitHub integration"
    }
  ]
}
```

**Step 4: Users Install**
```bash
# Add your marketplace
/plugin marketplace add willfung28/agentic-coding-library

# Install plugin
/plugin install tac-core

# Use immediately
/begin
```

---

## 🎯 Plugin vs Script vs Submodule

| Approach | Ease | Updates | Distribution | Verdict |
|----------|------|---------|--------------|---------|
| **Plugin** | ⭐⭐⭐⭐⭐ | Auto | Marketplace | ⭐ **BEST** |
| Script | ⭐⭐⭐⭐ | Manual | curl/wget | Good |
| Submodule | ⭐⭐ | Auto | Git | Complex |

**Plugin wins because:**
1. ✅ Native to Claude Code ecosystem
2. ✅ Automatic updates via `/plugin update`
3. ✅ Marketplace discovery
4. ✅ Easy to toggle on/off
5. ✅ Built-in version management

---

## 🛠️ Implementation Checklist

**Phase 1: Fix Plugin Structure** (1-2 hours)
- [ ] Flatten `commands/` directory
- [ ] Update `.claude-plugin/manifest.json`
- [ ] Test locally with `/plugin load ./tac-core-plugin`
- [ ] Verify all commands work

**Phase 2: Package Components** (2-4 hours)
- [ ] Convert ADW workflows to subagents
- [ ] Package webhook as MCP server
- [ ] Update hooks for plugin system
- [ ] Add comprehensive README

**Phase 3: Publish** (1 hour)
- [ ] Push to GitHub
- [ ] Update marketplace.json
- [ ] Write installation docs
- [ ] Announce to community

**Phase 4: Iterate** (Ongoing)
- [ ] Gather user feedback
- [ ] Add telemetry (opt-in)
- [ ] Version updates
- [ ] Build community

---

## 📊 Skills: Optional Add-On

**You could ALSO create skills for:**

1. **TAC Principles Skill**
   - Loads TAC methodology
   - Guides spec-first development
   - Auto-loads when planning features

2. **ADW Workflow Skill**
   - Understands ADW patterns
   - Recommends optimal workflow
   - Auto-loads when processing issues

3. **GitHub Automation Skill**
   - Webhook configuration expertise
   - GitHub API best practices
   - Auto-loads for integration tasks

**But these are supplementary** — Plugin is your main distribution method.

---

## ✅ Final Recommendation

### **Primary: Claude Code Plugin**

Your TAC/ADW system is a **perfect fit for a plugin**:
- Complete SDLC automation
- Multiple components (commands, workflows, webhooks, hooks)
- Designed for Claude Code
- Community/team sharing

### **Steps:**
1. Fix command structure (flatten)
2. Update manifest
3. Test locally
4. Publish to GitHub
5. Users install via `/plugin`

### **Secondary: Installation Script as Fallback**
- For users who prefer manual install
- For customization needs
- For testing before plugin

### **Future: Skills for Specific Expertise**
- Create focused skills for TAC methodology
- Make them work across Claude products
- Complement the main plugin

---

## 🎉 Conclusion

**You were RIGHT to try the plugin approach!** You just need to:
1. Flatten the command structure
2. Update the manifest
3. Publish it

**The plugin ecosystem is PERFECT for your use case.**

Next step: Want me to help fix the tac-core-plugin structure and create the proper manifest? 🚀
