from enum import Enum, auto
from typing import List
from .all_hands import poker_hands
from .card import CardNumber

class HandType(Enum):
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9
    
    def __str__(self):
        # Map the enum value to the corresponding poker hand name
        return str(poker_hands[self.value + 1])

class HandValue:
    def __init__(self, hand_type: HandType, kickers: List[int]):
        self.hand_type = hand_type
        self.kickers = kickers
    
    def __lt__(self, other):
        if self.hand_type.value != other.hand_type.value:
            return self.hand_type.value < other.hand_type.value
        
        for i in range(min(len(self.kickers), len(other.kickers))):
            if self.kickers[i] != other.kickers[i]:
                return self.kickers[i] < other.kickers[i]
        
        return len(self.kickers) < len(other.kickers)
    
    def __eq__(self, other):
        if not isinstance(other, HandValue):
            return False
        
        if self.hand_type != other.hand_type:
            return False
        
        if len(self.kickers) != len(other.kickers):
            return False
        
        for i in range(len(self.kickers)):
            if self.kickers[i] != other.kickers[i]:
                return False
        
        return True
    
    def __str__(self):
        return f"{self.hand_type}"
