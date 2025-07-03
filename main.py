"""AI Rummy Games - Command Line Interface."""

from typing import List, Optional, Dict, Tuple
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.text import Text
import random

from ai_rummy_games.models import Card, Deck, Player, Meld, GameState
from ai_rummy_games.validator import Validator

# Initialize Rich console and Typer app
console = Console()
app = typer.Typer(name="ai-rummy-games", help="A command-line interface for AI Rummy Games", rich_markup_mode="rich")

# Add validator instance
validator = Validator()


def enter_player_names() -> List[str]:
    """Prompt user to enter player names and return them as a list.

    Returns:
        List of player names (2-6 players supported).
    """
    console.print("\n[bold cyan]Setting up players...[/bold cyan]")

    players = []
    min_players = 2
    max_players = 6

    # Get number of players
    while True:
        try:
            num_players = int(Prompt.ask(f"How many players? ({min_players}-{max_players})", default="2"))
            if min_players <= num_players <= max_players:
                break
            else:
                console.print(f"[red]Please enter a number between {min_players} and {max_players}[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")

    # Get player names
    for i in range(num_players):
        while True:
            name = Prompt.ask(f"Enter name for Player {i + 1}")
            if name.strip():
                if name not in players:
                    players.append(name.strip())
                    break
                else:
                    console.print("[red]That name is already taken. Please choose a different name.[/red]")
            else:
                console.print("[red]Name cannot be empty. Please enter a valid name.[/red]")

    console.print(f"\n[green]Players registered: {', '.join(players)}[/green]")
    return players


def show_menu(options: List[str], title: str = "Menu") -> int:
    """Display a menu with numbered options and return the selected choice.

    Args:
        options: List of menu option strings.
        title: Title for the menu.

    Returns:
        Index of the selected option (0-based).
    """
    console.print(f"\n[bold yellow]{title}[/bold yellow]")

    table = Table(show_header=False, show_lines=False, padding=(0, 2))
    table.add_column("Option", style="cyan", width=8)
    table.add_column("Description", style="white")

    for i, option in enumerate(options, 1):
        table.add_row(f"[{i}]", option)

    console.print(table)

    while True:
        try:
            choice = int(Prompt.ask("Select an option")) - 1
            if 0 <= choice < len(options):
                return choice
            else:
                console.print(f"[red]Please enter a number between 1 and {len(options)}[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")


def display_hand(player_name: str, cards: List[Card], show_all: bool = True) -> None:
    """Display a player's hand of cards in a formatted table.

    Args:
        player_name: Name of the player.
        cards: List of Card objects in the player's hand.
        show_all: If False, only show first 3 cards with "..." indicator.
    """
    console.print(f"\n[bold magenta]{player_name}'s Hand ({len(cards)} cards)[/bold magenta]")

    if not cards:
        console.print("[dim]No cards in hand[/dim]")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", width=4)
    table.add_column("Card", min_width=15)
    table.add_column("Type", width=8)

    display_cards = cards if show_all else cards[:3]

    for i, card in enumerate(display_cards, 1):
        card_type = "Joker" if card.is_joker else "Regular"
        # Color code suits according to traditional card colors:
        # - Red for Hearts (♥) and Diamonds (♦)
        # - White/Black for Spades (♠) and Clubs (♣)
        # This ensures proper visual distinction of suits in terminal
        if card.is_joker:
            card_style = "bold red"
        elif card.suit in ["Hearts", "Diamonds"]:
            card_style = "bold red"
        else:
            card_style = "bold white"
        table.add_row(str(i), f"[{card_style}]{str(card)}[/{card_style}]", card_type)

    if not show_all and len(cards) > 3:
        table.add_row("...", f"[dim]+{len(cards) - 3} more cards[/dim]", "")

    console.print(table)


