from typing import List, Dict, Tuple
from .card import Suit, CardNumber, Card
import itertools

def get_all_cards() -> List[Card]:
    return [Card(card_number, suit) for card_number in CardNumber for suit in Suit]

def get_all_possible_table_cards(current_table_cards: List[Card], all_unused_cards: List[Card]) -> Dict[Tuple[Tuple[int, int], ...], Tuple[List[Card], int]]:
    """ Still very inefficient compared to itertools.combinations, but homemade = cooler"""
    remaining_cards = 5 - len(current_table_cards)

    if remaining_cards <= 0:
        sorted_cards = sorted(current_table_cards, key=lambda card: (card.number, card.suit))
        key = tuple((card.number, card.suit) for card in sorted_cards)
        return {key: (sorted_cards, 1)}

    current_possible_table_cards_dict: Dict[Tuple[Tuple[int, int], ...], Tuple[List[Card], int]] = {}
    
    # Create a copy to avoid modifying the original list
    sorted_cards = sorted(current_table_cards, key=lambda card: (card.number, card.suit))
    table_cards_key = tuple((card.number, card.suit) for card in sorted_cards)
    current_possible_table_cards_dict[table_cards_key] = (sorted_cards.copy(), 1)
    
    last_possible_table_cards_dict = {}

    # Add to table cards one at a time
    for i in range(remaining_cards):
        print(f"{remaining_cards - i} cards remaining")
        last_possible_table_cards_dict = current_possible_table_cards_dict.copy()
        current_possible_table_cards_dict.clear()
        
        # Go over all unique last table cards
        for j, key in enumerate(last_possible_table_cards_dict.keys()):
            cards_tuple = last_possible_table_cards_dict[key]
            current_cards = cards_tuple[0]
            count = cards_tuple[1]
            
            for unused_card in all_unused_cards:
                # Check if unused card is already used in current table cards
                if unused_card not in current_cards:
                    # Add card to table
                    new_cards = current_cards.copy() + [unused_card]
                    
                    # Create standardized key for table cards using tuples (more efficient than strings)
                    sorted_cards = sorted(new_cards, key=lambda card: (card.number, card.suit))
                    new_key = tuple((card.number, card.suit) for card in sorted_cards)
                    
                    # Update dict -> add new unique table hand or inc existing
                    if new_key not in current_possible_table_cards_dict:
                        current_possible_table_cards_dict[new_key] = (sorted_cards, count)
                    else:
                        existing_tuple = current_possible_table_cards_dict[new_key]
                        current_possible_table_cards_dict[new_key] = (existing_tuple[0], existing_tuple[1] + count)
            
            if j % 10000 == 0:
                print(f"Processed {round((j+1) / len(last_possible_table_cards_dict) * 100, 2)}% of possible table cards from last step.")

    return current_possible_table_cards_dict

def get_all_possible_table_cards_itertools(current_table_cards: List[Card], all_unused_cards: List[Card]) -> Dict[Tuple[Tuple[int, int], ...], Tuple[List[Card], int]]:
    remaining_cards = 5 - len(current_table_cards)
    
    if remaining_cards <= 0:
        sorted_cards = sorted(current_table_cards, key=lambda card: (card.number, card.suit))
        key = tuple((card.number, card.suit) for card in sorted_cards)
        return {key: (sorted_cards, 1)}
    
    available_cards = [card for card in all_unused_cards if card not in current_table_cards]
    
    combinations_dict = {}
    
    # generate all ways to add remaining_cards using itertools
    for additional_cards in itertools.combinations(available_cards, remaining_cards):
        full_table = current_table_cards + list(additional_cards)
        
        # Use a tuple of (number, suit) pairs as key - more efficient than strings
        sorted_cards = sorted(full_table, key=lambda card: (card.number, card.suit))
        key = tuple((card.number, card.suit) for card in sorted_cards)
        
        if key not in combinations_dict:
            combinations_dict[key] = (sorted_cards, 1)
        else:
            existing_tuple = combinations_dict[key]
            combinations_dict[key] = (existing_tuple[0], existing_tuple[1] + 1)
    
    return combinations_dict