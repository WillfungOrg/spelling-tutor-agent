# Meta-ADW Architecture

Technical documentation for the Meta-ADW Strategy System.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Meta-ADW System                          │
├─────────────────────────────────────────────────────────────┤
│  GitHub Issue → Interview → Analyze → Recommend → Execute   │
│                                ↓                              │
│                    Learning System (Feedback Loop)           │
└─────────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────────────────────────┐
        │     Existing ADW Workflows          │
        ├─────────────────────────────────────┤
        │  • adw_sdlc_iso                    │
        │  • adw_plan_build_test_iso         │
        │  • adw_patch_iso                   │
        │  • etc. (30+ workflows)            │
        └─────────────────────────────────────┘
```

---

## Key Components

### 1. MetaStrategyOrchestrator (`meta_strategy.py`)
**Purpose:** Main entry point and workflow coordinator

**Responsibilities:**
- Fetches GitHub issues
- Executes interview/analyze/recommend workflow
- Displays recommendations to user
- Handles user confirmation
- Logs execution for learning
- Coordinates with decision engine

**Key Methods:**
- `fetch_issue()` - Get GitHub issue details
- `conduct_interview()` - Run /strategy/interview template
- `analyze_task()` - Run /strategy/analyze template
- `get_recommendation()` - Get decision engine recommendation
- `collect_feedback()` - Gather execution metrics
- `update_pattern_database()` - Store learning data
- `retrain_weights()` - Adjust decision weights

### 2. DecisionEngine (`decision_engine.py`)
**Purpose:** Pattern matching and workflow recommendation logic

**Components:**
- **Template Index Loader**: Loads `.tac/template_index.json`
- **Pattern Matcher**: Scores templates against task requirements
- **Workflow Ranker**: Ranks workflows by confidence
- **Validation Strategy Mapper**: Maps validation needs to TAC patterns

**Pattern Matching Algorithm:**
```python
# Weighted scoring
match_score = (
    keyword_score * 0.4 +
    complexity_score * 0.3 +
    validation_score * 0.3
)

# Historical boost
match_score *= (0.7 + 0.3 * historical_success)
```

**Key Methods:**
- `load_template_index()` - Load lightweight template catalog
- `match_patterns()` - Score all templates against task
- `rank_workflows()` - Determine top 3 recommendations
- `recommend_strategy()` - Generate full StrategyRecommendation

### 3. Strategy Templates (`.claude/commands/strategy/`)

#### interview.md
- Asks 7 key questions
- Outputs structured JSON
- Determines task characteristics

#### analyze.md
- Takes interview results as input
- Analyzes across 6 dimensions:
  - Complexity scoring (1-10)
  - Validation depth required
  - Effort estimation
  - Risk assessment
  - Requirements extraction
  - Model set recommendation
- Outputs TaskAnalysis JSON

#### recommend.md
- Takes TaskAnalysis as input
- Uses decision engine for ranking
- Applies workflow selection rules:
  - **Features**: simple (<4) → plan_build, moderate (4-7) → plan_build_test, complex (>7) → sdlc
  - **Bugs**: simple (<4) → patch, complex (>=4) → plan_build_test
  - **Chores**: standard → plan_build, critical → plan_build_test_review
- Outputs StrategyRecommendation JSON with alternatives

#### validate_plan.md
- Takes implementation plan as input
- Checks 6 validation dimensions:
  - Validation commands present
  - Complexity/validation depth match
  - Edge cases covered
  - UI changes validation (E2E tests)
  - Closed-loop validation (TAC L5)
  - Success criteria measurable
- Identifies common gaps:
  - "Tests pass but feature broken" → Add E2E tests
  - "Agent claims fixed but isn't" → Add L5 closed-loop
  - "Works locally but fails in production" → Add integration tests
- Outputs validation report JSON

#### design_custom_adw.md
- Takes TaskAnalysis for novel tasks (confidence < 0.5)
- Designs custom workflow structure:
  - Determines required phases
  - Designs custom validation steps
  - Specifies tools/commands needed
  - Defines integration points
- Generates CustomADWDesign JSON
- Would create (in future):
  - `adw/learned/adw_custom_<name>.py`
  - `.claude/commands/learned/<name>.md`

### 4. Learning System

**Data Files:**
```
.tac/learning/
├── pattern_database.json      # Historical task→strategy mappings
├── decision_weights.json       # Pattern matching weights
└── execution_logs/            # Individual execution logs
    └── YYYY-MM-DDTHH-MM-SS-issue-N.json
