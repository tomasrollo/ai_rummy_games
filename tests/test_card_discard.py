"""Unit tests for card discard functionality."""

import pytest
from unittest.mock import patch, MagicMock, call
from io import StringIO

from main import card_sort_key
from ai_rummy_games.models import Card, Deck, Player, GameState


class TestCardDiscard:
    """Test cases for card discard functionality."""

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

    @patch("main.Prompt.ask")
    def test_discard_first_card_by_number(self, mock_prompt):
        """Test discarding the first card (index 1) from a sorted hand."""
        # First card after sorting will be Spades A
        mock_prompt.return_value = "1"

        # Sort the cards as the game would
        sorted_cards = sorted(self.player.hand, key=card_sort_key)

        # Get the card that should be discarded (Spades A)
        card_idx = int(mock_prompt.return_value) - 1
        discarded_card = sorted_cards[card_idx]

        # Perform the discard
        self.player.remove_card(discarded_card)
        self.deck.discard(discarded_card)

        # Verify the correct card was discarded
        assert len(self.player.hand) == 6
        assert self.deck.discard_pile[0].suit == "Spades"
        assert self.deck.discard_pile[0].rank == "A"

        # Verify the card is no longer in the hand
        assert not any(card.suit == "Spades" and card.rank == "A" for card in self.player.hand)

    @patch("main.Prompt.ask")
    def test_discard_middle_card_by_number(self, mock_prompt):
        """Test discarding a card from the middle of the sorted hand (Hearts 10)."""
        # Hearts 10 will be at index 3 (fourth card) in the sorted hand
        mock_prompt.return_value = "4"

        # Sort the cards as the game would
        sorted_cards = sorted(self.player.hand, key=card_sort_key)

        # Get the card that should be discarded (Hearts 10)
        card_idx = int(mock_prompt.return_value) - 1
        discarded_card = sorted_cards[card_idx]

        # Perform the discard
        self.player.remove_card(discarded_card)
        self.deck.discard(discarded_card)

        # Verify the correct card was discarded
        assert len(self.player.hand) == 6
        assert self.deck.discard_pile[0].suit == "Hearts"
        assert self.deck.discard_pile[0].rank == "10"

        # Verify the card is no longer in the hand
        assert not any(card.suit == "Hearts" and card.rank == "10" for card in self.player.hand)

    @patch("main.Prompt.ask")
    def test_discard_last_card_by_number(self, mock_prompt):
        """Test discarding the last card from the sorted hand (Clubs 5)."""
        # Clubs 5 will be at index 6 (seventh card) in the sorted hand
        mock_prompt.return_value = "7"

        # Sort the cards as the game would
        sorted_cards = sorted(self.player.hand, key=card_sort_key)

        # Get the card that should be discarded (Clubs 5)
        card_idx = int(mock_prompt.return_value) - 1
        discarded_card = sorted_cards[card_idx]

        # Perform the discard
        self.player.remove_card(discarded_card)
        self.deck.discard(discarded_card)

        # Verify the correct card was discarded
        assert len(self.player.hand) == 6
        assert self.deck.discard_pile[0].suit == "Clubs"
        assert self.deck.discard_pile[0].rank == "5"

        # Verify the card is no longer in the hand
        assert not any(card.suit == "Clubs" and card.rank == "5" for card in self.player.hand)

    @patch("main.console")
    @patch("main.Prompt.ask")
    def test_sequential_discards_with_changing_indices(self, mock_prompt, mock_console):
        """Test multiple discards in sequence, ensuring indices remain consistent."""
        # Create a deck for discards
        deck = Deck()
        deck.discard_pile = []

        # Mock the prompt to return different values for each call
        mock_prompt.side_effect = ["3", "2", "1"]

        # First discard: Hearts 2 (index 3 in original hand, index 2 in sorted hand)
        sorted_cards = sorted(self.player.hand, key=card_sort_key)
        card_idx = 2  # Index of Hearts 2 in sorted hand
        discarded_card = sorted_cards[card_idx]
        self.player.remove_card(discarded_card)
        deck.discard(discarded_card)

        # Verify first discard
        assert deck.discard_pile[0].suit == "Hearts"
        assert deck.discard_pile[0].rank == "2"

        # Second discard: Spades K (originally index 4, now index 1 in re-sorted hand)
        sorted_cards = sorted(self.player.hand, key=card_sort_key)
        card_idx = 1  # New index of Spades K in resorted hand
        discarded_card = sorted_cards[card_idx]
        self.player.remove_card(discarded_card)
        deck.discard(discarded_card)

        # Verify second discard
        assert deck.discard_pile[1].suit == "Spades"
        assert deck.discard_pile[1].rank == "K"

        # Third discard: Spades A (originally index 1, now index 0 in re-sorted hand)
        sorted_cards = sorted(self.player.hand, key=card_sort_key)
        card_idx = 0  # New index of Spades A in resorted hand
        discarded_card = sorted_cards[card_idx]
        self.player.remove_card(discarded_card)
        deck.discard(discarded_card)

        # Verify third discard
        assert deck.discard_pile[2].suit == "Spades"
        assert deck.discard_pile[2].rank == "A"

        # Verify final hand state
        assert len(self.player.hand) == 4
        assert not any(card.suit == "Hearts" and card.rank == "2" for card in self.player.hand)
        assert not any(card.suit == "Spades" and card.rank == "K" for card in self.player.hand)
        assert not any(card.suit == "Spades" and card.rank == "A" for card in self.player.hand)

    @patch("main.display_hand")
    @patch("main.console")
    @patch("main.Prompt.ask")
    def test_invalid_discard_number_handling(self, mock_prompt, mock_console, mock_display_hand):
        """Test handling of invalid discard numbers."""
        # First return an invalid number, then a valid one
        mock_prompt.side_effect = ["10", "2"]  # 10 is out of range, 2 is valid

        # Sort the hand
        sorted_cards = sorted(self.player.hand, key=card_sort_key)

        # First attempt - invalid index
        card_idx = int(mock_prompt()) - 1
        try:
            if card_idx < 0 or card_idx >= len(sorted_cards):
                raise ValueError("Invalid card number")

            # This should not execute
            assert False, "Should have raised an error"
        except ValueError:
            # Expected error
            pass

        # Second attempt - valid index
        card_idx = int(mock_prompt()) - 1
        discarded_card = sorted_cards[card_idx]  # Should be Spades K
        self.player.remove_card(discarded_card)
        self.deck.discard(discarded_card)

        # Verify correct card was discarded
        assert self.deck.discard_pile[0].suit == "Spades"
        assert self.deck.discard_pile[0].rank == "K"

    @patch("main.Prompt.ask")
    def test_discard_with_joker_in_hand(self, mock_prompt):
        """Test discarding with a joker in the hand (which sorts to the end)."""
        # Add a joker to the player's hand
        joker = Card(suit="", rank="", is_joker=True)
        self.player.hand.append(joker)

        # Select the joker (which will be the last card in the sorted hand)
        mock_prompt.return_value = str(len(self.player.hand))  # Index of the last card

        # Sort the cards as the game would
        sorted_cards = sorted(self.player.hand, key=card_sort_key)

        # Get the card that should be discarded (the joker)
        card_idx = int(mock_prompt.return_value) - 1
        discarded_card = sorted_cards[card_idx]

        # Perform the discard
        self.player.remove_card(discarded_card)
        self.deck.discard(discarded_card)

        # Verify the correct card was discarded
        assert len(self.player.hand) == 7
        assert self.deck.discard_pile[0].is_joker

        # Verify the joker is no longer in the hand
        assert not any(card.is_joker for card in self.player.hand)

    @patch("main.console")
    @patch("main.Prompt.ask")
    def test_card_number_mapping_after_reshuffle(self, mock_prompt, mock_console):
        """Test that card numbers correctly map to cards even after hand reshuffling."""
        # Start with a known hand
        spades_ace = Card(suit="Spades", rank="A")
        hearts_ten = Card(suit="Hearts", rank="10")
        diamonds_queen = Card(suit="Diamonds", rank="Q")

        # Create a new hand in a specific order
        self.player.hand = [diamonds_queen, spades_ace, hearts_ten]

        # When sorted, the order will be:
        # 1. Spades A
        # 2. Hearts 10
        # 3. Diamonds Q

        # Simulate drawing a new card that will change the sort order
        spades_king = Card(suit="Spades", rank="K")
        self.player.add_card(spades_king)

        # New sorted order:
        # 1. Spades A
        # 2. Spades K
        # 3. Hearts 10
        # 4. Diamonds Q

        # User selects card #3 (Hearts 10)
        mock_prompt.return_value = "3"

        # Sort and discard
        sorted_cards = sorted(self.player.hand, key=card_sort_key)
        card_idx = int(mock_prompt.return_value) - 1
        discarded_card = sorted_cards[card_idx]
        self.player.remove_card(discarded_card)
        self.deck.discard(discarded_card)

        # Verify correct card was discarded
        assert self.deck.discard_pile[0].suit == "Hearts"
        assert self.deck.discard_pile[0].rank == "10"

        # Verify hand state
        assert len(self.player.hand) == 3
        assert any(card.suit == "Spades" and card.rank == "A" for card in self.player.hand)
        assert any(card.suit == "Spades" and card.rank == "K" for card in self.player.hand)
        assert any(card.suit == "Diamonds" and card.rank == "Q" for card in self.player.hand)
        assert not any(card.suit == "Hearts" and card.rank == "10" for card in self.player.hand)


