# [Project Name] - Project Context

**Purpose:** This file provides AI agents with essential project context to work effectively.

**TAC Principle:** Agent Perspective - Structure for AI consumption, not just human reference.

---

## Project Overview

**Name:** [Your project name]

**Purpose:** [What this project does in 1-2 sentences]

**Stage:** [MVP / Development / Production]

**Repository:** [GitHub URL]

**Documentation:** [Link to main docs]

---

## Tech Stack

### Core Technologies
- **Language:** [Python / JavaScript / Go / Rust / etc.]
- **Version:** [Specific version - e.g., Python 3.11, Node 20.x]
- **Framework:** [Django / React / FastAPI / Next.js / etc.]
- **Database:** [PostgreSQL / MongoDB / etc.]

### Key Dependencies
1. **[Library 1]** (v[X.Y.Z]) - [Purpose - e.g., Authentication]
2. **[Library 2]** (v[X.Y.Z]) - [Purpose - e.g., API client]
3. **[Library 3]** (v[X.Y.Z]) - [Purpose - e.g., Testing]
4. **[Library 4]** (v[X.Y.Z]) - [Purpose - e.g., State management]
5. **[Library 5]** (v[X.Y.Z]) - [Purpose - e.g., UI components]

### Infrastructure
- **Hosting:** [Vercel / AWS / Heroku / etc.]
- **CI/CD:** [GitHub Actions / GitLab CI / etc.]
- **Monitoring:** [Sentry / DataDog / etc.]

---

## Codebase Structure

```
your-project/
├── src/                  # Source code
│   ├── components/       # [What goes here]
│   ├── services/         # [What goes here]
│   ├── utils/            # [What goes here]
│   └── types/            # [Type definitions]
├── tests/                # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── config/               # Configuration files
├── docs/                 # Documentation
├── .claude/              # Claude Code configuration
│   ├── commands/         # Workflow commands
│   ├── specs/            # Feature specifications
│   └── project-context.md  # This file
└── [other directories]
```

### Key Files
- `[file1.ext]` - [Purpose]
- `[file2.ext]` - [Purpose]
- `[file3.ext]` - [Purpose]

---

## Environment Variables

### Required
- `VAR_NAME` - [Purpose and where to get it]
- `API_KEY` - [Purpose and where to get it]
- `DATABASE_URL` - [Connection string format]

### Optional
- `OPTIONAL_VAR` - [Purpose and default value]

### Where to Find Values
- See `.env.example` for template
- Secrets stored in: [1Password / AWS Secrets Manager / etc.]
- Local development: [Instructions]

---

## Coding Conventions

### Naming Conventions
- **Files:** [kebab-case / snake_case / PascalCase]
- **Functions:** [camelCase / snake_case]
- **Classes:** [PascalCase]
- **Constants:** [UPPER_SNAKE_CASE]
- **Components:** [PascalCase for React, etc.]

### Code Organization
- **One component per file:** Yes / No
- **File naming:** [Match export name / descriptive]
- **Import order:** [Standard library, external, internal]
- **Export pattern:** [Named exports / default exports]

### Testing Conventions
- **Framework:** [Jest / Pytest / etc.]
- **Coverage Target:** [80% / 90% / etc.]
- **Test File Naming:** `[name].test.js` or `test_[name].py`
- **Test Structure:** [Arrange-Act-Assert / Given-When-Then]

### Code Quality
- **Linter:** [ESLint / Pylint / Clippy / etc.]
- **Formatter:** [Prettier / Black / rustfmt / etc.]
- **Type Checking:** [TypeScript / mypy / etc.]
- **Pre-commit Hooks:** [Yes/No - what they check]

---

## Development Workflow

### Initial Setup
```bash
# Clone repository
git clone [repo-url]

# Install dependencies
[npm install / pip install -r requirements.txt / etc.]

# Setup environment
cp .env.example .env
# Edit .env with your values

# Run migrations (if applicable)
[migration command]
```

### Daily Development
```bash
# Start dev server
[npm run dev / python manage.py runserver / etc.]

# Run tests
[npm test / pytest / etc.]

# Run linter
[npm run lint / pylint src/ / etc.]

# Run type checker (if applicable)
[npm run type-check / mypy src/ / etc.]
```

### Before Committing
```bash
# Run all checks
[npm run lint && npm test && npm run build]

# Format code (if not auto-formatted)
[npm run format / black src/ / etc.]
```

### Build & Deploy
```bash
# Build for production
[npm run build / python setup.py build / etc.]

# Deploy (if applicable)
[deployment command or process]
```

---

## What AI Should Know

### Always Do
- [Run tests before committing]
- [Follow the naming conventions above]
- [Update documentation when changing APIs]
- [Add tests for new features]
- [Check for security vulnerabilities]