def display_game_state(game_state: GameState, deck: Deck) -> None:
    """Display the current game state in a formatted way.

    Args:
        game_state: Current game state.
        deck: Current deck state.
    """
    # Game info panel
    game_info = Text()
    game_info.append(f"Round: {game_state.current_round} | ", style="bold blue")
    game_info.append(f"Current Player: {game_state.current_player().name} | ", style="bold green")
    game_info.append(f"Cards Left: {deck.cards_remaining()}", style="bold yellow")

    console.print(Panel(game_info, title="Game Status", border_style="blue"))

    # Players summary
    players_table = Table(show_header=True, header_style="bold magenta")
    players_table.add_column("Player")
    players_table.add_column("Cards")
    players_table.add_column("Declared", justify="center")

    for player in game_state.players:
        players_table.add_row(player.name, str(player.hand_size()), "✅" if player.has_declared else "❌")

    console.print(players_table)

    # Melds on table
    if game_state.melds_on_table:
        console.print(f"\n[bold cyan]Melds on Table ({len(game_state.melds_on_table)}):[/bold cyan]")
        for i, meld in enumerate(game_state.melds_on_table, 1):
            cards_str = ", ".join(str(card) for card in meld.cards)
            console.print(f"  {i}. {meld.type.title()}: {cards_str}")

    # Top discard card
    top_discard = deck.peek_top_discard()
    if top_discard:
        console.print(f"\n[bold yellow]Top Discard: {top_discard}[/bold yellow]")


@app.command(name="demo")
def run_demo():
    """Run the models demonstration."""
    console.print("[bold green]Running models demo...[/bold green]")

    # Import and run the demo
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "demo.py"], capture_output=False, cwd="/Users/tomas/Documents/projects/ai_rummy_games"
    )

    if result.returncode != 0:
        console.print("[red]Demo failed to run[/red]")
        raise typer.Exit(1)