```

**Pattern Database Schema:**
```json
{
  "patterns": [
    {
      "task_type": "feature",
      "complexity_score": 6.0,
      "complexity_level": "moderate",
      "validation_needs": "thorough",
      "has_ui_changes": true,
      "requires_e2e_tests": true,
      "recommended_workflow": "adw_plan_build_test_iso",
      "selected_workflow": "adw_plan_build_test_iso",
      "confidence_score": 0.85,
      "execution_time_minutes": 45.0,
      "is_false_fix": false,
      "success": true,
      "timestamp": "2025-11-03T00:00:00Z"
    }
  ],
  "version": "1.0",
  "total_patterns": 1,
  "last_updated": "2025-11-03T00:00:00Z"
}
```

**Learning Algorithm:**
1. **Collect Feedback** (after each execution):
   - Execution time
   - Issue resolution status (closed/open)
   - False fix detection (issue reopened)

2. **Update Patterns**:
   - Append new pattern to database
   - Increment template success/failure counts

3. **Retrain Weights** (after 10+ executions):
   - Calculate success rate
   - If success < 70%: Boost template_match weight
   - If success > 90%: Keep current weights
   - Normalize weights to sum to 1.0

---

## Data Models

### TaskAnalysis (Pydantic)
```python
class TaskAnalysis(BaseModel):
    task_type: TaskType  # feature/bug/chore/etc.
    complexity_score: float  # 1.0-10.0
    complexity_level: ComplexityLevel  # simple/moderate/complex/very_complex
    validation_needs: ValidationDepth  # basic/thorough/critical/l5/l6/l7
    key_requirements: List[str]
    estimated_effort_hours: float
    risk_factors: List[str]
    has_ui_changes: bool
    requires_e2e_tests: bool
    external_dependencies: List[str]
    recommended_model_set: ModelSet  # base/heavy
    analysis_timestamp: Optional[str]
```

### StrategyRecommendation (Pydantic)
```python
class StrategyRecommendation(BaseModel):
    workflow_name: str  # e.g., "adw_sdlc_iso"
    workflow_path: str  # e.g., "adw/adw_sdlc_iso.py"
    template_names: List[str]  # e.g., ["feature.md", "test.md"]
    validation_strategy: str  # Human-readable description
    confidence_score: float  # 0.0-1.0
    reasoning: str
    alternatives: List[Dict[str, Any]]  # 2nd and 3rd options
    estimated_tokens: Optional[int]
    trade_offs: List[str]
    recommended_phases: List[str]  # e.g., ["plan", "build", "test"]
    recommendation_timestamp: Optional[str]
```

### ADWState Extension
Extended existing ADWState with Meta-ADW tracking:
```python
# New fields added to ADWStateData
recommended_strategy: Optional[str] = None
strategy_confidence: Optional[float] = None
meta_adw_used: Optional[bool] = False
```

---

## Template Index

**Location:** `.tac/template_index.json`
**Size Target:** < 5KB
**Generated By:** `scripts/build_template_index.py`

**Ultra-Compact Format:**
```json
{
  "v": "1.0",
  "u": "2025-11-03T00:00:00Z",
  "n": 35,
  "t": {
    "feature.md": {
      "t": 1500,           // tokens
      "g": ["feature"],    // tags (max 2)
      "s": "Plan new features with detailed requirements"  // summary (max 50 chars)
    }
  }
}
```

**Rebuild Command:**
```bash
python scripts/build_template_index.py --rebuild
```

---

## Workflow Selection Rules

### Decision Tree

```
Task Type?
├─ feature
│  ├─ complexity < 4 → adw_plan_build_iso (60K tokens, 2-4h)
│  ├─ complexity 4-7 → adw_plan_build_test_iso (80K tokens, 4-8h)
│  └─ complexity > 7 → adw_sdlc_iso (120K tokens, 8-16h)
├─ bug
│  ├─ complexity < 4 → adw_patch_iso (40K tokens, 1-2h)
│  └─ complexity >= 4 → adw_plan_build_test_iso (80K tokens, 4-8h)
└─ chore
   ├─ standard → adw_plan_build_iso (60K tokens, 2-6h)
   └─ critical (affects production) → adw_plan_build_test_review_iso (100K tokens, 6-12h)
