# Spelling Tutor Voice Agent - MVP Specification

## High-Level Objective

Create a LiveKit voice agent that helps a single child practice spelling 15-25 words through interactive phonics-based guidance, with parent-managed word lists and basic progress tracking stored in SQLite.

## Mid-Level Objectives

- Build SQLite database schema for child profile, word lists, and session history
- Implement word list upload/management system for parents
- Create LiveKit voice agent with OpenAI TTS and Deepgram STT integration
- Design tutor logic using phonics-based hints and positive reinforcement
- Add CLI interface for parent word list management and agent launching
- Implement basic progress tracking (word mastery, session completion)

## Implementation Notes

- Use SQLite for database (easy to deploy, no server required)
- LiveKit Agents Python SDK for voice interaction
- OpenAI TTS (tts-1 model) for voice output
- Deepgram Nova-2 for speech-to-text
- Phonics hints follow Common Core standards (CVC, digraphs, blends)
- Agent personality: encouraging, patient, game-like tone
- Session length: 15-25 words, child can pause/resume
- Database schema: `child_profile`, `word_lists`, `words`, `sessions`, `word_attempts`
- Type hints for all functions
- Async/await pattern for LiveKit agent
- Environment variables for all API keys
- Comment every function with docstring

## Context

### Beginning Context
- Empty project directory
- Will create all files from scratch

### Ending Context
- `pyproject.toml` (new)
- `.env.example` (new)
- `.gitignore` (new)
- `README.md` (new)
- `src/spelling_tutor/__init__.py` (new)
- `src/spelling_tutor/types.py` (new)
- `src/spelling_tutor/config.py` (new)
- `src/spelling_tutor/database.py` (new)
- `src/spelling_tutor/word_manager.py` (new)
- `src/spelling_tutor/tutor_logic.py` (new)
- `src/spelling_tutor/agent.py` (new)
- `src/spelling_tutor/main.py` (new)
- `tests/test_database.py` (new)
- `tests/test_word_manager.py` (new)
- `tests/test_tutor_logic.py` (new)
- `data/word_lists/.gitkeep` (new)

## Low-Level Tasks
> Ordered from start to finish

### Task 1: Create project configuration and types
```
CREATE pyproject.toml:
    dependencies: livekit>=0.15.0, livekit-agents>=0.8.0, openai>=1.0.0, deepgram-sdk>=3.0.0, python-dotenv>=1.0.0
    dev-dependencies: pytest>=7.0.0, pytest-asyncio>=0.21.0, pytest-cov>=4.0.0

CREATE .env.example:
    LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
    OPENAI_API_KEY
    DEEPGRAM_API_KEY

CREATE .gitignore:
    __pycache__/, *.pyc, .env, *.db, .pytest_cache/, data/word_lists/*.txt

CREATE src/spelling_tutor/types.py:
    class ChildProfile: id: int, name: str, age: int, created_at: str
    class WordList: id: int, name: str, created_at: str
    class Word: id: int, word_list_id: int, word: str, difficulty: str
    class Session: id: int, child_id: int, word_list_id: int, started_at: str, completed_at: str | None
    class WordAttempt: id: int, session_id: int, word_id: int, attempts: int, correct: bool, hints_used: list[str]
```

### Task 2: Create configuration management
```
CREATE src/spelling_tutor/config.py:
    def load_config() -> dict:
        load from .env using dotenv
        validate required keys: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, OPENAI_API_KEY, DEEPGRAM_API_KEY
        return config dict
    
    def get_db_path() -> str:
        return "data/spelling_tutor.db"
```

### Task 3: Create database layer
```
CREATE src/spelling_tutor/database.py:
    import sqlite3, types.py
    
    def init_database(db_path: str) -> None:
        create tables: child_profiles, word_lists, words, sessions, word_attempts
        add indexes on foreign keys
    
    def create_child_profile(name: str, age: int) -> ChildProfile
    def get_child_profile(child_id: int) -> ChildProfile | None
    
    def create_word_list(name: str, words: list[str]) -> WordList:
        insert word_list, then insert words with difficulty auto-detected
    
    def get_word_list(word_list_id: int) -> tuple[WordList, list[Word]]
    def list_word_lists() -> list[WordList]
    
    def create_session(child_id: int, word_list_id: int) -> Session
    def complete_session(session_id: int) -> None
    def get_child_sessions(child_id: int) -> list[Session]
    
    def record_word_attempt(session_id: int, word_id: int, attempts: int, correct: bool, hints_used: list[str]) -> None
    def get_word_mastery(child_id: int, word_id: int) -> dict:
        return {total_attempts: int, correct_count: int, mastery_level: float}

CREATE tests/test_database.py:
    def test_init_database()
    def test_create_child_profile()
    def test_create_word_list()
    def test_session_workflow()
    def test_word_mastery_calculation()
```

