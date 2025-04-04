from re import X
from typing import List, Dict, Optional, Tuple
import enum
import time
from collections import Counter

class PokerHand:
    def __init__(self, name: str, value: int, defining_cards: int):
        self.name = name
        self.value = value
        self.defining_cards = defining_cards

    def __repr__(self):
        return f"PokerHand(name='{self.name}', value={self.value}, defining_cards={self.defining_cards})"

# Define the standard poker hand rankings
poker_hands = {
    1: PokerHand('High Card', 1, 1),
    2: PokerHand('Pair', 2, 2),
    3: PokerHand('Two Pair', 3, 4),
    4: PokerHand('Three of a Kind', 4, 3),
    5: PokerHand('Straight', 5, 5),
    6: PokerHand('Flush', 6, 5),
    7: PokerHand('Full House', 7, 5),
    8: PokerHand('Four of a Kind', 8, 4),
    9: PokerHand('Straight Flush', 9, 5),
    10: PokerHand('Royal Flush', 10, 5)
}

class CardNumber(enum.IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Suit(enum.IntEnum):
    HEARTS = 1
    DIAMONDS = 2
    CLUBS = 3
    SPADES = 4


class Card:
    def __init__(self, card : CardNumber, suit : Suit):
        self.number = card
        self.suit = suit
    
    def __str__(self):
        return f'{self.number} of {self.suit}'
    
    def __repr__(self):
        return f'{self.number} of {self.suit}'
    
    def __eq__(self, other):
        return self.number == other.number and self.suit == other.suit

class HandValue:
    type_value : int
    high_card_in_type_value : int
    second_high_card_in_type_value : int
    high_cards : List[int]
    def __init__(self, type_value : int, high_card_in_type_value : int, second_high_card_in_type_value : int, high_cards : List[int]):
        self.type_value = type_value
        self.high_card_in_type_value = high_card_in_type_value
        # For 2 pairs and full house
        self.second_high_card_in_type_value = second_high_card_in_type_value
        self.high_cards = high_cards

    def compare_high_card_lists(self, list1, list2):
        for i in range(len(list1)):
            if list1[i] != list2[i]:
                return list1[i] - list2[i]
        return 0

    def compare_to(self, other) -> float:
        if self.type_value != other.type_value:
            return self.type_value - other.type_value
        if self.high_card_in_type_value != other.high_card_in_type_value:
            return self.high_card_in_type_value - other.high_card_in_type_value
        if self.second_high_card_in_type_value != other.second_high_card_in_type_value:
            return self.second_high_card_in_type_value - other.second_high_card_in_type_value
        return self.compare_high_card_lists(self.high_cards, other.high_cards)
    
    def __str__(self):
        Type = f'Type: {poker_hands[self.type_value].name}'
        if self.high_card_in_type_value != -1:
            high_card_in_type = f', High card in type: {CardNumber(self.high_card_in_type_value).name}'
        else:
            high_card_in_type = ''
        
        if self.second_high_card_in_type_value != -1:
            second_high_card_in_type = f', Second high card in type: {CardNumber(self.second_high_card_in_type_value).name}'
        else:
            second_high_card_in_type = ''

        if self.high_cards != []:
            high_cards = f', High cards: {[card.name for card in self.high_cards]}'
        else:
            high_cards = ''
        return f'{Type}{high_card_in_type}{second_high_card_in_type}{high_cards}'

    def __eq__(self, other):
        return self.compare_to(other) == 0
    
    def __ne__(self, other):
        return self.compare_to(other) != 0
    
    def __lt__(self, other):
        return self.compare_to(other) < 0
    
    def __le__(self, other):
        return self.compare_to(other) <= 0
    
    def __gt__(self, other):
        return self.compare_to(other) > 0
    
    def __ge__(self, other):
        return self.compare_to(other) >= 0

class Hand:
    def __init__(self, cards : List[Card]):
        if len(cards) != 7:
            raise ValueError("Hold'em requires 7 cards")

        # Store cards sorted by number (descending is often easier for evaluation)
        self.cards = sorted(cards, key=lambda card: card.number, reverse=True)

        # Count ranks and suits
        self.rank_counts = Counter(card.number for card in self.cards)
        self.suit_counts = Counter(card.suit for card in self.cards)

        # Group cards by suit, sorted descending by rank within each suit
        self.cards_by_suit: Dict[Suit, List[Card]] = {s: [] for s in Suit}
        for card in self.cards:
            self.cards_by_suit[card.suit].append(card)
        for s in self.cards_by_suit:
            self.cards_by_suit[s].sort(key=lambda card: card.number, reverse=True)

        # Rank counts lookup (count -> list of ranks), sorted descending for direct access of highest
        self.counts_to_values: Dict[int, List[int]] = {}
        for value, count in self.rank_counts.items():
            if count not in self.counts_to_values:
                self.counts_to_values[count] = []
            self.counts_to_values[count].append(value)
        for count in self.counts_to_values:
            self.counts_to_values[count].sort(reverse=True)

        # Store unique ranks sorted descending (useful for straight checks)
        self.unique_ranks = sorted(self.rank_counts.keys(), reverse=True)

    def _get_kickers(self, defining_card_ranks: List[int], num_kickers: int) -> List[int]:
        """Helper to get kicker card ranks."""
        kickers = []
        defining_set = set(defining_card_ranks) # Faster lookups
        for card in self.cards:
            if card.number not in defining_set:
                kickers.append(card.number)
                if len(kickers) == num_kickers:
                    break
        return kickers

    def _check_flush_straight_and_sf(self) -> Optional[HandValue]:
        """
        Checks for Straight Flush, Flush, and Straight.
        Prioritizes SF > Flush > Straight.
        Returns the corresponding HandValue if found, otherwise None.
        """
        best_flush_ranks: Optional[List[int]] = None

        # Check suits with 5+ cards for Flush / Straight Flush potential
        for suit, count in self.suit_counts.items():
            if count >= 5:
                suit_cards = self.cards_by_suit[suit]
                suit_ranks = [card.number for card in suit_cards]

                # Check for Straight Flush within this suit's cards
                # Normal Straight Flush check (descending)
                for i in range(len(suit_ranks) - 4):
                    is_sf = True
                    for j in range(4):
                        if suit_ranks[i+j] != suit_ranks[i+j+1] + 1:
                            is_sf = False
                            break
                    if is_sf:
                        high_card = suit_ranks[i]
                        hand_type = 10 if high_card == CardNumber.ACE else 9
                        return HandValue(hand_type, high_card, -1, []) # Found best possible hand

                # Ace-low Straight Flush check (A, 5, 4, 3, 2)
                suit_ranks_set = set(suit_ranks)
                if {CardNumber.ACE, CardNumber.FIVE, CardNumber.FOUR, CardNumber.THREE, CardNumber.TWO}.issubset(suit_ranks_set):
                     # Ace-low SF found (5 high)
                     return HandValue(9, CardNumber.FIVE, -1, [])

                # If we reached here for this suit, it's *not* a Straight Flush.
                # But since count >= 5, it *is* a Flush. Record it.
                # We only need to do this once, as only one flush suit possible in 7 cards.
                best_flush_ranks = suit_ranks[:5] # Top 5 cards of the suit
                break # Found the flush suit, no need to check other suits

        # If we found a Flush (but not SF), return the Flush HandValue
        if best_flush_ranks:
            # Hand type 6 (Flush), high card is best_flush_ranks[0], kickers are the rest
            return HandValue(6, best_flush_ranks[0], -1, best_flush_ranks[1:5])

        # Use unique ranks across all suits
        ranks = self.unique_ranks
        if len(ranks) >= 5:
            # Normal straight check (descending)
            for i in range(len(ranks) - 4):
                is_straight = True
                for j in range(4):
                    if ranks[i+j] != ranks[i+j+1] + 1:
                        is_straight = False
                        break
                if is_straight:
                    # Hand type 5 (Straight), high card is ranks[i]
                    return HandValue(5, ranks[i], -1, [])

            # Ace-low straight check (A, 2, 3, 4, 5) - needs set of all ranks
            all_ranks_set = set(self.rank_counts.keys())
            if {CardNumber.ACE, CardNumber.TWO, CardNumber.THREE, CardNumber.FOUR, CardNumber.FIVE}.issubset(all_ranks_set):
                 # Hand type 5 (Straight), high card is 5
                 return HandValue(5, CardNumber.FIVE, -1, [])

        # No SF, Flush, or Straight found
        return None

    def _check_rank_based_hands(self) -> Optional[HandValue]:
        """Checks for 4K, FH, 3K, 2P, P. Returns HandValue or None."""

        # 4 of a Kind
        if 4 in self.counts_to_values:
            quad_rank = self.counts_to_values[4][0]
            kickers = self._get_kickers([quad_rank], 1)
            return HandValue(8, quad_rank, -1, kickers)

        # Full House (Check relies on 3-of-a-kind existing)
        if 3 in self.counts_to_values:
            rank3 = self.counts_to_values[3][0] # Highest triple
            # Check for a pair (either from another triple or a pair group)
            if len(self.counts_to_values[3]) > 1: # Lower triple acts as pair
                rank2 = self.counts_to_values[3][1]
                return HandValue(7, rank3, rank2, [])
            elif 2 in self.counts_to_values: # Highest pair
                rank2 = self.counts_to_values[2][0]
                return HandValue(7, rank3, rank2, [])
            else:
                # We already know it's not a Full House if we are here
                trip_rank = self.counts_to_values[3][0]
                kickers = self._get_kickers([trip_rank], 2)
                return HandValue(4, trip_rank, -1, kickers)

        # Two Pair
        if 2 in self.counts_to_values and len(self.counts_to_values[2]) >= 2:
            high_pair = self.counts_to_values[2][0]
            low_pair = self.counts_to_values[2][1]
            kickers = self._get_kickers([high_pair, low_pair], 1)
            return HandValue(3, high_pair, low_pair, kickers)

        # Pair
        if 2 in self.counts_to_values:
            # We know it's not Two Pair if we are here
            pair_rank = self.counts_to_values[2][0]
            kickers = self._get_kickers([pair_rank], 3)
            return HandValue(2, pair_rank, -1, kickers)

        return None # No rank-based hand found

    def _check_high_card(self) -> HandValue:
        """Determines the High Card hand value."""
        # Highest 5 cards overall define the hand
        high_card = self.cards[0].number
        kickers = [card.number for card in self.cards[1:5]] # Next 4 highest cards
        return HandValue(1, high_card, -1, kickers)

    def check_hand_value(self) -> HandValue:
        # 1. Check for Flush variations (SF, Flush) and Straight first.
        # They are combined is because they all need to loop over the cards
        # Can Return, since they are better than any rank based hands that are still possible if they exist
        flush_straight_sf_hand = self._check_flush_straight_and_sf()
        if flush_straight_sf_hand:
            return flush_straight_sf_hand

        # 2. Check Rank-based hands (4K, FH, 3K, 2P, P)
        rank_hand = self._check_rank_based_hands()
        if rank_hand:
            return rank_hand

        # 3. High Card (Fallback)
        return self._check_high_card()

    def compare_to(self, other) -> float:
        return self.check_hand_value().compare_to(other.check_hand_value())

    def compare(self, other) -> Optional[bool]:
        val = self.compare_to(other)
        if val > 0: return True
        elif val < 0: return False
        else: return None # Tie

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
print(hand_1.compare(hand_2))

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

def calc_odds(all_player_cards: List[List[Card]], table_cards: List[Card]) -> Tuple[List[float], List[float]]:
    # Gewinnchancen jedes Spielers in momentaner Situation (table cards) berechnen
    all_used_cards = table_cards + [card for player_cards in all_player_cards for card in player_cards]
    all_unused_cards = [card for card in get_all_cards() if card not in all_used_cards]
    
    start_time = time.time()
    all_possible_table_cards_dict = get_all_possible_table_cards(table_cards, all_unused_cards)
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