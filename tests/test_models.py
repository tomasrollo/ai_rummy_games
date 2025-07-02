"""Unit tests for Card and Deck models."""

import pytest
from ai_rummy_games.models import Card, Deck, Player, Meld, GameState


class TestCard:
    """Test cases for the Card class."""

    def test_card_creation(self):
        """Test creating a regular card."""
        card = Card(suit="Hearts", rank="A")
        assert card.suit == "Hearts"
        assert card.rank == "A"
        assert card.is_joker is False

    def test_joker_creation(self):
        """Test creating a joker card."""
        joker = Card(suit="", rank="", is_joker=True)
        assert joker.suit == ""
        assert joker.rank == ""
        assert joker.is_joker is True

    def test_card_string_representation(self):
        """Test string representation of cards."""
        card = Card(suit="Spades", rank="K")
        assert str(card) == "K of Spades"

        joker = Card(suit="", rank="", is_joker=True)
        assert str(joker) == "Joker"

    def test_card_repr(self):
        """Test detailed representation of cards."""
        card = Card(suit="Diamonds", rank="7")
        expected = "Card(suit='Diamonds', rank='7', is_joker=False)"
        assert repr(card) == expected


class TestDeck:
    """Test cases for the Deck class."""

    def test_deck_initialization(self):
        """Test that deck initializes with 108 cards."""
        deck = Deck()
        assert deck.cards_remaining() == 108
        assert deck.discard_pile_size() == 0

    def test_deck_composition(self):
        """Test that deck contains correct cards."""
        deck = Deck()

        # Count jokers
        jokers = [card for card in deck.draw_pile if card.is_joker]
        assert len(jokers) == 4

        # Count regular cards (should be 104: 52 * 2 decks)
        regular_cards = [card for card in deck.draw_pile if not card.is_joker]
        assert len(regular_cards) == 104

        # Verify we have exactly 2 of each regular card
        card_counts = {}
        for card in regular_cards:
            key = (card.suit, card.rank)
            card_counts[key] = card_counts.get(key, 0) + 1

        # Should have 2 of each card (13 ranks * 4 suits = 52 unique cards, 2 each)
        assert len(card_counts) == 52
        assert all(count == 2 for count in card_counts.values())

    def test_shuffle_changes_order(self):
        """Test that shuffle changes the order of cards."""
        deck = Deck()
        original_order = deck.draw_pile.copy()

        deck.shuffle()

        # After shuffling, order should be different
        # (There's a tiny chance it could be the same, but extremely unlikely)
        assert deck.draw_pile != original_order

        # But same cards should still be present
        assert len(deck.draw_pile) == len(original_order)
        assert set(str(card) for card in deck.draw_pile) == set(str(card) for card in original_order)

    def test_draw_reduces_draw_pile(self):
        """Test that drawing reduces draw pile size and returns a Card."""
        deck = Deck()
        initial_count = deck.cards_remaining()

        card = deck.draw()

        assert isinstance(card, Card)
        assert deck.cards_remaining() == initial_count - 1

    def test_draw_from_empty_deck(self):
        """Test drawing from an empty deck returns None."""
        deck = Deck()

        # Draw all cards
        while deck.cards_remaining() > 0:
            deck.draw()

        # Drawing from empty deck should return None
        assert deck.draw() is None
        assert deck.cards_remaining() == 0

    def test_discard_adds_to_discard_pile(self):
        """Test that discarding adds cards to discard pile."""
        deck = Deck()
        card = deck.draw()
        initial_discard_size = deck.discard_pile_size()

        deck.discard(card)

        assert deck.discard_pile_size() == initial_discard_size + 1
        assert deck.peek_top_discard() == card

    def test_multiple_discards(self):
        """Test multiple discards maintain correct order."""
        deck = Deck()

        card1 = deck.draw()
        card2 = deck.draw()

        deck.discard(card1)
        deck.discard(card2)

        assert deck.discard_pile_size() == 2
        assert deck.peek_top_discard() == card2  # Last discarded should be on top

    def test_peek_top_discard_empty_pile(self):
        """Test peeking at empty discard pile returns None."""
        deck = Deck()
        assert deck.peek_top_discard() is None

    def test_deck_constants(self):
        """Test that deck constants are correct."""
        assert len(Deck.SUITS) == 4
        assert len(Deck.RANKS) == 13
        assert "Hearts" in Deck.SUITS
        assert "Diamonds" in Deck.SUITS
        assert "Clubs" in Deck.SUITS
        assert "Spades" in Deck.SUITS
        assert "A" in Deck.RANKS
        assert "K" in Deck.RANKS


