# Poker Calculator

A Python-based poker odds calculator that computes win probabilities and equity for multiple players in Texas Hold'em poker.
Results can differ about 1-5 hundredths from the actual probabilities (in Percent), but are then rounded to tenths.
So accuracy is +- 0.1%
## Features

- Calculate exact win percentages and tie percentages for multiple players
- Support for pre-flop, flop, turn, and river calculations
- Fast computation using optimized algorithms
- Detailed hand evaluation based on poker hand rankings

## Project Structure

- `main.py` - Main script with example calculations
- `modules/` - Core functionality modules:
  - `card.py` - Card representation with suits and numbers
  - `hand.py` - Hand evaluation and comparison
  - `hand_value.py` - Poker hand value calculations
  - `all_cards.py` - Utilities for generating card combinations
  - `all_hands.py` - Hand generation utilities


## Requirements

- Python 3.9+
- No external dependencies required
