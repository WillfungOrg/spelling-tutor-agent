# Webhook Hub Modules

## ⚠️ Module Ownership & Boundaries

This directory contains **ONLY** the core modules required by the webhook hub server at runtime.

### ✅ What BELONGS Here

**Webhook Infrastructure Modules:**
- GitHub API operations (`github.py`)
- Queue management (`state.py`)
- Agent execution (`agent.py`, `agent_sdk.py`)
- Git operations (`git_ops.py`, `worktree_ops.py`)
- Data models (`data_types.py`)
- Utilities (`utils.py`)
- Workflow operations (`workflow_ops.py`)
- Integration modules (`tac_integration.py`, `aea_data_types.py`)

**Characteristics:**
- Stable infrastructure code
- Minimal changes over time  
- Runtime dependencies of webhook server
- No AI/learning logic

### ❌ What DOES NOT Belong Here

**Learning System Modules** → `tac-core-plugin/workflows/adw_modules/`
- `learning_extractor.py`
- `learning_feedback.py`
- `learning_integration.py`
- `learning_query.py`
- `cross_project_learning.py`
- `prompt_refiner.py`
- `manual_session_logger.py`
- `meta_adw_types.py`

**Workflow Logic** → `tac-core-plugin/workflows/`
- `adw_*.py` workflow files
- `decision_engine.py`
- `meta_strategy.py`

**Templates & Commands** → `tac-core-plugin/`
- Slash commands (`commands/`)
- Specification templates (`templates/`)
- Validation checklists (`validation-checklists/`)

## 📊 Current Modules (12)

| Module | Purpose | Used By |
|--------|---------|---------|
| `__init__.py` | Package initialization | All |
| `utils.py` | Utilities (make_adw_id, setup_logger, etc.) | All triggers |
| `github.py` | GitHub API operations | `trigger_webhook.py`, `queue_worker.py` |
| `workflow_ops.py` | Workflow extraction & execution | `trigger_webhook.py` |
| `state.py` | ADWState management | `trigger_webhook.py`, workflows |
| `data_types.py` | Core data models | `state.py`, `workflow_ops.py` |
| `agent.py` | Claude Code agent execution | `workflow_ops.py` |
| `agent_sdk.py` | Agent SDK (used by agent.py) | `agent.py` |
| `worktree_ops.py` | Git worktree management | `workflow_ops.py` |
| `git_ops.py` | Git operations | Various |
| `tac_integration.py` | TAC integration | Workflows |
| `aea_data_types.py` | AEA data types | `adw_trigger_aea_server.py` |

## 🔍 Dependency Chain

**Direct imports by webhook triggers:**
```python
# trigger_webhook.py
from hub_modules.utils import make_adw_id, setup_logger
from hub_modules.github import make_issue_comment
from hub_modules.workflow_ops import extract_adw_info_async
from hub_modules.state import ADWState

# queue_worker.py
from hub_modules.github import make_issue_comment
from hub_modules.utils import make_adw_id, get_safe_subprocess_env
```

**Transitive dependencies:**
- `workflow_ops.py` → `agent.py`, `data_types.py`, `worktree_ops.py`
- `agent.py` → `agent_sdk.py`
- `state.py` → `data_types.py`

## 🚨 Adding New Modules

Before adding a new module to this directory, ask:

1. **Is it required by webhook server at runtime?**
   - Yes → Can add here
   - No → Add to `tac-core-plugin/` instead

2. **Is it learning/AI logic?**
   - Yes → Must go in `tac-core-plugin/workflows/adw_modules/`
   - No → Might belong here

3. **Is it workflow-specific logic?**
   - Yes → Must go in `tac-core-plugin/workflows/`
   - No → Might belong here

4. **Is it stable infrastructure code?**
   - Yes → Belongs here
   - No → Probably belongs in plugin

**When in doubt:** Put it in `tac-core-plugin/` first. It's easier to move stable code here later than to untangle infrastructure from evolving AI logic.

## 📝 Architecture Principle

**Separation of Concerns:**
- **webhook-hub/hub_modules/** = Stable webhook infrastructure
- **tac-core-plugin/** = Evolving AI workflows, learning, commands

**Single Source of Truth:**
- Webhook hub copies plugin to target repos
- Target repos run workflows from their local plugin copy
- Learning happens in target repos, not in webhook hub

## 🔗 See Also

- `webhook-hub/triggers/` - Webhook server & queue worker
- `tac-core-plugin/workflows/` - Workflow implementations
- `tac-core-plugin/workflows/adw_modules/` - Learning system modules
- `CLAUDE.md` - Full project documentation
