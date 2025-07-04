"""Unit tests for card selection and discard functionality."""

import pytest
from unittest.mock import patch, MagicMock, call

from main import card_sort_key, display_hand
from ai_rummy_games.models import Card, Deck, Player, GameState


class TestCardSorting:
    """Test cases for card sorting functionality."""

    def test_card_sort_key(self):
        """Test that card_sort_key returns correct sort keys."""
        # Test joker
        joker = Card(suit="", rank="", is_joker=True)
        assert card_sort_key(joker) == (4, 0)

        # Test regular cards
        spades_ace = Card(suit="Spades", rank="A")
        hearts_ten = Card(suit="Hearts", rank="10")
        diamonds_queen = Card(suit="Diamonds", rank="Q")
        clubs_two = Card(suit="Clubs", rank="2")

        # Check suit ordering
        assert card_sort_key(spades_ace)[0] < card_sort_key(hearts_ten)[0]
        assert card_sort_key(hearts_ten)[0] < card_sort_key(diamonds_queen)[0]
        assert card_sort_key(diamonds_queen)[0] < card_sort_key(clubs_two)[0]

        # Check rank ordering
        assert card_sort_key(Card(suit="Spades", rank="A"))[1] < card_sort_key(Card(suit="Spades", rank="2"))[1]
        assert card_sort_key(Card(suit="Spades", rank="10"))[1] < card_sort_key(Card(suit="Spades", rank="J"))[1]
        assert card_sort_key(Card(suit="Spades", rank="Q"))[1] < card_sort_key(Card(suit="Spades", rank="K"))[1]

    def test_sorted_cards_order(self):
        """Test that cards are sorted correctly."""
        cards = [
            Card(suit="Diamonds", rank="K"),
            Card(suit="Spades", rank="A"),
            Card(suit="Hearts", rank="10"),
            Card(suit="Clubs", rank="5"),
            Card(suit="Spades", rank="K"),
            Card(suit="", rank="", is_joker=True),
            Card(suit="Hearts", rank="2"),
            Card(suit="Diamonds", rank="3"),
        ]

        sorted_cards = sorted(cards, key=card_sort_key)

        # Check expected order
        assert sorted_cards[0].suit == "Spades" and sorted_cards[0].rank == "A"  # Spades A
        assert sorted_cards[1].suit == "Spades" and sorted_cards[1].rank == "K"  # Spades K
        assert sorted_cards[2].suit == "Hearts" and sorted_cards[2].rank == "2"  # Hearts 2
        assert sorted_cards[3].suit == "Hearts" and sorted_cards[3].rank == "10"  # Hearts 10
        assert sorted_cards[4].suit == "Diamonds" and sorted_cards[4].rank == "3"  # Diamonds 3
        assert sorted_cards[5].suit == "Diamonds" and sorted_cards[5].rank == "K"  # Diamonds K
        assert sorted_cards[6].suit == "Clubs" and sorted_cards[6].rank == "5"  # Clubs 5
        assert sorted_cards[7].is_joker  # Joker at the end


