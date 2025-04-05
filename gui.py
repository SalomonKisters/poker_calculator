import tkinter as tk
from tkinter import ttk
import os
from typing import List, Dict, Optional
from modules.card import Card, CardNumber, Suit
from main import calc_odds

class PokerCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Calculator")
        self.root.geometry("1000x1000")
        self.root.resizable(True, True)
        
        # Store player cards and table cards
        self.player_cards: List[List[Card]] = []
        self.table_cards: List[Card] = []
        
        # Player management
        self.player_frames = []
        self.current_players = 0
        self.max_players = 10  # Maximum number of players
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Poker Odds Calculator", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Players section with scrollable frame
        players_section = ttk.LabelFrame(main_frame, text="Players", padding="10")
        players_section.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Player management buttons
        player_buttons_frame = ttk.Frame(players_section)
        player_buttons_frame.pack(fill=tk.X, pady=5)
        
        add_player_btn = ttk.Button(player_buttons_frame, text="Add Player", command=self.add_player)
        add_player_btn.pack(side=tk.LEFT, padx=5)
        
        remove_player_btn = ttk.Button(player_buttons_frame, text="Remove Player", command=self.remove_player)
        remove_player_btn.pack(side=tk.LEFT, padx=5)
        
        # Create scrollable canvas for players
        self.players_canvas = tk.Canvas(players_section, borderwidth=0)
        players_scrollbar = ttk.Scrollbar(players_section, orient="vertical", command=self.players_canvas.yview)
        self.players_frame = ttk.Frame(self.players_canvas)
        
        self.players_canvas.configure(yscrollcommand=players_scrollbar.set)
        
        players_scrollbar.pack(side="right", fill="y")
        self.players_canvas.pack(side="left", fill="both", expand=True)
        self.players_window = self.players_canvas.create_window((0, 0), window=self.players_frame, anchor="nw")
        
        self.players_frame.bind("<Configure>", self.on_frame_configure)
        self.players_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Add initial players
        self.add_player()  # Add player 1
        self.add_player()  # Add player 2
        
        # Table cards frame
        table_frame = ttk.LabelFrame(main_frame, text="Table Cards", padding="10")
        table_frame.pack(fill=tk.X, pady=5)
        
        table_cards_frame = ttk.Frame(table_frame)
        table_cards_frame.pack(fill=tk.X)
        
        self.table_card_widgets = []
        for i in range(5):  # 5 cards max on the table
            card_frame = ttk.Frame(table_cards_frame)
            card_frame.grid(row=0, column=i, padx=5, pady=5)
            
            ttk.Label(card_frame, text=f"Card {i+1}:").pack(anchor=tk.W)
            
            card_number = ttk.Combobox(card_frame, values=[n.name for n in CardNumber])
            card_number.pack(fill=tk.X, pady=2)
            
            card_suit = ttk.Combobox(card_frame, values=[s.name for s in Suit])
            card_suit.pack(fill=tk.X, pady=2)
            
            self.table_card_widgets.append({
                'number': card_number,
                'suit': card_suit
            })
        
        # Calculate button
        calculate_button = ttk.Button(main_frame, text="Calculate Odds", command=self.calculate_odds)
        calculate_button.pack(pady=10)
        
        # Results frame
        self.results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Results text
        self.results_text = tk.Text(self.results_frame, height=10, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
    def get_card_from_widgets(self, number_widget, suit_widget) -> Optional[Card]:
        number_str = number_widget.get()
        suit_str = suit_widget.get()
        
        if not number_str or not suit_str:
            return None
        
        try:
            card_number = CardNumber[number_str]
            suit = Suit[suit_str]
            return Card(card_number, suit)
        except (KeyError, ValueError):
            return None
    
    def collect_player_cards(self):
        self.player_cards = []
        
        for player_widgets in self.player_frames:
            card1 = self.get_card_from_widgets(
                player_widgets['card1_number'], 
                player_widgets['card1_suit']
            )
            
            card2 = self.get_card_from_widgets(
                player_widgets['card2_number'], 
                player_widgets['card2_suit']
            )
            
            if card1 and card2:
                self.player_cards.append([card1, card2])
    
    def collect_table_cards(self):
        self.table_cards = []
        
        for card_widgets in self.table_card_widgets:
            card = self.get_card_from_widgets(
                card_widgets['number'],
                card_widgets['suit']
            )
            
            if card:
                self.table_cards.append(card)
    
    def calculate_odds(self):
        self.collect_player_cards()
        self.collect_table_cards()
        
        # Filter out empty player hands
        active_players = self.player_cards
        
        if len(active_players) < 2:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Please select cards for at least 2 players")
            return
        
        try:
            win_percentages, tie_percentages, player_wins, player_ties = calc_odds(active_players, self.table_cards)
            
            self.results_text.delete(1.0, tk.END)
            
            for i in range(len(active_players)):
                self.results_text.insert(tk.END, f"Player {i+1}:\n")
                self.results_text.insert(tk.END, f"  Win: {win_percentages[i]}%\n")
                self.results_text.insert(tk.END, f"  Tie: {tie_percentages[i]}%\n")
                total_equity = win_percentages[i] + (tie_percentages[i] / len(active_players))
                self.results_text.insert(tk.END, f"  Total equity: {round(total_equity, 2)}%\n")
                self.results_text.insert(tk.END, "-" * 40 + "\n")
                
        except Exception as e:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Error calculating odds: {str(e)}")

    def add_player(self):
        """Add a new player to the interface"""
        if self.current_players >= self.max_players:
            return  # Maximum number of players reached
        
        # Create a new player frame
        player_frame = ttk.LabelFrame(self.players_frame, text=f"Player {self.current_players + 1}", padding="5")
        player_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Card 1 selection
        card1_frame = ttk.Frame(player_frame)
        card1_frame.pack(fill=tk.X, pady=2)
        ttk.Label(card1_frame, text="Card 1:").pack(side=tk.LEFT)
        
        card1_number = ttk.Combobox(card1_frame, values=[n.name for n in CardNumber])
        card1_number.pack(side=tk.LEFT, padx=2)
        card1_suit = ttk.Combobox(card1_frame, values=[s.name for s in Suit])
        card1_suit.pack(side=tk.LEFT, padx=2)
        
        # Card 2 selection
        card2_frame = ttk.Frame(player_frame)
        card2_frame.pack(fill=tk.X, pady=2)
        ttk.Label(card2_frame, text="Card 2:").pack(side=tk.LEFT)
        
        card2_number = ttk.Combobox(card2_frame, values=[n.name for n in CardNumber])
        card2_number.pack(side=tk.LEFT, padx=2)
        card2_suit = ttk.Combobox(card2_frame, values=[s.name for s in Suit])
        card2_suit.pack(side=tk.LEFT, padx=2)
        
        self.player_frames.append({
            'frame': player_frame,
            'card1_number': card1_number,
            'card1_suit': card1_suit,
            'card2_number': card2_number,
            'card2_suit': card2_suit
        })
        
        self.current_players += 1
        self.update_player_labels()
    
    def remove_player(self):
        """Remove the last player from the interface"""
        if self.current_players <= 2:
            return  # Minimum 2 players required
        
        if self.player_frames:
            # Get the last player frame and destroy it
            last_player = self.player_frames.pop()
            last_player['frame'].destroy()
            self.current_players -= 1
            self.update_player_labels()
    
    def update_player_labels(self):
        """Update the player labels to reflect the current order"""
        for i, player_data in enumerate(self.player_frames):
            player_data['frame'].configure(text=f"Player {i + 1}")
    
    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.players_canvas.configure(scrollregion=self.players_canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Resize the canvas window to the size of canvas"""
        self.players_canvas.itemconfig(self.players_window, width=event.width)

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerCalculatorGUI(root)
    root.mainloop()