class TestPlayer:
    """Test cases for the Player class."""

    def test_player_creation(self):
        """Test creating a player."""
        player = Player(name="Alice")
        assert player.name == "Alice"
        assert player.hand == []
        assert player.has_declared is False
        assert player.hand_size() == 0

    def test_add_card(self):
        """Test adding cards to player's hand."""
        player = Player(name="Bob")
        card1 = Card(suit="Hearts", rank="A")
        card2 = Card(suit="Spades", rank="K")

        player.add_card(card1)
        assert player.hand_size() == 1
        assert card1 in player.hand

        player.add_card(card2)
        assert player.hand_size() == 2
        assert card2 in player.hand

    def test_remove_card(self):
        """Test removing cards from player's hand."""
        player = Player(name="Carol")
        card1 = Card(suit="Hearts", rank="A")
        card2 = Card(suit="Spades", rank="K")

        player.add_card(card1)
        player.add_card(card2)

        player.remove_card(card1)
        assert player.hand_size() == 1
        assert card1 not in player.hand
        assert card2 in player.hand

    def test_remove_nonexistent_card(self):
        """Test removing a card that's not in hand raises ValueError."""
        player = Player(name="Dave")
        card1 = Card(suit="Hearts", rank="A")
        card2 = Card(suit="Spades", rank="K")

        player.add_card(card1)

        with pytest.raises(ValueError, match="Card .* not found in Dave's hand"):
            player.remove_card(card2)

    def test_declare(self):
        """Test player declaration."""
        player = Player(name="Eve")
        assert player.has_declared is False

        player.declare()
        assert player.has_declared is True

    def test_player_serialization(self):
        """Test player serialization and deserialization."""
        original_player = Player(name="Frank")
        original_player.add_card(Card(suit="Hearts", rank="A"))
        original_player.add_card(Card(suit="", rank="", is_joker=True))
        original_player.declare()

        # Serialize
        player_dict = original_player.to_dict()

        # Deserialize
        restored_player = Player.from_dict(player_dict)

        assert restored_player.name == original_player.name
        assert restored_player.has_declared == original_player.has_declared
        assert restored_player.hand_size() == original_player.hand_size()

        # Check cards are equivalent
        for orig_card, rest_card in zip(original_player.hand, restored_player.hand):
            assert orig_card.suit == rest_card.suit
            assert orig_card.rank == rest_card.rank
            assert orig_card.is_joker == rest_card.is_joker


