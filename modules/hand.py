from typing import List, Dict, Optional, Tuple
from collections import Counter
from .card import Suit, CardNumber, Card
from .hand_value import HandValue

class Hand:
    def __init__(self, cards : List[Card]):
        if len(cards) != 7:
            raise ValueError("Hold'em requires 7 cards")

        # Store cards sorted by rank (descending for easy high card access)
        self.cards = sorted(cards, key=lambda card: card.number, reverse=True)

        self.rank_counts = Counter(card.number for card in self.cards)
        self.suit_counts = Counter(card.suit for card in self.cards)

        # Group cards by suit, sorted descending by rank within each suit
        # -> Easily find flush, straight, etc.
        self.cards_by_suit: Dict[Suit, List[Card]] = {s: [] for s in Suit}
        for card in self.cards:
            self.cards_by_suit[card.suit].append(card)
        for s in self.cards_by_suit:
            self.cards_by_suit[s].sort(key=lambda card: card.number, reverse=True)
        # Unique ranks descending for straights
        self.unique_ranks = sorted(self.rank_counts.keys(), reverse=True)

    async def _initialize_rank_based_lookup(self):
        # Rank counts lookup (count -> list of ranks), sorted
        # -> easily find highest 4, 3, 2 of a kind
        # Only called once needed, since no sf,flush or straight found
        self.counts_to_values: Dict[int, List[int]] = {}
        for value, count in self.rank_counts.items():
            if count not in self.counts_to_values:
                self.counts_to_values[count] = []
            self.counts_to_values[count].append(value)
        for count in self.counts_to_values:
            self.counts_to_values[count].sort(reverse=True)

    async def _get_kickers(self, defining_card_ranks: List[int], num_kickers: int) -> List[int]:
        # Get kickers (high cards)
        kickers = []
        defining_set = set(defining_card_ranks) # Faster lookups
        for card in self.cards:
            if card.number not in defining_set:
                kickers.append(card.number)
                if len(kickers) == num_kickers:
                    break
        return kickers

    async def _check_straight(self,ranks_sorted) -> Tuple[bool, Optional[CardNumber]]:
        # Check for normal straight
        for i in range(len(ranks_sorted) - 4):
            is_straight = True
            for j in range(4):
                if ranks_sorted[i+j] != ranks_sorted[i+j+1] + 1:
                    is_straight = False
                    # Enough checked for straight to be no longer possible
                    break
            if is_straight:
                return True, ranks_sorted[i]

        # Check for (A,5,4,3,2)
        ranks_set = set(ranks_sorted)
        if {CardNumber.ACE, CardNumber.FIVE, CardNumber.FOUR, CardNumber.THREE, CardNumber.TWO}.issubset(ranks_set):
            return True, CardNumber.FIVE

        return False, None

    async def _check_sf_flush_and_straight(self) -> Optional[HandValue]:
        best_flush_ranks: Optional[List[int]] = None

        # Check suits with 5+ cards for Flush / Straight Flush
        for suit, count in self.suit_counts.items():
            if count >= 5:
                suit_cards = self.cards_by_suit[suit]
                suit_ranks = sorted([card.number for card in suit_cards], reverse=True)

                # Check for Straight Flush using _check_straight
                is_straight, high_card = await self._check_straight(suit_ranks)
                if is_straight:
                    # Royal flush check
                    hand_type = 10 if high_card == CardNumber.ACE else 9
                    return HandValue(hand_type, high_card, -1, [])

                # Not a SF, but still 5 in suit -> return flush
                best_flush_ranks = suit_ranks[:5]
                return HandValue(6, best_flush_ranks[0], -1, best_flush_ranks[1:5])

        # Use unique ranks across suits for straight check
        ranks = self.unique_ranks
        is_straight, high_card = await self._check_straight(ranks)
        if is_straight:
            # Return Straight
            return HandValue(5, high_card, -1, [])

        # No SF, Flush, or Straight
        return None


    async def _check_rank_based_hands(self) -> Optional[HandValue]:
        # 4 of a Kind
        if 4 in self.counts_to_values:
            quad_rank = self.counts_to_values[4][0]
            kickers = await self._get_kickers([quad_rank], 1)
            return HandValue(8, quad_rank, -1, kickers)

        # 3 of a kind or full house
        if 3 in self.counts_to_values:
            rank3 = self.counts_to_values[3][0] # Highest triple
            # Check for pair from triple or pair
            # if another triple, no pair possible
            if len(self.counts_to_values[3]) > 1:
                rank2 = self.counts_to_values[3][1]
                return HandValue(7, rank3, rank2, [])
            elif 2 in self.counts_to_values:
                rank2 = self.counts_to_values[2][0]
                return HandValue(7, rank3, rank2, [])
            else:
                # Not a Full House, return
                trip_rank = self.counts_to_values[3][0]
                kickers = await self._get_kickers([trip_rank], 2)
                return HandValue(4, trip_rank, -1, kickers)

        # Two Pair
        if 2 in self.counts_to_values and len(self.counts_to_values[2]) >= 2:
            high_pair = self.counts_to_values[2][0]
            low_pair = self.counts_to_values[2][1]
            kickers = await self._get_kickers([high_pair, low_pair], 1)
            return HandValue(3, high_pair, low_pair, kickers)

        # Pair
        if 2 in self.counts_to_values:
            # We know it's not Two Pair if we are here
            pair_rank = self.counts_to_values[2][0]
            kickers = await self._get_kickers([pair_rank], 3)
            return HandValue(2, pair_rank, -1, kickers)

        # No rank-based hand
        return None 

    async def _check_high_card(self) -> HandValue:
        # Highest card and 4 next highest cards async define hand
        high_card = self.cards[0].number
        kickers = [card.number for card in self.cards[1:5]]
        return HandValue(1, high_card, -1, kickers)

    async def check_hand_value(self) -> HandValue:
        # 1. Check for Flush variations (SF, Flush) and Straight first.
        # They are combined is because they all need to loop over the cards
        # Can Return, since they are better than any rank based hands that are still possible if they exist
        flush_straight_sf_hand = await self._check_sf_flush_and_straight()
        if flush_straight_sf_hand:
            return flush_straight_sf_hand

        # 2. Check Rank-based hands (4K, FH, 3K, 2P, P)
        await self._initialize_rank_based_lookup()
        rank_hand = await self._check_rank_based_hands()
        if rank_hand:
            return rank_hand

        # 3. High Card (Fallback)
        return await self._check_high_card()