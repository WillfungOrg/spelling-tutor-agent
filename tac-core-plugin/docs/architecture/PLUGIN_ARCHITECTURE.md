# TAC Plugin Architecture: What Goes Where?

**Created:** 2025-11-05
**Purpose:** Define what belongs in the Claude Code plugin vs external infrastructure

---

## 🏗️ System Architecture

Your complete system has **TWO layers**:

```
┌─────────────────────────────────────────────────┐
│  LAYER 1: Claude Code Plugin (tac-core)        │
│  - Slash commands (27)                          │
│  - Subagents (ADW workflows)                    │
│  - Hooks (optional)                             │
│  ✅ Installed via: /plugin install tac-core    │
└─────────────────────────────────────────────────┘
                      ↓ uses
┌─────────────────────────────────────────────────┐
│  LAYER 2: Infrastructure (Webhook Server)       │
│  - FastAPI webhook server                       │
│  - Queue system (SQLite)                        │
│  - Cloudflare tunnel                            │
│  - GitHub webhook integration                   │
│  ✅ Deployed separately (runs 24/7)            │
└─────────────────────────────────────────────────┘
```

---

## 📊 What's in Your OLD Plugin (tac-core-plugin/)

**Status:** Created before webhook/Agent SDK migration

```
tac-core-plugin/
├── commands/              ❌ Nested (needs flattening)
├── workflows/             ⚠️ OLD Agent SDK (needs update)
│   └── adw_triggers/      ⚠️ OLD webhook (outdated)
├── hooks/                 ✅ Good
├── docs/                  ✅ Good
└── templates/             ✅ Good
```

**Missing:**
- ❌ New Agent SDK integration (built today)
- ❌ FastAPI webhook system (built today)
- ❌ Queue management (built today)
- ❌ Cloudflare tunnel setup
- ❌ Updated ADW workflows with new SDK

---

## 📦 What Should Be IN the Plugin

### **1. Slash Commands** ✅
```
.claude/commands/
├── begin.md               # Intelligent router
├── spec.md                # Spec generation
├── feature.md, bug.md     # Planning
├── implement.md           # Implementation
├── test.md, review.md     # Validation
├── commit.md, pull_request.md  # Integration
└── ... (all 27 commands)
```

**Source:** Flatten from `tac-core-plugin/commands/*/`

---

### **2. Subagents (ADW Workflows)** ✅
```
subagents/
├── adw_plan_iso.py        # Planning workflow
├── adw_build_iso.py       # Implementation
├── adw_test_iso.py        # Testing
├── adw_review_iso.py      # Review
├── adw_document_iso.py    # Documentation
├── adw_sdlc_iso.py        # Complete SDLC
└── adw_modules/           # Shared modules
    ├── agent_sdk.py       # NEW SDK (built today)
    ├── workflow_ops.py
    ├── worktree_ops.py
    └── github.py
```

**Source:** Updated `adw/` with new Agent SDK

**Note:** These run ON-DEMAND when user calls `/implement <issue>` or via webhook trigger

---

### **3. Hooks** ✅ (Optional)
```
hooks/
├── pre_tool_use.py        # Before tool execution
├── post_tool_use.py       # After tool execution
└── user_prompt_submit.py  # Before user submits
```

**Source:** `tac-core-plugin/hooks/` (if you want them)

---

### **4. Templates & Docs** ✅
```
templates/                 # Spec templates, etc.
docs/                      # TAC documentation
validation-checklists/     # Validation guides
```

---

### **5. MCP Server Definition** ⚠️ (Optional)

**Option A: Include webhook code in plugin**
```
mcp/webhook-server/
├── server.py              # FastAPI server
├── queue_manager.py
├── queue_worker.py
└── README.md              # Deployment instructions
```

**Option B: Separate repository** (Recommended)
- Keep webhook as separate infrastructure
- Plugin provides SETUP SCRIPT to deploy it
- Users run setup once

---

## 🌐 What Should Be SEPARATE Infrastructure

### **Webhook Server System** (Runs 24/7)

**Why separate:**
- ❌ Not part of Claude Code lifecycle (runs independently)
- ❌ Needs to be accessible 24/7 (even when Claude Code closed)
- ❌ Requires public URL (Cloudflare tunnel)
- ❌ Manages persistent queue (SQLite database)
- ❌ May run on separate machine/server

**Components:**
```
webhook-infrastructure/
├── trigger_webhook.py     # FastAPI server
├── queue_worker.py        # Background processor
├── queue_manager.py       # Queue system
├── webhook_security.py    # HMAC verification
├── start_adw_services.sh  # Startup script
└── .env                   # Environment config
```

**Deployment:** Users run once to set up

---

## 🎯 Recommended Plugin Structure

### **Updated tac-core-plugin/**

