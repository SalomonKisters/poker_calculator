def get_results_str(all_player_cards, total_win_percentages, total_tie_percentages, total_player_wins, total_player_ties):
    result_str = ""
    for j in range(len(all_player_cards)):
        result_str += f'Player {j+1} wins {total_player_wins[j]} times or {round(total_win_percentages[j], 2)}%\n'
        result_str += f'Player {j+1} ties {total_player_ties[j]} times or {round(total_tie_percentages[j], 2)}%\n'
        total_equity = total_win_percentages[j] + (total_tie_percentages[j] / len(all_player_cards))
        result_str += f'Player {j+1} total equity: {round(total_equity, 2)}%\n'
        result_str += '-' * 40 + '\n'
    return result_str

def check_validity(all_player_cards, table_cards):
    # Check for duplicate cards
    all_cards = [card for player_cards in all_player_cards for card in player_cards] + table_cards
    if len(all_cards) != len(set(all_cards)):
        raise ValueError("Duplicate cards found in all_player_cards or table_cards")
    
    for player_cards in all_player_cards:
        if len(player_cards) != 2:
            raise ValueError("Each player must have exactly 2 cards")
    
    if len(table_cards) > 5:
        raise ValueError("table_cards must contain 5 or fewer cards")

    if len(table_cards) not in [0,3,4,5]:
        raise ValueError(f"In Texas Holdem, there can never be {len(table_cards)} cards on the table")
