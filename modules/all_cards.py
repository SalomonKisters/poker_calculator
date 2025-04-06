from typing import List, Dict, Tuple
from .card import Suit, CardNumber, Card
import itertools
import random
import math
from typing import List, Tuple, Dict, Optional

def get_all_cards() -> List[Card]:
    return [Card(card_number, suit) for card_number in CardNumber for suit in Suit]

def get_all_possible_table_cards(current_table_cards: List[Card], all_unused_cards: List[Card]) -> Dict[Tuple[Tuple[int, int], ...], Tuple[List[Card], int]]:
    """ 
    Still very inefficient compared to itertools.combinations, but homemade = cooler
    """
    remaining_cards = 5 - len(current_table_cards)

    if remaining_cards <= 0:
        sorted_cards = sorted(current_table_cards, key=lambda card: (card.number, card.suit))
        key = tuple((card.number, card.suit) for card in sorted_cards)
        return {key: (sorted_cards, 1)}

    available_cards = [card for card in all_unused_cards if card not in current_table_cards]

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

def get_sampled_table_cards(
    current_table_cards: List[Card],
    all_unused_cards: List[Card],
    sample_size: int = 100000
) -> Dict[Tuple[Tuple[int, int], ...], Tuple[List[Card], int]]:
    """
    Samples a specific amount of random table combinations.
    """

    remaining_cards = 5 - len(current_table_cards)

    if remaining_cards <= 0:
        sorted_cards = sorted(current_table_cards, key=lambda card: (card.number, card.suit))
        key = tuple((card.number, card.suit) for card in sorted_cards)
        return {key: (sorted_cards, 1)}

    available_cards = [card for card in all_unused_cards if card not in current_table_cards]

    total_combinations = math.comb(len(available_cards), remaining_cards)
    actual_sample_size = min(sample_size, total_combinations)

    # Generate random indices for sampling
    chosen_indices = sorted(random.sample(range(total_combinations), actual_sample_size))
    sampled_combinations_dict = {}

    # Initialize iterator and first target index
    target_indices_iter = iter(chosen_indices)
    next_target_index = next(target_indices_iter, None) # Get the first target index

    combinations_iterator = itertools.combinations(available_cards, remaining_cards)

    for i, additional_cards_tuple in enumerate(combinations_iterator):
        # Check if we reached next target index
        if i == next_target_index:
            full_table = current_table_cards + list(additional_cards_tuple)

            # Use a tuple of (number, suit) pairs as key - more efficient than strings
            sorted_cards = sorted(full_table, key=lambda card: (card.number, card.suit))
            key = tuple((card.number, card.suit) for card in sorted_cards)

            sampled_combinations_dict[key] = (sorted_cards, 1)
            next_target_index = next(target_indices_iter, None)

            # Stop if all samples collected
            if next_target_index is None:
                break

    return sampled_combinations_dict


def get_sampled_table_cards_by_division(
    current_table_cards: List[Card],
    all_unused_cards: List[Card],
    division: int,
    numerators_to_check: List[int],
    previously_sampled_indices: Optional[set] = set()
) -> Dict[Tuple[Tuple[int, int], ...], Tuple[List[Card], int]]:
    """
    Samples table combinations at specific fractional intervals.
    """    
    remaining_cards = 5 - len(current_table_cards)
    result_dict = {}

    if remaining_cards <= 0:
        sorted_cards = sorted(current_table_cards, key=lambda card: (card.number, card.suit))
        key = tuple((card.number, card.suit) for card in sorted_cards)
        return {key: (sorted_cards, 1)}

    available_cards = [card for card in all_unused_cards if card not in current_table_cards]
    
    # Get the combination at the target index
    for i, additional_cards_tuple in enumerate(itertools.combinations(available_cards, remaining_cards)):
        if i % division in numerators_to_check:
            # Create the full table and sort the cards
            full_table = current_table_cards + list(additional_cards_tuple)
            sorted_cards = sorted(full_table, key=lambda card: (card.number, card.suit))
            key = tuple((card.number, card.suit) for card in sorted_cards)
            
            # Add to the result dictionary
            result_dict[key] = (sorted_cards, 1)
    
    return result_dict