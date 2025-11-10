# Feature: Webhook Automation Test

## Metadata
issue_number: `14`
adw_id: `685b74ed`
issue_json: `{"number":14,"title":"[TAC] Test: Auto plan","body":"### Work Type\n\nfeature\n\n### Task Description\n\nTesting webhook automation\n\n### Acceptance Criteria\n\n_No response_\n\n### Additional Context\n\n_No response_"}`

## Feature Description

Create a comprehensive test feature to validate the webhook automation system. This feature will implement a simple test marker file that demonstrates the webhook automation is working correctly. The test will create a `.webhook_test_marker.json` file that includes metadata about when the webhook was triggered, the issue number, ADW ID, and timestamp. This provides clear evidence that the automated workflow successfully executed from webhook trigger to implementation.

The feature serves as both a validation mechanism and a template for future webhook-triggered workflows. It demonstrates the complete end-to-end automation flow: GitHub webhook event → ADW trigger → plan generation → implementation → PR creation.

## User Story

As a **TAC framework maintainer**
I want to **validate that webhook automation triggers ADW workflows successfully**
So that **I can confidently rely on zero-touch automation for issue processing**

## Problem Statement

When setting up webhook automation for the TAC framework, there's currently no simple way to verify that:
1. GitHub webhooks are correctly configured and firing
2. The webhook server is receiving and processing events
3. ADW workflows are being triggered automatically
4. The complete automation chain (webhook → plan → build → PR) executes successfully
5. The system can handle multiple webhook triggers without conflicts

Without a test mechanism, it's difficult to confirm the webhook automation is working as expected, leading to uncertainty about the reliability of zero-touch execution.

## Solution Statement

Create a simple webhook automation test feature that:
1. **Generates a test marker file** containing webhook execution metadata
2. **Validates the complete workflow chain** from webhook trigger to PR creation
3. **Provides clear evidence** of successful automation through file contents and timestamps
4. **Serves as a minimal example** for future webhook-triggered features

The implementation will:
- Create a `.webhook_test_marker.json` file in the repository root
- Include metadata: issue_number, adw_id, timestamp, workflow_name, trigger_type
- Add comprehensive logging to track execution flow
- Include unit tests to validate marker file generation
- Document the webhook automation testing process

This provides a low-risk, easily verifiable test case for the webhook automation system.

## Relevant Files

Use these files to implement the feature:

### ADW Infrastructure Files
- **adw/adw_triggers/trigger_webhook.py** - FastAPI webhook endpoint that receives GitHub events. Shows how webhooks trigger workflows and extract ADW info. Review to understand webhook event handling and workflow triggering logic.
- **adw/adw_triggers/trigger_cron.py** - Cron-based trigger alternative. Shows polling mechanism and issue processing logic. Compare with webhook approach.
- **adw/adw_modules/workflow_ops.py** - Core workflow operations including format_issue_message(), AVAILABLE_ADW_WORKFLOWS list. Use for workflow execution patterns.
- **adw/adw_modules/state.py** - ADWState persistence management. Use to understand how state is tracked across workflow phases.
- **adw/adw_modules/utils.py** - Utility functions including make_adw_id(), setup_logger(). Use for consistent ID generation and logging.
- **adw/adw_modules/github.py** - GitHub API operations including make_issue_comment(). Use for posting results back to GitHub.
- **adw/adw_modules/data_types.py** - Pydantic models for ADW data structures. Extend if needed for test metadata.

### Documentation Files
- **WEBHOOK_SETUP.md** - Webhook setup guide showing configuration and testing process. Reference for understanding webhook flow.
- **adw/README.md** - ADW system documentation explaining isolated workflows, ADW IDs, and workflow chains. Use to understand system architecture.
- **CLAUDE.md** - Master documentation file. Update with webhook testing information if needed.

### Testing Reference Files
- **.claude/commands/test_e2e.md** - E2E test runner template. Shows test execution pattern and output format.
- **.claude/commands/e2e/test_basic_query.md** - Example E2E test structure. Use as reference for creating validation tests.
- **.claude/commands/conditional_docs.md** - Conditional documentation guide. Check if webhook testing should be added.

### New Files

#### Implementation Files
- **scripts/create_webhook_test_marker.py** - Python script to generate the webhook test marker file with metadata (issue_number, adw_id, timestamp, workflow_name, trigger_type).
- **.webhook_test_marker.json** - Generated marker file containing test execution metadata in JSON format.

#### Testing Files
- **adw/adw_tests/test_webhook_automation.py** - Unit tests for webhook test marker generation, file validation, and metadata accuracy.

#### E2E Validation
- **.claude/commands/e2e/test_webhook_automation.md** - E2E test file to validate webhook test marker exists and contains correct data.

