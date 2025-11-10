# Feature: Meta-ADW Strategy System

## Metadata
issue_number: `7`
adw_id: `7`
issue_json: `{"number": 7, "title": "Build Meta-ADW Strategy System", "body": "## Work Type\nfeature\n\n## Description\n\nBuild an intelligent TAC strategy advisor system that sits above existing ADWs and helps users select the optimal approach for any task.\n\n### What It Does\n- Interviews users about their task (via strategy/interview.md)\n- Analyzes task complexity and requirements (via strategy/analyze.md)\n- Recommends optimal template/ADW combination from library\n- Selects appropriate validation strategy (L5 patterns)\n- Creates custom ADWs when no existing template fits\n- Learns from execution outcomes over time\n- Prevents validation gaps (e.g., \"agent says fixed but isn't\")\n\n### Why We Need This\nCurrent pain points:\n1. 30+ templates/ADWs available - unclear which to use\n2. No guidance on validation strategy (when to use L5 closed loops, L6 specialization)\n3. Agent claims \"fixed\" but issues persist in production\n4. No mechanism to handle novel scenarios\n\nMeta-ADW solves this by being the \"TAC instructor sitting beside you.\"\n\n## Acceptance Criteria\n\n### Core System\n- [ ] `meta_strategy.py` - Main orchestrator functional\n- [ ] `decision_engine.py` - Pattern matching logic works\n- [ ] Strategy templates created:\n  - [ ] `interview.md` - User interview\n  - [ ] `analyze.md` - Task analysis  \n  - [ ] `recommend.md` - Strategy selection\n  - [ ] `validate_plan.md` - Plan validation\n  - [ ] `design_custom_adw.md` - Custom ADW creator\n\n### Infrastructure\n- [ ] `scripts/build_template_index.py` - Template indexer works\n- [ ] `.tac/template_index.json` - Generated and accurate\n- [ ] `.tac/learning/pattern_database.json` - Initialized\n- [ ] `.tac/learning/execution_logs/` - Directory created\n\n### Integration\n- [ ] Integrates with existing `adw_plan_build.py`\n- [ ] Can call existing templates dynamically\n- [ ] Respects token budget (< 150K per execution)\n- [ ] Works with Claude CLI OAuth (no API)\n\n### Quality\n- [ ] Unit tests for decision engine\n- [ ] Integration tests for full workflow\n- [ ] Documentation complete (README, usage guide)\n- [ ] Example execution logs\n\n## Success Metrics\n\n**Quantitative:**\n- Template selection accuracy > 90%\n- Token usage < 150K average\n- \"False fix\" reduction by 80%\n- Success rate improves 10%/month\n\n**Qualitative:**\n- Feels like \"expert sitting beside you\"\n- Eliminates decision paralysis\n- Confident in recommendations"}`

## Feature Description

Build an intelligent TAC strategy advisor system (Meta-ADW) that acts as a decision-making layer above existing ADW workflows. This system interviews users about their tasks, analyzes complexity and requirements, and recommends the optimal template/ADW combination from the library. It can select appropriate validation strategies (L5 patterns), create custom ADWs when no existing template fits, and learn from execution outcomes over time.

The Meta-ADW system addresses critical pain points:
- Confusion over which of 30+ templates/ADWs to use for a given task
- Lack of guidance on validation strategy selection (L5 closed loops, L6 specialization)
- Agent claims "fixed" but issues persist in production (validation gaps)
- No systematic mechanism to handle novel scenarios

This creates value by being the "TAC instructor sitting beside you" - eliminating decision paralysis and improving workflow selection accuracy.

## User Story

As a **developer using the TAC framework**
I want to **receive intelligent recommendations on which ADW workflow and templates to use for any given task**
So that **I can execute tasks efficiently with the right validation strategy, without needing to understand all 30+ templates and their nuances**

## Problem Statement

The current TAC framework offers 30+ templates and ADW workflows, creating decision paralysis for users. There is no systematic way to:
1. Select the optimal workflow for a specific task type
2. Determine the appropriate validation strategy depth (L5 vs L6 patterns)
3. Detect and prevent validation gaps where agents claim success but issues persist
4. Handle novel scenarios that don't fit existing templates
5. Learn from past executions to improve future recommendations

This leads to suboptimal workflow selection, missed validation steps, and wasted developer time.

## Solution Statement

Create a Meta-ADW Strategy System that sits above existing ADWs as an intelligent orchestration layer. The system will:

