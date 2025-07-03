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


if __name__ == "__main__":
    pytest.main([__file__])