#### Documentation
- **docs/webhook_testing_guide.md** - Guide for running webhook automation tests and interpreting results.

## Implementation Plan

### Phase 1: Foundation
Create the basic infrastructure for webhook testing:
1. Design the webhook test marker JSON schema (fields: issue_number, adw_id, timestamp, workflow_name, trigger_type, repository, branch_name)
2. Set up logging infrastructure to track webhook execution flow
3. Create placeholder for marker file generation script
4. Define test metadata data structure in Pydantic models (if needed)

### Phase 2: Core Implementation
Implement the webhook test marker generation:
1. Build `scripts/create_webhook_test_marker.py` script with:
   - Command-line argument parsing (issue_number, adw_id)
   - Metadata collection from environment and arguments
   - JSON file generation with proper formatting
   - Error handling and validation
2. Add logging to track marker creation process
3. Implement file writing with atomic operations to prevent corruption
4. Add validation to ensure marker file is well-formed JSON

### Phase 3: Integration
Integrate webhook testing with existing ADW workflows:
1. Create unit tests in `adw/adw_tests/test_webhook_automation.py` to verify:
   - Marker file is created with correct schema
   - Metadata accuracy (issue_number, adw_id match inputs)
   - Timestamp is in ISO 8601 format
   - File is valid JSON
2. Create E2E test file `.claude/commands/e2e/test_webhook_automation.md` to:
   - Verify marker file exists at repository root
   - Validate JSON structure and required fields
   - Check timestamp is recent (within test execution window)
   - Confirm ADW ID and issue number match
3. Update `docs/webhook_testing_guide.md` with:
   - How to trigger webhook tests manually
   - How to interpret marker file contents
   - Troubleshooting common webhook issues
   - Expected execution timeline

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Create webhook test marker schema and Python script
- Define JSON schema with required fields: issue_number, adw_id, timestamp, workflow_name, trigger_type, repository, branch_name
- Create `scripts/create_webhook_test_marker.py` with:
  - Argument parsing using argparse (--issue-number, --adw-id, --workflow, --trigger-type)
  - Environment variable collection (GITHUB_REPO_URL, current branch from git)
  - Timestamp generation in ISO 8601 format
  - JSON file writing to `.webhook_test_marker.json`
  - Error handling for file system operations
  - Logging for debugging
- Make script executable and add shebang line
- Test script manually to ensure it creates valid JSON

### 2. Create unit tests for marker generation
- Create `adw/adw_tests/test_webhook_automation.py` with test cases:
  - `test_marker_file_creation` - Verify file is created
  - `test_marker_json_valid` - Verify file contains valid JSON
  - `test_marker_schema` - Verify all required fields present
  - `test_marker_metadata_accuracy` - Verify field values match inputs
  - `test_marker_timestamp_format` - Verify ISO 8601 timestamp format
- Use pytest fixtures for temporary directories and cleanup
- Mock environment variables for consistent testing
- Add assertions for file existence, JSON validity, schema compliance

### 3. Create E2E test for webhook automation validation
- Read `.claude/commands/test_e2e.md` to understand E2E test structure
- Read `.claude/commands/e2e/test_basic_query.md` as reference example
- Create `.claude/commands/e2e/test_webhook_automation.md` with:
  - User Story: Validate webhook automation executed successfully
  - Test Steps:
    1. Verify `.webhook_test_marker.json` exists in repository root
    2. Read and parse JSON file
    3. Verify required fields exist (issue_number, adw_id, timestamp, workflow_name, trigger_type)
    4. Verify issue_number matches expected value (14)
    5. Verify adw_id matches expected value (685b74ed)
    6. Verify timestamp is in ISO 8601 format
    7. Verify timestamp is recent (within last hour)
    8. Take screenshot of file contents
  - Success Criteria:
    - Marker file exists
    - JSON is valid and well-formed
    - All required fields present
    - Metadata matches execution context
    - Timestamp indicates recent execution

### 4. Implement marker creation in workflow
- Update the plan to call `scripts/create_webhook_test_marker.py` during implementation phase
- Pass required arguments: issue_number (14), adw_id (685b74ed), workflow_name (adw_sdlc_iso or similar), trigger_type (webhook or manual)
- Ensure script runs successfully and creates marker file
- Verify marker file is committed to git

### 5. Create webhook testing documentation
- Create `docs/webhook_testing_guide.md` with sections:
  - **Overview**: Purpose of webhook automation testing
  - **How It Works**: Webhook event → trigger → plan → build → marker creation
  - **Running Tests**:
    - Manual trigger: Create issue with "adw_" keyword in body
    - Automatic trigger: Configure GitHub webhook
    - Validation: Check for `.webhook_test_marker.json` file
  - **Interpreting Results**:
    - Marker file presence indicates successful execution
    - Check timestamp to verify when workflow ran
    - Verify metadata matches trigger context
  - **Troubleshooting**:
    - Missing marker file → workflow didn't complete
    - Invalid JSON → script error during creation
    - Wrong metadata → argument passing issue
    - Old timestamp → workflow ran but wasn't recent
  - **Next Steps**: How to build on this test for production webhooks

