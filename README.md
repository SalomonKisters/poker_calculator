# Poker Calculator

A Python-based poker odds calculator that computes win probabilities and equity for multiple players in Texas Hold'em poker.

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

## Usage Example

See main.py

## How It Works

The calculator uses a combinatorial approach to evaluate all possible board combinations given the known cards. It then determines the best 5-card hand for each player from their cards and the table cards, comparing them to find win/tie scenarios.

Performance is optimized by:
1. Efficiently generating card combinations using itertools
2. Using fast hand evaluation algorithms, and only calculating until best possible combination is found
3. Tracking win/tie counts for accurate probability calculations

## Future Improvements

[x] For dict with unique table card combinations, implement more efficient hashing of list of cards, instead of using sorted string
[ ] Add asynchronous processing for improved performance
[ ] Implement step-by-step hand evaluation for faster multi-player calculations
[ ] Create a user interface for easier interaction

## Requirements

- Python 3.9+
- No external dependencies required
