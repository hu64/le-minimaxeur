#!/bin/bash

# Define the starting position for mate in 2: White to move
# Example position: White to move, mate in 2 with Qh5+ followed by Qxf7#
POSITION="position startpos moves e2e4 e7e5 d1h5 b8c6 f1c4 g8f6"

# Run the engine and capture its output
ENGINE_OUTPUT=$(python3 uci_minimax.py <<EOF
uci
isready
ucinewgame
$POSITION
go depth 5
quit
EOF
)

# Print the engine's output for debugging
echo "Engine Output:"
echo "$ENGINE_OUTPUT"

# Check if the engine found the correct first move for mate in 2
if echo "$ENGINE_OUTPUT" | grep -q "bestmove h5f7"; then
  echo "Engine found the first move for mate in 2!"
else
  echo "Engine failed to find the first move for mate in 2."
fi