### Task 4: Create word management system
```
CREATE src/spelling_tutor/word_manager.py:
    def parse_word_list_file(file_path: str) -> list[str]:
        read text file, one word per line, strip whitespace, lowercase
    
    def detect_word_difficulty(word: str) -> str:
        return "easy" if len <= 4
        return "medium" if 5 <= len <= 7
        return "hard" if len > 7
    
    def upload_word_list(name: str, file_path: str) -> WordList:
        parse file, create word list in database
    
    def get_phonics_category(word: str) -> str:
        detect CVC, digraphs (sh, ch, th, wh), blends (bl, cr, st, etc)
        return category string

CREATE tests/test_word_manager.py:
    def test_parse_word_list_file()
    def test_detect_word_difficulty()
    def test_get_phonics_category()
```

### Task 5: Create tutor logic with phonics hints
```
CREATE src/spelling_tutor/tutor_logic.py:
    class SpellingTutor:
        def __init__(self, word: str, difficulty: str)
        
        def get_introduction(self) -> str:
            return encouraging phrase + "Let's spell the word [word]"
        
        def get_phonics_hint(self, attempt_number: int) -> str:
            attempt 1: "Think about the sounds you hear. What sound does it start with?"
            attempt 2: "Let's break it into parts. It has [syllable_count] syllables."
            attempt 3: "The word has these sounds: [phoneme_breakdown]"
            return hint based on attempt number and phonics_category
        
        def check_spelling(self, user_input: str) -> tuple[bool, str]:
            normalize input (lowercase, strip)
            if correct: return True, positive_feedback()
            if close (1-2 chars off): return False, "Almost! Try again."
            return False, get_phonics_hint()
        
        def get_positive_feedback(self) -> str:
            return random encouraging phrase: "Awesome!", "Great job!", "You got it!", "Fantastic!"

CREATE tests/test_tutor_logic.py:
    def test_get_phonics_hint()
    def test_check_spelling_correct()
    def test_check_spelling_close()
    def test_positive_feedback()
```

### Task 6: Create LiveKit voice agent
```
CREATE src/spelling_tutor/agent.py:
    import livekit, livekit.agents, openai, deepgram
    from tutor_logic import SpellingTutor
    from database import get_word_list, create_session, record_word_attempt, complete_session
    
    class SpellingTutorAgent:
        def __init__(self, config: dict, child_id: int, word_list_id: int)
        
        async def start(self) -> None:
            initialize LiveKit room
            setup OpenAI TTS (tts-1, voice: nova)
            setup Deepgram STT (nova-2)
            load word list from database
            create session in database
            await self.run_session()
        
        async def run_session(self) -> None:
            for word in self.words:
                tutor = SpellingTutor(word.word, word.difficulty)
                await self.speak(tutor.get_introduction())
                
                attempts = 0
                max_attempts = 3
                correct = False
                hints_used = []
                
                while attempts < max_attempts and not correct:
                    user_input = await self.listen()
                    attempts += 1
                    correct, feedback = tutor.check_spelling(user_input)
                    
                    if not correct and attempts < max_attempts:
                        hint = tutor.get_phonics_hint(attempts)
                        hints_used.append(hint)
                        await self.speak(f"{feedback} {hint}")
                    else:
                        await self.speak(feedback)
                
                record_word_attempt(self.session.id, word.id, attempts, correct, hints_used)
                
                if not correct:
                    await self.speak(f"The correct spelling is {word.word}. Let's remember this!")
            
            complete_session(self.session.id)
            await self.speak("Great work today! You've completed your spelling practice!")
        
        async def speak(self, text: str) -> None:
            use OpenAI TTS to generate audio
            send to LiveKit room
        
        async def listen(self) -> str:
            use Deepgram STT to transcribe
            return user speech as text
```

