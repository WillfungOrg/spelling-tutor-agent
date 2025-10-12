#!/bin/bash
# Agent management script for spelling tutor

AGENT_LOG="agent.log"
AGENT_PID_FILE=".agent.pid"

case "$1" in
  start)
    # Check if already running
    if [ -f "$AGENT_PID_FILE" ]; then
      PID=$(cat "$AGENT_PID_FILE")
      if ps -p "$PID" > /dev/null 2>&1; then
        echo "❌ Agent is already running (PID: $PID)"
        exit 1
      fi
    fi

    # Clean up any orphaned processes on port 8081
    PORT_PID=$(lsof -t -i :8081 2>/dev/null)
    if [ -n "$PORT_PID" ]; then
      echo "⚠️  Cleaning up orphaned process on port 8081 (PID: $PORT_PID)..."
      kill "$PORT_PID" 2>/dev/null || kill -9 "$PORT_PID" 2>/dev/null
      sleep 1
    fi

    # Clean up any orphaned agent_worker processes
    ORPHAN_PIDS=$(pgrep -f "spelling_tutor.agent_worker" 2>/dev/null)
    if [ -n "$ORPHAN_PIDS" ]; then
      echo "⚠️  Cleaning up orphaned agent processes..."
      pkill -f "spelling_tutor.agent_worker" 2>/dev/null
      sleep 1
    fi

    echo "🚀 Starting spelling tutor agent..."
    rm -f "$AGENT_LOG"
    nohup python -m spelling_tutor.agent_worker start > "$AGENT_LOG" 2>&1 &
    AGENT_PID=$!
    echo $AGENT_PID > "$AGENT_PID_FILE"

    echo "⏳ Waiting for agent to initialize..."
    sleep 5

    if ps -p "$AGENT_PID" > /dev/null 2>&1; then
      if grep -q "registered worker" "$AGENT_LOG"; then
        WORKER_ID=$(grep "registered worker" "$AGENT_LOG" | tail -1 | grep -o '"id": "[^"]*"' | cut -d'"' -f4)
        echo "✅ Agent started successfully!"
        echo "   PID: $AGENT_PID"
        echo "   Worker ID: $WORKER_ID"
        echo "   Log: tail -f $AGENT_LOG"
      else
        echo "⚠️  Agent started but may not be ready yet"
        echo "   Check logs: tail -f $AGENT_LOG"
      fi
    else
      echo "❌ Agent failed to start. Check $AGENT_LOG for errors"
      rm -f "$AGENT_PID_FILE"
      exit 1
    fi
    ;;

  stop)
    if [ ! -f "$AGENT_PID_FILE" ]; then
      echo "🔍 No PID file found. Checking for running agents..."
      pkill -f "spelling_tutor.agent_worker" && echo "✅ Stopped all agent processes" || echo "ℹ️  No agent processes found"
      exit 0
    fi

    PID=$(cat "$AGENT_PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
      echo "🛑 Stopping agent (PID: $PID)..."
      kill "$PID"
      sleep 2

      # Force kill if still running
      if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  Agent didn't stop gracefully, force killing..."
        kill -9 "$PID"
      fi

      echo "✅ Agent stopped"
    else
      echo "ℹ️  Agent is not running (stale PID file)"
    fi

    rm -f "$AGENT_PID_FILE"

    # Clean up any other agent processes
    pkill -f "spelling_tutor.agent_worker" 2>/dev/null
    ;;

  restart)
    "$0" stop
    sleep 2
    "$0" start
    ;;

  status)
    if [ -f "$AGENT_PID_FILE" ]; then
      PID=$(cat "$AGENT_PID_FILE")
      if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Agent is running (PID: $PID)"

        # Show worker ID if available
        if [ -f "$AGENT_LOG" ] && grep -q "registered worker" "$AGENT_LOG"; then
          WORKER_ID=$(grep "registered worker" "$AGENT_LOG" | tail -1 | grep -o '"id": "[^"]*"' | cut -d'"' -f4)
          echo "   Worker ID: $WORKER_ID"
        fi

        # Show uptime
        UPTIME=$(ps -o etime= -p "$PID" | tr -d ' ')
        echo "   Uptime: $UPTIME"

        # Show port
        PORT=$(lsof -p "$PID" -a -i :8081 2>/dev/null | grep LISTEN | wc -l | tr -d ' ')
        if [ "$PORT" -gt 0 ]; then
          echo "   Port 8081: ✅ Listening"
        fi

        exit 0
      else
        echo "❌ Agent is not running (stale PID file)"
        rm -f "$AGENT_PID_FILE"
        exit 1
      fi
    else
      # Check if any agent processes are running
      PIDS=$(pgrep -f "spelling_tutor.agent_worker")
      if [ -n "$PIDS" ]; then
        echo "⚠️  Agent processes found without PID file:"
        echo "$PIDS" | while read pid; do
          echo "   PID: $pid"
        done
        exit 1
      else
        echo "❌ Agent is not running"
        exit 1
      fi
    fi
    ;;

  logs)
    if [ -f "$AGENT_LOG" ]; then
      tail -f "$AGENT_LOG"
    else
      echo "❌ No log file found"
      exit 1
    fi
    ;;

  *)
    echo "Spelling Tutor Agent Manager"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|logs}"
    echo ""
    echo "Commands:"
    echo "  start    - Start the agent in background"
    echo "  stop     - Stop the agent"
    echo "  restart  - Restart the agent"
    echo "  status   - Check if agent is running"
    echo "  logs     - Tail the agent logs (Ctrl+C to exit)"
    echo ""
    exit 1
    ;;
esac