@app.command(name="start")
def start_game():
    """Start a new game of AI Rummy."""
    import random

    console.print(Panel.fit("[bold green]🃏 Welcome to AI Rummy Games! 🃏[/bold green]", border_style="green"))

    # Get player names
    player_names = enter_player_names()

    # Initialize game
    console.print("\n[yellow]Initializing game...[/yellow]")
    game_state = GameState()

    # Create players
    for name in player_names:
        game_state.add_player(Player(name=name))

    # Create and shuffle deck
    deck = Deck()
    deck.shuffle()
    console.print(f"[green]Deck shuffled with {deck.cards_remaining()} cards[/green]")

    # Deal 13 cards to each player
    cards_per_player = 13
    console.print(f"\n[cyan]Dealing {cards_per_player} cards to each player...[/cyan]")
    for _ in range(cards_per_player):
        for player in game_state.players:
            player.add_card(deck.draw())

    # Set up draw and discard piles
    # Move remaining cards to draw_pile (already in deck.draw_pile)
    # Flip top card to discard pile
    first_discard = deck.draw()
    deck.discard(first_discard)

    # Assign piles to game state
    game_state.draw_pile = deck.draw_pile.copy()
    game_state.discard_pile = deck.discard_pile.copy()

    # Randomly select starting player
    starting_index = random.randint(0, len(game_state.players) - 1)
    game_state.current_player_index = starting_index
    game_state.current_round = 1
    console.print(f"[green]Starting player: {game_state.players[starting_index].name}[/green]")
    console.print("[green]Game setup complete![/green]")

    # Main game loop with round/turn management
    while True:
        display_game_state(game_state, deck)

        current_player = game_state.current_player()

        # Show current player's hand
        display_hand(current_player.name, current_player.hand)

        # Gate options based on round number and player's declaration status
        menu_options = [
            "Draw from deck",
            "View my hand",
        ]

        # Options for round 4+ only
        if game_state.current_round >= 4:
            menu_options.append("Draw from discard pile")
            menu_options.append("Show melds on table")
            menu_options.append("Declare")

            # Extension only available if player has already declared
            if current_player.has_declared:
                menu_options.append("Extend meld")

                # Close option only available if player has declared and has 0-1 cards left
                if game_state.can_player_close(current_player):
                    menu_options.append("Close game")

        menu_options.append("Save and quit")

        choice = show_menu(menu_options, f"{current_player.name}'s Turn")

        # Map menu choice to action index
        declare_option_index = 4 if game_state.current_round >= 4 else None
        extend_option_index = 5 if (game_state.current_round >= 4 and current_player.has_declared) else None
        close_option_index = (
            6
            if (
                game_state.current_round >= 4
                and current_player.has_declared
                and game_state.can_player_close(current_player)
            )
            else None
        )
        save_quit_index = len(menu_options) - 1  # Always the last option

        # Handle menu choices
        if choice == 0:  # Draw from deck
            card = deck.draw()
            if card:
                current_player.add_card(card)
                console.print(f"[green]Drew: {card}[/green]")
            else:
                console.print("[red]Deck is empty![/red]")

        elif choice == 1:  # View hand
            display_hand(current_player.name, current_player.hand)
            Prompt.ask("Press Enter to continue", default="")
            continue

        elif game_state.current_round >= 4 and choice == 2:  # Draw from discard pile
            top_card = deck.peek_top_discard()
            if top_card:
                deck.discard_pile.pop()
                current_player.add_card(top_card)
                console.print(f"[green]Drew from discard: {top_card}[/green]")
            else:
                console.print("[red]Discard pile is empty![/red]")

        elif game_state.current_round >= 4 and choice == 3:  # Show melds
            if game_state.melds_on_table:
                console.print(f"\n[bold cyan]Melds on Table:[/bold cyan]")
                for i, meld in enumerate(game_state.melds_on_table, 1):
                    cards_str = ", ".join(str(card) for card in meld.cards)
                    valid = "✅" if meld.is_valid() else "❌"
                    console.print(f"  {i}. {meld.type.title()}: {cards_str} {valid}")
            else:
                console.print("[dim]No melds on table yet.[/dim]")
            Prompt.ask("Press Enter to continue", default="")
            continue

        elif declare_option_index is not None and choice == declare_option_index:  # Declare
            if Confirm.ask(f"Are you sure {current_player.name} wants to declare?"):
                if handle_declaration(game_state, current_player):
                    console.print(
                        f"[bold green]{current_player.name}'s declaration processed successfully![/bold green]"
                    )
                else:
                    console.print("[yellow]Declaration was not processed.[/yellow]")
                    continue  # Skip discard phase if declaration failed

        elif extend_option_index is not None and choice == extend_option_index:  # Extend meld
            if extend_meld(game_state, current_player):
                console.print("[green]Meld extension processed successfully![/green]")
            else:
                console.print("[yellow]Meld extension was not processed.[/yellow]")
                continue  # Skip discard phase if extension failed

        elif close_option_index is not None and choice == close_option_index:  # Close game
            if handle_game_closure(game_state, current_player):
                console.print("\n[bold green]Game closed successfully![/bold green]")
                break  # End the game loop
            else:
                console.print("[yellow]Game closure was not processed.[/yellow]")
                continue  # Skip discard phase if closure failed

        elif choice == save_quit_index:  # Save and quit
            console.print("[yellow]Save functionality not implemented yet[/yellow]")
            if Confirm.ask("Quit without saving?"):
                break

        # Must discard a card if hand size > 7 (simplified rule)
        if current_player.hand_size() > 7:
            console.print(f"\n[yellow]{current_player.name} must discard a card:[/yellow]")
            display_hand(current_player.name, current_player.hand)

            while True:
                try:
                    card_idx = int(Prompt.ask("Enter card number to discard")) - 1
                    if 0 <= card_idx < current_player.hand_size():
                        discarded_card = current_player.hand[card_idx]
                        current_player.remove_card(discarded_card)
                        deck.discard(discarded_card)
                        console.print(f"[red]Discarded: {discarded_card}[/red]")
                        break
                    else:
                        console.print(f"[red]Please enter a number between 1 and {current_player.hand_size()}[/red]")
                except (ValueError, IndexError):
                    console.print("[red]Please enter a valid card number[/red]")

        # Next turn and round management
        game_state.next_turn()

    if game_state.is_game_closed:
        console.print("\n[bold green]Game has ended![/bold green]")
        display_scoreboard(game_state)

    console.print("\n[bold green]Thanks for playing AI Rummy Games![/bold green]")


