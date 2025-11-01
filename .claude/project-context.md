# Spelling Tutor Voice Agent - Project Context

**Purpose:** LiveKit-powered voice agent for children ages 6-10 to practice spelling through phonics-based guidance.

**Stage:** MVP/Prototype

**Repository:** (Local development)

---

## Tech Stack

### Core Technologies
- **Language:** Python 3.8+
- **Framework:** LiveKit Agents 1.2.0+
- **Database:** SQLite (local storage)
- **Voice Services:** OpenAI TTS + Deepgram STT

### Key Dependencies
- `livekit>=0.15.0` - Real-time communication SDK
- `livekit-agents>=1.2.0` - Agent framework
- `livekit-plugins-openai>=1.0.0` - OpenAI TTS integration
- `livekit-plugins-deepgram>=1.0.0` - Deepgram STT integration
- `livekit-plugins-silero>=1.0.0` - Voice activity detection
- `livekit-plugins-turn-detector>=1.0.0` - Turn-based conversation
- `openai>=1.0.0` - OpenAI API client
- `deepgram-sdk>=3.0.0` - Deepgram API client
- `python-dotenv>=1.0.0` - Environment variable management
- `click>=8.0.0` - CLI framework

### Development Dependencies
- `pytest>=7.0.0` - Test framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-cov>=4.0.0` - Code coverage reporting

### Infrastructure
- **Hosting:** Local development / LiveKit Cloud
- **CI/CD:** None detected (can be added)
- **Voice Pipeline:** OpenAI "alloy" voice + Deepgram "nova-2" model

---

## Codebase Structure

```
spelling-tutor-agent/
├── src/spelling_tutor/        # Main application package
│   ├── agent.py               # LiveKit voice agent implementation
│   ├── agent_worker.py        # Agent worker launcher
│   ├── config.py              # Environment configuration
│   ├── database.py            # SQLite database operations
│   ├── main.py                # CLI interface
│   ├── tutor_logic.py         # Spelling tutor logic & phonics hints
│   ├── types.py               # Data classes
│   └── word_manager.py        # Word list file management
├── tests/                     # Test suite
│   ├── test_database.py       # Database tests
│   ├── test_tutor_logic.py    # Tutor logic tests
│   └── test_word_manager.py   # Word manager tests
├── data/
│   ├── word_lists/            # Text-based word lists (week1.txt, etc.)
│   └── spelling_tutor.db      # SQLite database
├── specs/                     # Project specifications
├── .claude/                   # Agentic coding framework
├── adw/                       # Automated development workflows
├── pyproject.toml             # Project configuration
└── .env                       # Environment variables (gitignored)
```

---

## Environment Variables

Required environment variables (see `.env.example`):

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_api_key

# Deepgram Configuration
DEEPGRAM_API_KEY=your_deepgram_api_key
```

**Setup:** Copy `.env.example` to `.env` and fill in API credentials.

---

## Coding Conventions

### Python Style
- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Async/await for all LiveKit agent methods
- Clear docstrings for public functions

### File Naming
- Snake_case for Python files: `agent_worker.py`
- Lowercase for directories: `spelling_tutor/`
- Descriptive names for word lists: `week1.txt`, `cvc_words.txt`

### Code Organization
- Keep agent logic in `agent.py`
- Separate business logic from framework code
- Database operations isolated in `database.py`
- Tutor logic and phonics rules in `tutor_logic.py`

### Testing
- Write tests for all new features
- Use pytest fixtures for setup/teardown
- Test async functions with pytest-asyncio
- Maintain high code coverage (current: detailed coverage tracking)

---

## Development Workflow

### Initial Setup
```bash
# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
# Then initialize database
python -m spelling_tutor.main setup --name "Emma" --age 7
```

### Daily Development
```bash
# Start agent in background
./manage_agent.sh start

# Check agent status
./manage_agent.sh status

# View live logs
./manage_agent.sh logs

# Stop agent
./manage_agent.sh stop

# Console testing mode (text-based)
python -m spelling_tutor.agent_worker console
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=spelling_tutor --cov-report=html

# Test specific module
pytest tests/test_tutor_logic.py -v
```

### Word List Management
```bash
# List all word lists
python3 list_words.py

# View words in a specific list
python3 list_words.py week1

# Add new word list (just create a .txt file)
cat > data/word_lists/week2.txt << EOF
apple
banana
orange
EOF
```

### LiveKit Testing
```bash
# Generate access token for testing
python3 generate_livekit_token.py

# Test in LiveKit Playground
# 1. Start agent: ./manage_agent.sh start
# 2. Generate token: python3 generate_livekit_token.py
# 3. Go to: https://agents-playground.livekit.io/
# 4. Paste URL and token
```

---

## Key Features

### Educational Approach
- **Progressive Hints:** 3-level phonics-based hint system
  - Level 1: Starting sound identification
  - Level 2: Syllable breakdown
  - Level 3: Phoneme analysis (CVC, digraphs, blends)
- **Close Spelling Detection:** Levenshtein distance for near-misses
- **Positive Reinforcement:** Encouraging feedback for children
- **Mastery Tracking:** Records attempts, hints, and success rates

### Architecture Highlights
- **File-Based Word Lists:** Easy to add/update via text files in `data/word_lists/`
- **Adaptive Learning:** Difficulty detection and personalized feedback
- **Voice Pipeline:** OpenAI TTS (child-friendly "alloy" voice) + Deepgram STT (accurate "nova-2" model)
- **LiveKit Integration:** Uses Agents 1.2.14+ framework with fixed thinking→speaking cycle

---

## What AI Should Know

### Always Do
- Run tests before committing (`pytest tests/ -v`)
- Maintain phonics-based educational approach in hints
- Keep voice agent child-friendly (ages 6-10)
- Preserve async/await patterns for LiveKit compatibility
- Update tests when adding new features
- Follow PEP 8 style guidelines

### Never Do
**Important:** Always ask before making significant changes to:
- Core agent logic in `agent.py`
- Database schema modifications
- Dependency version updates
- LiveKit framework integration code
- Voice pipeline configuration

### Ask First
- **Major architectural changes** - Discuss impact on LiveKit integration
- **New dependencies** - Verify compatibility with LiveKit Agents 1.2+
- **Database schema changes** - Requires migration planning
- **API changes** - Affects agent worker and CLI interface
- **Testing strategy changes** - Ensure coverage remains comprehensive

### Known Issues (Fixed in Latest Version)
- ✅ `RuntimeError: trying to generate reply without an LLM model` - Fixed
- ✅ `TypeError: on_user_turn_completed() got unexpected keyword argument` - Fixed
- OpenAI 500 errors are temporary service issues (agent auto-retries)

---

## Future Enhancement Ideas

Documented in README.md:
- Multi-user support for family accounts
- Custom phonics rules configuration
- Visual progress dashboard (web-based)
- Mobile app integration for parents
- Gamification (badges, streaks, achievements)
- Advanced AI-powered learning paths
- Multi-language and accent support
- Collaborative group spelling sessions

---

**Last Updated:** 2025-11-01
**Auto-generated by:** /begin command
**Maintained by:** William Fung
