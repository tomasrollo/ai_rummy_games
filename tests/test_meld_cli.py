"""Unit tests for the CLI meld and extension commands."""

import pytest
import typer
from typer.testing import CliRunner
from rich.console import Console

import main
from ai_rummy_games.models import Card, Meld, Player, GameState


class TestMeldCLI:
    """Test cases for the CLI meld and extension functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Mock data for testing
        self.player = Player(name="TestPlayer")
        self.game_state = GameState()
        self.game_state.add_player(self.player)
        self.game_state.current_round = 4  # Allow declarations

        # Create some test cards
        self.hearts_sequence = [
            Card(suit="Hearts", rank="3"),
            Card(suit="Hearts", rank="4"),
            Card(suit="Hearts", rank="5"),
        ]
        self.king_set = [
            Card(suit="Hearts", rank="K"),
            Card(suit="Spades", rank="K"),
            Card(suit="Clubs", rank="K"),
        ]

        # Add cards to player's hand
        for card in self.hearts_sequence + self.king_set:
            self.player.add_card(card)

        # Create a meld on the table
        self.table_meld = Meld(
            cards=[
                Card(suit="Diamonds", rank="7"),
                Card(suit="Diamonds", rank="8"),
                Card(suit="Diamonds", rank="9"),
            ],
            type="sequence",
        )
        self.game_state.add_meld_to_table(self.table_meld)

    def test_create_new_meld_function(self, monkeypatch):
        """Test the create_new_meld function with valid cards."""
        # Mock card selection to return the hearts sequence
        monkeypatch.setattr(main, "select_cards_from_hand", lambda p, m: self.hearts_sequence)

        # Mock menu to return "sequence" option
        monkeypatch.setattr(main, "show_menu", lambda o, t: 0)  # 0 = sequence

        # Call the function and check result
        meld = main.create_new_meld(self.player)

        assert meld is not None
        assert meld.type == "sequence"
        assert len(meld.cards) == 3
        assert all(card.suit == "Hearts" for card in meld.cards)

    def test_create_new_meld_invalid(self, monkeypatch):
        """Test the create_new_meld function with invalid meld."""
        # Create an invalid mixed-suit "sequence"
        invalid_cards = [
            Card(suit="Hearts", rank="3"),
            Card(suit="Spades", rank="4"),
            Card(suit="Hearts", rank="5"),
        ]

        # Mock card selection to return the invalid cards
        monkeypatch.setattr(main, "select_cards_from_hand", lambda p, m: invalid_cards)

        # Mock menu to return "sequence" option
        monkeypatch.setattr(main, "show_menu", lambda o, t: 0)  # 0 = sequence

        # Call the function and check result (should return None for invalid meld)
        meld = main.create_new_meld(self.player)

        assert meld is None

    def test_extend_meld_function(self, monkeypatch):
        """Test the extend_meld function."""
        # Add extension card to player's hand
        extension_card = Card(suit="Diamonds", rank="10")
        self.player.add_card(extension_card)

        # Mock meld selection to return the table meld
        monkeypatch.setattr(main, "select_meld_from_table", lambda gs: (0, self.table_meld))

        # Mock card selection to return the extension card
        monkeypatch.setattr(main, "select_cards_from_hand", lambda p, m: [extension_card])

        # Call the function and check result
        result = main.extend_meld(self.game_state, self.player)

        assert result is True
        assert len(self.table_meld.cards) == 4  # Original 3 + 1 extension
        assert self.table_meld.cards[-1] == extension_card

        # Verify card was removed from player's hand
        assert extension_card not in self.player.hand

    def test_extend_meld_invalid(self, monkeypatch):
        """Test the extend_meld function with invalid extension."""
        # Add invalid extension card to player's hand
        invalid_card = Card(suit="Hearts", rank="Q")  # Wrong suit
        self.player.add_card(invalid_card)

        # Mock meld selection to return the table meld
        monkeypatch.setattr(main, "select_meld_from_table", lambda gs: (0, self.table_meld))

        # Mock card selection to return the invalid card
        monkeypatch.setattr(main, "select_cards_from_hand", lambda p, m: [invalid_card])

        # Call the function and check result
        result = main.extend_meld(self.game_state, self.player)

        assert result is False
        assert len(self.table_meld.cards) == 3  # Unchanged
        assert invalid_card in self.player.hand  # Card still in hand

    def test_handle_declaration_initial(self, monkeypatch):
        """Test handling an initial declaration."""
        from unittest.mock import MagicMock

        # Add high-value cards to meet 48-point requirement
        high_value_cards = [
            Card(suit="Hearts", rank="5"),  # Using numeric cards for sequence
            Card(suit="Hearts", rank="6"),
            Card(suit="Hearts", rank="7"),
            Card(suit="Spades", rank="Q"),
            Card(suit="Diamonds", rank="Q"),
            Card(suit="Clubs", rank="Q"),
        ]
        for card in high_value_cards:
            self.player.add_card(card)

        # Create a sequence meld with high-value cards
        valid_sequence = Meld(cards=[high_value_cards[0], high_value_cards[1], high_value_cards[2]], type="sequence")

        # Create a set meld
        valid_set = Meld(cards=[high_value_cards[3], high_value_cards[4], high_value_cards[5]], type="set")

        # Mock create_new_meld to return our sequence and set on consecutive calls
        meld_returns = [valid_sequence, valid_set]
        monkeypatch.setattr(main, "create_new_meld", lambda p: meld_returns.pop(0) if meld_returns else None)

        # Mock confirmation to continue after first meld, then stop
        ask_returns = [True, False]  # First True (add another meld), then False (done)
        monkeypatch.setattr(main.Confirm, "ask", lambda p: ask_returns.pop(0) if ask_returns else False)

        # Mock the GameState's validate_and_process_declaration method
        mock_validate = MagicMock(return_value=True)
        monkeypatch.setattr(self.game_state, "validate_and_process_declaration", mock_validate)

        # Call the function and check result
        result = main.handle_declaration(self.game_state, self.player)

        # Check that validate_and_process_declaration was called
        mock_validate.assert_called_once()

        assert result is True

    def test_handle_declaration_subsequent(self, monkeypatch):
        """Test handling a subsequent declaration after player has declared."""
        # Set player as already declared
        self.player.has_declared = True

        # Create a new meld for subsequent declaration
        new_meld = Meld(cards=self.king_set, type="set")

        # Mock create_new_meld to return our set
        monkeypatch.setattr(main, "create_new_meld", lambda p: new_meld)

        # Mock confirmation to stop after one meld
        monkeypatch.setattr(main.Confirm, "ask", lambda p: False)

        # Call the function and check result
        result = main.handle_declaration(self.game_state, self.player)

        assert result is True
        assert len(self.game_state.melds_on_table) == 2  # Initial + new declaration

        # Check that the cards were removed from player's hand
        for card in self.king_set:
            assert card not in self.player.hand


if __name__ == "__main__":
    pytest.main([__file__])
