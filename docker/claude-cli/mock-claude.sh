#!/bin/bash
# docker/claude-cli/mock-claude.sh
# Mock Claude CLI for testing without API calls

# Commands for testing:
# STREAM - outputs text with delay
# DELAY:N - waits N seconds
# ERROR - exits with error
# HANG - never exits (for interrupt testing)
# EXIT - exits normally

echo "Mock Claude CLI v1.0.0"
echo "Ready for input..."

while IFS= read -r line; do
    case "$line" in
        STREAM)
            for i in {1..5}; do
                echo "Streaming line $i..."
                sleep 0.1
            done
            ;;
        DELAY:*)
            seconds="${line#DELAY:}"
            sleep "$seconds"
            echo "Waited $seconds seconds"
            ;;
        ERROR)
            echo "Error: Simulated failure" >&2
            exit 1
            ;;
        HANG)
            echo "Hanging forever (send SIGINT to stop)..."
            while true; do sleep 1; done
            ;;
        EXIT)
            echo "Exiting normally"
            exit 0
            ;;
        *)
            echo "Echo: $line"
            ;;
    esac
done
