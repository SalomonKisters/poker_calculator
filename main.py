from typing import List, Tuple
from modules.card import Suit, CardNumber, Card
from modules.hand import Hand
from modules.all_cards import get_all_cards, get_all_possible_table_cards, get_all_possible_table_cards_itertools
import time
import asyncio

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

async def get_table_results(table_cards, card_amount, all_player_cards):
    all_player_hands = []
        
    player_wins = [0] * len(all_player_cards)
    player_ties = [0] * len(all_player_cards)

    # Hand = Kombination aus Spielerkarten und Tischkarten
    for player_cards in all_player_cards:
        all_cards = player_cards + table_cards
        current_player_hand = Hand(all_cards)
        all_player_hands.append(current_player_hand)

    # Properly await all hand value calculations in parallel
    hand_value_tasks = [hand.check_hand_value() for hand in all_player_hands]
    all_hand_values = await asyncio.gather(*hand_value_tasks)

    best_hand_value = max(all_hand_values)
    
    # Find winner, if multiple -> increase their tie amount
    best_hand_players = [j for j, value in enumerate(all_hand_values) if value == best_hand_value]
    if len(best_hand_players) == 1:
        player_wins[best_hand_players[0]] += card_amount
    else:
        for player_idx in best_hand_players:
            player_ties[player_idx] += card_amount

    return player_wins, player_ties
    
        
async def calc_odds(all_player_cards: List[List[Card]], table_cards: List[Card]) -> Tuple[List[float], List[float], List[int], List[int]]:
    # Win chances each player current situation
    all_used_cards = table_cards + [card for player_cards in all_player_cards for card in player_cards]
    all_unused_cards = [card for card in await get_all_cards() if card not in all_used_cards]
    
    start_time = time.time()
    all_possible_table_cards_dict = await get_all_possible_table_cards_itertools(table_cards, all_unused_cards)
    end_time = time.time()
    print(f"Time taken to calculate all possible table cards: {round(end_time - start_time, 2)}s")

    start_time = time.time()
    total_card_amount = 0
    all_result_find_tasks = []
    
    # Control concurrency with a semaphore to avoid overwhelming the system
    # Adjust the value based on your CPU cores (typically 2x number of cores)
    sem = asyncio.Semaphore(8)
    
    async def process_table_cards(table_cards, card_amount):
        async with sem:
            return await get_table_results(table_cards, card_amount, all_player_cards)
    
    for table_cards_str in all_possible_table_cards_dict.keys():
        table_cards, card_amount = all_possible_table_cards_dict[table_cards_str]
        
        current_table_result_find_task = asyncio.create_task(process_table_cards(table_cards, card_amount))
        all_result_find_tasks.append(current_table_result_find_task)

        total_card_amount += card_amount
    
    all_player_wins = [0] * len(all_player_cards)
    all_player_ties = [0] * len(all_player_cards)
    
    # Properly await all tasks and gather results
    all_results = await asyncio.gather(*all_result_find_tasks)
    
    for player_wins, player_ties in all_results:
        for i, wins in enumerate(player_wins):
            all_player_wins[i] += wins
            all_player_ties[i] += player_ties[i]

    end_time = time.time()
    print(f"Time taken to calculate player wins for all possible table cards: {round(end_time - start_time, 2)}s")

    win_percentages = [round(win / total_card_amount * 100, 2) for win in all_player_wins]
    tie_percentages = [round(tie / total_card_amount * 100, 2) for tie in all_player_ties]
    
    return win_percentages, tie_percentages, all_player_wins, all_player_ties

start_cards_p2 = [Card(CardNumber.ACE, Suit.CLUBS), Card(CardNumber.ACE, Suit.DIAMONDS)]
start_cards_p1 = [Card(CardNumber.KING, Suit.CLUBS), Card(CardNumber.KING, Suit.DIAMONDS)]
start_cards_p3 = [Card(CardNumber.QUEEN, Suit.CLUBS), Card(CardNumber.QUEEN, Suit.DIAMONDS)]
start_cards_p4 = [Card(CardNumber.JACK, Suit.CLUBS), Card(CardNumber.JACK, Suit.DIAMONDS)]

all_player_cards = [start_cards_p1, start_cards_p2, start_cards_p3, start_cards_p4]
table_cards = [Card(CardNumber.JACK, Suit.SPADES)]

win_percentages, tie_percentages, player_wins, player_ties = asyncio.run(calc_odds(all_player_cards, table_cards))

# total equity = win + (tie / number of players)
for i in range(len(all_player_cards)):
    print(f'Player {i+1} wins {player_wins[i]} times or {win_percentages[i]}%')
    print(f'Player {i+1} ties {player_ties[i]} times or {tie_percentages[i]}%')
    total_equity = win_percentages[i] + (tie_percentages[i] / len(all_player_cards))
    print(f'Player {i+1} total equity: {round(total_equity, 2)}%')
    print('-' * 40)

# TODO: Instead of calculating full values for both full hands:
# 1. Calculate one step for each hand, if one returns and others dont, we know that one wins
# 2. If none return, go to next step, etc. Until one or multiple return
# Especially more efficient for more than 2 handed play. 
# This would reduce the calculations to hands*number_of_checks_before_highest_hand returns
# e.g. in 6 handed play, for 50% of 6 hands, rank-based hands would not have to be checked

# TODO: Async calculation of hand values, etc. And later accumulation and comparison.
# This would speed the process up number_of_cores times