from typing import List
from .all_hands import poker_hands
from .card import CardNumber
from enum import IntEnum

class HandType(IntEnum):
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
        high_card_in_type = second_high_card_in_type = ''
        if self.high_card_in_type_value:
            high_card_in_type = f', High card in type: {CardNumber(self.high_card_in_type_value).name}'
        
        if self.second_high_card_in_type_value:
            second_high_card_in_type = f', Second high card in type: {CardNumber(self.second_high_card_in_type_value).name}'
        if self.high_cards and self.high_cards != []:
            high_cards = f', High cards: {[card.name for card in self.high_cards]}'
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