### 6. Run validation commands
- Execute all validation commands listed in the `Validation Commands` section below
- Ensure all tests pass with zero errors
- Verify marker file is created and contains correct data
- Confirm E2E test validates marker file successfully

## Testing Strategy

### Unit Tests
Create comprehensive unit tests for webhook marker generation:

**Test Cases:**
1. **test_marker_file_creation**
   - Create marker file with test data
   - Assert file exists at expected path
   - Assert file permissions are correct

2. **test_marker_json_valid**
   - Create marker file
   - Read file contents
   - Assert JSON parses without errors
   - Assert returned data structure is dict

3. **test_marker_schema**
   - Create marker file with all fields
   - Parse JSON
   - Assert all required fields present: issue_number, adw_id, timestamp, workflow_name, trigger_type, repository, branch_name
   - Assert no extra unexpected fields

4. **test_marker_metadata_accuracy**
   - Create marker with specific test values
   - Parse JSON
   - Assert issue_number matches input
   - Assert adw_id matches input
   - Assert workflow_name matches input
   - Assert trigger_type matches input

5. **test_marker_timestamp_format**
   - Create marker file
   - Parse JSON
   - Assert timestamp matches ISO 8601 format (regex: `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}`)
   - Assert timestamp is parseable by datetime library

6. **test_marker_error_handling**
   - Test with missing required arguments
   - Assert script raises appropriate errors
   - Test with invalid file path
   - Assert error is logged correctly

**Fixtures:**
- `temp_dir`: Temporary directory for test marker files
- `sample_metadata`: Sample webhook metadata for testing
- `cleanup`: Automatic cleanup of test marker files

### Edge Cases
Test critical edge cases to ensure robustness:

1. **Concurrent Webhook Triggers**
   - Multiple webhooks trigger simultaneously
   - Each should create unique marker file (or append to array)
   - No file corruption or race conditions

2. **Missing Environment Variables**
   - GITHUB_REPO_URL not set
   - Script should handle gracefully with defaults or clear error message

3. **File System Permissions**
   - Repository root is read-only
   - Script should fail gracefully with clear error message

4. **Invalid Metadata Values**
   - Issue number is not an integer
   - ADW ID is wrong format (not 8 hex chars)
   - Script should validate inputs

5. **Large Metadata Payloads**
   - Very long branch names
   - Special characters in fields
   - JSON encoding should handle correctly

6. **File Already Exists**
   - Previous test marker exists
   - Script should overwrite or append (document behavior)

## Acceptance Criteria

- [x] `.webhook_test_marker.json` file is created in repository root
- [x] Marker file contains all required fields: issue_number, adw_id, timestamp, workflow_name, trigger_type, repository, branch_name
- [x] `scripts/create_webhook_test_marker.py` script is executable and well-documented
- [x] Unit tests in `adw/adw_tests/test_webhook_automation.py` cover marker creation, JSON validation, schema compliance, and metadata accuracy
- [x] E2E test in `.claude/commands/e2e/test_webhook_automation.md` validates marker file existence and contents
- [x] Documentation in `docs/webhook_testing_guide.md` explains how to run and interpret webhook tests
- [x] Marker file metadata accurately reflects webhook execution context (correct issue_number and adw_id)
- [x] Timestamp is in ISO 8601 format and indicates recent execution
- [x] All validation commands execute successfully with zero errors
- [x] JSON in marker file is valid and well-formed

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

**1. Create webhook test marker**
```bash
cd /Users/williamfung/agentic-coding-library/trees/685b74ed
python scripts/create_webhook_test_marker.py --issue-number 14 --adw-id 685b74ed --workflow adw_sdlc_iso --trigger-type webhook
```

**2. Verify marker file exists and is valid JSON**
```bash
cd /Users/williamfung/agentic-coding-library/trees/685b74ed
test -f .webhook_test_marker.json && echo "✅ Marker file exists" || echo "❌ Marker file missing"
cat .webhook_test_marker.json | python -m json.tool && echo "✅ Valid JSON" || echo "❌ Invalid JSON"
```

**3. Run unit tests for webhook automation**
```bash
cd /Users/williamfung/agentic-coding-library/trees/685b74ed
pytest adw/adw_tests/test_webhook_automation.py -v
```