class TestMeld:
    """Test cases for the Meld class."""

    def test_meld_creation(self):
        """Test creating a meld."""
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Hearts", rank="2"), Card(suit="Hearts", rank="3")]
        meld = Meld(type="sequence", cards=cards)
        assert meld.type == "sequence"
        assert len(meld.cards) == 3

    def test_valid_set(self):
        """Test validation of a valid set."""
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Spades", rank="A"), Card(suit="Clubs", rank="A")]
        meld = Meld(type="set", cards=cards)
        assert meld.is_valid() is True

    def test_invalid_set_different_ranks(self):
        """Test validation of invalid set with different ranks."""
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Spades", rank="K"), Card(suit="Clubs", rank="A")]
        meld = Meld(type="set", cards=cards)
        assert meld.is_valid() is False

    def test_invalid_set_duplicate_suits(self):
        """Test validation of invalid set with duplicate suits."""
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Hearts", rank="A"), Card(suit="Clubs", rank="A")]
        meld = Meld(type="set", cards=cards)
        assert meld.is_valid() is False

    def test_valid_sequence(self):
        """Test validation of a valid sequence."""
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Hearts", rank="2"), Card(suit="Hearts", rank="3")]
        meld = Meld(type="sequence", cards=cards)
        assert meld.is_valid() is True

    def test_valid_sequence_with_face_cards(self):
        """Test validation of sequence with face cards."""
        cards = [Card(suit="Spades", rank="J"), Card(suit="Spades", rank="Q"), Card(suit="Spades", rank="K")]
        meld = Meld(type="sequence", cards=cards)
        assert meld.is_valid() is True

    def test_invalid_sequence_different_suits(self):
        """Test validation of invalid sequence with different suits."""
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Spades", rank="2"), Card(suit="Hearts", rank="3")]
        meld = Meld(type="sequence", cards=cards)
        assert meld.is_valid() is False

    def test_invalid_sequence_non_consecutive(self):
        """Test validation of invalid sequence with non-consecutive ranks."""
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Hearts", rank="3"), Card(suit="Hearts", rank="5")]
        meld = Meld(type="sequence", cards=cards)
        assert meld.is_valid() is False

    def test_meld_too_short(self):
        """Test that melds with less than 3 cards are invalid."""
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Hearts", rank="2")]
        meld = Meld(type="sequence", cards=cards)
        assert meld.is_valid() is False

        set_meld = Meld(type="set", cards=cards)
        assert set_meld.is_valid() is False

    def test_meld_with_jokers_set(self):
        """Test set validation with jokers."""
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Spades", rank="A"), Card(suit="", rank="", is_joker=True)]
        meld = Meld(type="set", cards=cards)
        assert meld.is_valid() is True

    def test_meld_serialization(self):
        """Test meld serialization and deserialization."""
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Hearts", rank="2"), Card(suit="Hearts", rank="3")]
        original_meld = Meld(type="sequence", cards=cards)

        # Serialize
        meld_dict = original_meld.to_dict()

        # Deserialize
        restored_meld = Meld.from_dict(meld_dict)

        assert restored_meld.type == original_meld.type
        assert len(restored_meld.cards) == len(original_meld.cards)

        for orig_card, rest_card in zip(original_meld.cards, restored_meld.cards):
            assert orig_card.suit == rest_card.suit
            assert orig_card.rank == rest_card.rank
            assert orig_card.is_joker == rest_card.is_joker


