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
[x] Add asynchronous processing for improved performance
[x] Try Multiprocessing instead of async processing
[x] Implement step-by-step hand evaluation for faster multi-player calculations
[ ] Implement comparison of hands by comparing 6-card hands first, and for both, checking what cards would improve the hand. Give current winner all wins where the other doesnt improve or doesnt improve enough to beat the current winner. Then check all 7-handed hands that would improve the loser. Give the original loser all wins where the original winner doesnt improve.
[ ] Create a user interface for easier interaction
[ ] Add some kind of caching for table cards / already checked hand combinations (?)
[ ] Benchmark cached 5 card eval approach vs current approach (?)

## Requirements

- Python 3.9+
- No external dependencies required