def select_cards(player: Player, max_cards: int) -> List[Card]:
    """Prompt the player to select cards from their hand.

    Args:
        player: The player selecting cards.
        max_cards: Maximum number of cards the player can select.

    Returns:
        List of selected Card objects.
    """
    while True:
        try:
            card_indices = Prompt.ask(
                f"{player.name}, select up to {max_cards} cards by number (comma-separated), or press Enter to skip",
                default="",
            ).split(",")

            if not card_indices or (len(card_indices) == 1 and card_indices[0] == ""):
                return []

            indices = [int(idx.strip()) - 1 for idx in card_indices]
            if any(idx < 0 or idx >= len(player.hand) for idx in indices):
                raise ValueError("Invalid card number selected")

            selected_cards = [player.hand[idx] for idx in indices]
            if len(selected_cards) > max_cards:
                console.print(f"[red]You can only select up to {max_cards} cards[/red]")
                continue

            return selected_cards

        except (ValueError, IndexError) as e:
            console.print(f"[red]Error: {e}. Please try again.[/red]")


def create_meld(player: Player, round_number: int) -> Optional[Meld]:
    """Prompt the player to create a meld from selected cards.

    Args:
        player: The player creating the meld.
        round_number: The current round number.

    Returns:
        The created Meld object, or None if meld creation was skipped.
    """
    console.print(f"\n[bold cyan]{player.name}, it's time to create a meld![/bold cyan]")

    # Select cards for the meld
    max_cards = 7 if round_number >= 4 else 6
    selected_cards = select_cards(player, max_cards)

    if not selected_cards:
        console.print("[yellow]No cards selected for meld. Skipping meld creation.[/yellow]")
        return None

    # Validate and create the meld
    meld_type = (
        "set"
        if len(selected_cards) > 2 and all(card.rank == selected_cards[0].rank for card in selected_cards)
        else "run"
    )
    meld = Meld(type=meld_type, cards=selected_cards)

    if validator.validate_meld(meld, player.hand):
        player.add_meld(meld)
        console.print(f"[green]Meld created: {meld}[/green]")
        return meld
    else:
        console.print("[red]Invalid meld. Please try again.[/red]")
        return None


def extend_meld(player: Player) -> None:
    """Prompt the player to extend an existing meld with additional cards.

    Args:
        player: The player extending the meld.
    """
    console.print(f"\n[bold cyan]{player.name}, it's time to extend a meld![/bold cyan]")

    # Show existing melds
    if not player.melds:
        console.print("[dim]No melds available to extend.[/dim]")
        return

    for i, meld in enumerate(player.melds, 1):
        cards_str = ", ".join(str(card) for card in meld.cards)
        console.print(f"  {i}. {meld.type.title()}: {cards_str}")

    # Select meld to extend
    while True:
        try:
            meld_index = IntPrompt.ask("Select meld number to extend") - 1
            if meld_index < 0 or meld_index >= len(player.melds):
                raise ValueError("Invalid meld number")

            selected_meld = player.melds[meld_index]
            break
        except (ValueError, IndexError):
            console.print("[red]Please enter a valid meld number[/red]")

    # Select cards to add to the meld
    max_cards = 7 - len(selected_meld.cards)
    additional_cards = select_cards(player, max_cards)

    if not additional_cards:
        console.print("[yellow]No additional cards selected. Meld extension skipped.[/yellow]")
        return

    # Validate and extend the meld
    for card in additional_cards:
        selected_meld.add_card(card)

    if validator.validate_meld(selected_meld, player.hand):
        console.print(f"[green]Meld extended: {selected_meld}[/green]")
    else:
        console.print("[red]Invalid meld extension. Please try again.[/red]")


def select_cards_from_hand(player: Player, message: str = "Select cards from your hand") -> List[Card]:
    """Prompt the player to select cards from their hand.

    Args:
        player: The player selecting cards
        message: Message to display during selection

    Returns:
        List of selected cards
    """
    if not player.hand:
        console.print("[red]You don't have any cards in your hand![/red]")
        return []

    console.print(f"\n[bold cyan]{message}[/bold cyan]")
    display_hand(player.name, player.hand)
    console.print("[yellow]Enter card numbers separated by spaces (e.g. 1 3 5) or 0 to cancel[/yellow]")

    while True:
        selection = Prompt.ask("Card selection").strip()
        if selection == "0":
            return []

        try:
            # Parse card indices (1-based in UI, 0-based in code)
            indices = [int(idx) - 1 for idx in selection.split()]

            # Check for valid indices
            invalid_indices = [i + 1 for i in indices if i < 0 or i >= player.hand_size()]
            if invalid_indices:
                console.print(f"[red]Invalid card numbers: {', '.join(map(str, invalid_indices))}[/red]")
                continue

            # Return selected cards
            selected_cards = [player.hand[i] for i in indices]
            return selected_cards
        except ValueError:
            console.print("[red]Please enter valid card numbers[/red]")
            continue


