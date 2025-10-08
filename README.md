# Spelling Tutor Voice Agent

LiveKit-powered voice agent for children ages 6-10 to practice spelling through phonics-based guidance.

## Features

- 🗣️ **Voice Interaction** - Natural speech-to-text and text-to-speech using OpenAI and Deepgram
- 📚 **Phonics Hints** - Progressive educational hints based on CVC patterns, digraphs, and blends
- 📊 **Progress Tracking** - Detailed session history and word mastery analytics
- 👨‍👩‍👧‍👦 **Parent-Managed Word Lists** - Easy upload and management of custom word lists
- 💾 **SQLite Storage** - Local database for child profiles, sessions, and progress data
- 🎯 **Adaptive Learning** - Difficulty detection and personalized feedback
- 🎵 **Child-Friendly** - Encouraging feedback and age-appropriate voice interaction

## Requirements

- **Python 3.10+**
- **LiveKit Account** - For real-time voice communication
- **OpenAI API Key** - For text-to-speech generation
- **Deepgram API Key** - For speech-to-text transcription

## Setup

### Step 1: Install Dependencies
```bash
pip install -e ".[dev]"
```

### Step 2: Copy Environment File
```bash
cp .env.example .env
```

### Step 3: Fill in API Keys
Edit `.env` file with your API credentials:

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

### Step 4: Initialize Database and Create Child Profile
```bash
python -m spelling_tutor.main setup --name "Emma" --age 7
```

## Usage

### Start Voice Agent

Start the LiveKit voice agent worker:
```bash
python -m spelling_tutor.agent_worker
```

For console testing with text/audio input:
```bash
python -m spelling_tutor.agent_worker console
```

The agent will:
- Connect to your LiveKit server using Agents Framework 1.2.14+
- Initialize with child_id=1 and word_list_id=1 (configurable in production)
- Provide voice-based spelling practice with OpenAI TTS (nova voice) and Deepgram STT
- Process spelling attempts and provide phonics-based hints
- Track progress in the local SQLite database

**Features:**
- 🎯 **Adaptive Learning**: Progressive hints based on attempt number
- 🔊 **Child-Friendly Voice**: OpenAI TTS with "nova" voice optimized for children
- 🎤 **Accurate Recognition**: Deepgram STT with "nova-2" model
- 📊 **Progress Tracking**: Records attempts, hints used, and success rates
- 🧠 **Smart Hints**: Phonics-based hints using CVC patterns, digraphs, and blends

**Console Mode**: Press [Ctrl+B] to toggle between text/audio input, [Q] to quit.

Note: The agent worker must be running before users can connect via LiveKit client SDK or Agents Playground.

### Upload Word List
```bash
python -m spelling_tutor.main upload --name "Week 1 Words" --file data/word_lists/week1.txt
```

### List Word Lists
```bash
python -m spelling_tutor.main list-words
```


### Check Progress
```bash
python -m spelling_tutor.main show-progress --child-id 1
```

## Word List Format

Word lists should be text files with one word per line:

```txt
cat
dog
house
friend
school
elephant
```

Example file: `data/word_lists/week1.txt`

## Testing

### Test Voice Agent
Test the voice agent in console mode:
```bash
python -m spelling_tutor.agent_worker console
```

Try speaking or typing spelling attempts like:
- "cat" (correct spelling)
- "kat" (close spelling - should give hints)
- "dog" (wrong word - should provide hints)

### Run All Tests
```bash
pytest tests/ -v
```

### Run Tests with Coverage
```bash
pytest tests/ --cov=spelling_tutor --cov-report=html
```

## Troubleshooting

### Voice Agent Issues

**No audio output:**
- Verify OpenAI API key is valid and has sufficient credits
- Check system audio settings and volume
- Try console mode for testing: `python -m spelling_tutor.agent_worker console`

**Speech recognition not working:**
- Verify Deepgram API key is valid
- Check microphone permissions on macOS
- Ensure your microphone is working and not muted

**Agent startup errors:**
```bash
# Test configuration
python -c "from spelling_tutor.config import Config; c = Config(); print('✅ Config loaded')"

# Test database
python -c "from spelling_tutor.database import get_word_list; print('✅ Database accessible')"
```

**Missing environment variables:**
```bash
# Copy and edit the environment file
cp .env.example .env
# Then edit .env with your API keys
```

### Common Error Messages

- `RuntimeError: trying to generate reply without an LLM model` → Fixed in latest version
- `TypeError: on_user_turn_completed() got unexpected keyword argument` → Fixed in latest version
- `OpenAI 500 server error` → Temporary OpenAI service issue, agent will retry automatically

## How It Works

The spelling tutor provides an adaptive learning experience:

1. **Progressive Hints**: The tutor provides 3 levels of hints using phonics principles:
   - **Attempt 1**: "What sound does it start with?"
   - **Attempt 2**: Syllable breakdown
   - **Attempt 3**: Phoneme analysis (CVC, digraphs, blends)

2. **Close Spelling Detection**: Uses Levenshtein distance to detect near-misses and provide "Almost! Try again." feedback

3. **Positive Feedback**: Random encouraging responses for correct answers

4. **Mastery Tracking**: Records attempts, hints used, and success rates per word for detailed progress analysis

## Project Structure

```
spelling-tutor-agent/
├── src/spelling_tutor/
│   ├── __init__.py
│   ├── agent.py              # LiveKit voice agent
│   ├── agent_worker.py       # Agent worker launcher
│   ├── config.py             # Environment configuration
│   ├── database.py           # SQLite database operations
│   ├── main.py               # CLI interface
│   ├── tutor_logic.py        # Spelling tutor logic
│   ├── types.py              # Data classes
│   └── word_manager.py       # Word list management
├── tests/
│   ├── test_database.py      # Database tests
│   ├── test_tutor_logic.py   # Tutor logic tests
│   └── test_word_manager.py  # Word manager tests
├── data/
│   ├── word_lists/           # Sample word lists
│   └── spelling_tutor.db     # SQLite database
├── specs/
│   └── specs_mvp.md          # Project specifications
├── pyproject.toml            # Project configuration
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Future Enhancements

- 🌐 **Multi-User Support** - Multiple children per family account
- 🎨 **Custom Phonics Rules** - Configurable phonics pattern detection
- 📈 **Visual Progress Dashboard** - Web-based progress visualization
- 📱 **Mobile App Integration** - Companion mobile app for parents
- 🎮 **Gamification** - Badges, streaks, and achievement systems
- 🤖 **AI Tutoring** - Advanced AI-powered personalized learning paths
- 🗣️ **Accent Support** - Multiple language and accent recognition
- 👥 **Collaborative Learning** - Group spelling sessions with friends

## License

MIT License

Copyright (c) 2025 Spelling Tutor Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.