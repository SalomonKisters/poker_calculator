from typing import List, Tuple
from modules.card import Card
from modules.hand import Hand
from modules.all_cards import get_all_cards, get_all_possible_table_cards_itertools
import time



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