def create_new_meld(player: Player) -> Optional[Meld]:
    """Prompt the player to create a new meld from their hand.

    Args:
        player: The player creating the meld

    Returns:
        The created meld or None if cancelled
    """
    # Select cards for the meld
    console.print("\n[bold cyan]Create a new meld[/bold cyan]")
    selected_cards = select_cards_from_hand(player, "Select at least 3 cards for your meld")

    if not selected_cards:
        console.print("[yellow]Meld creation cancelled[/yellow]")
        return None

    if len(selected_cards) < 3:
        console.print("[red]A meld must contain at least 3 cards![/red]")
        return None

    # Select meld type
    console.print("\n[bold cyan]Select meld type:[/bold cyan]")
    meld_type = show_menu(
        ["Sequence (consecutive cards of same suit)", "Set (same rank, different suits)"], "Meld Type"
    )
    meld_type_str = "sequence" if meld_type == 0 else "set"

    # Validate the meld
    if validator.validate_new_meld(selected_cards, meld_type_str):
        return Meld(cards=selected_cards, type=meld_type_str)
    else:
        console.print(f"[red]Invalid {meld_type_str} meld! Check the rules and try again.[/red]")
        return None


def select_meld_from_table(game_state: GameState) -> Optional[Tuple[int, Meld]]:
    """Prompt the user to select a meld from the table.

    Args:
        game_state: Current game state

    Returns:
        Tuple of (index, meld) or None if cancelled
    """
    if not game_state.melds_on_table:
        console.print("[yellow]No melds on the table to select.[/yellow]")
        return None

    console.print("\n[bold cyan]Melds on table:[/bold cyan]")

    for i, meld in enumerate(game_state.melds_on_table, 1):
        meld_type = meld.type.title()
        cards_str = ", ".join(str(card) for card in meld.cards)
        console.print(f"  {i}. {meld_type}: {cards_str}")

    console.print("[yellow]Enter the number of the meld you want to select (or 0 to cancel)[/yellow]")

    while True:
        try:
            meld_idx = int(Prompt.ask("Meld number")) - 1

            if meld_idx == -1:  # User entered 0 to cancel
                return None

            if 0 <= meld_idx < len(game_state.melds_on_table):
                return (meld_idx, game_state.melds_on_table[meld_idx])
            else:
                console.print(f"[red]Please enter a number between 1 and {len(game_state.melds_on_table)}[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")


def extend_meld(game_state: GameState, player: Player) -> bool:
    """Allow a player to extend a meld on the table.

    Args:
        game_state: Current game state
        player: The player extending the meld

    Returns:
        True if meld was extended successfully, False otherwise
    """
    console.print("\n[bold cyan]Extend a meld on the table[/bold cyan]")

    # Select the meld to extend
    meld_selection = select_meld_from_table(game_state)
    if not meld_selection:
        console.print("[yellow]Meld extension cancelled[/yellow]")
        return False

    meld_index, meld = meld_selection

    # Select cards to extend with
    console.print(f"\n[bold cyan]Selected {meld.type} meld:[/bold cyan]")
    cards_str = ", ".join(str(card) for card in meld.cards)
    console.print(f"Cards: {cards_str}")

    # Select cards from hand to add to the meld
    added_cards = select_cards_from_hand(player, "Select cards to add to this meld")
    if not added_cards:
        console.print("[yellow]Meld extension cancelled[/yellow]")
        return False

    # Validate the extension
    if validator.validate_extension(meld, added_cards):
        # Update the meld on the table
        for card in added_cards:
            # Remove cards from player's hand
            player.remove_card(card)
            # Add cards to the meld
            meld.cards.append(card)

        console.print("[green]Meld extended successfully![/green]")
        return True
    else:
        console.print(f"[red]Invalid extension! Check the rules for extending a {meld.type}.[/red]")
        return False


