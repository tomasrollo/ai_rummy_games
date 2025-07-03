"""Unit tests for meld extension logic."""

import pytest
from ai_rummy_games.models import Card, Meld
from ai_rummy_games.validator import Validator


class TestMeldExtension:
    """Test cases for meld extensions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = Validator()

    def test_validate_new_meld_sequence(self):
        """Test validation of a new sequence meld."""
        # Valid sequence
        valid_sequence = [Card(suit="Hearts", rank="4"), Card(suit="Hearts", rank="5"), Card(suit="Hearts", rank="6")]
        assert self.validator.validate_new_meld(valid_sequence, "sequence")

        # Invalid sequence (mixed suits)
        invalid_sequence = [
            Card(suit="Hearts", rank="4"),
            Card(suit="Spades", rank="5"),
            Card(suit="Hearts", rank="6"),
        ]
        assert not self.validator.validate_new_meld(invalid_sequence, "sequence")

    def test_validate_new_meld_set(self):
        """Test validation of a new set meld."""
        # Valid set
        valid_set = [Card(suit="Hearts", rank="Q"), Card(suit="Spades", rank="Q"), Card(suit="Clubs", rank="Q")]
        assert self.validator.validate_new_meld(valid_set, "set")

        # Invalid set (mixed ranks)
        invalid_set = [Card(suit="Hearts", rank="J"), Card(suit="Spades", rank="Q"), Card(suit="Clubs", rank="K")]
        assert not self.validator.validate_new_meld(invalid_set, "set")

    def test_sequence_extension_valid_end(self):
        """Test extending a sequence at the end."""
        # Original sequence: 5-6-7 of Hearts
        existing_sequence = Meld(
            cards=[Card(suit="Hearts", rank="5"), Card(suit="Hearts", rank="6"), Card(suit="Hearts", rank="7")],
            type="sequence",
        )

        # Add 8 of Hearts to the end
        extension_cards = [Card(suit="Hearts", rank="8")]

        assert self.validator.validate_extension(existing_sequence, extension_cards)

    def test_sequence_extension_valid_beginning(self):
        """Test extending a sequence at the beginning."""
        # Original sequence: 5-6-7 of Hearts
        existing_sequence = Meld(
            cards=[Card(suit="Hearts", rank="5"), Card(suit="Hearts", rank="6"), Card(suit="Hearts", rank="7")],
            type="sequence",
        )

        # Add 4 of Hearts to the beginning
        extension_cards = [Card(suit="Hearts", rank="4")]

        assert self.validator.validate_extension(existing_sequence, extension_cards)

    def test_sequence_extension_with_joker(self):
        """Test extending a sequence with a joker."""
        # Original sequence: 5-6-7 of Hearts
        existing_sequence = Meld(
            cards=[Card(suit="Hearts", rank="5"), Card(suit="Hearts", rank="6"), Card(suit="Hearts", rank="7")],
            type="sequence",
        )

        # Add joker (representing 8 of Hearts)
        extension_cards = [Card(suit="", rank="", is_joker=True)]

        assert self.validator.validate_extension(existing_sequence, extension_cards)

    def test_sequence_extension_invalid_suit(self):
        """Test extending a sequence with a card of different suit."""
        # Original sequence: 5-6-7 of Hearts
        existing_sequence = Meld(
            cards=[Card(suit="Hearts", rank="5"), Card(suit="Hearts", rank="6"), Card(suit="Hearts", rank="7")],
            type="sequence",
        )

        # Add 8 of Spades (wrong suit)
        extension_cards = [Card(suit="Spades", rank="8")]

        assert not self.validator.validate_extension(existing_sequence, extension_cards)

    def test_sequence_extension_invalid_rank(self):
        """Test extending a sequence with a non-consecutive rank."""
        # Original sequence: 5-6-7 of Hearts
        existing_sequence = Meld(
            cards=[Card(suit="Hearts", rank="5"), Card(suit="Hearts", rank="6"), Card(suit="Hearts", rank="7")],
            type="sequence",
        )

        # Add 9 of Hearts (skipping 8)
        extension_cards = [Card(suit="Hearts", rank="9")]

        assert not self.validator.validate_extension(existing_sequence, extension_cards)

    def test_sequence_extension_invalid_ace_wrap(self):
        """Test sequence cannot wrap from King to Ace."""
        # Original sequence: J-Q-K of Hearts
        existing_sequence = Meld(
            cards=[Card(suit="Hearts", rank="J"), Card(suit="Hearts", rank="Q"), Card(suit="Hearts", rank="K")],
            type="sequence",
        )

        # Try to add Ace (invalid wrap-around)
        extension_cards = [Card(suit="Hearts", rank="A")]

        assert not self.validator.validate_extension(existing_sequence, extension_cards)

    def test_set_extension_valid(self):
        """Test extending a set with a new card."""
        # Original set: Q of Hearts, Spades, Clubs
        existing_set = Meld(
            cards=[Card(suit="Hearts", rank="Q"), Card(suit="Spades", rank="Q"), Card(suit="Clubs", rank="Q")],
            type="set",
        )

        # Add Q of Diamonds
        extension_cards = [Card(suit="Diamonds", rank="Q")]

        assert self.validator.validate_extension(existing_set, extension_cards)

    def test_set_extension_with_joker(self):
        """Test extending a set with a joker."""
        # Original set: Q of Hearts, Spades
        existing_set = Meld(cards=[Card(suit="Hearts", rank="Q"), Card(suit="Spades", rank="Q")], type="set")

        # Add joker (representing Q of another suit)
        extension_cards = [Card(suit="", rank="", is_joker=True)]

        assert self.validator.validate_extension(existing_set, extension_cards)

    def test_set_extension_invalid_rank(self):
        """Test extending a set with a card of different rank."""
        # Original set: Q of Hearts, Spades, Clubs
        existing_set = Meld(
            cards=[Card(suit="Hearts", rank="Q"), Card(suit="Spades", rank="Q"), Card(suit="Clubs", rank="Q")],
            type="set",
        )

        # Add K of Diamonds (wrong rank)
        extension_cards = [Card(suit="Diamonds", rank="K")]

        assert not self.validator.validate_extension(existing_set, extension_cards)

    def test_set_extension_invalid_duplicate_suit(self):
        """Test extending a set with a duplicate suit."""
        # Original set: Q of Hearts, Spades, Clubs
        existing_set = Meld(
            cards=[Card(suit="Hearts", rank="Q"), Card(suit="Spades", rank="Q"), Card(suit="Clubs", rank="Q")],
            type="set",
        )

        # Add Q of Hearts (duplicate suit)
        extension_cards = [Card(suit="Hearts", rank="Q")]

        assert not self.validator.validate_extension(existing_set, extension_cards)

    def test_set_extension_invalid_too_many_cards(self):
        """Test extending a set beyond 4 cards."""
        # Original set: Q of Hearts, Spades, Clubs, Diamonds (already full)
        existing_set = Meld(
            cards=[
                Card(suit="Hearts", rank="Q"),
                Card(suit="Spades", rank="Q"),
                Card(suit="Clubs", rank="Q"),
                Card(suit="Diamonds", rank="Q"),
            ],
            type="set",
        )

        # Try to add joker (would exceed 4 cards)
        extension_cards = [Card(suit="", rank="", is_joker=True)]

        assert not self.validator.validate_extension(existing_set, extension_cards)


if __name__ == "__main__":
    pytest.main([__file__])