class TestGameState:
    """Test cases for the GameState class."""

    def test_gamestate_creation(self):
        """Test creating a game state."""
        game_state = GameState()
        assert game_state.players == []
        assert game_state.draw_pile == []
        assert game_state.discard_pile == []
        assert game_state.melds_on_table == []
        assert game_state.current_round == 1
        assert game_state.current_player_index == 0

    def test_add_player(self):
        """Test adding players to the game."""
        game_state = GameState()
        player1 = Player(name="Alice")
        player2 = Player(name="Bob")

        game_state.add_player(player1)
        assert len(game_state.players) == 1
        assert game_state.players[0] == player1

        game_state.add_player(player2)
        assert len(game_state.players) == 2
        assert game_state.players[1] == player2

    def test_remove_player(self):
        """Test removing players from the game."""
        game_state = GameState()
        player1 = Player(name="Alice")
        player2 = Player(name="Bob")
        player3 = Player(name="Carol")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)

        game_state.remove_player("Bob")
        assert len(game_state.players) == 2
        assert player2 not in game_state.players
        assert player1 in game_state.players
        assert player3 in game_state.players

    def test_remove_nonexistent_player(self):
        """Test removing a player that doesn't exist raises ValueError."""
        game_state = GameState()
        player1 = Player(name="Alice")
        game_state.add_player(player1)

        with pytest.raises(ValueError, match="Player 'Nonexistent' not found"):
            game_state.remove_player("Nonexistent")

    def test_next_turn(self):
        """Test advancing turns."""
        game_state = GameState()
        player1 = Player(name="Alice")
        player2 = Player(name="Bob")
        player3 = Player(name="Carol")

        game_state.add_player(player1)
        game_state.add_player(player2)
        game_state.add_player(player3)

        assert game_state.current_player_index == 0
        assert game_state.current_round == 1

        game_state.next_turn()
        assert game_state.current_player_index == 1
        assert game_state.current_round == 1

        game_state.next_turn()
        assert game_state.current_player_index == 2
        assert game_state.current_round == 1

        # Should wrap around and increment round
        game_state.next_turn()
        assert game_state.current_player_index == 0
        assert game_state.current_round == 2

    def test_current_player(self):
        """Test getting the current player."""
        game_state = GameState()

        # No players
        assert game_state.current_player() is None

        player1 = Player(name="Alice")
        player2 = Player(name="Bob")
        game_state.add_player(player1)
        game_state.add_player(player2)

        assert game_state.current_player() == player1

        game_state.next_turn()
        assert game_state.current_player() == player2

    def test_add_meld_to_table(self):
        """Test adding melds to the table."""
        game_state = GameState()
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Hearts", rank="2"), Card(suit="Hearts", rank="3")]
        meld = Meld(type="sequence", cards=cards)

        game_state.add_meld_to_table(meld)
        assert len(game_state.melds_on_table) == 1
        assert game_state.melds_on_table[0] == meld

    def test_gamestate_with_three_players(self):
        """Test instantiating GameState with 3 players and verify defaults."""
        game_state = GameState()

        # Add 3 players
        for name in ["Alice", "Bob", "Carol"]:
            game_state.add_player(Player(name=name))

        # Verify defaults
        assert len(game_state.players) == 3
        assert game_state.current_round == 1
        assert len(game_state.melds_on_table) == 0
        assert len(game_state.draw_pile) == 0
        assert len(game_state.discard_pile) == 0

        # Verify all players have empty hands
        for player in game_state.players:
            assert player.hand_size() == 0

    def test_gamestate_serialization(self):
        """Test game state serialization and deserialization."""
        original_state = GameState()

        # Add players
        player1 = Player(name="Alice")
        player1.add_card(Card(suit="Hearts", rank="A"))
        player2 = Player(name="Bob")
        original_state.add_player(player1)
        original_state.add_player(player2)

        # Add cards to piles
        original_state.draw_pile.append(Card(suit="Spades", rank="K"))
        original_state.discard_pile.append(Card(suit="Clubs", rank="Q"))

        # Add meld
        meld_cards = [
            Card(suit="Diamonds", rank="2"),
            Card(suit="Diamonds", rank="3"),
            Card(suit="Diamonds", rank="4"),
        ]
        meld = Meld(type="sequence", cards=meld_cards)
        original_state.add_meld_to_table(meld)

        original_state.current_round = 3
        original_state.current_player_index = 1

        # Serialize
        state_dict = original_state.to_dict()

        # Deserialize
        restored_state = GameState.from_dict(state_dict)

        assert len(restored_state.players) == len(original_state.players)
        assert restored_state.current_round == original_state.current_round
        assert restored_state.current_player_index == original_state.current_player_index
        assert len(restored_state.draw_pile) == len(original_state.draw_pile)
        assert len(restored_state.discard_pile) == len(original_state.discard_pile)
        assert len(restored_state.melds_on_table) == len(original_state.melds_on_table)


class TestCardSerialization:
    """Test cases for Card serialization."""

    def test_card_serialization(self):
        """Test card serialization and deserialization."""
        original_card = Card(suit="Hearts", rank="A", is_joker=False)

        # Serialize
        card_dict = original_card.to_dict()

        # Deserialize
        restored_card = Card.from_dict(card_dict)

        assert restored_card.suit == original_card.suit
        assert restored_card.rank == original_card.rank
        assert restored_card.is_joker == original_card.is_joker

    def test_joker_serialization(self):
        """Test joker card serialization."""
        original_joker = Card(suit="", rank="", is_joker=True)

        # Serialize
        joker_dict = original_joker.to_dict()

        # Deserialize
        restored_joker = Card.from_dict(joker_dict)

        assert restored_joker.suit == original_joker.suit
        assert restored_joker.rank == original_joker.rank
        assert restored_joker.is_joker == original_joker.is_joker