**4. Read and execute E2E test for webhook automation**
Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_webhook_automation.md` test file to validate webhook automation works correctly.

**5. Verify all required fields in marker file**
```bash
cd /Users/williamfung/agentic-coding-library/trees/685b74ed
cat .webhook_test_marker.json | python -c "
import json, sys
data = json.load(sys.stdin)
required = ['issue_number', 'adw_id', 'timestamp', 'workflow_name', 'trigger_type', 'repository', 'branch_name']
missing = [f for f in required if f not in data]
if missing:
    print(f'❌ Missing fields: {missing}')
    sys.exit(1)
else:
    print('✅ All required fields present')
    print(f'  Issue: {data[\"issue_number\"]}')
    print(f'  ADW ID: {data[\"adw_id\"]}')
    print(f'  Timestamp: {data[\"timestamp\"]}')
    print(f'  Workflow: {data[\"workflow_name\"]}')
"
```

**6. Verify timestamp format**
```bash
cd /Users/williamfung/agentic-coding-library/trees/685b74ed
cat .webhook_test_marker.json | python -c "
import json, sys
from datetime import datetime
data = json.load(sys.stdin)
try:
    dt = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    print(f'✅ Valid ISO 8601 timestamp: {dt}')
except Exception as e:
    print(f'❌ Invalid timestamp format: {e}')
    sys.exit(1)
"
```

**7. Verify metadata accuracy**
```bash
cd /Users/williamfung/agentic-coding-library/trees/685b74ed
cat .webhook_test_marker.json | python -c "
import json, sys
data = json.load(sys.stdin)
errors = []
if data.get('issue_number') != '14':
    errors.append(f'Issue number mismatch: expected 14, got {data.get(\"issue_number\")}')
if data.get('adw_id') != '685b74ed':
    errors.append(f'ADW ID mismatch: expected 685b74ed, got {data.get(\"adw_id\")}')
if errors:
    print('❌ Metadata errors:')
    for e in errors:
        print(f'  - {e}')
    sys.exit(1)
else:
    print('✅ Metadata accurate')
"
```

**Note:** The following standard validation commands are NOT applicable to this library repository since it doesn't have app/server or app/client directories. This is a TAC framework library, not an application with server/client code.

## Notes

### Design Decisions

1. **Marker File Location**: Placed at repository root (`.webhook_test_marker.json`) for easy discovery and validation. Could be moved to `agents/{adw_id}/` for isolation, but root location better demonstrates end-to-end automation.

2. **Marker File Format**: JSON chosen for:
   - Easy parsing and validation
   - Human-readable
   - Standard format for metadata
   - Extensible for future fields

3. **Metadata Fields**: Selected to provide comprehensive webhook execution context:
   - `issue_number`: Links marker to triggering issue
   - `adw_id`: Unique workflow identifier for traceability
   - `timestamp`: When webhook executed (ISO 8601 for standardization)
   - `workflow_name`: Which ADW workflow ran
   - `trigger_type`: "webhook" vs "manual" for debugging
   - `repository`: GitHub repo URL for multi-repo setups
   - `branch_name`: Git branch for correlation

4. **Test Strategy**: Three-tier validation approach:
   - Unit tests: Fast, isolated testing of marker generation logic
   - E2E tests: Real-world validation of marker file in context
   - Manual validation: Bash commands for quick verification

### Future Enhancements

1. **Historical Tracking**: Instead of overwriting `.webhook_test_marker.json`, could append to array or create timestamped files (`markers/marker-{timestamp}.json`) for audit trail.

2. **Webhook Signature Validation**: Add verification that webhook actually came from GitHub using signature validation in marker metadata.

3. **Performance Metrics**: Add fields for execution time, resource usage, success/failure status.

4. **Multi-Webhook Support**: Handle multiple concurrent webhooks by using ADW ID in filename (`.webhook_test_marker_{adw_id}.json`).

5. **Cleanup Automation**: Add script to clean up old test markers after validation.

6. **Dashboard Integration**: Display marker data in webhook monitoring dashboard.

### Webhook Automation Context

This test feature validates the complete webhook automation chain described in `WEBHOOK_SETUP.md`:

```
Phone: Create issue →
GitHub: Fires webhook →
Laptop: Receives event (trigger_webhook.py) →
Agent: Processes autonomously (adw_plan_iso.py → adw_build_iso.py) →
GitHub: PR created!
```

The marker file provides proof that the entire chain executed successfully. When this plan is implemented via webhook automation, the resulting `.webhook_test_marker.json` file will demonstrate zero-touch execution from issue creation to implementation.

### Library Repository Note

This is a **library repository** for the TAC framework, not an application with server/client code. Therefore:
- No `app/server` or `app/client` directories exist
- Standard validation commands for pytest/TypeScript/build are NOT applicable
- Validation focuses on ADW system functionality and webhook automation
- Tests use `adw/adw_tests/` for framework-specific unit tests
- E2E tests validate ADW workflows, not application features