1. **Interview & Analyze**: Use strategy templates to interview users and analyze task complexity
2. **Recommend**: Apply pattern matching logic to recommend optimal template/ADW combinations
3. **Validate**: Ensure selected strategies include appropriate validation depth
4. **Adapt**: Create custom ADWs when existing templates don't fit
5. **Learn**: Track execution outcomes and improve recommendations over time

The system uses a lightweight template index (~5KB) for token efficiency, lazy-loads full templates only when executing, and maintains a shared learning database across projects. It integrates seamlessly with existing ADW workflows while respecting the token budget constraint (< 150K per execution).

## Relevant Files

Use these files to implement the feature:

### Existing ADW Infrastructure
- **adw/adw_modules/workflow_ops.py** - Contains existing workflow orchestration logic, agent name constants (AGENT_PLANNER, AGENT_IMPLEMENTOR), format_issue_message(), and AVAILABLE_ADW_WORKFLOWS list. Use as reference for integration patterns.
- **adw/adw_modules/data_types.py** - Defines ADWWorkflow, SlashCommand, ModelSet, GitHubIssue, AgentTemplateRequest, and other Pydantic models. Extend with new MetaADW-specific data types.
- **adw/adw_modules/agent.py** - Contains execute_template() function for running slash commands via Claude CLI. Use this for executing strategy templates.
- **adw/adw_modules/state.py** - Manages ADWState persistence in agents/<adw_id>/adw_state.json. Extend to track strategy recommendations and learning data.
- **adw/adw_plan_iso.py** - Reference implementation showing full ADW workflow: fetch issue → classify → create worktree → generate plan → commit → PR. Integration point for Meta-ADW.

### Existing Slash Commands
- **.claude/commands/classify_issue.md** - Shows pattern for issue classification. Use as template for strategy classification logic.
- **.claude/commands/feature.md** - The current command being executed. Shows plan format and structure to follow.
- **.claude/commands/conditional_docs.md** - Documents conditional documentation loading pattern. Apply similar approach for conditional template loading.

### Documentation References
- **CLAUDE.md** - Master documentation file describing TAC framework, ADW system, and repository structure. Update with Meta-ADW details.
- **.claude/commands/tac-process.md** - Shows TAC workflow pattern. Meta-ADW should follow similar structure.
- **.tac/docs/meta-adw-design/meta-adw-requirements.md** - Complete specification for Meta-ADW system. Read this first to understand requirements and architecture.
- **.tac/docs/meta-adw-design/architecture-decisions.md** - Key design decisions (overlay architecture, CLI vs API, lazy loading, three-tier selection). Follow these patterns.
- **.tac/docs/meta-adw-design/tac-implementation-guide.md** - Step-by-step implementation guide. Use as reference during development.
- **.tac/docs/meta-adw-design/quick-start-summary.md** - Quick reference for Meta-ADW concepts.

### New Files

The following new files need to be created:

#### Core Meta-ADW System
- **adw/meta_strategy.py** - Main orchestrator script. Entry point for Meta-ADW execution. Interviews users, analyzes tasks, recommends workflows.
- **adw/decision_engine.py** - Pattern matching logic for workflow selection. Scores templates against task requirements.
- **adw/adw_modules/meta_adw_types.py** - Pydantic models for Meta-ADW (TaskAnalysis, StrategyRecommendation, LearningRecord, etc.)

#### Strategy Templates
- **.claude/commands/strategy/interview.md** - Slash command template for interviewing users about their task
- **.claude/commands/strategy/analyze.md** - Slash command template for analyzing task complexity and requirements
- **.claude/commands/strategy/recommend.md** - Slash command template for recommending optimal workflow strategy
- **.claude/commands/strategy/validate_plan.md** - Slash command template for validating selected strategy includes proper validation
- **.claude/commands/strategy/design_custom_adw.md** - Slash command template for creating custom ADWs when no template fits

