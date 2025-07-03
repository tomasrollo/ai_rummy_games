"""Main entry point for AI Rummy Games."""

from ai_rummy_games.models import Deck, Player, Meld, GameState, Card
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


def main():
    """Demonstrate the Card, Deck, Player, Meld, and GameState functionality."""
    console = Console()

    console.print(Panel.fit("[bold green]AI Rummy Games - Complete Models Demo[/bold green]"))

    # Create a game state with 3 players
    console.print("\n[blue]Setting up game with 3 players...[/blue]")
    game_state = GameState()

    players = [Player(name="Alice"), Player(name="Bob"), Player(name="Carol")]

    for player in players:
        game_state.add_player(player)

    console.print(f"[green]Game created with {len(game_state.players)} players[/green]")
    console.print(f"  • Current round: {game_state.current_round}")
    console.print(f"  • Current player: {game_state.current_player().name}")

    # Create and setup deck
    deck = Deck()
    deck.shuffle()
    console.print(f"\n[yellow]Deck shuffled with {deck.cards_remaining()} cards[/yellow]")

    # Deal cards to players
    console.print("\n[cyan]Dealing 7 cards to each player...[/cyan]")
    for _ in range(7):
        for player in game_state.players:
            card = deck.draw()
            if card:
                player.add_card(card)

    # Display player hands
    hands_table = Table(show_header=True, header_style="bold magenta")
    hands_table.add_column("Player")
    hands_table.add_column("Hand Size")
    hands_table.add_column("Sample Cards")
    hands_table.add_column("Declared")

    for player in game_state.players:
        sample_cards = ", ".join(str(card) for card in player.hand[:3])
        if len(player.hand) > 3:
            sample_cards += "..."

        hands_table.add_row(player.name, str(player.hand_size()), sample_cards, "Yes" if player.has_declared else "No")

    console.print(hands_table)

    # Create a sample meld
    console.print("\n[cyan]Creating sample melds...[/cyan]")

    # Create a sequence meld
    sequence_cards = [Card(suit="Hearts", rank="7"), Card(suit="Hearts", rank="8"), Card(suit="Hearts", rank="9")]
    sequence_meld = Meld(type="sequence", cards=sequence_cards)

    # Create a set meld
    set_cards = [Card(suit="Hearts", rank="K"), Card(suit="Spades", rank="K"), Card(suit="Clubs", rank="K")]
    set_meld = Meld(type="set", cards=set_cards)

    # Display meld validation
    melds_table = Table(show_header=True, header_style="bold magenta")
    melds_table.add_column("Meld Type")
    melds_table.add_column("Cards")
    melds_table.add_column("Valid")

    sequence_cards_str = ", ".join(str(card) for card in sequence_cards)
    set_cards_str = ", ".join(str(card) for card in set_cards)

    melds_table.add_row("Sequence", sequence_cards_str, "✅" if sequence_meld.is_valid() else "❌")

    melds_table.add_row("Set", set_cards_str, "✅" if set_meld.is_valid() else "❌")

    console.print(melds_table)

    # Add melds to table
    if sequence_meld.is_valid():
        game_state.add_meld_to_table(sequence_meld)
    if set_meld.is_valid():
        game_state.add_meld_to_table(set_meld)

    console.print(f"\n[green]Melds on table: {len(game_state.melds_on_table)}[/green]")

    # Simulate some turns
    console.print("\n[cyan]Simulating game turns...[/cyan]")
    turn_table = Table(show_header=True, header_style="bold magenta")
    turn_table.add_column("Turn")
    turn_table.add_column("Round")
    turn_table.add_column("Current Player")

    for turn in range(1, 8):
        turn_table.add_row(str(turn), str(game_state.current_round), game_state.current_player().name)
        game_state.next_turn()

    console.print(turn_table)

    # Demonstrate serialization
    console.print("\n[yellow]Testing serialization...[/yellow]")

    # Serialize the entire game state
    game_dict = game_state.to_dict()
    console.print("[green]✅ Game state serialized to dictionary[/green]")

    # Deserialize back
    restored_game = GameState.from_dict(game_dict)
    console.print("[green]✅ Game state restored from dictionary[/green]")

    # Verify restoration
    assert len(restored_game.players) == len(game_state.players)
    assert restored_game.current_round == game_state.current_round
    console.print("[green]✅ Serialization round-trip successful[/green]")

    # Player declaration demo
    console.print("\n[cyan]Player declaration demo...[/cyan]")
    alice = game_state.players[0]
    alice.declare()
    console.print(f"[green]{alice.name} has declared: {alice.has_declared}[/green]")

    console.print(f"\n[blue]Demo completed! Final state:[/blue]")
    console.print(f"  • Players: {len(game_state.players)}")
    console.print(f"  • Round: {game_state.current_round}")
    console.print(f"  • Melds on table: {len(game_state.melds_on_table)}")
    console.print(f"  • Cards remaining in deck: {deck.cards_remaining()}")


if __name__ == "__main__":
    main()