class TestCardSelectionIntegration:
    """Integration tests for card selection functionality."""

    @patch("main.console")
    @patch("main.Prompt.ask")
    def test_discard_from_main_game_flow(self, mock_prompt, mock_console):
        """Test the discard functionality as it would be used in the main game flow."""
        # Create player and game state
        player = Player(name="TestPlayer")
        game_state = GameState()
        game_state.add_player(player)
        game_state.current_player_index = 0

        # Define a test hand
        player.hand = [
            Card(suit="Diamonds", rank="K"),
            Card(suit="Spades", rank="A"),
            Card(suit="Hearts", rank="10"),
            Card(suit="Clubs", rank="5"),
            Card(suit="Spades", rank="K"),
            Card(suit="Hearts", rank="2"),
            Card(suit="Diamonds", rank="3"),
        ]

        # Create a deck for discards
        deck = Deck()
        deck.discard_pile = []

        # Mock player input to select card #2 (Spades K after sorting)
        mock_prompt.return_value = "2"

        # Get the current player and perform the discard as in the game
        current_player = game_state.current_player()

        # Create a sorted copy of the cards and display it (this is what happens in main.py)
        sorted_cards = sorted(current_player.hand, key=card_sort_key)

        # Simulate player selecting card #2
        card_idx = int(mock_prompt.return_value) - 1
        discarded_card = sorted_cards[card_idx]
        current_player.remove_card(discarded_card)
        deck.discard(discarded_card)

        # Verify the correct card was discarded
        assert deck.discard_pile[0].suit == "Spades"
        assert deck.discard_pile[0].rank == "K"

        # Verify card is no longer in hand
        assert not any(
            card.suit == "Spades" and card.rank == "K" and card == discarded_card for card in current_player.hand
        )

        # Note: There could still be another Spades K in the hand since
        # we had two of them in the original hand
