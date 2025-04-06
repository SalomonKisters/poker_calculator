import tkinter as tk
from tkinter import ttk, messagebox
from modules.card import Suit, CardNumber, Card
from modules.calculator import calc_odds
from modules.utils import check_validity
import multiprocessing as mp
import time
import threading

class PokerCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Odds Calculator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.num_players = tk.IntVar(value=2)
        self.division = tk.IntVar(value=32)
        self.players_cards = []
        self.table_cards = []
        self.progress_var = tk.DoubleVar(value=0)
        
        self.create_frames()
        
        self.create_settings_widgets()
        self.create_table_widgets()
        self.create_results_widgets()
        
        self.update_player_frames()
    
    def create_frames(self):
        self.settings_frame = ttk.LabelFrame(self.root, text="Settings")
        self.settings_frame.pack(fill="x", padx=10, pady=5)
        
        self.players_frame = ttk.LabelFrame(self.root, text="Players")
        self.players_frame.pack(fill="x", padx=10, pady=5)
        
        self.table_frame = ttk.LabelFrame(self.root, text="Table Cards")
        self.table_frame.pack(fill="x", padx=10, pady=5)
        
        self.results_frame = ttk.LabelFrame(self.root, text="Results")
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.player_card_frames = []
    
    def create_settings_widgets(self):
        ttk.Label(self.settings_frame, text="Number of Players:").grid(row=0, column=0, padx=5, pady=5)
        player_spin = ttk.Spinbox(self.settings_frame, from_=2, to=10, textvariable=self.num_players, width=5)
        player_spin.grid(row=0, column=1, padx=5, pady=5)
        player_spin.bind("<Return>", lambda e: self.update_player_frames())
        
        ttk.Button(self.settings_frame, text="Update", command=self.update_player_frames).grid(row=0, column=2, padx=5, pady=5)
        
        # Division (calculation accuracy)
        ttk.Label(self.settings_frame, text="Calculation Accuracy:").grid(row=0, column=3, padx=5, pady=5)
        ttk.Spinbox(self.settings_frame, from_=4, to=256, increment=4, textvariable=self.division, width=5).grid(row=0, column=4, padx=5, pady=5)
        
        # Calculate button
        ttk.Button(self.settings_frame, text="Calculate Odds", command=self.calculate_odds).grid(row=0, column=5, padx=20, pady=5)
    
    def create_table_widgets(self):
        # Table cards
        self.table_cards_var = []
        self.table_card_labels = []
        
        for i in range(5):
            frame = ttk.Frame(self.table_frame)
            frame.pack(side="left", padx=10, pady=5)
            
            # Card label
            card_label = ttk.Label(frame, text="🂠", font=("Arial", 24))
            card_label.pack()
            self.table_card_labels.append(card_label)
            
            # Card selection
            card_frame = ttk.Frame(frame)
            card_frame.pack()
            
            # Card number
            number_var = tk.StringVar(value="")
            number_combo = ttk.Combobox(card_frame, textvariable=number_var, width=5)
            number_combo['values'] = [str(CardNumber(i)) for i in range(2, 15)]
            number_combo.pack(side="left")
            
            # Card suit
            suit_var = tk.StringVar(value="")
            suit_combo = ttk.Combobox(card_frame, textvariable=suit_var, width=5)
            suit_combo['values'] = [s.symbol() for s in Suit]
            suit_combo.pack(side="left")
            
            self.table_cards_var.append((number_var, suit_var))
            
            # Bind events
            number_combo.bind("<<ComboboxSelected>>", lambda e, idx=i: self.update_card_display(idx, "table"))
            suit_combo.bind("<<ComboboxSelected>>", lambda e, idx=i: self.update_card_display(idx, "table"))
    
    def create_results_widgets(self):
        # Progress bar
        ttk.Label(self.results_frame, text="Progress:").pack(anchor="w", padx=10, pady=5)
        self.progress_bar = ttk.Progressbar(self.results_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        
        # Results text
        self.results_text = tk.Text(self.results_frame, height=15, width=80)
        self.results_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(self.results_text, command=self.results_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        # Time label
        self.time_label = ttk.Label(self.results_frame, text="Time: 0.00s")
        self.time_label.pack(anchor="e", padx=10, pady=5)
    
    def update_player_frames(self):
        # Clear existing player frames
        for frame in self.player_card_frames:
            frame.destroy()
        
        self.player_card_frames = []
        self.players_cards_var = []
        
        # Create new player frames
        for i in range(self.num_players.get()):
            player_frame = ttk.LabelFrame(self.players_frame, text=f"Player {i+1}")
            player_frame.pack(side="left", padx=10, pady=5)
            self.player_card_frames.append(player_frame)
            
            player_cards_var = []
            card_labels = []
            
            for j in range(2):  # Each player has 2 cards
                card_frame = ttk.Frame(player_frame)
                card_frame.pack(pady=5)
                
                # Card label
                card_label = ttk.Label(card_frame, text="🂠", font=("Arial", 24))
                card_label.pack()
                card_labels.append(card_label)
                
                # Card selection
                selection_frame = ttk.Frame(card_frame)
                selection_frame.pack()
                
                # Card number
                number_var = tk.StringVar(value="")
                number_combo = ttk.Combobox(selection_frame, textvariable=number_var, width=5)
                number_combo['values'] = [str(CardNumber(i)) for i in range(2, 15)]
                number_combo.pack(side="left")
                
                # Card suit
                suit_var = tk.StringVar(value="")
                suit_combo = ttk.Combobox(selection_frame, textvariable=suit_var, width=5)
                suit_combo['values'] = [s.symbol() for s in Suit]
                suit_combo.pack(side="left")
                
                player_cards_var.append((number_var, suit_var))
                
                # Bind events
                number_combo.bind("<<ComboboxSelected>>", lambda e, p_idx=i, c_idx=j: self.update_card_display(c_idx, "player", p_idx))
                suit_combo.bind("<<ComboboxSelected>>", lambda e, p_idx=i, c_idx=j: self.update_card_display(c_idx, "player", p_idx))
            
            self.players_cards_var.append(player_cards_var)
    
    def update_card_display(self, card_idx, card_type, player_idx=None):
        if card_type == "table":
            number_var, suit_var = self.table_cards_var[card_idx]
            if number_var.get() and suit_var.get():
                self.table_card_labels[card_idx].config(text=f"{number_var.get()}{suit_var.get()}")
            else:
                self.table_card_labels[card_idx].config(text="🂠")
        elif card_type == "player" and player_idx is not None:
            number_var, suit_var = self.players_cards_var[player_idx][card_idx]
            if number_var.get() and suit_var.get():
                # Find the card label
                card_frame = self.player_card_frames[player_idx].winfo_children()[card_idx]
                card_label = card_frame.winfo_children()[0]
                card_label.config(text=f"{number_var.get()}{suit_var.get()}")
            else:
                card_frame = self.player_card_frames[player_idx].winfo_children()[card_idx]
                card_label = card_frame.winfo_children()[0]
                card_label.config(text="🂠")
    
    def get_card_from_vars(self, number_var, suit_var):
        if not number_var.get() or not suit_var.get():
            return None
        
        # Convert string to CardNumber
        number_str = number_var.get()
        if number_str == "A":
            number = CardNumber.ACE
        elif number_str == "K":
            number = CardNumber.KING
        elif number_str == "Q":
            number = CardNumber.QUEEN
        elif number_str == "J":
            number = CardNumber.JACK
        else:
            number = CardNumber(int(number_str))
        
        # Convert symbol to Suit
        suit_symbol = suit_var.get()
        if suit_symbol == "♣":
            suit = Suit.CLUBS
        elif suit_symbol == "♦":
            suit = Suit.DIAMONDS
        elif suit_symbol == "♥":
            suit = Suit.HEARTS
        elif suit_symbol == "♠":
            suit = Suit.SPADES
        else:
            return None
        
        return Card(number, suit)
    
    def collect_cards(self):
        # Collect player cards
        all_player_cards = []
        for player_vars in self.players_cards_var:
            player_cards = []
            for number_var, suit_var in player_vars:
                card = self.get_card_from_vars(number_var, suit_var)
                if card:
                    player_cards.append(card)
            
            all_player_cards.append(player_cards)
        
        # Collect table cards
        table_cards = []
        for number_var, suit_var in self.table_cards_var:
            card = self.get_card_from_vars(number_var, suit_var)
            if card:
                table_cards.append(card)
        
        return all_player_cards, table_cards
    
    def display_results(self, all_player_cards, total_win_percentages, total_tie_percentages, total_player_wins, total_player_ties):
        self.results_text.delete(1.0, tk.END)
        
        for j in range(len(all_player_cards)):
            result = f'Player {j+1} wins {total_player_wins[j]} times or {round(total_win_percentages[j], 2)}%\n'
            result += f'Player {j+1} ties {total_player_ties[j]} times or {round(total_tie_percentages[j], 2)}%\n'
            total_equity = total_win_percentages[j] + (total_tie_percentages[j] / len(all_player_cards))
            result += f'Player {j+1} total equity: {round(total_equity, 2)}%\n'
            result += '-' * 40 + '\n'
            
            self.results_text.insert(tk.END, result)
    
    def update_progress(self, current, total):
        progress = (current / total) * 100
        self.progress_var.set(progress)
        self.results_text.insert(tk.END, f"Progress: {current}/{total}\n")
        self.results_text.see(tk.END)
    
    def calculate_odds(self):
        all_player_cards, table_cards = self.collect_cards()
        if all_player_cards is None or table_cards is None:
            return
        
        # Clear results
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        
        # Start calculation in a separate thread to keep UI responsive
        threading.Thread(target=self.run_calculation, args=(all_player_cards, table_cards), daemon=True).start()
    
    def run_calculation(self, all_player_cards, table_cards):
        start_time = time.time()
        division = self.division.get()

        try:
            
            check_validity(all_player_cards, table_cards)
            # Moving average only needed for 0 table cards, otherwise its overhead outweighs the benefits
            if len(all_player_cards) != 0:
                division = 1
            
            # Initial calculation
            current_amount = 1
            prev_max_numerator = 0
            numerators_to_check = [prev_max_numerator]
            
            total_win_percentages, total_tie_percentages, total_player_wins, total_player_ties = calc_odds(
                all_player_cards, table_cards, division=division, numerators_to_check=numerators_to_check
            )
            
            # Display initial results
            self.root.after(0, lambda: self.display_results(
                all_player_cards, total_win_percentages, total_tie_percentages, total_player_wins, total_player_ties
            ))
            self.root.after(0, lambda: self.update_progress(prev_max_numerator+1, division))
            
            # Iterative calculations for better accuracy
            while prev_max_numerator < division - 1:
                current_max_numerator = prev_max_numerator + current_amount
                current_numerators_to_check = list(range(prev_max_numerator + 1, current_max_numerator + 1))
                
                win_percentages, tie_percentages, player_wins, player_ties = calc_odds(
                    all_player_cards, table_cards, division=division, numerators_to_check=current_numerators_to_check
                )
                
                for j in range(len(all_player_cards)):
                    total_win_percentages[j] = (total_win_percentages[j] * (current_amount-1) + win_percentages[j] * current_amount) / (current_amount*2-1)
                    total_tie_percentages[j] = (total_tie_percentages[j] * (current_amount-1) + tie_percentages[j] * current_amount) / (current_amount*2-1)
                    total_player_wins[j] = total_player_wins[j] + player_wins[j]
                    total_player_ties[j] = total_player_ties[j] + player_ties[j]
                
                prev_max_numerator = current_max_numerator
                current_amount *= 2
                
                # Update UI
                self.root.after(0, lambda win=total_win_percentages, tie=total_tie_percentages, 
                                        p_win=total_player_wins, p_tie=total_player_ties: 
                                self.display_results(all_player_cards, win, tie, p_win, p_tie))
                self.root.after(0, lambda curr=prev_max_numerator+1, tot=division: 
                                self.update_progress(curr, tot))
            
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 2)
            self.root.after(0, lambda t=elapsed_time: self.time_label.config(text=f"Time: {t}s"))

        except Exception as e:
            messagebox.showerror("Error", f"{e}")
            return None, None

def main():
    # This is required for multiprocessing to work correctly on Windows
    mp.freeze_support()
    
    root = tk.Tk()
    app = PokerCalculatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    # This is required for multiprocessing to work correctly on Windows
    mp.freeze_support()
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Total time taken: {round(end_time - start_time, 2)}s")