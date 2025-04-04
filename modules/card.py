import enum

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