# Poker Calculator

A Python-based poker odds calculator that computes win probabilities and equity for multiple players in Texas Hold'em poker.

## Features

- Calculate exact win percentages and tie percentages for multiple players
- Support for pre-flop, flop, turn, and river calculations
- Fast computation using optimized algorithms (lazy evaluation in hand comparison) and multiprocessing
- Moving average implementation for quick results, getting better with time, especially important for pre-flop, where the number of possible board combinations is large
- Detailed hand evaluation with win chance, tie chance, and equity

## Project Structure

- `main.py` - Main script with example calculations
- `gui.py` - GUI script
- `modules/` - Core functionality modules:
  - `card.py` - Card representation with suits and numbers
  - `hand.py` - Hand evaluation
  - `calculator.py` - Multithreaded hand comparison, and odds calcultion
  - `hand_value.py` - Poker hand value calculations
  - `utils.py` - Utility functions for calculations and printing results
  - `all_cards.py` - Utilities for generating card combinations
  - `all_hands.py` - Hand generation utilities (mainly getting all table cards)

## Usage

python gui.py

## How It Works

The calculator uses a combinatorial approach to evaluate all possible board combinations given the known cards. It then determines the best 5-card hand for each player from their cards and the table cards, comparing them to find win/tie scenarios.

Performance is optimized by:
1. Efficiently generating card combinations using itertools
2. Using fast hand evaluation algorithms, and only calculating until best possible combination is found
3. Tracking win/tie counts for accurate probability calculations
4. Using multiprocessing for parallel processing
5. Using moving average for quick results, getting better with time

## Future Improvements

[x] For dict with unique table card combinations, implement more efficient hashing of list of cards, instead of using sorted string
[x] Add asynchronous processing for improved performance
[x] Try Multiprocessing instead of async processing
[x] Implement step-by-step hand evaluation for faster multi-player calculations
[x] Create moving average implementation for quick results, getting better with time
[x] Create a user interface for easier interaction
[ ] Better GUI (See lenitl pull request)

## Potential improvements to research

[ ] Implement comparison of hands by comparing 6-card hands first, and for both, checking what cards would improve the hand. Give current winner all wins where the other doesnt improve or doesnt improve enough to beat the current winner. Then check all 7-handed hands that would improve the loser. Give the original loser all wins where the original winner doesnt improve.
[ ] Seperate selection for each of the table card combinations in one step, so not all possibilities are gone over every time (not sure if this is needed, since it will slow down initial calculations again)
[ ] Add some kind of caching for table cards / already checked hand combinations
[ ] Benchmark cached 5 card eval approach vs current approach

## Requirements

- Python 3.9+
- No external dependencies required