class TestCardDiscard:
    """Test cases for card discard functionality."""

    @patch("main.Prompt.ask")
    def test_discard_from_sorted_hand(self, mock_prompt):
        """Test that the correct card is discarded based on its position in the sorted hand."""
        # Setup player with an unsorted hand
        player = Player(name="TestPlayer")
        player.hand = [
            Card(suit="Diamonds", rank="K"),
            Card(suit="Spades", rank="A"),
            Card(suit="Hearts", rank="10"),
            Card(suit="Clubs", rank="5"),
        ]

        # Create a deck
        deck = Deck()
        deck.discard_pile = []

        # When sorted, the order should be:
        # 1. Spades A
        # 2. Hearts 10
        # 3. Diamonds K
        # 4. Clubs 5

        # Set up the game state with our player
        game_state = GameState()
        game_state.add_player(player)
        game_state.current_player_index = 0

        # Simulate player selecting card #2 (Hearts 10)
        mock_prompt.return_value = "2"

        # Call the discard function manually with our mocks
        # We're testing the underlying logic, not the full CLI flow
        sorted_cards = sorted(player.hand, key=card_sort_key)
        card_idx = int(mock_prompt.return_value) - 1
        discarded_card = sorted_cards[card_idx]  # Should be Hearts 10
        player.remove_card(discarded_card)
        deck.discard(discarded_card)

        # Verify correct card was discarded
        assert len(player.hand) == 3
        assert deck.discard_pile[0].suit == "Hearts"
        assert deck.discard_pile[0].rank == "10"

        # Verify discarded card is no longer in player's hand
        assert not any(card.suit == "Hearts" and card.rank == "10" for card in player.hand)

    @patch("main.console")
    @patch("main.Prompt.ask")
    def test_multiple_discard_selections(self, mock_prompt, mock_console):
        """Test discarding multiple cards in sequence to ensure indexes remain consistent."""
        # Setup player with a known hand
        player = Player(name="TestPlayer")
        player.hand = [
            Card(suit="Diamonds", rank="K"),
            Card(suit="Spades", rank="A"),
            Card(suit="Hearts", rank="10"),
            Card(suit="Clubs", rank="5"),
            Card(suit="Spades", rank="K"),
        ]

        # Create deck for discards
        deck = Deck()
        deck.discard_pile = []

        # When sorted, the order should be:
        # 1. Spades A
        # 2. Spades K
        # 3. Hearts 10
        # 4. Diamonds K
        # 5. Clubs 5

        # Simulate player selecting card #1 (Spades A)
        mock_prompt.return_value = "1"

        # Manual discard logic
        sorted_cards = sorted(player.hand, key=card_sort_key)
        card_idx = int(mock_prompt.return_value) - 1
        discarded_card = sorted_cards[card_idx]  # Should be Spades A
        player.remove_card(discarded_card)
        deck.discard(discarded_card)

        # Verify first discard
        assert deck.discard_pile[0].suit == "Spades"
        assert deck.discard_pile[0].rank == "A"

        # Now remaining hand sorted would be:
        # 1. Spades K
        # 2. Hearts 10
        # 3. Diamonds K
        # 4. Clubs 5

        # Simulate player selecting card #2 again (now Hearts 10)
        mock_prompt.return_value = "2"

        # Discard again
        sorted_cards = sorted(player.hand, key=card_sort_key)  # Re-sort after first discard
        card_idx = int(mock_prompt.return_value) - 1
        discarded_card = sorted_cards[card_idx]  # Should be Hearts 10
        player.remove_card(discarded_card)
        deck.discard(discarded_card)

        # Verify second discard
        assert deck.discard_pile[1].suit == "Hearts"
        assert deck.discard_pile[1].rank == "10"

        # Verify final hand state
        assert len(player.hand) == 3
        assert not any(card.suit == "Spades" and card.rank == "A" for card in player.hand)
        assert not any(card.suit == "Hearts" and card.rank == "10" for card in player.hand)


@patch("main.console")
class TestSortedHandDisplay(object):
    """Test cases for displaying sorted hands."""

    def test_hand_display_sorting(self, mock_console):
        """Test that cards are displayed in sorted order."""
        # Create a deliberately unsorted hand
        cards = [
            Card(suit="Diamonds", rank="K"),
            Card(suit="Spades", rank="A"),
            Card(suit="Hearts", rank="10"),
            Card(suit="Clubs", rank="5"),
        ]

        # Display the hand (which should sort it)
        display_hand("TestPlayer", cards)

        # Check that mock_console.print was called with a Table
        mock_console.print.assert_called()

        # We'd need to inspect the Table to fully verify the sorting,
        # but that's complex with mocking. This test primarily ensures
        # the function runs without errors and calls console.print.
