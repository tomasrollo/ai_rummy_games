"""Tests for the UI card selection integration with card display and discard logic."""

import pytest
from unittest.mock import patch, MagicMock
from rich.console import Console
from rich.table import Table
from io import StringIO

from main import display_hand, card_sort_key
from ai_rummy_games.models import Card, Deck, Player, GameState


class TestUICardSelection:
    """Tests for UI card selection and interaction with the game logic."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a player with a known hand of cards
        self.player = Player(name="TestPlayer")

        # Define a test hand with cards in a specific unsorted order
        self.test_hand = [
            Card(suit="Diamonds", rank="K"),  # Will be at index 5 after sorting
            Card(suit="Spades", rank="A"),  # Will be at index 0 after sorting
            Card(suit="Hearts", rank="10"),  # Will be at index 3 after sorting
            Card(suit="Clubs", rank="5"),  # Will be at index 6 after sorting
            Card(suit="Spades", rank="K"),  # Will be at index 1 after sorting
            Card(suit="Hearts", rank="2"),  # Will be at index 2 after sorting
            Card(suit="Diamonds", rank="3"),  # Will be at index 4 after sorting
        ]

        # Set the player's hand
        self.player.hand = self.test_hand.copy()

        # Create a deck for testing
        self.deck = Deck()
        self.deck.discard_pile = []

    @patch("main.console")
    def test_display_hand_sorting_order(self, mock_console):
        """Test that display_hand shows cards in the expected sorted order."""
        # Call display_hand
        display_hand(self.player.name, self.player.hand)

        # Check console.print was called (we can't easily check the exact table content)
        mock_console.print.assert_called()

        # Get expected sorted order for verification
        sorted_cards = sorted(self.player.hand, key=card_sort_key)
        expected_order = [str(card) for card in sorted_cards]

        # Verify order matches our expected sorted order
        assert expected_order[0] == "A♠"  # Spades Ace should be first
        assert expected_order[1] == "K♠"  # Spades King should be second
        assert expected_order[2] == "2♥"  # Hearts 2 should be third
        assert expected_order[3] == "10♥"  # Hearts 10 should be fourth
        assert expected_order[4] == "3♦"  # Diamonds 3 should be fifth
        assert expected_order[5] == "K♦"  # Diamonds King should be sixth
        assert expected_order[6] == "5♣"  # Clubs 5 should be last

    @patch("main.Prompt.ask")
    @patch("main.console")
    def test_user_input_maps_to_correct_sorted_card(self, mock_console, mock_prompt):
        """Test that user input correctly maps to the card in the sorted display."""
        # Create sorted version of cards (as the UI would display)
        sorted_cards = sorted(self.player.hand, key=card_sort_key)

        # Display the hand (this would sort them)
        display_hand(self.player.name, self.player.hand)

        # Get the actual order of cards for verification
        card_strings = [str(card) for card in sorted_cards]

        # Test individual positions
        # Position 1 (index 0)
        mock_prompt.return_value = "1"
        card_idx = int(mock_prompt.return_value) - 1
        selected_card = sorted_cards[card_idx]
        assert str(selected_card) == "A♠"  # First card should be Spades Ace

        # Position 3 (index 2)
        mock_prompt.return_value = "3"
        card_idx = int(mock_prompt.return_value) - 1
        selected_card = sorted_cards[card_idx]
        assert str(selected_card) == "2♥"  # Third card should be Hearts 2

        # Position 6 (index 5)
        mock_prompt.return_value = "6"
        card_idx = int(mock_prompt.return_value) - 1
        selected_card = sorted_cards[card_idx]
        assert str(selected_card) == "K♦"  # Sixth card should be Diamonds King

    @patch("main.Prompt.ask")
    @patch("main.console")
    def test_discard_with_subsequent_display_update(self, mock_console, mock_prompt):
        """Test that discarded cards are removed and display updates correctly."""
        # Mock the first discard selection (index 3 - Hearts 10)
        mock_prompt.return_value = "4"  # 4th card in sorted order

        # First display and discard
        sorted_cards = sorted(self.player.hand, key=card_sort_key)
        display_hand(self.player.name, self.player.hand)

        # Get the selected card and discard it
        card_idx = int(mock_prompt.return_value) - 1
        selected_card = sorted_cards[card_idx]
        self.player.remove_card(selected_card)
        self.deck.discard(selected_card)

        # Verify discarded card
        assert str(selected_card) == "10♥"
        assert len(self.player.hand) == 6

        # Now display the updated hand
        display_hand(self.player.name, self.player.hand)

        # Get the new sorted order - Hearts 10 should be gone
        updated_sorted_cards = sorted(self.player.hand, key=card_sort_key)
        expected_cards = [str(card) for card in updated_sorted_cards]

        # Verify the new order
        assert "10♥" not in expected_cards
        assert expected_cards[0] == "A♠"
        assert expected_cards[1] == "K♠"
        assert expected_cards[2] == "2♥"
        # Hearts 10 is gone, so Diamonds 3 should now be at index 3
        assert expected_cards[3] == "3♦"

    @patch("main.console")
    @patch("main.Prompt.ask")
    def test_integration_with_discard_workflow(self, mock_prompt, mock_console):
        """Test the full integration of display, selection and discard."""
        # Create a game state
        game_state = GameState()
        game_state.add_player(self.player)
        game_state.current_player_index = 0

        # Mock the sequence of card selections
        mock_prompt.side_effect = ["2", "3", "1"]  # Select Spades K, then Hearts 10, then Spades A

        # First discard
        sorted_cards = sorted(self.player.hand, key=card_sort_key)
        card_idx = int(mock_prompt()) - 1
        card = sorted_cards[card_idx]  # Should be Spades K
        self.player.remove_card(card)
        self.deck.discard(card)

        # Verify first discard
        assert str(card) == "K♠"
        assert len(self.player.hand) == 6

        # Second discard - use updated sorted hand
        sorted_cards = sorted(self.player.hand, key=card_sort_key)
        card_idx = int(mock_prompt()) - 1
        card = sorted_cards[card_idx]  # Should be Hearts 10
        self.player.remove_card(card)
        self.deck.discard(card)

        # Verify second discard
        assert str(card) == "10♥"
        assert len(self.player.hand) == 5

        # Third discard - use updated sorted hand again
        sorted_cards = sorted(self.player.hand, key=card_sort_key)
        card_idx = int(mock_prompt()) - 1
        card = sorted_cards[card_idx]  # Should be Spades A
        self.player.remove_card(card)
        self.deck.discard(card)

        # Verify third discard
        assert str(card) == "A♠"
        assert len(self.player.hand) == 4

        # Verify discard pile contains our three discarded cards in order
        assert str(self.deck.discard_pile[0]) == "K♠"
        assert str(self.deck.discard_pile[1]) == "10♥"
        assert str(self.deck.discard_pile[2]) == "A♠"

        # Verify remaining cards in the hand
        remaining_cards = [str(card) for card in sorted(self.player.hand, key=card_sort_key)]
        assert remaining_cards == ["2♥", "3♦", "K♦", "5♣"]