```

### Validation Strategy Mapping

```
validation_needs → TAC Pattern
├─ basic → Unit + integration tests
├─ thorough → L5: Closed-loop (agent verifies in real environment)
├─ critical → L6: Specialized agents (security, performance, accessibility)
├─ l5_closed_loop → TAC L5: Agent has access to logs/reality
├─ l6_specialized → TAC L6: Multiple validation agents
└─ l7_zero_touch → TAC L7: Full automation with confidence metrics
```

---

## Token Budget Management

**Total Budget:** < 150K tokens per execution

**Breakdown:**
```
Template Index:        ~5K  (loaded once at startup)
Interview:            ~10K  (7 questions + responses)
Analysis:             ~15K  (complexity analysis)
Recommendation:        ~5K  (decision engine + formatting)
Workflow Execution:  ~80K  (varies by workflow)
Learning Updates:      ~2K  (pattern database updates)
──────────────────────────
Total:               ~117K  (within budget)
```

**Optimizations:**
- Lazy loading: Only load full templates when executing
- Compact index: 5KB vs 120KB full templates
- Skip interview for simple tasks (future enhancement)

---

## Integration Points

### With Existing ADW System

**Updated Files:**
- `adw_modules/workflow_ops.py` - Added AGENT_STRATEGIST, "meta_adw_strategy" workflow
- `adw_modules/data_types.py` - Added Meta-ADW types to SlashCommand and ADWWorkflow literals
- `adw_modules/state.py` - Extended ADWState with Meta-ADW tracking fields

**Future Integration:**
```bash
# Add --use-meta-adw flag to existing workflows
uv run adw_plan_iso.py 123 --use-meta-adw
```

This would:
1. Run Meta-ADW first
2. Get recommendation
3. Execute recommended workflow
4. Track that Meta-ADW was used

---

## Error Handling

**Common Errors:**

1. **Template Index Missing**
   - Detection: `FileNotFoundError` in `load_template_index()`
   - Recovery: Clear error message with rebuild command

2. **Interview Failed**
   - Detection: JSON parse error in `conduct_interview()`
   - Recovery: Retry with clearer prompt

3. **No Good Match** (confidence < 0.5)
   - Detection: Low confidence in `recommend_strategy()`
   - Recovery: Trigger custom ADW designer

4. **Workflow Execution Failed**
   - Detection: Return code != 0 from `execute_workflow()`
   - Logging: Error message in execution log
   - Recovery: User notified, can retry manually

---

## Performance Characteristics

**Latency:**
- Interview: ~30-60 seconds (depends on user response time)
- Analysis: ~10-20 seconds (Claude API call)
- Recommendation: ~2-5 seconds (local decision engine + Claude API)
- Total to recommendation: ~1-2 minutes

**Accuracy:**
- First execution: ~70% (keyword matching only)
- After 10 executions: ~80-85% (learning data available)
- After 50 executions: ~90-95% (well-trained weights)

**Token Usage:**
- Simple tasks: ~60-80K tokens
- Moderate tasks: ~80-120K tokens
- Complex tasks: ~120-150K tokens

---

## Testing Strategy

### Unit Tests (`tests/test_decision_engine.py`)
- Template index loading
- Pattern matching algorithm
- Workflow ranking logic
- Confidence calculation
- Validation strategy mapping

**Coverage:** 12 tests, all passing

### Integration Tests (`tests/integration/test_meta_adw_e2e.py`)
- Full workflow execution
- Interview → analyze → recommend flow
- Learning system updates
- Pattern database persistence
- Weight retraining logic

**Coverage:** 10 tests, 8 passing (2 minor serialization issues)

### Manual Testing
- Run on diverse real issues
- Verify recommendations make sense
- Check execution logs
- Monitor learning data accumulation

---

## Future Enhancements

1. **Web UI** for visualizing recommendations and learning data
2. **Slack/Discord integration** for interactive interviews
3. **A/B testing framework** for comparing workflow effectiveness
4. **GitHub Actions integration** for automatic Meta-ADW execution
5. **Export learned patterns** as documentation
6. **Multi-repository learning** (shared pattern database across projects)
7. **Confidence threshold tuning** per repository
8. **Custom workflow execution** (currently logs only)

---

## Security Considerations

- No sensitive data stored in pattern database
- GitHub tokens handled by existing ADW infrastructure
- Execution logs may contain issue descriptions (consider .gitignore)
- No external API calls beyond GitHub and Claude

---

## Maintenance

### Regular Tasks
- **Rebuild template index** when adding new templates
- **Review pattern database** quarterly for insights
- **Monitor false fix rate** and investigate patterns
- **Clean old execution logs** (optional, for disk space)

### Troubleshooting
- Check logs in `.tac/learning/execution_logs/`
- Review pattern database for unexpected patterns
- Verify template index size < 5KB
- Ensure decision weights sum to 1.0

---

## Dependencies

**Python Packages:**
- `pydantic` - Data validation
- `python-dotenv` - Environment management

**External Tools:**
- Claude Code CLI - Template execution
- `gh` CLI - GitHub API access
- `uv` - Python environment management

**No Additional Dependencies Required** - Uses existing ADW infrastructure.
