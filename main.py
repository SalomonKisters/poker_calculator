from modules.card import Suit, CardNumber, Card
from modules.calculator import calc_odds
import multiprocessing as mp

def main():
    start_cards_p2 = [Card(CardNumber.ACE, Suit.CLUBS), Card(CardNumber.ACE, Suit.DIAMONDS)]
    start_cards_p1 = [Card(CardNumber.KING, Suit.CLUBS), Card(CardNumber.KING, Suit.DIAMONDS)]
    start_cards_p3 = [Card(CardNumber.QUEEN, Suit.CLUBS), Card(CardNumber.QUEEN, Suit.DIAMONDS)]
    start_cards_p4 = [Card(CardNumber.JACK, Suit.CLUBS), Card(CardNumber.JACK, Suit.DIAMONDS)]

    all_player_cards = [start_cards_p1, start_cards_p2, start_cards_p3, start_cards_p4]
    table_cards = []

    win_percentages, tie_percentages, player_wins, player_ties = calc_odds(all_player_cards, table_cards) # 0.81s

    # total equity = win + (tie / number of players)
    for i in range(len(all_player_cards)):
        print(f'Player {i+1} wins {player_wins[i]} times or {win_percentages[i]}%')
        print(f'Player {i+1} ties {player_ties[i]} times or {tie_percentages[i]}%')
        total_equity = win_percentages[i] + (tie_percentages[i] / len(all_player_cards))
        print(f'Player {i+1} total equity: {round(total_equity, 2)}%')
        print('-' * 40)

if __name__ == "__main__":
    # This is required for multiprocessing to work correctly on Windows
    mp.freeze_support()
    main()