### Task 7: Create CLI interface
```
CREATE src/spelling_tutor/main.py:
    import click, asyncio
    from config import load_config, get_db_path
    from database import init_database, create_child_profile, list_word_lists
    from word_manager import upload_word_list
    from agent import SpellingTutorAgent
    
    @click.group()
    def cli():
        """Spelling Tutor Voice Agent CLI"""
        pass
    
    @cli.command()
    @click.option("--name", required=True, help="Child's name")
    @click.option("--age", required=True, type=int, help="Child's age")
    def setup(name: str, age: int):
        """Initialize database and create child profile"""
        init_database(get_db_path())
        child = create_child_profile(name, age)
        click.echo(f"Profile created! Child ID: {child.id}")
    
    @cli.command()
    @click.option("--name", required=True, help="Word list name")
    @click.option("--file", required=True, type=click.Path(exists=True), help="Word list file")
    def upload(name: str, file: str):
        """Upload a word list from text file"""
        word_list = upload_word_list(name, file)
        click.echo(f"Uploaded {name} with {len(word_list.words)} words")
    
    @cli.command()
    def list_words():
        """List all word lists"""
        lists = list_word_lists()
        for wl in lists:
            click.echo(f"ID: {wl.id} | Name: {wl.name} | Created: {wl.created_at}")
    
    @cli.command()
    @click.option("--child-id", required=True, type=int)
    @click.option("--word-list-id", required=True, type=int)
    def start(child_id: int, word_list_id: int):
        """Start spelling practice session"""
        config = load_config()
        agent = SpellingTutorAgent(config, child_id, word_list_id)
        asyncio.run(agent.start())
    
    if __name__ == "__main__":
        cli()
```

### Task 8: Create README documentation
```
CREATE README.md:
    # Spelling Tutor Voice Agent
    
    ## Setup
    1. Install: pip install -e ".[dev]"
    2. Configure: cp .env.example .env (fill in API keys)
    3. Initialize: python -m spelling_tutor.main setup --name "Alex" --age 8
    
    ## Usage
    Upload word list:
        python -m spelling_tutor.main upload --name "Week 1" --file words.txt
    
    List word lists:
        python -m spelling_tutor.main list-words
    
    Start session:
        python -m spelling_tutor.main start --child-id 1 --word-list-id 1
    
    ## Testing
    pytest tests/ -v
    
    ## Word List Format
    Create a .txt file with one word per line:
    cat
    dog
    jump
    play
```

### Task 9: Add comprehensive tests
```
UPDATE tests/test_database.py:
    ADD test for init_database creates all tables
    ADD test for child_profile CRUD
    ADD test for word_list creation with difficulty detection
    ADD test for session workflow: create, record attempts, complete
    ADD test for word_mastery calculation

UPDATE tests/test_word_manager.py:
    ADD test for parse_word_list_file with sample file
    ADD test for detect_word_difficulty edge cases
    ADD test for get_phonics_category coverage

UPDATE tests/test_tutor_logic.py:
    ADD test for get_introduction()
    ADD test for get_phonics_hint progression
    ADD test for check_spelling with correct/incorrect/close inputs
    ADD test for positive_feedback randomization
```

---

## Testing Strategy

**Framework:** pytest with pytest-asyncio for async tests

**Run tests:**
```bash
pytest tests/ -v
pytest tests/ --cov=src/spelling_tutor --cov-report=html
```

**Test Coverage Goals:**
- Database operations: 90%+
- Word manager functions: 95%+
- Tutor logic: 85%+
- Agent: 70% (mocking LiveKit/API calls)

---

## Success Criteria

✅ Database initializes with correct schema
✅ Parent can upload word list from .txt file
✅ Child profile created and stored
✅ Voice agent connects to LiveKit room
✅ Agent speaks introductions and feedback via OpenAI TTS
✅ Agent listens to child input via Deepgram STT
✅ Phonics hints provided based on attempt number
✅ Progress tracked: attempts, hints used, mastery
✅ Session completes and stores history
✅ All tests pass with 80%+ coverage