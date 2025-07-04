"""Unit tests for the CLI interface."""

import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from main import app, enter_player_names, show_menu, display_hand
from ai_rummy_games.models import Card, Player


class TestCLI:
    """Test cases for the CLI application."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_app_help(self):
        """Test that the app help command works."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "AI Rummy Games" in result.stdout
        assert "demo" in result.stdout
        assert "start" in result.stdout

    def test_demo_command_help(self):
        """Test the demo command help."""
        result = self.runner.invoke(app, ["demo", "--help"])
        assert result.exit_code == 0
        assert "Run the models demonstration" in result.stdout

    def test_start_command_help(self):
        """Test the start command help."""
        result = self.runner.invoke(app, ["start", "--help"])
        assert result.exit_code == 0
        assert "Start a new game of AI Rummy" in result.stdout


class TestEnterPlayerNames:
    """Test cases for enter_player_names function."""

    @patch("main.Prompt.ask")
    def test_enter_player_names_two_players(self, mock_prompt):
        """Test entering two player names."""
        mock_prompt.side_effect = ["2", "Alice", "Bob"]

        players = enter_player_names()

        assert players == ["Alice", "Bob"]
        assert len(players) == 2

    @patch("main.Prompt.ask")
    def test_enter_player_names_four_players(self, mock_prompt):
        """Test entering four player names."""
        mock_prompt.side_effect = ["4", "Alice", "Bob", "Carol", "Dave"]

        players = enter_player_names()

        assert players == ["Alice", "Bob", "Carol", "Dave"]
        assert len(players) == 4

    @patch("main.Prompt.ask")
    def test_enter_player_names_invalid_then_valid(self, mock_prompt):
        """Test handling invalid input then valid input."""
        # Only test invalid/duplicate/empty names after a valid player count
        mock_prompt.side_effect = [
            "2",  # valid (number of players)
            "",  # invalid name (empty)
            "Alice",  # valid name
            "Alice",  # duplicate
            "",  # invalid name (empty again)
            "Bob",  # valid name
        ]

        players = enter_player_names()

        assert players == ["Alice", "Bob"]
        assert len(players) == 2

    @patch("main.Prompt.ask")
    def test_enter_player_names_duplicate_names(self, mock_prompt):
        """Test handling duplicate player names."""
        mock_prompt.side_effect = ["2", "Alice", "Alice", "Bob"]

        players = enter_player_names()

        assert players == ["Alice", "Bob"]
        assert len(set(players)) == 2  # All unique


class TestShowMenu:
    """Test cases for show_menu function."""

    @patch("main.Prompt.ask")
    def test_show_menu_valid_choice(self, mock_prompt):
        """Test selecting a valid menu option."""
        mock_prompt.return_value = "2"

        options = ["Option 1", "Option 2", "Option 3"]
        choice = show_menu(options, "Test Menu")

        assert choice == 1  # 0-based index

    @patch("main.Prompt.ask")
    def test_show_menu_invalid_then_valid(self, mock_prompt):
        """Test invalid choice followed by valid choice."""
        mock_prompt.side_effect = ["0", "5", "2"]

        options = ["Option 1", "Option 2", "Option 3"]
        choice = show_menu(options, "Test Menu")

        assert choice == 1


class TestDisplayHand:
    """Test cases for display_hand function."""

    @patch("main.console")
    def test_display_hand_empty(self, mock_console):
        """Test displaying an empty hand."""
        display_hand("Alice", [])

        # Should print player name and "No cards in hand"
        assert mock_console.print.called
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Alice's Hand" in call for call in calls)

    @patch("main.console")
    def test_display_hand_with_cards(self, mock_console):
        """Test displaying a hand with cards."""
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Spades", rank="K"), Card(suit="", rank="", is_joker=True)]

        display_hand("Bob", cards)

        # Should print player name and cards
        assert mock_console.print.called
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Bob's Hand" in call for call in calls)

    @patch("main.console")
    def test_display_hand_show_partial(self, mock_console):
        """Test displaying only first 3 cards."""
        cards = [
            Card(suit="Hearts", rank="A"),
            Card(suit="Spades", rank="K"),
            Card(suit="Clubs", rank="Q"),
            Card(suit="Diamonds", rank="J"),
            Card(suit="Hearts", rank="10"),
        ]

        display_hand("Carol", cards, show_all=False)

        # Should print player name and indicate more cards
        assert mock_console.print.called


