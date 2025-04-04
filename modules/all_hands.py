class PokerHand:
    def __init__(self, name: str, value: int, defining_cards: int):
        self.name = name
        self.value = value
        self.defining_cards = defining_cards

    def __repr__(self):
        return f"PokerHand(name='{self.name}', value={self.value}, defining_cards={self.defining_cards})"

    def __str__(self):
        return f"{self.name}"

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