### Never Do
- [Commit directly to main branch]
- [Skip tests or linting]
- [Hardcode secrets or API keys]
- [Remove error handling without replacement]
- [Make breaking changes without version bump]

### Ask First
- [Database schema changes]
- [Dependency version updates (major versions)]
- [Architecture changes]
- [API contract changes]
- [Changes affecting other teams/services]

---

## Knowledge Gaps - MCP Resources

### Recommended MCP Servers
To fill knowledge gaps, connect these MCP servers:

1. **Official Framework Docs**
   - Server: Archon MCP or similar
   - For: [Framework name] latest patterns and APIs
   - When: Starting new features using framework

2. **Project-Specific Docs**
   - Server: [Your custom MCP / GitHub MCP]
   - For: Internal documentation and conventions
   - When: Understanding project architecture

3. **Database Docs**
   - Server: [Database documentation MCP]
   - For: Query optimization and schema patterns
   - When: Working with database

### Documentation Links
- **Framework Docs:** [URL]
- **API Docs:** [URL]
- **Architecture Docs:** [URL or path in repo]
- **Runbooks:** [URL or path]

### Common Knowledge Gaps
Based on past work, AI often needs:
- [Common gap 1 - e.g., "Latest React 18 patterns"]
- [Common gap 2 - e.g., "Internal API authentication flow"]
- [Common gap 3 - e.g., "Deployment process details"]

Use `/knowledge_gap_check` command before starting work.

---

## Testing Strategy

### Test Levels
1. **Unit Tests:** Test individual functions/components
2. **Integration Tests:** Test component interactions
3. **E2E Tests:** Test full user workflows

### Running Tests
```bash
# All tests
[npm test]

# Specific test file
[npm test -- path/to/test.js]

# With coverage
[npm run test:coverage]

# E2E tests
[npm run test:e2e]

# Watch mode (for development)
[npm test -- --watch]
```

### Test Requirements
- New features MUST have tests
- Bug fixes MUST have regression tests
- Coverage must not decrease
- All tests must pass before merge

---

## Performance Targets

- **Page Load:** [<2s / <3s / etc.]
- **API Response:** [<300ms / <500ms / etc.]
- **Time to Interactive:** [<3s / <5s / etc.]
- **Bundle Size:** [<500KB / <1MB / etc.]

Monitor via: [Tool or process]

---

## Security Requirements

### Authentication
- **Method:** [OAuth / JWT / Session-based]
- **Provider:** [Auth0 / Custom / etc.]
- **Token Storage:** [localStorage / httpOnly cookies]

### Authorization
- **Pattern:** [RBAC / ABAC / etc.]
- **Roles:** [Admin, User, Guest, etc.]

### Security Practices
- All user input MUST be validated
- SQL injection prevention: [Parameterized queries]
- XSS prevention: [Content Security Policy, sanitization]
- CSRF protection: [CSRF tokens]
- Dependencies: Regular security audits

---

## Success Criteria

### Project Goals
- [ ] [Key goal 1 - measurable]
- [ ] [Key goal 2 - measurable]
- [ ] [Key goal 3 - measurable]

### Quality Gates
- [ ] Test coverage >80%
- [ ] No critical security vulnerabilities
- [ ] All linting rules passing
- [ ] Performance targets met
- [ ] Accessibility WCAG 2.1 AA (if applicable)

---

## Team & Collaboration

### Code Review Process
- [Process description - e.g., "2 approvals required"]
- [Review checklist location]

### Communication Channels
- **Issues:** GitHub Issues
- **Chat:** [Slack / Discord / etc.]
- **Docs:** [Notion / Confluence / etc.]

### Release Process
- **Versioning:** [Semantic versioning]
- **Release Schedule:** [Continuous / Weekly / etc.]
- **Changelog:** [Keep a CHANGELOG.md]

---

## Troubleshooting

### Common Issues

**Issue:** [Common problem 1]
**Solution:** [How to fix]

**Issue:** [Common problem 2]
**Solution:** [How to fix]

### Getting Help
- Check `docs/` directory
- Ask in [team channel]
- Review past issues/PRs for similar problems

---

## Related Documentation

- **TAC Principles:** `.claude/TAC-PRINCIPLES.md`
- **Commands Reference:** `.claude/commands/`
- **Validation Checklists:** `.claude/validation-checklists/`
- **Spec Templates:** `templates/spec-template.md`

---

**Last Updated:** [Date]
**Maintained By:** [Team/Person]

---

## Notes for AI

This project-context.md file should be:
- ✅ **Read before every new task** via `/prime` or `/start`
- ✅ **Referenced in specs** via "From project-context.md"
- ✅ **Updated when conventions change**
- ✅ **Kept concise** but comprehensive

When in doubt, `/knowledge_gap_check` will identify what else you need to know.