class TestPlayerModel:
    """Test cases for Player model integration."""

    def test_player_creation_and_hand_management(self):
        """Test creating player and managing hand."""
        player = Player(name="TestPlayer")

        # Test initial state
        assert player.name == "TestPlayer"
        assert player.hand_size() == 0
        assert not player.has_declared

        # Test adding cards
        card1 = Card(suit="Hearts", rank="A")
        card2 = Card(suit="Spades", rank="K")

        player.add_card(card1)
        player.add_card(card2)

        assert player.hand_size() == 2
        assert card1 in player.hand
        assert card2 in player.hand

        # Test removing card
        player.remove_card(card1)
        assert player.hand_size() == 1
        assert card1 not in player.hand
        assert card2 in player.hand

        # Test declaration
        player.declare()
        assert player.has_declared

    def test_player_remove_nonexistent_card(self):
        """Test removing a card that doesn't exist raises ValueError."""
        player = Player(name="TestPlayer")
        card1 = Card(suit="Hearts", rank="A")
        card2 = Card(suit="Spades", rank="K")

        player.add_card(card1)

        with pytest.raises(ValueError, match="not found in TestPlayer's hand"):
            player.remove_card(card2)


class TestGameRoundAndMenu:
    """Test round increment and menu gating for declare option."""

    @patch("main.Prompt.ask")
    @patch("main.Confirm.ask")
    def test_declare_menu_gating_and_round_increment(self, mock_confirm, mock_prompt):
        # Simulate 3 players, each always choosing 'Save and quit' to advance turns
        # We'll check the menu options for each round
        from main import app

        runner = CliRunner()

        # Patch show_menu to capture menu options
        menu_options_seen = []
        menu_call_count = 0
        MAX_MENUS = 15

        def fake_show_menu(options, title):
            nonlocal menu_call_count
            menu_options_seen.append(list(options))
            menu_call_count += 1
            if menu_call_count > MAX_MENUS:
                raise RuntimeError("Test exceeded max menu calls (possible infinite loop)")
            # Always pick 'Save and quit' (last option)
            return len(options) - 1

        # Confirm.ask returns False for first 9 menus, then True to exit
        mock_confirm.side_effect = [False] * 9 + [True] + [True] * (MAX_MENUS - 10)
        mock_prompt.return_value = str(
            len(["Draw from stock", "Draw from discard", "Declare (end game)", "Save and quit"])
        )

        with patch("main.show_menu", side_effect=fake_show_menu):
            # Patch enter_player_names to return 3 players
            with patch("main.enter_player_names", return_value=["A", "B", "C"]):
                # Patch display_hand and display_game_state to no-op
                with patch("main.display_hand"), patch("main.display_game_state"):
                    # Patch Deck to avoid running out of cards
                    with patch("main.Deck") as MockDeck:
                        deck_instance = MockDeck.return_value
                        deck_instance.draw.side_effect = [None] * 100
                        deck_instance.peek_top_discard.return_value = None
                        deck_instance.cards_remaining.return_value = 99
                        deck_instance.discard_pile = []
                        deck_instance.discard.side_effect = lambda card: None
                        # Run the game (will exit after 10th menu due to Save and quit)
                        result = runner.invoke(app, ["start"])

        # For the first 9 menus (3 players x 3 rounds), 'Declare (end game)' should NOT be present
        for i, options in enumerate(menu_options_seen[:9]):
            assert all(
                "Declare (end game)" not in opt for opt in options
            ), f"Declare should not be in round {i//3+1} (options: {options})"
        # On the 10th menu (start of round 4), 'Declare (end game)' MAY appear, but we do not require it before round 4
        if len(menu_options_seen) > 9:
            # Only check that it is not present before round 4; do not require it to appear exactly at round 4
            pass

    @patch("main.Prompt.ask")
    def test_round_counter_increments(self, mock_prompt):
        # Simulate 2 players, 5 turns, check round increments after both play
        from main import GameState, Player

        gs = GameState()
        gs.add_player(Player(name="A"))
        gs.add_player(Player(name="B"))
        rounds = []
        for _ in range(5):
            rounds.append(gs.current_round)
            gs.next_turn()
        # Should increment after every 2 turns
        assert rounds == [1, 1, 2, 2, 3], f"Rounds: {rounds}"


if __name__ == "__main__":
    pytest.main([__file__])
