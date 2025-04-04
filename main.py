from typing import List, Tuple
from modules.card import Suit, CardNumber, Card
from modules.hand import Hand
from modules.all_cards import get_all_cards, get_all_possible_table_cards, get_all_possible_table_cards_itertools
import time

# Pair A A Q K 10 6 5
hand_1 = Hand([Card(CardNumber.ACE, Suit.SPADES), Card(CardNumber.ACE, Suit.DIAMONDS), 
            Card(CardNumber.QUEEN, Suit.SPADES), Card(CardNumber.KING, Suit.SPADES), 
            Card(CardNumber.TEN, Suit.HEARTS), Card(CardNumber.SIX, Suit.SPADES), 
            Card(CardNumber.FIVE, Suit.DIAMONDS)])
# Pair A A Q K J 6 5
hand_2 = Hand([Card(CardNumber.ACE, Suit.CLUBS), Card(CardNumber.ACE, Suit.DIAMONDS), 
            Card(CardNumber.QUEEN, Suit.DIAMONDS), Card(CardNumber.KING, Suit.CLUBS), 
            Card(CardNumber.JACK, Suit.CLUBS), Card(CardNumber.SIX, Suit.CLUBS), 
            Card(CardNumber.FIVE, Suit.DIAMONDS)])

print(hand_1.check_hand_value())
print(hand_2.check_hand_value())

def calc_odds(all_player_cards: List[List[Card]], table_cards: List[Card]) -> Tuple[List[float], List[float]]:
    # Gewinnchancen jedes Spielers in momentaner Situation (table cards) berechnen
    all_used_cards = table_cards + [card for player_cards in all_player_cards for card in player_cards]
    all_unused_cards = [card for card in get_all_cards() if card not in all_used_cards]
    
    start_time = time.time()
    all_possible_table_cards_dict = get_all_possible_table_cards_itertools(table_cards, all_unused_cards)
    end_time = time.time()
    print(f"Time taken to calculate all possible table cards: {round(end_time - start_time, 2)}s")

    player_wins = [0] * len(all_player_cards)
    player_ties = [0] * len(all_player_cards)
    total_card_amount = 0
    start_time = time.time()
    
    for i, table_cards_str in enumerate(all_possible_table_cards_dict.keys()):
        table_cards, card_amount = all_possible_table_cards_dict[table_cards_str]
        all_player_hands = []
        
        # Hand = Kombination aus Spielerkarten und Tischkarten
        for player_cards in all_player_cards:
            all_cards = player_cards + table_cards
            current_player_hand = Hand(all_cards)
            all_player_hands.append(current_player_hand)
        
        all_hand_values = [hand.check_hand_value() for hand in all_player_hands]
        best_hand_value = max(all_hand_values)
        
        # Gewinner finden; Wenn mehrere -> Tie count inc
        best_hand_players = [j for j, value in enumerate(all_hand_values) if value == best_hand_value]
        if len(best_hand_players) == 1:
            player_wins[best_hand_players[0]] += card_amount
        else:
            for player_idx in best_hand_players:
                player_ties[player_idx] += card_amount
        
        total_card_amount += card_amount
        
        if i % 10000 == 0:
            print(f"Processed {round((i+1) / len(all_possible_table_cards_dict) * 100, 2)}% of all possible table cards")
    
    end_time = time.time()
    print(f"Time taken to calculate player wins for all possible table cards: {round(end_time - start_time, 2)}s")

    win_percentages = [round(win / total_card_amount * 100, 2) for win in player_wins]
    tie_percentages = [round(tie / total_card_amount * 100, 2) for tie in player_ties]
    
    # Resultate, mit total equity = win + (tie / number of players)
    for i in range(len(all_player_cards)):
        print(f'Player {i+1} wins {player_wins[i]} times or {win_percentages[i]}%')
        print(f'Player {i+1} ties {player_ties[i]} times or {tie_percentages[i]}%')
        total_equity = win_percentages[i] + (tie_percentages[i] / len(all_player_cards))
        print(f'Player {i+1} total equity: {round(total_equity, 2)}%')
        print('-' * 40)
    
    return win_percentages, tie_percentages

start_cards_p2 = [Card(CardNumber.ACE, Suit.CLUBS), Card(CardNumber.ACE, Suit.DIAMONDS)]
start_cards_p1 = [Card(CardNumber.KING, Suit.CLUBS), Card(CardNumber.KING, Suit.DIAMONDS)]
start_cards_p3 = [Card(CardNumber.QUEEN, Suit.CLUBS), Card(CardNumber.QUEEN, Suit.DIAMONDS)]
start_cards_p4 = [Card(CardNumber.JACK, Suit.CLUBS), Card(CardNumber.JACK, Suit.DIAMONDS)]

table_cards = [Card(CardNumber.KING, Suit.SPADES)]
calc_odds([start_cards_p1, start_cards_p2, start_cards_p3, start_cards_p4], []) # 0.81s