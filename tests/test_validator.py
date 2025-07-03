"""Unit tests for the Validator class."""

import pytest
from ai_rummy_games.models import Card, Meld, Player
from ai_rummy_games.validator import Validator


class TestValidator:
    """Test cases for the Validator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = Validator()

    def test_card_points_calculation(self):
        """Test point calculation for individual cards."""
        # Test numeric cards
        card_2 = Card(suit="Hearts", rank="2")
        card_5 = Card(suit="Spades", rank="5")
        card_10 = Card(suit="Clubs", rank="10")

        # Test face cards
        card_j = Card(suit="Diamonds", rank="J")
        card_q = Card(suit="Hearts", rank="Q")
        card_k = Card(suit="Spades", rank="K")
        card_a = Card(suit="Clubs", rank="A")

        # Test joker
        joker = Card(suit="", rank="", is_joker=True)

        # Create melds to test point calculation
        meld_numeric = Meld(cards=[card_2, card_5, card_10], type="set")
        meld_face = Meld(cards=[card_j, card_q, card_k], type="set")
        meld_with_joker = Meld(cards=[card_a, joker, card_k], type="set")

        assert self.validator._calculate_single_meld_points(meld_numeric) == 17  # 2+5+10
        assert self.validator._calculate_single_meld_points(meld_face) == 30  # 10+10+10
        assert self.validator._calculate_single_meld_points(meld_with_joker) == 40  # 10+20+10

    def test_valid_set_recognition(self):
        """Test recognition of valid sets."""
        # Valid set: three cards of same rank, different suits
        cards_valid = [Card(suit="Hearts", rank="K"), Card(suit="Spades", rank="K"), Card(suit="Clubs", rank="K")]
        assert self.validator._is_valid_set(cards_valid)

        # Valid set with joker
        cards_with_joker = [
            Card(suit="Hearts", rank="Q"),
            Card(suit="Spades", rank="Q"),
            Card(suit="", rank="", is_joker=True),
        ]
        assert self.validator._is_valid_set(cards_with_joker)

        # Invalid set: different ranks
        cards_invalid_rank = [
            Card(suit="Hearts", rank="K"),
            Card(suit="Spades", rank="Q"),
            Card(suit="Clubs", rank="J"),
        ]
        assert not self.validator._is_valid_set(cards_invalid_rank)

        # Invalid set: duplicate suits
        cards_duplicate_suit = [
            Card(suit="Hearts", rank="K"),
            Card(suit="Hearts", rank="K"),
            Card(suit="Clubs", rank="K"),
        ]
        assert not self.validator._is_valid_set(cards_duplicate_suit)

        # Invalid set: too few cards
        cards_too_few = [Card(suit="Hearts", rank="K"), Card(suit="Spades", rank="K")]
        assert not self.validator._is_valid_set(cards_too_few)

    def test_valid_sequence_recognition(self):
        """Test recognition of valid sequences."""
        # Valid sequence: consecutive ranks, same suit
        cards_valid = [Card(suit="Hearts", rank="5"), Card(suit="Hearts", rank="6"), Card(suit="Hearts", rank="7")]
        assert self.validator._is_valid_sequence(cards_valid)

        # Valid sequence with joker filling gap
        cards_with_joker = [
            Card(suit="Spades", rank="8"),
            Card(suit="", rank="", is_joker=True),
            Card(suit="Spades", rank="10"),
        ]
        assert self.validator._is_valid_sequence(cards_with_joker)

        # Invalid sequence: different suits
        cards_different_suits = [
            Card(suit="Hearts", rank="5"),
            Card(suit="Spades", rank="6"),
            Card(suit="Hearts", rank="7"),
        ]
        assert not self.validator._is_valid_sequence(cards_different_suits)

        # Invalid sequence: non-consecutive
        cards_non_consecutive = [
            Card(suit="Hearts", rank="5"),
            Card(suit="Hearts", rank="7"),
            Card(suit="Hearts", rank="9"),
        ]
        assert not self.validator._is_valid_sequence(cards_non_consecutive)

        # Invalid sequence: too few cards
        cards_too_few = [Card(suit="Hearts", rank="5"), Card(suit="Hearts", rank="6")]
        assert not self.validator._is_valid_sequence(cards_too_few)

    def test_pure_sequence_detection(self):
        """Test detection of pure sequences (no jokers)."""
        # Pure sequence
        pure_seq = Meld(
            cards=[Card(suit="Hearts", rank="3"), Card(suit="Hearts", rank="4"), Card(suit="Hearts", rank="5")],
            type="sequence",
        )
        assert self.validator._is_pure_sequence(pure_seq)

        # Sequence with joker (not pure)
        impure_seq = Meld(
            cards=[
                Card(suit="Hearts", rank="3"),
                Card(suit="", rank="", is_joker=True),
                Card(suit="Hearts", rank="5"),
            ],
            type="sequence",
        )
        assert not self.validator._is_pure_sequence(impure_seq)

        # Set (not a sequence)
        set_meld = Meld(
            cards=[Card(suit="Hearts", rank="K"), Card(suit="Spades", rank="K"), Card(suit="Clubs", rank="K")],
            type="set",
        )
        assert not self.validator._is_pure_sequence(set_meld)

    def test_valid_initial_declaration(self):
        """Test validation of valid initial declarations."""
        player = Player(name="TestPlayer")

        # Create a valid hand with enough points and a pure sequence
        hand_cards = [
            # Pure sequence (30 points)
            Card(suit="Hearts", rank="Q"),
            Card(suit="Hearts", rank="K"),
            Card(suit="Hearts", rank="A"),
            # Set (30 points)
            Card(suit="Spades", rank="10"),
            Card(suit="Clubs", rank="10"),
            Card(suit="Diamonds", rank="10"),
            # Extra cards
            Card(suit="Hearts", rank="2"),
            Card(suit="Spades", rank="3"),
        ]

        for card in hand_cards:
            player.add_card(card)

        # Create melds
        pure_sequence = Meld(cards=[hand_cards[0], hand_cards[1], hand_cards[2]], type="sequence")
        valid_set = Meld(cards=[hand_cards[3], hand_cards[4], hand_cards[5]], type="set")

        melds = [pure_sequence, valid_set]

        assert self.validator.validate_initial_declaration(player.hand, melds)

    def test_invalid_declaration_insufficient_points(self):
        """Test rejection of declarations with insufficient points."""
        player = Player(name="TestPlayer")

        # Create a hand with valid melds but insufficient points
        hand_cards = [
            # Pure sequence (only 15 points)
            Card(suit="Hearts", rank="2"),
            Card(suit="Hearts", rank="3"),
            Card(suit="Hearts", rank="4"),
            # Set (only 18 points)
            Card(suit="Spades", rank="6"),
            Card(suit="Clubs", rank="6"),
            Card(suit="Diamonds", rank="6"),
        ]

        for card in hand_cards:
            player.add_card(card)

        pure_sequence = Meld(cards=[hand_cards[0], hand_cards[1], hand_cards[2]], type="sequence")
        valid_set = Meld(cards=[hand_cards[3], hand_cards[4], hand_cards[5]], type="set")

        melds = [pure_sequence, valid_set]

        assert not self.validator.validate_initial_declaration(player.hand, melds)

    def test_invalid_declaration_no_pure_sequence(self):
        """Test rejection of declarations without pure sequence."""
        player = Player(name="TestPlayer")

        # Create a hand with enough points but no pure sequence
        hand_cards = [
            # Impure sequence (using joker)
            Card(suit="Hearts", rank="Q"),
            Card(suit="", rank="", is_joker=True),
            Card(suit="Hearts", rank="A"),
            # Set (30 points)
            Card(suit="Spades", rank="K"),
            Card(suit="Clubs", rank="K"),
            Card(suit="Diamonds", rank="K"),
        ]

        for card in hand_cards:
            player.add_card(card)

        impure_sequence = Meld(cards=[hand_cards[0], hand_cards[1], hand_cards[2]], type="sequence")
        valid_set = Meld(cards=[hand_cards[3], hand_cards[4], hand_cards[5]], type="set")

        melds = [impure_sequence, valid_set]

        assert not self.validator.validate_initial_declaration(player.hand, melds)

    def test_invalid_declaration_cards_not_in_hand(self):
        """Test rejection when meld cards are not in player's hand."""
        player = Player(name="TestPlayer")

        # Add only some cards to hand
        hand_cards = [Card(suit="Hearts", rank="Q"), Card(suit="Hearts", rank="K"), Card(suit="Hearts", rank="A")]

        for card in hand_cards:
            player.add_card(card)

        # Try to create meld with cards not in hand
        fake_meld = Meld(
            cards=[
                Card(suit="Spades", rank="K"),  # Not in hand
                Card(suit="Clubs", rank="K"),  # Not in hand
                Card(suit="Diamonds", rank="K"),  # Not in hand
            ],
            type="set",
        )

        melds = [fake_meld]

        assert not self.validator.validate_initial_declaration(player.hand, melds)

    def test_sequence_with_ace_low(self):
        """Test sequences with Ace as low card (A-2-3)."""
        cards = [Card(suit="Hearts", rank="A"), Card(suit="Hearts", rank="2"), Card(suit="Hearts", rank="3")]
        assert self.validator._is_valid_sequence(cards)

    def test_sequence_with_ace_high(self):
        """Test sequences with Ace as high card (J-Q-K-A not valid in this implementation)."""
        # In this implementation, A=1, so A-K-Q would not be consecutive
        cards = [
            Card(suit="Hearts", rank="J"),
            Card(suit="Hearts", rank="Q"),
            Card(suit="Hearts", rank="K"),
            Card(suit="Hearts", rank="A"),
        ]
        # This should fail because A=1, K=13, so they're not consecutive
        assert not self.validator._is_valid_sequence(cards)

    def test_meld_validation_integration(self):
        """Test the overall meld validation."""
        # Valid set
        valid_set = Meld(
            cards=[Card(suit="Hearts", rank="7"), Card(suit="Spades", rank="7"), Card(suit="Clubs", rank="7")],
            type="set",
        )
        assert self.validator._validate_meld(valid_set)

        # Valid sequence
        valid_sequence = Meld(
            cards=[Card(suit="Diamonds", rank="9"), Card(suit="Diamonds", rank="10"), Card(suit="Diamonds", rank="J")],
            type="sequence",
        )
        assert self.validator._validate_meld(valid_sequence)

        # Invalid meld type
        invalid_meld = Meld(
            cards=[Card(suit="Hearts", rank="7"), Card(suit="Spades", rank="7"), Card(suit="Clubs", rank="7")]
        )
        # Override the type with an invalid value
        invalid_meld.type = "unknown"
        assert not self.validator._validate_meld(invalid_meld)


if __name__ == "__main__":
    pytest.main([__file__])