```
tac-core-plugin/
├── .claude-plugin/
│   └── manifest.json      # Plugin metadata
│
├── commands/              # ⚠️ FLATTEN (remove subdirs)
│   ├── begin.md
│   ├── spec.md
│   ├── feature.md
│   └── ... (27 commands)
│
├── subagents/            # ADW workflows with NEW SDK
│   ├── adw_plan_iso.py
│   ├── adw_build_iso.py
│   └── ...
│   └── adw_modules/      # NEW Agent SDK
│       ├── agent_sdk.py  # ⚠️ NEW (update from adw/)
│       └── ...
│
├── hooks/                # Optional event hooks
│   └── ...
│
├── templates/            # Spec templates
│   └── ...
│
├── docs/                 # Documentation
│   └── ...
│
├── scripts/              # Setup & utility scripts
│   ├── setup-webhook.sh  # ⚠️ NEW: Setup webhook infra
│   └── flatten-commands.sh
│
└── README.md             # Installation guide
```

---

## 🚀 How Users Install & Use

### **Step 1: Install Plugin**
```bash
/plugin marketplace add willfung28/agentic-coding-library
/plugin install tac-core
```

**This gives them:**
- ✅ All 27 slash commands
- ✅ ADW workflows (subagents)
- ✅ Templates & documentation
- ✅ Setup scripts

### **Step 2: Setup Webhook (Optional)**
```bash
# Run setup script from plugin
~/.claude/plugins/tac-core/scripts/setup-webhook.sh

# Or manual:
cd ~/.claude/plugins/tac-core/webhook-infrastructure
./start_adw_services.sh
```

**This sets up:**
- ✅ Webhook server running on port 8000
- ✅ Queue worker processing tasks
- ✅ Cloudflare tunnel (optional)
- ✅ GitHub webhook configuration

### **Step 3: Use the System**

**Manual workflow:**
```
/begin
/spec
/implement
/test
/review
```

**Automated workflow (if webhook setup):**
```
1. Create GitHub issue with auto-plan label
2. Webhook triggers ADW workflow
3. PR appears automatically
```

---

## 📝 What You Need to Update

### **1. Update tac-core-plugin/** ⚠️ Priority

**Tasks:**
- [ ] Flatten `commands/` directory
- [ ] Copy NEW `adw/adw_modules/agent_sdk.py` to `subagents/adw_modules/`
- [ ] Update all workflows to use new SDK
- [ ] Add `scripts/setup-webhook.sh`
- [ ] Update manifest.json

### **2. Decide: Webhook in Plugin or Separate?**

**Option A: Include in Plugin** (easier for users)
```
tac-core-plugin/
└── webhook-infrastructure/
    ├── trigger_webhook.py
    ├── queue_worker.py
    └── setup.sh
```
**Pros:** Everything in one place
**Cons:** Mixes plugin code with infrastructure

**Option B: Separate Repo** (cleaner)
```
agentic-coding-library/        # Plugin
tac-webhook-infrastructure/    # Separate repo
```
**Pros:** Clear separation
**Cons:** Two repos to maintain

**Recommendation:** **Option A** (include in plugin with clear docs)

---

## 🎯 Final Architecture

```
Plugin Components (installed via /plugin):
├── Commands (slash commands)
├── Subagents (ADW workflows with NEW SDK)
├── Hooks (optional)
├── Templates & Docs
└── Scripts (includes webhook setup)

Infrastructure (optional, user deploys):
├── Webhook Server (FastAPI)
├── Queue System (SQLite)
└── Cloudflare Tunnel
```

**Key principle:** Plugin provides EVERYTHING needed, but webhook is OPTIONAL infrastructure users can deploy.

---

## ✅ Decision Summary

| Component | In Plugin? | Why |
|-----------|-----------|-----|
| Slash commands | ✅ Yes | Core plugin feature |
| ADW workflows | ✅ Yes (as subagents) | Core plugin feature |
| Agent SDK | ✅ Yes | Required by workflows |
| Hooks | ⚠️ Optional | If you want event customization |
| Templates | ✅ Yes | Needed by commands |
| Documentation | ✅ Yes | Users need it |
| Webhook code | ✅ Yes | Include for deployment |
| Webhook running | ❌ No | User deploys separately |
| Cloudflare setup | ❌ No | User infrastructure |

---

## 🚀 Next Steps

1. **Update tac-core-plugin/** with:
   - Flattened commands
   - New Agent SDK
   - Webhook infrastructure code
   - Setup scripts

2. **Test the plugin**:
   ```bash
   /plugin load ./tac-core-plugin
   /begin
   ```

3. **Publish to marketplace**:
   - Push to GitHub
   - Users install via `/plugin`

Want me to help update the plugin structure? 🛠️
