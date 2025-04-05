import tkinter as tk
from tkinter import ttk
import time
from typing import List, Dict, Tuple
import itertools
from enum import Enum, auto
import math
import random

class Suit(Enum):
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

class CardNumber(Enum):
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

class Hand:
    def __init__(self, cards: List[Card]):
        self.cards = cards
    
    def check_hand_value(self) -> float:
        """Evaluates the best 5-card hand value within a collection of 5+ cards."""
        if len(self.cards) < 5:
            return 0
        
        best_value = 0
        for five_cards in itertools.combinations(self.cards, 5):
            value = self._evaluate_five_card_hand(list(five_cards))
            best_value = max(best_value, value)
        
        return best_value
    
    def _evaluate_five_card_hand(self, cards: List[Card]) -> float:
        """Returns a numeric value that can be used to compare poker hands."""
        number_counts = {}
        for card in cards:
            number_counts[card.number] = number_counts.get(card.number, 0) + 1
        
        sorted_cards = sorted(cards, key=lambda c: c.number.value, reverse=True)
        is_flush = all(card.suit == cards[0].suit for card in cards)
        
        card_values = [card.number.value for card in sorted_cards]
        is_straight = False
        
        # Check for straight (including the special A-2-3-4-5 case)
        if len(set(card_values)) == 5:
            if max(card_values) - min(card_values) == 4:
                is_straight = True
            elif set(card_values) == {14, 5, 4, 3, 2}:  # A, 5, 4, 3, 2
                is_straight = True
                # Adjust sorted cards if it's a 5-high straight
                sorted_cards = sorted_cards[1:] + [sorted_cards[0]]
        
        hand_type = 0
        kickers = []
        
        # Royal Flush
        if is_flush and is_straight and sorted_cards[0].number == CardNumber.ACE and sorted_cards[1].number == CardNumber.KING:
            hand_type = HandType.ROYAL_FLUSH.value
        
        # Straight Flush
        elif is_flush and is_straight:
            hand_type = HandType.STRAIGHT_FLUSH.value
            kickers = [sorted_cards[0].number.value]
        
        # Four of a kind
        elif 4 in number_counts.values():
            hand_type = HandType.FOUR_OF_A_KIND.value
            four_of_a_kind_value = next(num for num, count in number_counts.items() if count == 4)
            kicker = next(num for num, count in number_counts.items() if count == 1)
            kickers = [four_of_a_kind_value.value, kicker.value]
        
        # Full House
        elif 3 in number_counts.values() and 2 in number_counts.values():
            hand_type = HandType.FULL_HOUSE.value
            three_of_a_kind_value = next(num for num, count in number_counts.items() if count == 3)
            pair_value = next(num for num, count in number_counts.items() if count == 2)
            kickers = [three_of_a_kind_value.value, pair_value.value]
        
        # Flush
        elif is_flush:
            hand_type = HandType.FLUSH.value
            kickers = [card.number.value for card in sorted_cards]
        
        # Straight
        elif is_straight:
            hand_type = HandType.STRAIGHT.value
            kickers = [sorted_cards[0].number.value]
        
        # Three of a kind
        elif 3 in number_counts.values():
            hand_type = HandType.THREE_OF_A_KIND.value
            three_of_a_kind_value = next(num for num, count in number_counts.items() if count == 3)
            other_values = sorted([num.value for num, count in number_counts.items() if count == 1], reverse=True)
            kickers = [three_of_a_kind_value.value] + other_values
        
        # Two Pair
        elif list(number_counts.values()).count(2) == 2:
            hand_type = HandType.TWO_PAIR.value
            pairs = sorted([num.value for num, count in number_counts.items() if count == 2], reverse=True)
            kicker = next(num.value for num, count in number_counts.items() if count == 1)
            kickers = pairs + [kicker]
        
        # One Pair
        elif 2 in number_counts.values():
            hand_type = HandType.PAIR.value
            pair_value = next(num for num, count in number_counts.items() if count == 2)
            other_values = sorted([num.value for num, count in number_counts.items() if count == 1], reverse=True)
            kickers = [pair_value.value] + other_values
        
        # High Card
        else:
            hand_type = HandType.HIGH_CARD.value
            kickers = [card.number.value for card in sorted_cards]
        
        # Combine hand type with kickers for final numeric value
        value = hand_type
        for i, kicker in enumerate(kickers):
            # Each kicker is placed in a decreasing decimal "slot" so they can be compared
            value += kicker / (100 ** (i + 1))
        
        return value

