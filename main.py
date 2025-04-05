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
    # Win chances each player current situation
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
        
        # Find winner, if multiple -> increase their tie amount
        best_hand_players = [j for j, value in enumerate(all_hand_values) if value == best_hand_value]
        if len(best_hand_players) == 1:
            player_wins[best_hand_players[0]] += card_amount
        else:
            for player_idx in best_hand_players:
                player_ties[player_idx] += card_amount
        
        total_card_amount += card_amount
        
        if i % 100000 == 0:
            print(f"Processed {round((i+1) / len(all_possible_table_cards_dict) * 100, 2)}% of all possible table cards")
    
    end_time = time.time()
    print(f"Time taken to calculate player wins for all possible table cards: {round(end_time - start_time, 2)}s")

    win_percentages = [round(win / total_card_amount * 100, 2) for win in player_wins]
    tie_percentages = [round(tie / total_card_amount * 100, 2) for tie in player_ties]
    
    return win_percentages, tie_percentages, player_wins, player_ties

    
# TODO: Instead of calculating full values for both full hands:
# 1. Calculate one step for each hand, if one returns and others dont, we know that one wins
# 2. If none return, go to next step, etc. Until one or multiple return
# Especially more efficient for more than 2 handed play. 
# This would reduce the calculations to hands*number_of_checks_before_highest_hand returns
# e.g. in 6 handed play, for 50% of 6 hands, rank-based hands would not have to be checked

# TODO: Async calculation of hand values, etc. And later accumulation and comparison.
# This would speed the process up number_of_cores times