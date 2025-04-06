from typing import List, Tuple, Callable, Optional
from modules.card import Card
from modules.hand import Hand, HandValue
from modules.all_cards import get_all_cards, get_all_possible_table_cards_itertools
import time
import multiprocessing as mp
from multiprocessing import Pool
from functools import partial

def compare_hands(all_player_hands: List[Hand]) -> List[Hand]:
    winners = []
    highest_win = HandValue(-1, -1, -1, [])

    # Check for highest hand value
    for i, hand in enumerate(all_player_hands):
        value = hand._check_sf_flush_and_straight(highest_win_type = highest_win.type_value)
        if value is not None:
            if value > highest_win:
                highest_win = value
                winners = [i]
            elif value == highest_win:
                winners.append(i)

    if winners != []:
        return winners

    # Check for highest hand value
    for i, hand in enumerate(all_player_hands):
        hand._initialize_rank_based_lookup()
        value = hand._check_rank_based_hands(highest_win_type = highest_win.type_value)
        if value is not None:
            if value > highest_win:
                highest_win = value
                winners = [i]
            elif value == highest_win:
                winners.append(i)

    if winners != []:
        return winners
    
    # Check for highest hand value
    for i, hand in enumerate(all_player_hands):
        value = hand._check_high_card()
        if value is not None:
            if value > highest_win:
                highest_win = value
                winners = [i]
            elif value == highest_win:
                winners.append(i)

    if winners != []:
        return winners

def get_table_results(table_cards, card_amount, all_player_cards):
    all_player_hands = []
        
    player_wins = [0] * len(all_player_cards)
    player_ties = [0] * len(all_player_cards)

    # hand = combination of player cards and table cards
    for player_cards in all_player_cards:
        all_cards = player_cards + table_cards
        current_player_hand = Hand(all_cards)
        all_player_hands.append(current_player_hand)

    # Find winner, if multiple -> increase their tie amount
    best_hand_players = compare_hands(all_player_hands)
    if len(best_hand_players) == 1:
        player_wins[best_hand_players[0]] += card_amount
    else:
        for player_idx in best_hand_players:
            player_ties[player_idx] += card_amount

    return player_wins, player_ties
    

def process_batch(batch_items, all_player_cards):
    """Process a batch of table card combinations and return win/tie counts."""
    batch_wins = [0] * len(all_player_cards)
    batch_ties = [0] * len(all_player_cards)
    batch_card_amount = 0
    
    for table_cards, card_amount in batch_items:
        player_wins, player_ties = get_table_results(table_cards, card_amount, all_player_cards)
        batch_wins = [total + player for total, player in zip(batch_wins, player_wins)]
        batch_ties = [total + player for total, player in zip(batch_ties, player_ties)]
        batch_card_amount += card_amount
    return batch_wins, batch_ties, batch_card_amount

def calc_odds(all_player_cards: List[List[Card]], table_cards: List[Card]) -> Tuple[List[float], List[float], List[int], List[int]]:
    # Win chances each player current situation
    all_used_cards = table_cards + [card for player_cards in all_player_cards for card in player_cards]
    all_unused_cards = [card for card in get_all_cards() if card not in all_used_cards]
    
    start_time = time.time()
    all_possible_table_cards_dict = get_all_possible_table_cards_itertools(table_cards, all_unused_cards)
    end_time = time.time()
    print(f"Time taken to calculate all possible table cards: {round(end_time - start_time, 2)}s")
    print(f"Total possible table card combinations: {len(all_possible_table_cards_dict)}")
    
    # Convert dictionary items to list for processing
    items_list = list(all_possible_table_cards_dict.values())
    
    # Initialize counters
    total_player_wins = [0] * len(all_player_cards)
    total_player_ties = [0] * len(all_player_cards)
    total_card_amount = 0
    
    start_time = time.time()

    # One core free, never 0 cores
    num_cores = max(1, mp.cpu_count() - 1)
    if num_cores <= 0:
        num_cores = 1
    print(f"Using {num_cores} CPU cores for processing")
    
    # Each core gets 1 chunk of work from original list
    chunk_size = max(1, len(items_list) // num_cores)
    chunks = []
    
    for i in range(0, len(items_list), chunk_size):
        chunks.append(items_list[i:i + chunk_size])
    
    # Process chunks in parallel using a pool
    with Pool(processes=num_cores) as pool:
        # partial to fixate all_player_cards
        process_func = partial(process_batch, all_player_cards=all_player_cards)
        results = pool.map(process_func, chunks)
        
        # Combine results
        for batch_wins, batch_ties, batch_card_amount in results:
            total_player_wins = [total + batch for total, batch in zip(total_player_wins, batch_wins)]
            total_player_ties = [total + batch for total, batch in zip(total_player_ties, batch_ties)]
            total_card_amount += batch_card_amount
    
    end_time = time.time()
    print(f"Time taken to calculate player wins for all possible table cards: {round(end_time - start_time, 2)}s")

    win_percentages = [round(win / total_card_amount * 100, 2) for win in total_player_wins]
    tie_percentages = [round(tie / total_card_amount * 100, 2) for tie in total_player_ties]
    
    return win_percentages, tie_percentages, total_player_wins, total_player_ties