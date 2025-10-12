# Quick Start Guide

## Starting the Agent

```bash
./manage_agent.sh start
```

The script will automatically:
- Clean up any orphaned processes
- Start the agent in the background
- Save logs to `agent.log`

## Connecting to the Agent

1. **Generate a token:**
   ```bash
   python3 generate_livekit_token.py
   ```

2. **Copy the token** (saved to `livekit_token.txt`)

3. **Go to LiveKit Playground:**
   https://agents-playground.livekit.io/

4. **Paste your URL and token:**
   - URL: `wss://pediatricspellingtutor-fw79y05e.livekit.cloud`
   - Token: (the one you just generated)

5. **Click Connect** and start practicing!

## Managing the Agent

```bash
./manage_agent.sh status   # Check if running
./manage_agent.sh logs     # View live logs (Ctrl+C to exit)
./manage_agent.sh stop     # Stop the agent
./manage_agent.sh restart  # Restart the agent
```

## Managing Word Lists

### View available word lists:
```bash
python3 list_words.py
```

### View words in a specific list:
```bash
python3 list_words.py week1
```

### Add a new word list:
Just create a text file in `data/word_lists/`:

```bash
cat > data/word_lists/week2.txt << EOF
apple
banana
orange
grape
strawberry
EOF
```

### Edit existing word list:
```bash
nano data/word_lists/week1.txt
# or
code data/word_lists/week1.txt
```

Changes take effect immediately on next session!

## Using a Different Word List

Generate a token with a specific word list:

```bash
python3 generate_livekit_token.py --word-list week2
```

## Troubleshooting

### Agent won't start (port conflict)
```bash
./manage_agent.sh stop    # This will clean up all processes
./manage_agent.sh start   # Start fresh
```

### Check agent logs
```bash
tail -f agent.log
```

### Agent status
```bash
./manage_agent.sh status
```

## Quick Commands Summary

| Command | Description |
|---------|-------------|
| `./manage_agent.sh start` | Start the agent |
| `./manage_agent.sh stop` | Stop the agent |
| `./manage_agent.sh status` | Check agent status |
| `./manage_agent.sh logs` | View live logs |
| `python3 generate_livekit_token.py` | Generate access token |
| `python3 list_words.py` | List word lists |
| `python3 list_words.py week1` | View words in list |

## Notes

- The agent runs in the background and uses port 8081
- Stop the agent when not in use to free up resources: `./manage_agent.sh stop`
- Each token is valid for 24 hours
- Word lists are loaded from `data/word_lists/` directory
- The default word list is `week1.txt`
