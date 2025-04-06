from enum import Enum, auto
import enum

class Suit(enum.IntEnum):
    CLUBS = auto()
    DIAMONDS = auto()
    HEARTS = auto()
    SPADES = auto()
    
    def __str__(self):
        return self.name.capitalize()
    
    def symbol(self):
        if self == Suit.CLUBS:
            return "♣"
        elif self == Suit.DIAMONDS:
            return "♦"
        elif self == Suit.HEARTS:
            return "♥"
        elif self == Suit.SPADES:
            return "♠"

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
    
    def __str__(self):
        if self.value <= 10:
            return str(self.value)
        elif self == CardNumber.JACK:
            return "J"
        elif self == CardNumber.QUEEN:
            return "Q"
        elif self == CardNumber.KING:
            return "K"
        else:
            return "A"

class Card:
    def __init__(self, number: CardNumber, suit: Suit):
        self.number = number
        self.suit = suit
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.number == other.number and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.number, self.suit))
    
    def __str__(self):
        return f"{self.number}{self.suit.symbol()}"
    
    def __repr__(self):
        return f"Card({self.number}, {self.suit})"