cutechess-cli \
-engine cmd="engines/uci_minimax" \
-engine cmd="engines/uci_random_moves" \
-each proto=uci tc=40/60 \
-rounds 100