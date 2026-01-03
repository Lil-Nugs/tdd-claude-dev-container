#!/bin/bash
# docker/claude-cli/mock-claude.sh
# Mock Claude CLI for testing without API calls

set -euo pipefail

VERSION="mock-1.0.0"

# Parse arguments
case "${1:-}" in
    --version|-v)
        echo "Claude CLI $VERSION (mock)"
        exit 0
        ;;
    --help|-h)
        echo "Mock Claude CLI for testing"
        echo ""
        echo "Commands:"
        echo "  STREAM      - Output text with delay (simulates streaming)"
        echo "  DELAY:N     - Wait N seconds"
        echo "  ERROR       - Exit with error code 1"
        echo "  HANG        - Never exit (for interrupt testing)"
        echo "  EXIT        - Exit cleanly"
        echo "  ECHO:text   - Echo back the text"
        echo ""
        exit 0
        ;;
esac

echo "Mock Claude CLI $VERSION"
echo "Ready for input..."

while IFS= read -r line || [[ -n "$line" ]]; do
    case "$line" in
        STREAM)
            for i in {1..5}; do
                echo "Streaming response line $i..."
                sleep 0.1
            done
            echo "Stream complete."
            ;;
        DELAY:*)
            seconds="${line#DELAY:}"
            echo "Waiting $seconds seconds..."
            sleep "$seconds"
            echo "Done waiting."
            ;;
        ERROR)
            echo "Error: Simulated failure" >&2
            exit 1
            ;;
        ERROR:*)
            message="${line#ERROR:}"
            echo "Error: $message" >&2
            exit 1
            ;;
        HANG)
            echo "Hanging forever (send SIGINT to stop)..."
            trap 'echo "Interrupted!"; exit 130' INT TERM
            while true; do sleep 1; done
            ;;
        EXIT|exit|quit)
            echo "Exiting normally."
            exit 0
            ;;
        EXIT:*)
            code="${line#EXIT:}"
            echo "Exiting with code $code"
            exit "$code"
            ;;
        ECHO:*)
            text="${line#ECHO:}"
            echo "$text"
            ;;
        JSON:*)
            json="${line#JSON:}"
            echo "$json"
            ;;
        "")
            # Ignore empty lines
            ;;
        *)
            # Default: echo back with prefix
            echo "Claude: $line"
            ;;
    esac
done
