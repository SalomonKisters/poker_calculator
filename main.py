from modules.card import Suit, CardNumber, Card
from modules.calculator import calc_odds
import multiprocessing as mp
import time
from modules.utils import get_results_str, check_validity

def main():
    start_cards_p2 = [Card(CardNumber.ACE, Suit.CLUBS), Card(CardNumber.ACE, Suit.DIAMONDS)]
    start_cards_p1 = [Card(CardNumber.KING, Suit.CLUBS), Card(CardNumber.KING, Suit.DIAMONDS)]
    start_cards_p3 = [Card(CardNumber.QUEEN, Suit.CLUBS), Card(CardNumber.QUEEN, Suit.DIAMONDS)]
    start_cards_p4 = [Card(CardNumber.JACK, Suit.CLUBS), Card(CardNumber.JACK, Suit.DIAMONDS)]

    all_player_cards = [start_cards_p1, start_cards_p2, start_cards_p3, start_cards_p4]
    table_cards = []
    # Multiple of 2!!!
    division = 64
    # Moving average only needed for 0 table cards, otherwise its overhead outweighs the benefits
    if len(table_cards) != 0:
        division = 1

    current_amount = 1
    prev_max_numerator = 0
    numerators_to_check = [prev_max_numerator]
    check_validity(all_player_cards, table_cards)
    total_win_percentages, total_tie_percentages, total_player_wins, total_player_ties = calc_odds(all_player_cards, table_cards, division=division, numerators_to_check=numerators_to_check)
    print(get_results_str(all_player_cards, total_win_percentages, total_tie_percentages, total_player_wins, total_player_ties))
    print(f"progress: {prev_max_numerator+1}/{division}")
    
    # Start with 1 and double each time, to get almost instant first estimate, getting better iteratively.
    # This is, because keeping it linear, you either get a slow first result or a slow final result due to overhead of doing it 64 times for a small list
    while prev_max_numerator < division - 1:
        current_max_numerator = prev_max_numerator + current_amount
        current_numerators_to_check = list(range(prev_max_numerator + 1, current_max_numerator + 1))
        win_percentages, tie_percentages, player_wins, player_ties = calc_odds(all_player_cards, table_cards, division=division, numerators_to_check=current_numerators_to_check)
        for j in range(len(all_player_cards)):
            total_win_percentages[j] = (total_win_percentages[j] * (current_amount-1) + win_percentages[j] * current_amount) / (current_amount*2-1)
            total_tie_percentages[j] = (total_tie_percentages[j] * (current_amount-1) + tie_percentages[j] * current_amount) / (current_amount*2-1)
            total_player_wins[j] = total_player_wins[j] + player_wins[j]
            total_player_ties[j] = total_player_ties[j] + player_ties[j]
        prev_max_numerator = current_max_numerator
        current_amount *= 2
        print(get_results_str(all_player_cards, total_win_percentages, total_tie_percentages, total_player_wins, total_player_ties))
        print(f"progress: {prev_max_numerator+1}/{division}")

if __name__ == "__main__":
    # This is required for multiprocessing to work correctly on Windows
    mp.freeze_support()
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Total time taken: {round(end_time - start_time, 2)}s")