from typing import List, Dict, Tuple
from .card import Suit, CardNumber, Card

def get_all_cards() -> List[Card]:
    return [Card(card_number, suit) for card_number in CardNumber for suit in Suit]

def get_all_possible_table_cards(current_table_cards: List[Card], all_unused_cards: List[Card]) -> Tuple[Dict[str, Tuple[List[Card], int]], int]:
    """ Still very inefficient compared to itertools.combinations, but homemade = cooler"""
    remaining_cards = 5 - len(current_table_cards)

    current_possible_table_cards_dict: Dict[str, Tuple[List[Card], int]] = {}
    
    # Create a copy to avoid modifying the original list
    table_cards_key = str(sorted([str(card) for card in current_table_cards], key=str))
    current_possible_table_cards_dict[table_cards_key] = (current_table_cards.copy(), 1)
    
    last_possible_table_cards_dict = {}

    for i in range(remaining_cards):
        print(f"{remaining_cards - i} cards remaining")
        last_possible_table_cards_dict = current_possible_table_cards_dict.copy()
        current_possible_table_cards_dict.clear()
        
        for j, key in enumerate(last_possible_table_cards_dict.keys()):
            cards_tuple = last_possible_table_cards_dict[key]
            current_cards = cards_tuple[0]
            count = cards_tuple[1]
            
            for unused_card in all_unused_cards:
                # Check if card is already used
                if str(unused_card) not in [str(c) for c in current_cards]:
                    # Create a new list with the added card
                    new_cards = current_cards.copy() + [unused_card]
                    
                    # Create a standardized key
                    sorted_cards = sorted(new_cards, key=lambda card: (card.number, card.suit))
                    new_key = str([str(card) for card in sorted_cards])
                    
                    if new_key not in current_possible_table_cards_dict:
                        current_possible_table_cards_dict[new_key] = (sorted_cards, count)
                    else:
                        existing_tuple = current_possible_table_cards_dict[new_key]
                        current_possible_table_cards_dict[new_key] = (existing_tuple[0], existing_tuple[1] + count)
            
            if j % 10000 == 0:
                print(f"processed {round((j+1) / len(last_possible_table_cards_dict) * 100, 2)}% of last possible table cards")

    return current_possible_table_cards_dict