#### Infrastructure
- **scripts/build_template_index.py** - Script to scan .claude/commands/ and generate lightweight template index with summaries
- **.tac/template_index.json** - Generated lightweight catalog of all templates (~5KB). Contains template names, types, summaries, use cases.
- **.tac/learning/pattern_database.json** - Persistent database of learned task patterns and successful workflow selections
- **.tac/learning/decision_weights.json** - Learned weights for decision engine pattern matching
- **.tac/learning/execution_logs/** - Directory for storing execution logs (task, strategy, outcome)

#### Testing
- **adw/tests/test_decision_engine.py** - Unit tests for pattern matching logic
- **adw/tests/test_meta_strategy.py** - Integration tests for full Meta-ADW workflow
- **adw/tests/fixtures/sample_tasks.json** - Test fixtures with sample task descriptions

#### Documentation
- **adw/META_ADW_README.md** - Complete guide for using Meta-ADW system
- **adw/META_ADW_ARCHITECTURE.md** - Technical architecture documentation
- **.tac/docs/meta-adw-examples.md** - Example executions showing Meta-ADW in action

## Implementation Plan

### Phase 1: Foundation
Create the foundational infrastructure for Meta-ADW:
1. Set up directory structure (.tac/learning/, .claude/commands/strategy/)
2. Define Pydantic data models for Meta-ADW operations
3. Build template indexing system to create lightweight catalog
4. Initialize learning database files (pattern_database.json, decision_weights.json)
5. Create basic decision engine with placeholder pattern matching logic

### Phase 2: Core Implementation
Implement the core Meta-ADW functionality:
1. Build strategy templates for user interview and task analysis
2. Implement pattern matching logic in decision engine
3. Create main meta_strategy.py orchestrator with full workflow
4. Build recommendation template with scoring logic
5. Implement custom ADW creation capability
6. Add execution logging and learning data collection

### Phase 3: Integration
Integrate Meta-ADW with existing ADW system:
1. Update workflow_ops.py to expose Meta-ADW as callable workflow
2. Add Meta-ADW execution mode to adw_plan_iso.py (optional --use-meta-adw flag)
3. Update ADWState to track strategy recommendations
4. Create validation template to check strategy completeness
5. Build feedback collection mechanism for learning system
6. Write comprehensive documentation and usage examples

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 0. Read Design Documentation
- **CRITICAL FIRST STEP**: Read all design documents before implementation:
  - Read `.tac/docs/meta-adw-design/meta-adw-requirements.md` - Full requirements and architecture overview
  - Read `.tac/docs/meta-adw-design/architecture-decisions.md` - Key design patterns to follow
  - Read `.tac/docs/meta-adw-design/tac-implementation-guide.md` - Implementation guidance
  - Read `.tac/docs/meta-adw-design/quick-start-summary.md` - Quick reference
- Understand the three-tier template selection pattern (Existing → Adapt → Create)
- Understand overlay architecture (lives in `.claude/`, separate from app code)
- Understand Claude CLI OAuth approach (no API keys)
- Understand lazy loading with template index strategy

### 1. Set Up Directory Structure and Initialize Learning System
- Create `.tac/` directory if it doesn't exist
- Create `.tac/learning/` directory for persistent learning data
- Create `.tac/learning/execution_logs/` directory for execution logs
- Create `.tac/docs/` directory for Meta-ADW documentation
- Create `.claude/commands/strategy/` directory for strategy templates
- Create `adw/learned/` directory for custom ADWs
- Initialize `.tac/learning/pattern_database.json` with empty structure: `{"patterns": [], "version": "1.0"}`
- Initialize `.tac/learning/decision_weights.json` with default weights: `{"template_match": 0.4, "complexity_match": 0.3, "validation_depth": 0.3}`

### 2. Define Pydantic Data Models for Meta-ADW
- Create `adw/adw_modules/meta_adw_types.py`
- Define `TaskAnalysis` model (task_type, complexity_score, validation_needs, key_requirements)
- Define `StrategyRecommendation` model (workflow_name, template_names, validation_strategy, confidence_score, reasoning)
- Define `LearningRecord` model (task_description, recommended_strategy, outcome, success_metrics, timestamp)
- Define `TemplateIndexEntry` model (name, type, summary, use_cases, tags, validation_level)
- Define `PatternMatch` model (pattern_name, match_score, matched_keywords, recommended_templates)
- Add unit tests in `adw/tests/test_meta_adw_types.py` to verify model validation

### 3. Build Template Indexing System
- Create `scripts/build_template_index.py`
- Implement function to scan `.claude/commands/` directory recursively
- Extract metadata from each template (name, purpose, when to use, key patterns)
- Use Claude API or local parsing to generate 2-3 sentence summaries for each template
- Generate structured JSON index with `TemplateIndexEntry` objects
- Write output to `.tac/template_index.json`
- Keep index size < 5KB by using concise summaries
- Add CLI mode: `python scripts/build_template_index.py --rebuild`
- Test with existing templates to verify index generation

### 4. Create User Interview Template
- Create `.claude/commands/strategy/interview.md`
- Template should ask 5-7 key questions:
  - What type of task? (feature/bug/chore/investigation)
  - Complexity level? (simple/moderate/complex)
  - User interaction? (UI/backend/full-stack/infrastructure)
  - Testing requirements? (unit/integration/e2e/all)
  - Validation needs? (basic/thorough/critical)
  - Timeline? (quick-patch/normal/comprehensive)
  - Novel or standard task?
- Output JSON with structured answers
- Include examples for each question
- Test interview template by executing: `claude --command /strategy/interview "I need to add authentication"`

### 5. Create Task Analysis Template
- Create `.claude/commands/strategy/analyze.md`
- Template takes interview results as input
- Analyzes complexity using factors:
  - Number of files to modify
  - Cross-cutting concerns (affects multiple layers)
  - External dependencies
  - Testing complexity
  - Risk level (business impact)
- Outputs `TaskAnalysis` JSON with:
  - Complexity score (1-10)
  - Estimated effort (hours)
  - Key risk factors
  - Required validation depth (L5/L6/L7)
  - Recommended model set (base/heavy)
- Test analysis template with sample interview output

### 6. Implement Decision Engine Pattern Matching
- Create `adw/decision_engine.py`
- Implement `load_template_index()` - loads `.tac/template_index.json`
- Implement `load_learning_data()` - loads pattern_database.json and decision_weights.json
- Implement `match_patterns()` - scores templates against task requirements using:
  - Keyword matching (task description vs template use cases)
  - Complexity matching (task complexity vs template complexity range)
  - Validation depth matching (required validation vs template validation level)
  - Historical success rate (from learning database)
- Implement `rank_workflows()` - combines pattern matches into ranked workflow recommendations
- Implement `calculate_confidence()` - confidence score based on match strength
- Return top 3 recommendations with reasoning
- Add unit tests in `adw/tests/test_decision_engine.py`

### 7. Create Strategy Recommendation Template
- Create `.claude/commands/strategy/recommend.md`
- Template takes `TaskAnalysis` JSON as input
- Uses decision_engine to get ranked recommendations
- Formats recommendations with:
  - Primary recommendation (highest scoring)
  - Alternative approaches (2nd and 3rd place)
  - Reasoning for each recommendation
  - Trade-offs and considerations
  - Expected token usage for each option
  - Validation strategy included
- Outputs `StrategyRecommendation` JSON
- Test recommendation template with various task analysis inputs

### 8. Build Main Meta-Strategy Orchestrator
- Create `adw/meta_strategy.py` as executable script with uv run shebang
- Parse command line args: `<issue-number> [--adw-id <id>] [--model-set <base|heavy>]`
- Load environment variables and setup logger
- Fetch GitHub issue details
- Execute interview template → get user answers
- Execute analyze template → get TaskAnalysis
- Execute recommend template → get StrategyRecommendation
- Display recommendations to user (in issue comment)
- Prompt user to confirm or override recommendation
- Execute selected workflow (call appropriate adw_*_iso.py script)
- Log execution to `.tac/learning/execution_logs/<timestamp>-<issue-number>.json`
- Update pattern database with new data point
- Return success/failure status

### 9. Create Plan Validation Template
- Create `.claude/commands/strategy/validate_plan.md`
- Template takes generated implementation plan as input
- Checks for validation gaps:
  - Are validation commands included?
  - Does complexity match validation depth?
  - Are edge cases covered?
  - Is E2E testing included for UI changes?
  - Are success criteria measurable?
- Outputs validation report with:
  - Pass/fail status
  - List of missing validation steps
  - Recommendations to improve plan
- Auto-fixes: Can suggest additional validation steps to add
- Test validation template with sample plans (good and bad)

### 10. Create Custom ADW Designer Template
- Create `.claude/commands/strategy/design_custom_adw.md`
- Template takes TaskAnalysis for novel/unique tasks with no good template match
- Analyzes requirements and designs new ADW structure:
  - Required phases (plan/build/test/review/document)
  - Custom validation steps
  - Specific tools/commands needed
  - Integration points with existing system
- Generates new ADW script in `adw/learned/adw_custom_<description>.py`
- Generates corresponding slash command template in `.claude/commands/learned/`
- Updates template index with new template
- Outputs file paths for generated artifacts
- Test by designing a custom ADW for an unusual task type

### 11. Implement Learning System
- Add `collect_feedback()` function to meta_strategy.py
  - After workflow completion, check issue resolution status
  - Detect "false fixes" (agent marked done but issue reopened)
  - Collect metrics: time to complete, PR review feedback, test pass rate
- Add `update_pattern_database()` function
  - Store successful task→strategy mappings
  - Track failure patterns
  - Update template success rates
- Add `retrain_weights()` function
  - After 10+ executions, analyze patterns
  - Adjust decision_weights.json based on success correlations
  - Automatically improve recommendations over time
- Add test coverage for learning functions

### 12. Integration with Existing ADW System
- Update `adw/adw_modules/workflow_ops.py`
  - Add "meta_adw_strategy" to AVAILABLE_ADW_WORKFLOWS list
  - Add AGENT_STRATEGIST = "meta_strategist" constant
  - Create `execute_meta_adw()` helper function
- Update `adw/adw_modules/data_types.py`
  - Add "/strategy/interview", "/strategy/analyze", "/strategy/recommend", "/strategy/validate_plan", "/strategy/design_custom_adw" to SlashCommand literal
  - Add "meta_adw_strategy" to ADWWorkflow literal
- Update `adw/adw_plan_iso.py`
  - Add optional `--use-meta-adw` flag
  - When flag present, call meta_strategy.py instead of direct classify_issue
  - Pass Meta-ADW recommendation to planning phase
- Update `adw/adw_modules/state.py`
  - Add fields to ADWState: recommended_strategy, strategy_confidence, meta_adw_used
  - Track whether Meta-ADW was used for this workflow

### 13. Write Unit Tests
- Create `adw/tests/test_decision_engine.py`
  - Test pattern matching with known inputs
  - Test confidence calculation
  - Test edge cases (empty templates, missing data)
  - Test learning data integration
- Create `adw/tests/test_meta_strategy.py`
  - Test full workflow with mocked templates
  - Test error handling (failed interview, invalid analysis)
  - Test recommendation ranking
- Create test fixtures in `adw/tests/fixtures/`
  - sample_tasks.json with 10+ diverse task descriptions
  - sample_recommendations.json with expected outputs
- Verify all tests pass: `cd adw && uv run pytest tests/`

### 14. Write Integration Tests
- Create `adw/tests/integration/test_meta_adw_e2e.py`
- Test end-to-end flow:
  - Start with sample GitHub issue
  - Run meta_strategy.py
  - Verify interview executes
  - Verify analysis executes
  - Verify recommendation generated
  - Verify recommendation is valid ADW workflow
  - Verify execution logs created
- Test custom ADW creation for novel task
- Test learning system updates pattern database
- Run integration tests: `cd adw && uv run pytest tests/integration/`

### 15. Create Documentation
- Create `adw/META_ADW_README.md`
  - Overview of Meta-ADW system
  - When to use Meta-ADW vs direct ADW
  - Command line usage examples
  - Configuration options
  - Troubleshooting guide
- Create `adw/META_ADW_ARCHITECTURE.md`
  - System architecture diagrams (use ASCII art)
  - Data flow through components
  - Integration points with existing ADW
  - Learning system algorithm details
  - Token budget management strategy
- Create `.tac/docs/meta-adw-examples.md`
  - 5-6 example executions with different task types
  - Show interview → analyze → recommend → execute flow
  - Include example outputs at each stage
  - Show custom ADW creation example

### 16. Update Main Repository Documentation
- Update `CLAUDE.md`
  - Add Meta-ADW section to "Key Systems"
  - Explain when to use `/begin` vs `meta_strategy.py`
  - Add Meta-ADW to "Development Commands" section
  - Update "Repository Structure" with new Meta-ADW files
  - Add to "Critical Workflows" with example usage
- Update `.claude/commands/begin.md`
  - Add Meta-ADW as advanced option
  - Explain difference between `/begin` (quick routing) and Meta-ADW (deep analysis)
- Update `.claude/commands/conditional_docs.md`
  - Add Meta-ADW documentation paths with conditions

### 17. Generate Initial Template Index
- Run `python scripts/build_template_index.py --rebuild`
- Verify `.tac/template_index.json` is created
- Verify file size is < 5KB
- Verify all 30+ existing templates are indexed
- Verify summaries are accurate and useful
- Commit template index to repository

### 18. Create Example Execution Logs
- Run Meta-ADW on 3-4 sample tasks
- Tasks should cover: simple feature, complex bug, novel scenario
- Generate execution logs showing:
  - Interview questions and answers
  - Task analysis with complexity scoring
  - Recommended strategies with reasoning
  - Selected workflow and outcome
- Save logs to `.tac/learning/execution_logs/example-*.json`
- Reference these in documentation

### 19. Final Validation - Run Complete Workflow Test
Execute the full Validation Commands below to ensure:
- All components work together
- Template index is accurate
- Decision engine produces valid recommendations
- Integration with existing ADW works
- Documentation is complete and accurate
- Tests pass with zero regressions

## Testing Strategy

### Unit Tests

**Decision Engine Tests** (`adw/tests/test_decision_engine.py`):
- Test pattern matching against known good/bad matches
- Test confidence scoring with edge cases (perfect match vs no match)
- Test template ranking with multiple candidates
- Test learning data integration (pattern database affects recommendations)
- Test handling of missing/corrupted template index

**Meta-Strategy Tests** (`adw/tests/test_meta_strategy.py`):
- Test orchestration flow with mocked template executions
- Test error handling at each stage (interview fails, analysis fails, etc.)
- Test user confirmation prompt handling
- Test execution logging creates correct JSON structure
- Test pattern database updates correctly

**Data Model Tests** (`adw/tests/test_meta_adw_types.py`):
- Test Pydantic model validation (required fields, type checking)
- Test JSON serialization/deserialization
- Test model relationships (TaskAnalysis → StrategyRecommendation)

**Template Index Tests** (`adw/tests/test_template_index.py`):
- Test index builder scans all templates correctly
- Test index size stays under 5KB limit
- Test index JSON structure is valid
- Test incremental index updates (add new template)

### Integration Tests

**End-to-End Workflow Tests** (`adw/tests/integration/test_meta_adw_e2e.py`):
- Test complete flow: issue → interview → analyze → recommend → execute
- Test with real GitHub issue (use test repository)
- Verify all intermediate files created correctly
- Verify execution logs written to correct location
- Verify pattern database updated

**ADW Integration Tests** (`adw/tests/integration/test_adw_integration.py`):
- Test meta_strategy.py calls adw_plan_iso.py correctly
- Test --use-meta-adw flag in existing ADWs
- Test ADWState contains Meta-ADW tracking fields
- Verify Meta-ADW recommendation passed through to planning phase

**Learning System Tests** (`adw/tests/integration/test_learning_system.py`):
- Test pattern database grows with executions
- Test decision weights adjust after 10+ executions
- Test "false fix" detection and recording
- Test success rate tracking per template

### Edge Cases

1. **Empty Template Index**: Meta-ADW should handle missing/empty template_index.json gracefully, falling back to scanning .claude/commands/ directly
2. **Novel Task with No Match**: When decision engine finds no good matches (all confidence < 30%), should trigger custom ADW designer
3. **Corrupted Learning Data**: If pattern_database.json is corrupted, should initialize fresh and log warning
4. **User Overrides Recommendation**: When user chooses option #2 or #3 instead of primary, should still log as learning data
5. **Token Budget Exceeded**: If interview + analyze + recommend exceeds 50K tokens, should fall back to simpler analysis
6. **Concurrent Executions**: Multiple meta_strategy.py instances should handle concurrent access to pattern_database.json safely
7. **Missing Required Templates**: If strategy/ templates are missing, should fail fast with clear error message
8. **Invalid GitHub Issue Format**: If issue body doesn't contain expected structure, should guide user to fix format
9. **Offline Mode**: Should work without GitHub API access for local development/testing
10. **Template Index Out of Date**: Should detect when new templates added but index not rebuilt, prompt to run build_template_index.py

## Acceptance Criteria

1. ✅ `meta_strategy.py` executable script exists and runs successfully with `uv run adw/meta_strategy.py <issue-number>`
2. ✅ `decision_engine.py` loads template index and produces ranked recommendations with reasoning
3. ✅ All 5 strategy templates created and functional:
   - `interview.md` asks 5-7 questions and outputs JSON
   - `analyze.md` produces TaskAnalysis with complexity score
   - `recommend.md` returns top 3 StrategyRecommendation options
   - `validate_plan.md` checks for validation gaps in plans
   - `design_custom_adw.md` generates new ADW for novel tasks
4. ✅ `scripts/build_template_index.py` scans .claude/commands/ and generates `.tac/template_index.json` < 5KB
5. ✅ `.tac/learning/pattern_database.json` and `decision_weights.json` initialized and updated by executions
6. ✅ `.tac/learning/execution_logs/` directory contains JSON logs for each execution
7. ✅ Meta-ADW integrates with `adw_plan_iso.py` via `--use-meta-adw` flag
8. ✅ Decision engine uses learning data to improve recommendations over time
9. ✅ Token usage stays < 150K per execution (interview + analyze + recommend + execute workflow)
10. ✅ Works with Claude CLI OAuth (no ANTHROPIC_API_KEY required for slash command execution)
11. ✅ Unit tests pass: `cd adw && uv run pytest tests/` with > 80% coverage
12. ✅ Integration tests pass: `cd adw && uv run pytest tests/integration/`
13. ✅ Documentation complete: META_ADW_README.md, META_ADW_ARCHITECTURE.md, meta-adw-examples.md
14. ✅ CLAUDE.md updated with Meta-ADW system overview
15. ✅ Template index includes all 30+ existing templates with accurate summaries
16. ✅ Example execution logs demonstrate system working on diverse task types
17. ✅ Custom ADW designer can generate new ADW for task with no template match
18. ✅ Learning system detects "false fixes" and adjusts template success rates
19. ✅ Validation template catches common validation gaps (missing E2E tests, insufficient edge case coverage)
20. ✅ System provides confidence scores and reasoning for all recommendations (no black-box decisions)

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

### 1. Verify Directory Structure
```bash
# Check all required directories exist
ls -la .tac/learning/
ls -la .tac/learning/execution_logs/
ls -la .tac/docs/
ls -la .claude/commands/strategy/
ls -la adw/learned/
ls -la adw/tests/
ls -la adw/tests/fixtures/
ls -la adw/tests/integration/
```

### 2. Verify Data Files Initialized
```bash
# Check learning database files exist and have valid JSON
cat .tac/learning/pattern_database.json | python -m json.tool
cat .tac/learning/decision_weights.json | python -m json.tool
cat .tac/template_index.json | python -m json.tool
# Verify template index is under 5KB
wc -c .tac/template_index.json | awk '{print $1 " bytes (should be < 5120)"}'
```

### 3. Verify Template Index Generation
```bash
# Rebuild template index and verify output
cd scripts && uv run python build_template_index.py --rebuild
# Check index contains entries for all templates
cat ../.tac/template_index.json | python -c "import json, sys; data=json.load(sys.stdin); print(f'Indexed {len(data[\"templates\"])} templates')"
```

### 4. Test Strategy Templates Individually
```bash
# Test interview template
claude --command /strategy/interview "I need to add user authentication with OAuth"
# Test analyze template (requires interview output)
# Test recommend template (requires analysis output)
# Test validate_plan template (requires plan file)
# Verify each template produces valid JSON output
```

### 5. Test Decision Engine Pattern Matching
```bash
# Run decision engine unit tests
cd adw && uv run pytest tests/test_decision_engine.py -v
# Verify pattern matching scores templates correctly
# Verify confidence calculation is reasonable
```

### 6. Test Meta-Strategy Orchestrator
```bash
# Run meta-strategy unit tests
cd adw && uv run pytest tests/test_meta_strategy.py -v
# Test full workflow with mocked templates
```

### 7. Test Custom ADW Designer
```bash
# Test custom ADW creation for novel task
claude --command /strategy/design_custom_adw "Create a workflow for database migration with zero downtime"
# Verify generated ADW script in adw/learned/
# Verify generated slash command template in .claude/commands/learned/
```

### 8. Run Integration Tests
```bash
# Run full end-to-end integration tests
cd adw && uv run pytest tests/integration/ -v
# Verify Meta-ADW integrates with existing ADW system
# Verify execution logs created correctly
# Verify pattern database updates
```

### 9. Test Meta-ADW on Sample Issues
```bash
# Run Meta-ADW on 3 different sample issues
uv run adw/meta_strategy.py 7  # Feature issue (this one)
# Verify interview executes
# Verify analysis produces TaskAnalysis
# Verify recommendations make sense
# Verify execution log created in .tac/learning/execution_logs/
```

### 10. Verify Learning System
```bash
# Check pattern database updated after executions
cat .tac/learning/pattern_database.json | python -m json.tool
# Verify execution count increased
# Verify new patterns detected
```

### 11. Test ADW Integration
```bash
# Run existing ADW with Meta-ADW flag
cd adw && uv run adw_plan_iso.py 7 --use-meta-adw
# Verify Meta-ADW recommendation used in planning
# Check ADWState contains Meta-ADW tracking fields
```

### 12. Verify Documentation Complete
```bash
# Check all documentation files exist and are non-empty
wc -l adw/META_ADW_README.md
wc -l adw/META_ADW_ARCHITECTURE.md
wc -l .tac/docs/meta-adw-examples.md
# Verify CLAUDE.md updated
grep -A 5 "Meta-ADW" CLAUDE.md
```

### 13. Verify Token Usage
```bash
# Run Meta-ADW with token tracking
# Verify total tokens < 150K
# Check execution logs for token counts
cat .tac/learning/execution_logs/*.json | python -c "import json, sys; logs=[json.load(open(f)) for f in sys.argv[1:]]; print(f'Avg tokens: {sum(l.get(\"token_count\", 0) for l in logs)/len(logs)}')" .tac/learning/execution_logs/*.json
```

### 14. Run All Unit Tests
```bash
cd adw && uv run pytest tests/ -v --cov=. --cov-report=term-missing
# Verify > 80% code coverage
# Verify all tests pass with zero failures
```

### 15. Final System Validation
```bash
# Run complete validation suite
cd adw && uv run pytest tests/ tests/integration/ -v
# Verify no test failures
# Verify no warnings about missing dependencies
```

**Standard Project Tests** (no app/server or app/client in this repo, so these are informational):
- This is a library repository without a server/client application
- Standard validation commands don't apply
- Meta-ADW tests are the primary validation

## Notes

### Token Efficiency Strategy
- Template index is only ~5KB, loaded once at startup
- Full templates loaded lazily only when executing
- Decision engine uses lightweight keyword matching first, deep analysis only for top 3 candidates
- If token budget tight, can skip interview and use faster heuristic analysis
- Learning database enables progressively better recommendations without re-analyzing past patterns

### Learning System Details
- Pattern database tracks: task_description → (recommended_workflow, outcome, success_rate)
- After 10+ executions for similar task types, system detects patterns
- Decision weights automatically adjust based on correlation between features and success
- "False fix" detection: checks if issue reopened within 7 days of PR merge
- Success metrics tracked: PR approval time, test pass rate, reopened issue count

### Integration with Existing System
- Meta-ADW is optional enhancement, doesn't break existing ADW workflows
- Can be invoked standalone: `uv run adw/meta_strategy.py <issue>`
- Or integrated via flag: `uv run adw/adw_plan_iso.py <issue> --use-meta-adw`
- Existing workflows work unchanged if Meta-ADW not used
- ADWState backward compatible (new fields optional)

### Future Enhancements
- Web UI for visualizing recommendations and learning data
- Slack/Discord integration for interactive interviews
- Export learned patterns as documentation
- A/B testing framework for comparing workflow effectiveness
- Integration with GitHub Actions for automatic Meta-ADW execution on new issues

### Dependencies
- No new Python dependencies required (uses existing: pydantic, python-dotenv)
- Claude CLI must be installed and authenticated (OAuth)
- GitHub CLI (gh) required for issue/PR operations
- uv for Python environment management

### Known Limitations
- First execution has no learning data, recommendations based purely on keyword matching
- Custom ADW designer requires heavy model (Opus recommended) for quality
- Token usage increases with task complexity (interview may need 10K+ tokens for complex tasks)
- Learning system requires 10+ executions before patterns emerge
- Concurrent executions may conflict on pattern_database.json (needs file locking in v2)

### Backward Compatibility
- All existing ADW workflows continue to work without modification
- Template index generation is one-time setup (can be regenerated anytime)
- Learning data is optional (system works without it, just less accurate)
- If .tac/ directory missing, Meta-ADW falls back to direct template scanning

### Success Tracking
Monitor these metrics after deployment:
1. Template selection accuracy (user acceptance rate of primary recommendation)
2. Average token usage per Meta-ADW execution
3. "False fix" rate over time (should decrease)
4. Time to decision (interview → recommendation should be < 5 min)
5. Custom ADW creation frequency (indicates novel scenario handling)
6. Learning system impact (recommendation accuracy improvement over time)