def handle_declaration(game_state: GameState, player: Player) -> bool:
    """Handle a player's declaration (initial or subsequent).

    Args:
        game_state: Current game state
        player: The player making the declaration

    Returns:
        True if declaration was successful, False otherwise
    """
    console.print("\n[bold cyan]Declaration[/bold cyan]")

    # Initial declaration requires validation, subsequent declarations don't
    if not player.has_declared:
        console.print("[yellow]This is your INITIAL declaration.[/yellow]")
        console.print("[yellow]Remember: You need at least 48 points and one pure sequence![/yellow]")
    else:
        console.print("[green]You've already made your initial declaration.[/green]")
        console.print("[yellow]You can now add more melds.[/yellow]")

    melds = []
    while True:
        meld = create_new_meld(player)
        if meld:
            melds.append(meld)
            console.print(f"[green]Added {meld.type} meld with {len(meld.cards)} cards[/green]")

            # Ask if player wants to add more melds
            if not Confirm.ask("Add another meld?"):
                break
        else:
            if not melds:
                console.print("[yellow]Declaration cancelled[/yellow]")
                return False
            break

    if not melds:
        return False

    # For initial declarations, validate using GameState's method
    if not player.has_declared:
        if game_state.validate_and_process_declaration(player.name, melds):
            console.print("[bold green]Initial declaration successful![/bold green]")
            return True
        else:
            console.print(
                "[red]Declaration invalid! Make sure you have at least 48 points and one pure sequence.[/red]"
            )
            return False
    else:
        # For subsequent declarations, just validate each meld and add to table
        for meld in melds:
            # Remove cards from player's hand
            for card in meld.cards:
                player.remove_card(card)
            # Add meld to table
            game_state.add_meld_to_table(meld)

        console.print("[green]Melds added to the table![/green]")
        return True


def display_scoreboard(game_state: GameState) -> None:
    """Display the final scoreboard in a formatted table.

    Args:
        game_state: The game state containing scores
    """
    console.print("\n[bold cyan]🏆 Final Scores 🏆[/bold cyan]")

    # Create a table for the scores
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Player", style="cyan")
    table.add_column("Score", style="yellow", justify="right")
    table.add_column("Status", style="green", justify="center")

    # Sort players by score (lowest is best)
    sorted_players = sorted(game_state.players, key=lambda p: p.score)

    for player in sorted_players:
        status = "🏆 Winner" if player.name == game_state.closer_name else ""
        score_style = "bold green" if player.name == game_state.closer_name else "white"
        table.add_row(player.name, f"[{score_style}]{player.score}[/{score_style}]", status)

    console.print(table)


def handle_game_closure(game_state: GameState, player: Player) -> bool:
    """Handle a player's attempt to close the game.

    Args:
        game_state: Current game state
        player: The player attempting to close the game

    Returns:
        True if game was closed successfully, False otherwise
    """
    if not player.has_declared:
        console.print("[red]You must declare before closing the game![/red]")
        return False

    if player.hand_size() > 1:
        console.print(f"[red]You need to have 0 or 1 card left to close! You have {player.hand_size()} cards.[/red]")
        return False

    # If player has exactly one card left, they need to discard it
    if player.hand_size() == 1:
        # Get the last card
        last_card = player.hand[0]

        # Confirm the closure
        console.print(f"\n[bold yellow]Your last card: {last_card}[/bold yellow]")
        if not Confirm.ask(f"[bold]Are you sure you want to close the game by discarding this card?[/bold]"):
            return False

        # Remove the card from player's hand (will be placed face down to signal closure)
        player.remove_card(last_card)

    # Close the game and calculate scores
    if game_state.close_game(player.name):
        console.print(f"\n[bold green]🎉 {player.name} has closed the game! 🎉[/bold green]")
        display_scoreboard(game_state)
        return True
    else:
        console.print("[red]Failed to close the game. Please try again.[/red]")
        return False


if __name__ == "__main__":
    app()
