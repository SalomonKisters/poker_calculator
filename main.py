from modules.card import Suit, CardNumber, Card
from modules.calculator import calc_odds
import multiprocessing as mp
import time

def display_results(all_player_cards, total_win_percentages, total_tie_percentages, total_player_wins, total_player_ties):
    for j in range(len(all_player_cards)):
        print(f'Player {j+1} wins {total_player_wins[j]} times or {round(total_win_percentages[j], 2)}%')
        print(f'Player {j+1} ties {total_player_ties[j]} times or {round(total_tie_percentages[j], 2)}%')
        total_equity = total_win_percentages[j] + (total_tie_percentages[j] / len(all_player_cards))
        print(f'Player {j+1} total equity: {round(total_equity, 2)}%')
        print('-' * 40)

def main():
    start_cards_p2 = [Card(CardNumber.ACE, Suit.CLUBS), Card(CardNumber.ACE, Suit.DIAMONDS)]
    start_cards_p1 = [Card(CardNumber.KING, Suit.CLUBS), Card(CardNumber.KING, Suit.DIAMONDS)]
    start_cards_p3 = [Card(CardNumber.QUEEN, Suit.CLUBS), Card(CardNumber.QUEEN, Suit.DIAMONDS)]
    start_cards_p4 = [Card(CardNumber.JACK, Suit.CLUBS), Card(CardNumber.JACK, Suit.DIAMONDS)]

    all_player_cards = [start_cards_p1, start_cards_p2, start_cards_p3, start_cards_p4]
    table_cards = []
    
    total_win_percentages, total_tie_percentages, total_player_wins, total_player_ties = calc_odds(all_player_cards, table_cards, division=8, numerator_to_check=1)
    
    for i in range(2, 8):
        display_results(all_player_cards, total_win_percentages, total_tie_percentages, total_player_wins, total_player_ties)
        win_percentages, tie_percentages, player_wins, player_ties = calc_odds(all_player_cards, table_cards, division=8, numerator_to_check=i)
        for j in range(len(all_player_cards)):
            total_win_percentages[j] = (total_win_percentages[j] * (i-1) + win_percentages[j]) / i
            total_tie_percentages[j] = (total_tie_percentages[j] * (i-1) + tie_percentages[j]) / i
            total_player_wins[j] = total_player_wins[j] + player_wins[j]
            total_player_ties[j] = total_player_ties[j] + player_ties[j]
    
    display_results(all_player_cards, total_win_percentages, total_tie_percentages, total_player_wins, total_player_ties)


if __name__ == "__main__":
    # This is required for multiprocessing to work correctly on Windows
    mp.freeze_support()
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Total time taken: {round(end_time - start_time, 2)}s")