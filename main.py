"""AI Rummy Games - Command Line Interface."""

from typing import List, Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
import random

from ai_rummy_games.models import Card, Deck, Player, Meld, GameState

# Initialize Rich console and Typer app
console = Console()
app = typer.Typer(name="ai-rummy-games", help="A command-line interface for AI Rummy Games", rich_markup_mode="rich")


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
        card_style = "bold red" if card.is_joker else "white"
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
            card = deck.draw()
            if card:
                player.add_card(card)

    # Set up draw and discard piles
    # Move remaining cards to draw_pile (already in deck.draw_pile)
    # Flip top card to discard pile
    first_discard = deck.draw()
    if first_discard:
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

    # Main game loop (stub for now)
    while True:
        display_game_state(game_state, deck)

        current_player = game_state.current_player()

        # Show current player's hand
        display_hand(current_player.name, current_player.hand)

        # Show game menu
        menu_options = [
            "Draw from deck",
            "Draw from discard pile",
            "View my hand",
            "Show melds on table",
            "Declare (end game)",
            "Save and quit",
        ]

        choice = show_menu(menu_options, f"{current_player.name}'s Turn")

        # Handle menu choices (stub implementations)
        if choice == 0:  # Draw from deck
            card = deck.draw()
            if card:
                current_player.add_card(card)
                console.print(f"[green]Drew: {card}[/green]")
            else:
                console.print("[red]Deck is empty![/red]")

        elif choice == 1:  # Draw from discard pile
            top_card = deck.peek_top_discard()
            if top_card:
                # Remove from discard pile (simplified)
                deck.discard_pile.pop()
                current_player.add_card(top_card)
                console.print(f"[green]Drew from discard: {top_card}[/green]")
            else:
                console.print("[red]Discard pile is empty![/red]")

        elif choice == 2:  # View hand
            display_hand(current_player.name, current_player.hand)
            Prompt.ask("Press Enter to continue", default="")
            continue

        elif choice == 3:  # Show melds
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

        elif choice == 4:  # Declare
            if Confirm.ask(f"Are you sure {current_player.name} wants to declare?"):
                current_player.declare()
                console.print(f"[bold green]{current_player.name} has declared![/bold green]")
                console.print("[yellow]Game would end here (full game logic not implemented yet)[/yellow]")
                break

        elif choice == 5:  # Save and quit
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

        # Next turn
        game_state.next_turn()

    console.print("\n[bold green]Thanks for playing AI Rummy Games![/bold green]")


if __name__ == "__main__":
    app()
