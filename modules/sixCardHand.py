from typing import List, Dict, Optional, Tuple
from collections import Counter, defaultdict
from .card import Suit, CardNumber, Card
from .hand_value import HandValue, HandType
from modules import card

class Hand:
    def __init__(self, cards : List[Card]):
        if len(cards) != 6:
            raise ValueError("6 Card Hand requires 6 cards")

        # Store cards sorted by rank (descending)
        self.cards: List[Card] = sorted(cards, key=lambda card: card.number, reverse=True)

        # Count for ranks and suits
        self.rank_counts: Counter[CardNumber] = Counter(card.number for card in self.cards)
        self.suit_counts: Counter[Suit] = Counter(card.suit for card in self.cards)

        # Group cards by suit, sorted descending by rank within each suit
        self.cards_by_suit: Dict[Suit, List[Card]] = defaultdict(list)
        for card in self.cards:
            self.cards_by_suit[card.suit].append(card)
        for s in self.cards_by_suit:
            self.cards_by_suit[s].sort(key=lambda card: card.number, reverse=True)

        # Unique ranks present, sorted descending
        self.unique_ranks: List[CardNumber] = sorted(self.rank_counts.keys(), reverse=True)

        # Initialize lookup for rank-based hands (will be populated only if needed)
        self.counts_to_values: Optional[Dict[int, List[CardNumber]]] = None


    def _initialize_rank_based_lookup(self):
        """
        Lazy initialization of the rank-based lookup.
        Only called if no straight flush, flush, or straight is found.
        """
        # Prevent re-initialization
        if self.counts_to_values is not None:
            return

        self.counts_to_values = defaultdict(list)
        for value, count in self.rank_counts.items():
            # Can skip count <= 1 check as we only care about 2, 3, 4
            if count > 1:
                self.counts_to_values[count].append(value)

        # Sort the ranks within each count descending
        for count in self.counts_to_values:
            self.counts_to_values[count].sort(reverse=True)


    def _get_kickers(self, defining_card_ranks: List[CardNumber], num_kickers: int) -> List[CardNumber]:
        kickers: List[CardNumber] = []
        defining_set = set(defining_card_ranks) # Faster lookups
        for card in self.cards:
            if card.number not in defining_set:
                kickers.append(card.number)
                if len(kickers) == num_kickers:
                    break
        return kickers



    def _check_straight(self, ranks_sorted: List[CardNumber]) -> Tuple[List[Card], Tuple[bool, Optional[CardNumber]]]:
        """
        Check if there's a straight or potential straight draw in the hand.
        Returns:
            - List of cards that would improve the straight
            - Tuple containing (whether there's already a straight, highest card if exists)
        """
        # Need 4 to check for a draw
        if len(ranks_sorted) < 4:
            return [], (False, None)

        # Handle Ace as both high and low
        if CardNumber.ACE in ranks:
            ranks.append(CardNumber.ACE_LOW)
        
        num_in_a_row = 0
        improving_cards : List[Tuple[Card, HandValue]] = []
        first_straight_rank = None
        last_rank = None
        current_best_hand_value = HandValue(HandType.HIGH_CARD.value, None, None, [])
        for i, rank in enumerate(ranks):
            if not first_straight_rank:
                first_straight_rank = rank

            if rank != last_rank - 1:
                num_in_a_row = 1
                last_rank = rank
                continue
            
            num_in_a_row += 1
            
            # Improve by filling gap
            if num_in_a_row == 3:
                if ranks[i+2] == ranks[i] - 2:
                    if ranks[i+1] != ranks[i] - 1:
                        improving_card = Card(ranks[i] - 1, None)
                        if improving_card not in improving_cards:
                            improving_cards.append((improving_card, HandValue(HandType.STRAIGHT.value, first_straight_rank, None, [])))

            # Improve by adding a card
            if num_in_a_row == 4:
                if ranks[i+1] != ranks[i] - 1:
                    if ranks[i] - 1 >= CardNumber.TWO:
                        improving_card = Card(ranks[i] - 1, None)
                        if improving_card not in improving_cards:
                            improving_cards.append((improving_card, HandValue(HandType.STRAIGHT.value, first_straight_rank, None, [])))
                    if ranks[i] + 1 == CardNumber.TWO:
                        improving_card = Card(CardNumber.ACE, None)
                        if improving_card not in improving_cards:
                            improving_cards.append((improving_card, HandValue(HandType.STRAIGHT.value, CardNumber.ACE, None, [])))
            
            # Improve by removing a card
            if num_in_a_row == 5:
                if first_straight_rank != CardNumber.ACE:
                    improving_card = Card(first_straight_rank + 1, None)
                    if improving_card not in improving_cards:
                        improving_cards.append((improving_card, HandValue(HandType.STRAIGHT.value, first_straight_rank + 1, None, [])))
                current_best_hand_value = max(current_best_hand_value, HandValue(HandType.STRAIGHT.value, first_straight_rank, None, []))
            
            last_rank = rank
        
        actually_improving_cards = []
        for card, hand_value in improving_cards:
            if hand_value > current_best_hand_value:
                current_best_hand_value = hand_value
                actually_improving_cards.append((card, hand_value))
        
        return actually_improving_cards, (True, current_best_hand_value)

    def _check_sf_flush_and_straight(self, highest_win_type : HandType) -> Optional[HandValue]:
        for suit in self.suit_counts:
            if self.suit_counts[suit] >= 4:
                suit_ranks: List[CardNumber] = [card.number for card in self.cards_by_suit[suit]]

                # Check for Straight Flush using the ranks of this suit
                improving_cards, (is_sf, sf_high_card) = self._check_straight(suit_ranks)
                for card, hand_value in improving_cards:
                    hand_value.type_value = HandType.STRAIGHT_FLUSH.value
                    card.suit = suit
                if is_sf:
                    # Royal flush is a Straight Flush ending in Ace
                    is_royal = sf_high_card == CardNumber.ACE
                    hand_type = HandType.ROYAL_FLUSH if is_royal else HandType.STRAIGHT_FLUSH
                    # Royal Flush doesn't need kickers, SF uses high card
                    primary_rank = sf_high_card if not is_royal else CardNumber.ACE # Or some convention
                    return improving_cards,HandValue(hand_type.value, primary_rank, None, [])

                # If not a Straight Flush, it must be at least a Flush
                # The 5 highest cards of the suit define the flush
                improving_cards : List[Tuple[Card, HandValue]] = []
                if self.suit_counts[suit] >= 5:
                    for i in range(suit_ranks[0], 14):
                        improving_cards.append((Card(i, suit), HandValue(HandType.FLUSH.value, i, None, [])))
                    return improving_cards, HandValue(HandType.FLUSH.value, suit_ranks[0], None, suit_ranks[1:]) # Use None for secondary rank

        if highest_win_type >= HandType.FLUSH:
            return None

        # No flush found, check for regular Straight using all unique ranks
        is_straight, straight_high_card = self._check_straight(self.unique_ranks)
        if is_straight:
            return HandValue(HandType.STRAIGHT.value, straight_high_card, None, [])


        # No SF, Flush, or Straight found
        return None


    def _check_rank_based_hands(self, highest_win_type : HandType) -> Optional[HandValue]:
        if self.counts_to_values is None:
            raise RuntimeError("_initialize_rank_based_lookup must be called before _check_rank_based_hands") # Should not happen in normal flow

        # 4 of a Kind
        if 4 in self.counts_to_values:
            quad_rank = self.counts_to_values[4][0] # Highest quad rank
            kickers = self._get_kickers([quad_rank], 1)
            return HandValue(HandType.FOUR_OF_A_KIND.value, quad_rank, None, kickers)

        # Full House or 3 of a Kind
        if 3 in self.counts_to_values:
            rank3 = self.counts_to_values[3][0] # Highest triple rank
            # Full House:
            # Option 1: Two sets of trips (use lower trips as the 'pair')
            if len(self.counts_to_values[3]) > 1:
                rank2 = self.counts_to_values[3][1]
                return HandValue(HandType.FULL_HOUSE.value, rank3, rank2, [])
            # Option 2: One set of trips and at least one pair
            elif 2 in self.counts_to_values:
                rank2 = self.counts_to_values[2][0]
                return HandValue(HandType.FULL_HOUSE.value, rank3, rank2, [])
            # Otherwise, it's just 3 of a Kind
            else:
                kickers = self._get_kickers([rank3], 2)
                return HandValue(HandType.THREE_OF_A_KIND.value, rank3, None, kickers)

        if highest_win_type >= HandType.THREE_OF_A_KIND:
            return None

        # Two Pair
        if 2 in self.counts_to_values and len(self.counts_to_values[2]) >= 2:
            high_pair_rank = self.counts_to_values[2][0]
            low_pair_rank = self.counts_to_values[2][1]
            kickers = self._get_kickers([high_pair_rank, low_pair_rank], 1)
            return HandValue(HandType.TWO_PAIR.value, high_pair_rank, low_pair_rank, kickers)

        if highest_win_type >= HandType.TWO_PAIR:
            return None

        # One Pair
        if 2 in self.counts_to_values:
            pair_rank = self.counts_to_values[2][0]
            kickers = self._get_kickers([pair_rank], 3)
            return HandValue(HandType.PAIR.value, pair_rank, None, kickers)

        # No rank-based hand found
        return None


    def _check_high_card(self) -> HandValue:
        high_card_rank = self.cards[0].number
        kickers = [card.number for card in self.cards[1:5]]
        return HandValue(HandType.HIGH_CARD.value, high_card_rank, None, kickers)


    def check_hand_value(self) -> HandValue:
        # 1. Check for flush-based hands (SF, Flush) and Straights first.
        # These outrank all pair-based hands.
        highest_win_type = HandType.HIGH_CARD
        best_hand = self._check_sf_flush_and_straight(highest_win_type = highest_win_type)
        if best_hand:
            return best_hand

        # 2. Lazily initialize the rank counts lookup if needed.
        self._initialize_rank_based_lookup()

        # 3. Check Rank-based hands (4K, FH, 3K, 2P, P) in descending order of rank.
        best_hand = self._check_rank_based_hands(highest_win_type = highest_win_type)
        if best_hand:
            return best_hand

        # 4. If nothing else, it's High Card.
        return self._check_high_card()