def get_all_cards() -> List[Card]:
    """Return a list of all 52 cards in a standard deck."""
    return [Card(number, suit) for suit in Suit for number in CardNumber]

def calculate_hand_odds(all_player_cards: List[List[Card]], table_cards: List[Card],
                        status_callback, progress_callback):
    """
    Calculate the odds of each player winning or tying.

    Returns:
    - win_percentages: % of times each player wins outright
    - tie_percentages: % of times each player ties
    - player_wins: number of outright wins for each player
    - player_ties: number of ties for each player
    - total_card_amount: total number of boards evaluated
    """
    # Already-selected cards
    all_used_cards = table_cards + [card for player_cards in all_player_cards for card in player_cards]
    
    # All available cards in the deck minus used ones
    all_cards = get_all_cards()
    all_unused_cards = [card for card in all_cards 
                        if card not in all_used_cards]
    
    # Number of community cards still to draw
    cards_to_draw = 5 - len(table_cards)
    
    # If the table is already complete (5 cards), just compare
    if cards_to_draw <= 0:
        all_player_hands = []
        for player_cards in all_player_cards:
            combined = player_cards + table_cards
            current_hand = Hand(combined)
            all_player_hands.append(current_hand)
        
        all_hand_values = [hand.check_hand_value() for hand in all_player_hands]
        best_value = max(all_hand_values)
        best_indices = [idx for idx, val in enumerate(all_hand_values) if val == best_value]
        
        player_wins = [0] * len(all_player_cards)
        player_ties = [0] * len(all_player_cards)
        
        # If exactly one player has the best hand -> they win; else they tie
        if len(best_indices) == 1:
            player_wins[best_indices[0]] = 1
        else:
            for idx in best_indices:
                player_ties[idx] = 1
        
        # Out of 1 board
        win_percentages = [100.0 if w == 1 else 0.0 for w in player_wins]
        tie_percentages = [100.0 if t == 1 else 0.0 for t in player_ties]
        
        return win_percentages, tie_percentages, player_wins, player_ties, 1
    
    # Otherwise, we must enumerate or sample all possible ways to fill the remaining cards
    MAX_COMBINATIONS = 5000
    total_combinations = math.comb(len(all_unused_cards), cards_to_draw)
    
    use_sampling = total_combinations > MAX_COMBINATIONS
    
    if use_sampling:
        status_callback(f"Using sampling (out of {total_combinations:,} possible combinations)")
        all_combinations = []
        possible_indices = list(range(len(all_unused_cards)))
        for _ in range(MAX_COMBINATIONS):
            sampled_indices = random.sample(possible_indices, cards_to_draw)
            sampled_cards = [all_unused_cards[i] for i in sampled_indices]
            all_combinations.append(sampled_cards)
        total_count = MAX_COMBINATIONS
    else:
        status_callback(f"Calculating all {total_combinations:,} combinations")
        all_combinations = list(itertools.combinations(all_unused_cards, cards_to_draw))
        total_count = len(all_combinations)
    
    player_wins = [0] * len(all_player_cards)
    player_ties = [0] * len(all_player_cards)
    
    for i, combo in enumerate(all_combinations):
        complete_table = table_cards + list(combo)
        
        all_player_hands = []
        for player_cards in all_player_cards:
            combined = player_cards + complete_table
            current_hand = Hand(combined)
            all_player_hands.append(current_hand)
        
        all_hand_values = [hand.check_hand_value() for hand in all_player_hands]
        best_value = max(all_hand_values)
        best_indices = [idx for idx, val in enumerate(all_hand_values) if val == best_value]
        
        if len(best_indices) == 1:
            player_wins[best_indices[0]] += 1
        else:
            for idx in best_indices:
                player_ties[idx] += 1
        
        if i % 50 == 0 or i == (total_count - 1):
            progress = (i + 1) / total_count * 100
            progress_callback(progress)
    
    win_percentages = [round(w / total_count * 100, 2) for w in player_wins]
    tie_percentages = [round(t / total_count * 100, 2) for t in player_ties]
    
    return win_percentages, tie_percentages, player_wins, player_ties, total_count


class PokerOddsCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Odds Calculator")
        
        # Configure the theme for better aesthetics
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Primary colors
        bg_color = "#2c3e50"       # Dark blue
        secondary_bg = "#34495e"  # Slightly lighter
        accent_color = "#3498db"   # Soft blue
        text_color = "#ecf0f1"     # Light text
        highlight_color = "#f39c12"  # Soft orange
        
        # Configure styles
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel", background=bg_color, foreground=text_color)
        self.style.configure("TLabelframe", background=bg_color, foreground=text_color)
        self.style.configure("TLabelframe.Label", background=bg_color, foreground=highlight_color, font=('Arial', 10, 'bold'))
        
        # Button styles
        self.style.configure("TButton", background=secondary_bg, foreground=text_color, borderwidth=1)
        self.style.map("TButton", background=[('active', accent_color), ('pressed', secondary_bg)])
        
        # Combobox styles
        self.style.configure("TCombobox",
                             selectbackground=accent_color,
                             fieldbackground=secondary_bg,
                             background=secondary_bg,
                             foreground=text_color,
                             arrowcolor=text_color,
                             borderwidth=1)
        self.style.map("TCombobox",
                       fieldbackground=[('readonly', secondary_bg)],
                       selectbackground=[('readonly', accent_color)],
                       selectforeground=[('readonly', 'white')])
        
        # Special styles for buttons
        self.style.configure("Calculate.TButton", font=('Arial', 10, 'bold'))
        self.style.configure("Cancel.TButton", foreground="#e74c3c")
        
        # Progress bar style
        self.style.configure("TProgressbar", background=accent_color, troughcolor=secondary_bg)
        
        # Set fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(background=bg_color)
        
        # Variables
        self.players = []
        self.table_cards = []
        self.all_cards = get_all_cards()
        self.used_cards = []
        self.calculation_running = False
        self.cancel_calculation = False
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=15)
        
        # Title
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        title_label = tk.Label(
            title_frame,
            text="POKER ODDS CALCULATOR",
            font=("Arial", 22, "bold"),
            fg=highlight_color,
            bg=bg_color
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            title_frame,
            text="V0.3",
            font=("Arial", 10, "italic"),
            fg=text_color,
            bg=bg_color
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0), pady=(8, 0))
        
        # Exit fullscreen button
        exit_button = ttk.Button(header_frame, text="Exit Fullscreen", command=self.exit_fullscreen)
        exit_button.pack(side=tk.RIGHT)
        
        # Content area
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        
        # Players column
        self.players_frame = ttk.LabelFrame(content_frame, text="PLAYERS", padding="15")
        self.players_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        add_player_btn = ttk.Button(self.players_frame, text="+ Add Player", style="TButton", command=self.add_player)
        add_player_btn.pack(fill=tk.X, pady=10)
        
        self.players_container = ttk.Frame(self.players_frame)
        self.players_container.pack(fill=tk.BOTH, expand=True)
        
        # Right column
        right_column = ttk.Frame(content_frame)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Table cards section
        self.table_frame = ttk.LabelFrame(right_column, text="TABLE CARDS", padding="15")
        self.table_frame.pack(fill=tk.X, expand=False, pady=(0, 15))
        
        card_positions = ["Flop", "Flop", "Flop", "Turn", "River"]
        table_cards_container = ttk.Frame(self.table_frame)
        table_cards_container.pack(fill=tk.X)
        
        self.table_card_selectors = []
        for i in range(5):
            position_frame = ttk.Frame(table_cards_container)
            position_frame.pack(side=tk.LEFT, padx=10, pady=5)
            
            ttk.Label(position_frame, text=card_positions[i]).pack(anchor="center")
            
            card_frame = ttk.Frame(position_frame)
            card_frame.pack()
            
            card_selector = self.create_card_selector(card_frame, f"table_card_{i}")
            self.table_card_selectors.append(card_selector)
        
        # Results section
        self.results_frame = ttk.LabelFrame(right_column, text="RESULTS", padding="15")
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.style.configure("Results.TFrame", background=secondary_bg)
        results_container = ttk.Frame(self.results_frame, style="Results.TFrame")
        results_container.pack(fill=tk.BOTH, expand=True, pady=5)
        self.results_frame_container = results_container
        
        # Calculate & Cancel buttons
        button_frame = ttk.Frame(right_column)
        button_frame.pack(fill=tk.X, pady=15)
        
        self.calculate_button = ttk.Button(button_frame, text="CALCULATE ODDS",
                                           command=self.start_calculation,
                                           style="Calculate.TButton")
        self.calculate_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=8)
        
        self.cancel_button = ttk.Button(button_frame, text="CANCEL",
                                        command=self.cancel_calculation_handler,
                                        style="Cancel.TButton",
                                        state=tk.DISABLED)
        self.cancel_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0), ipady=8)
        
        # Add at least 2 players by default
        self.add_player()
        self.add_player()
        
        # Status frame
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to calculate poker odds")
        status_label = ttk.Label(self.status_frame, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.percentage_var = tk.StringVar()
        self.percentage_var.set("0%")
        self.percentage_label = ttk.Label(self.status_frame, textvariable=self.percentage_var,
                                          width=8, anchor=tk.CENTER, font=('Arial', 9, 'bold'))
        self.percentage_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.progress_var = tk.DoubleVar()
        self.progress_var.set(0)
        self.progress_bar = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL,
                                            length=100, mode='determinate',
                                            variable=self.progress_var,
                                            style="TProgressbar")
        self.progress_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))

    def exit_fullscreen(self):
        self.root.attributes('-fullscreen', False)
        self.root.geometry("1200x800")

    def create_card_selector(self, parent, name):
        frame = ttk.Frame(parent)
        frame.pack()
        
        self.style.configure("Card.TCombobox", padding=3, relief="flat", borderwidth=1)
        
        number_var = tk.StringVar()
        number_var.set("Select")
        number_dropdown = ttk.Combobox(
            frame,
            textvariable=number_var,
            width=6,
            state="readonly",
            style="Card.TCombobox"
        )
        
        # Populate number dropdown
        number_values = ["Select"]
        for number in CardNumber:
            val = str(number)
            if number == CardNumber.ACE:
                val = "A"
            elif number == CardNumber.KING:
                val = "K"
            elif number == CardNumber.QUEEN:
                val = "Q"
            elif number == CardNumber.JACK:
                val = "J"
            number_values.append(val)
        number_dropdown['values'] = number_values
        number_dropdown.pack(side=tk.LEFT, padx=(0, 2))
        
        suit_var = tk.StringVar()
        suit_var.set("Select")
        suit_dropdown = ttk.Combobox(
            frame,
            textvariable=suit_var,
            width=8,
            state="readonly",
            style="Card.TCombobox"
        )
        
        # Populate suit dropdown
        suit_values = ["Select"]
        for suit in Suit:
            suit_values.append(f"{suit.name.title()} {suit.symbol()}")
        suit_dropdown['values'] = suit_values
        suit_dropdown.pack(side=tk.LEFT)
        
        number_dropdown.bind('<<ComboboxSelected>>',
                             lambda e: self.update_card_selection(number_dropdown, suit_dropdown))
        suit_dropdown.bind('<<ComboboxSelected>>',
                           lambda e: self.update_card_selection(suit_dropdown, number_dropdown))
        
        return {
            "number": number_var,
            "suit": suit_var,
            "number_dropdown": number_dropdown,
            "suit_dropdown": suit_dropdown
        }

    def update_card_selection(self, changed_dropdown, other_dropdown):
        """Visual feedback if one dropdown is selected while the other is not."""
        self.style.configure("Hint.TCombobox", fieldbackground="#4a6990", foreground="white")
        self.style.configure("Error.TCombobox", fieldbackground="#e74c3c", foreground="white")
        
        if changed_dropdown.get() != "Select" and other_dropdown.get() == "Select":
            other_dropdown.configure(style="Hint.TCombobox")
        else:
            changed_dropdown.configure(style="Card.TCombobox")
            other_dropdown.configure(style="Card.TCombobox")
        
        self.update_used_cards()

    def add_player(self):
        player_num = len(self.players) + 1
        
        player_frame = ttk.LabelFrame(self.players_container,
                                      text=f"PLAYER {player_num}",
                                      padding="12")
        player_frame.pack(fill=tk.X, pady=8)
        
        info_frame = ttk.Frame(player_frame)
        info_frame.pack(fill=tk.X, pady=(0, 8))
        
        name_var = tk.StringVar(value=f"Player {player_num}")
        name_entry = ttk.Entry(info_frame, textvariable=name_var, width=15)
        name_entry.pack(side=tk.LEFT)
        
        remove_btn = ttk.Button(info_frame,
                                text="×",
                                width=3,
                                command=lambda f=player_frame, p=player_num: self.remove_player(f, p))
        remove_btn.pack(side=tk.RIGHT)
        
        cards_container = ttk.Frame(player_frame)
        cards_container.pack(fill=tk.X)
        
        card_labels = ["Card 1", "Card 2"]
        card_selectors = []
        
        for i in range(2):
            card_pos_frame = ttk.Frame(cards_container)
            card_pos_frame.pack(side=tk.LEFT, padx=10)
            
            ttk.Label(card_pos_frame, text=card_labels[i], font=("Arial", 9)).pack(anchor="center")
            
            card_frame = ttk.Frame(card_pos_frame)
            card_frame.pack()
            
            card_selector = self.create_card_selector(card_frame, f"player_{player_num}_card_{i}")
            card_selectors.append(card_selector)
        
        # Result label (displayed in the results section on the right)
        result_var = tk.StringVar(value="")
        result_label = ttk.Label(self.results_frame_container, textvariable=result_var,
                                 padding=(5, 8), font=('Arial', 10))
        result_label.pack(anchor=tk.W, pady=3, fill=tk.X)
        
        self.players.append({
            "frame": player_frame,
            "number": player_num,
            "name_var": name_var,
            "card_selectors": card_selectors,
            "result_label": result_var,
            "result_widget": result_label
        })

    def remove_player(self, frame, player_num):
        if len(self.players) <= 2:
            self.status_var.set("Cannot remove player. Minimum 2 players required.")
            return
        
        frame.destroy()
        
        player_to_remove = next((p for p in self.players if p["number"] == player_num), None)
        if player_to_remove:
            player_to_remove["result_widget"].destroy()
            self.players.remove(player_to_remove)
        
        self.update_used_cards()

    def update_used_cards(self):
        self.used_cards = []
        
        # Gather selected table cards
        for selector in self.table_card_selectors:
            card = self.get_card_from_selector(selector)
            if card:
                self.used_cards.append(card)
        
        # Gather selected player cards
        for player in self.players:
            for selector in player["card_selectors"]:
                card = self.get_card_from_selector(selector)
                if card:
                    self.used_cards.append(card)
        
        # Check for duplicates
        seen_cards = {}
        
        # Check table card duplicates
        for selector in self.table_card_selectors:
            card = self.get_card_from_selector(selector)
            if card:
                card_str = str(card)
                if card_str in seen_cards:
                    # Indicate duplicates in red
                    selector["number_dropdown"].configure(style="Error.TCombobox")
                    selector["suit_dropdown"].configure(style="Error.TCombobox")
                    seen_cards[card_str]["number_dropdown"].configure(style="Error.TCombobox")
                    seen_cards[card_str]["suit_dropdown"].configure(style="Error.TCombobox")
                else:
                    # Normal style if not just in a "hint" state
                    if (selector["number_dropdown"].cget("style") != "Hint.TCombobox" and
                            selector["suit_dropdown"].cget("style") != "Hint.TCombobox"):
                        selector["number_dropdown"].configure(style="Card.TCombobox")
                        selector["suit_dropdown"].configure(style="Card.TCombobox")
                    seen_cards[card_str] = selector
        
        # Check player card duplicates
        for player in self.players:
            for selector in player["card_selectors"]:
                card = self.get_card_from_selector(selector)
                if card:
                    card_str = str(card)
                    if card_str in seen_cards:
                        selector["number_dropdown"].configure(style="Error.TCombobox")
                        selector["suit_dropdown"].configure(style="Error.TCombobox")
                        seen_cards[card_str]["number_dropdown"].configure(style="Error.TCombobox")
                        seen_cards[card_str]["suit_dropdown"].configure(style="Error.TCombobox")
                    else:
                        if (selector["number_dropdown"].cget("style") != "Hint.TCombobox" and
                                selector["suit_dropdown"].cget("style") != "Hint.TCombobox"):
                            selector["number_dropdown"].configure(style="Card.TCombobox")
                            selector["suit_dropdown"].configure(style="Card.TCombobox")
                        seen_cards[card_str] = selector

    def get_card_from_selector(self, selector):
        number_str = selector["number"].get()
        suit_str = selector["suit"].get()
        
        if number_str == "Select" or suit_str == "Select":
            return None
        
        # Convert face letter to CardNumber
        if number_str == "A":
            number = CardNumber.ACE
        elif number_str == "K":
            number = CardNumber.KING
        elif number_str == "Q":
            number = CardNumber.QUEEN
        elif number_str == "J":
            number = CardNumber.JACK
        else:
            # Otherwise parse numeric
            number = next((n for n in CardNumber if str(n) == number_str), None)
        
        # Suit from suit string
        suit = None
        for s in Suit:
            if suit_str.startswith(s.name.title()):
                suit = s
                break
        
        if number and suit:
            return Card(number, suit)
        return None

    def cancel_calculation_handler(self):
        """Allows user to cancel an ongoing calculation."""
        if self.calculation_running:
            self.cancel_calculation = True
            self.status_var.set("Cancelling calculation...")

    def start_calculation(self):
        """Initiates odds calculation if it's not already running."""
        if self.calculation_running:
            return
        
        # Clear previous results
        for player in self.players:
            player["result_label"].set("")
        
        self.progress_var.set(0)
        self.percentage_var.set("0%")
        
        # Get table cards
        table_cards = []
        for selector in self.table_card_selectors:
            card = self.get_card_from_selector(selector)
            if card:
                table_cards.append(card)
        
        # Get player cards
        all_player_cards = []
        for player in self.players:
            player_cards = []
            for selector in player["card_selectors"]:
                card = self.get_card_from_selector(selector)
                if card:
                    player_cards.append(card)
            
            if len(player_cards) != 2:
                self.status_var.set(f"Player {player['number']} must have exactly 2 cards")
                return
            
            all_player_cards.append(player_cards)
        
        if len(all_player_cards) < 2:
            self.status_var.set("Need at least 2 players to calculate odds")
            return
        
        # Check for duplicates across all selected cards
        all_selected_cards = table_cards.copy()
        for pc in all_player_cards:
            all_selected_cards.extend(pc)
        
        seen = set()
        for c in all_selected_cards:
            if str(c) in seen:
                self.status_var.set(f"Error: Card {c} is used more than once")
                return
            seen.add(str(c))
        
        self.calculation_running = True
        self.cancel_calculation = False
        self.calculate_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        
        self.root.after(100, lambda: self.run_calculation(all_player_cards, table_cards))

    def run_calculation(self, all_player_cards, table_cards):
        """Runs calculation in the UI loop to avoid freezing."""
        try:
            start_time = time.time()
            self.status_var.set("Calculating odds... Please wait.")
            
            def update_status(message):
                self.status_var.set(message)
                self.root.update_idletasks()
            
            def update_progress(progress):
                self.progress_var.set(progress)
                self.percentage_var.set(f"{int(progress)}%")
                self.root.update_idletasks()
            
            win_percentages, tie_percentages, player_wins, player_ties, total_count = calculate_hand_odds(
                all_player_cards, table_cards, update_status, update_progress
            )
            
            if not self.cancel_calculation:
                # Highlight styles for results
                self.style.configure("Result.TLabel", 
                                     background="#34495e",
                                     foreground="#ecf0f1",
                                     padding=8,
                                     font=('Arial', 10))
                
                self.style.configure("StrongHand.TLabel", 
                                     background="#2980b9",
                                     foreground="white",
                                     padding=8,
                                     font=('Arial', 10, 'bold'))
                
                for i, player in enumerate(self.players):
                    # Retrieve or default to "Player n"
                    player_name = player['name_var'].get() if 'name_var' in player else f"Player {player['number']}"
                    
                    # Overall equity: win% + (tie% / number_of_tie_splits)
                    total_equity = win_percentages[i] + (tie_percentages[i] / len(self.players))
                    
                    # Format results
                    result_text = f"{player_name}\n"
                    result_text += f"Win: {win_percentages[i]}%   |   Tie: {tie_percentages[i]}%   |   "
                    result_text += f"Equity: {round(total_equity, 2)}%"
                    
                    player["result_label"].set(result_text)
                    
                    # Style based on equity
                    if total_equity > 50:
                        player["result_widget"].configure(style="StrongHand.TLabel")
                    else:
                        player["result_widget"].configure(style="Result.TLabel")
                
                end_time = time.time()
                calc_time = round(end_time - start_time, 2)
                self.status_var.set(f"✓ Calculation completed in {calc_time} seconds")
                self.progress_var.set(100)
                self.percentage_var.set("100%")
            else:
                self.status_var.set("✗ Calculation cancelled")
        
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
        
        finally:
            self.calculate_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            self.calculation_running = False
            self.cancel_calculation = False


def main():
    root = tk.Tk()
    app = PokerOddsCalculatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
