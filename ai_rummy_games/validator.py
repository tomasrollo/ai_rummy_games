"""Declaration validation logic for AI Rummy Games."""

from typing import List, Tuple, Dict, Set
from .models import Card, Meld


class Validator:
    """Handles validation of initial declarations and meld formations."""

    # Point values for cards
    CARD_POINTS = {
        "A": 10,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "J": 10,
        "Q": 10,
        "K": 10,
    }
    JOKER_POINTS = 20
    MINIMUM_DECLARATION_POINTS = 48

    def __init__(self):
        """Initialize the validator."""
        pass

    def validate_initial_declaration(self, player_hand: List[Card], melds: List[Meld]) -> bool:
        """
        Validate an initial declaration attempt.

        Args:
            player_hand: The player's current hand
            melds: List of melds the player wants to declare

        Returns:
            bool: True if declaration is valid, False otherwise
        """
        # Check if all cards in melds are from player's hand
        if not self._cards_available_in_hand(player_hand, melds):
            return False

        # Check minimum point requirement
        total_points = self._calculate_meld_points(melds)
        if total_points < self.MINIMUM_DECLARATION_POINTS:
            return False

        # Check for at least one pure sequence
        if not self._has_pure_sequence(melds):
            return False

        # Validate each individual meld
        for meld in melds:
            if not self._validate_meld(meld):
                return False

        return True

    def _cards_available_in_hand(self, player_hand: List[Card], melds: List[Meld]) -> bool:
        """Check if all cards in melds are available in the player's hand."""
        # Create a copy of the hand to track card usage
        hand_copy = player_hand.copy()

        for meld in melds:
            for card in meld.cards:
                try:
                    hand_copy.remove(card)
                except ValueError:
                    return False
        return True

    def _calculate_meld_points(self, melds: List[Meld]) -> int:
        """Calculate total points for all melds."""
        total_points = 0
        for meld in melds:
            total_points += self._calculate_single_meld_points(meld)
        return total_points

    def _calculate_single_meld_points(self, meld: Meld) -> int:
        """Calculate points for a single meld."""
        points = 0
        for card in meld.cards:
            if card.is_joker:
                points += self.JOKER_POINTS
            else:
                points += self.CARD_POINTS.get(card.rank, 0)
        return points

    def _has_pure_sequence(self, melds: List[Meld]) -> bool:
        """Check if there's at least one pure sequence among the melds."""
        for meld in melds:
            if self._is_pure_sequence(meld):
                return True
        return False

    def _is_pure_sequence(self, meld: Meld) -> bool:
        """Check if a meld is a pure sequence (no jokers)."""
        if meld.type != "sequence":
            return False

        # Check that no jokers are used
        for card in meld.cards:
            if card.is_joker:
                return False

        return self._is_valid_sequence(meld.cards)

    def _validate_meld(self, meld: Meld) -> bool:
        """Validate a single meld according to rummy rules."""
        if meld.type == "set":
            return self._is_valid_set(meld.cards)
        elif meld.type == "sequence":
            return self._is_valid_sequence(meld.cards)
        return False

    def _is_valid_set(self, cards: List[Card]) -> bool:
        """Check if cards form a valid set (same rank, different suits)."""
        if len(cards) < 3:
            return False

        # Get the base rank (excluding jokers)
        base_rank = None
        suits_used = set()
        joker_count = 0

        for card in cards:
            if card.is_joker:
                joker_count += 1
            else:
                if base_rank is None:
                    base_rank = card.rank
                elif card.rank != base_rank:
                    return False

                if card.suit in suits_used:
                    return False  # Duplicate suit
                suits_used.add(card.suit)

        # Check if we have too many jokers
        max_possible_suits = 4  # Hearts, Diamonds, Clubs, Spades
        available_suits = max_possible_suits - len(suits_used)

        return joker_count <= available_suits

    def _is_valid_sequence(self, cards: List[Card]) -> bool:
        """Check if cards form a valid sequence (consecutive ranks, same suit)."""
        if len(cards) < 3:
            return False

        # Separate jokers from regular cards
        regular_cards = [card for card in cards if not card.is_joker]
        joker_count = len(cards) - len(regular_cards)

        if not regular_cards:
            return False  # Can't have a sequence of only jokers

        # Check all regular cards are same suit
        suit = regular_cards[0].suit
        for card in regular_cards:
            if card.suit != suit:
                return False

        # Special case: handle QKA as a valid sequence
        ace_king_queen = sorted([c.rank for c in regular_cards]) == ["A", "K", "Q"]
        if ace_king_queen:
            return True

        # Sort regular cards by rank value
        rank_values = self._get_rank_values(regular_cards)
        rank_values.sort()

        # Check if jokers can fill gaps to make consecutive sequence
        return self._can_form_sequence_with_jokers(rank_values, joker_count)

    def _get_rank_values(self, cards: List[Card]) -> List[int]:
        """Convert card ranks to numerical values for sequence checking."""
        rank_to_value = {
            "A": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
        }
        return [rank_to_value[card.rank] for card in cards]

    def _can_form_sequence_with_jokers(self, sorted_ranks: List[int], joker_count: int) -> bool:
        """Check if sorted ranks can form a sequence with available jokers."""
        if not sorted_ranks:
            return False

        # Remove duplicates while preserving order
        unique_ranks = []
        for rank in sorted_ranks:
            if rank not in unique_ranks:
                unique_ranks.append(rank)
            else:
                return False  # Duplicate ranks not allowed in sequence

        # Calculate gaps that need to be filled
        gaps_needed = 0
        for i in range(1, len(unique_ranks)):
            gap = unique_ranks[i] - unique_ranks[i - 1] - 1
            gaps_needed += gap

        return gaps_needed <= joker_count

    def validate_extension(self, existing_meld: Meld, added_cards: List[Card]) -> bool:
        """
        Validate extension of an existing meld with new cards.

        Args:
            existing_meld: The meld already on the table
            added_cards: New cards to add to the meld

        Returns:
            bool: True if the extension is valid, False otherwise
        """
        if existing_meld.type == "sequence":
            return self._validate_sequence_extension(existing_meld.cards, added_cards)
        elif existing_meld.type == "set":
            return self._validate_set_extension(existing_meld.cards, added_cards)
        return False

    def validate_new_meld(self, cards: List[Card], meld_type: str) -> bool:
        """
        Validate if a new meld formation is valid according to the rules.

        Args:
            cards: Cards to form the new meld
            meld_type: Type of meld ("sequence" or "set")

        Returns:
            bool: True if the meld is valid, False otherwise
        """
        # Create temporary meld for validation
        temp_meld = Meld(cards=cards, type=meld_type)
        return self._validate_meld(temp_meld)

    def _validate_sequence_extension(self, existing_cards: List[Card], added_cards: List[Card]) -> bool:
        """
        Validate extension of an existing sequence.

        Args:
            existing_cards: Cards already in the sequence
            added_cards: New cards to add to the sequence

        Returns:
            bool: True if extension is valid, False otherwise
        """
        if not added_cards:
            return False

        # Get suit from the existing sequence
        regular_cards = [card for card in existing_cards if not card.is_joker]
        if not regular_cards:
            return False

        sequence_suit = regular_cards[0].suit

        # Check if all added cards match the suit or are jokers
        for card in added_cards:
            if not card.is_joker and card.suit != sequence_suit:
                return False

        # Combine cards and check if they form a valid sequence
        combined_cards = existing_cards + added_cards
        return self._is_valid_sequence(combined_cards)

    def _validate_set_extension(self, existing_cards: List[Card], added_cards: List[Card]) -> bool:
        """
        Validate extension of an existing set.

        Args:
            existing_cards: Cards already in the set
            added_cards: New cards to add to the set

        Returns:
            bool: True if extension is valid, False otherwise
        """
        if not added_cards:
            return False

        # Check if the combined set would exceed 4 cards (maximum in a set)
        if len(existing_cards) + len(added_cards) > 4:
            return False

        # Get rank from the existing set (excluding jokers)
        regular_cards = [card for card in existing_cards if not card.is_joker]
        if not regular_cards:
            return False

        set_rank = regular_cards[0].rank

        # Check if all added cards match the rank or are jokers
        for card in added_cards:
            if not card.is_joker and card.rank != set_rank:
                return False

        # Combine cards and check for duplicate suits (non-joker)
        suits_used = set()
        for card in existing_cards + added_cards:
            if not card.is_joker:
                if card.suit in suits_used:
                    return False
                suits_used.add(card.suit)

        return True
