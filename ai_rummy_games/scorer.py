"""Scoring logic for AI Rummy Games."""

from typing import Dict, List, Tuple
from .models import Player, Card, Meld, GameState


class Scorer:
    """Handles scoring calculations for game closure."""

    # Point values for cards (same as in Validator for consistency)
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

    # Constants for scoring
    UNDECLARED_PENALTY = 100
    JOKER_PENALTY = 50  # Additional penalty per joker for undeclared players
    JOKER_POINTS = 10  # Points for joker left in hand for declared players

    def __init__(self):
        """Initialize the scorer."""
        pass

    def calculate_scores(self, game_state: GameState, closer_name: str) -> Dict[str, int]:
        """
        Calculate final scores when a player closes the game.

        Args:
            game_state: Current game state
            closer_name: Name of the player who closed the game

        Returns:
            Dictionary mapping player names to their scores
        """
        scores = {}

        # The player who closed the game gets 0 points
        scores[closer_name] = 0

        # Calculate scores for other players
        for player in game_state.players:
            if player.name == closer_name:
                continue

            # Non-declared players get 100 points + 50 points per joker
            if not player.has_declared:
                joker_count = sum(1 for card in player.hand if card.is_joker)
                scores[player.name] = self.UNDECLARED_PENALTY + (self.JOKER_PENALTY * joker_count)
            else:
                # Declared players get points based on card values left in hand
                scores[player.name] = self._calculate_hand_points(player.hand)

        return scores

    def _calculate_hand_points(self, cards: List[Card]) -> int:
        """
        Calculate points for cards left in hand.

        Args:
            cards: List of cards to calculate points for

        Returns:
            Total points for the cards
        """
        total_points = 0

        for card in cards:
            if card.is_joker:
                total_points += self.JOKER_POINTS
            else:
                total_points += self.CARD_POINTS.get(card.rank, 0)

        return total_points

    def get_joker_substitution_value(self, joker: Card, meld: Meld) -> int:
        """
        Determine the value of a joker based on what card it substitutes in a meld.

        Args:
            joker: The joker card
            meld: The meld containing the joker

        Returns:
            Point value for the joker in this meld
        """
        if not joker.is_joker or joker not in meld.cards:
            return self.JOKER_POINTS

        if meld.type == "set":
            # In a set, joker substitutes a card of the same rank as others
            non_jokers = [card for card in meld.cards if not card.is_joker]
            if non_jokers:
                return self.CARD_POINTS.get(non_jokers[0].rank, 0)

        elif meld.type == "sequence":
            # In a sequence, we need to determine what position the joker is in
            non_jokers = [card for card in meld.cards if not card.is_joker]
            if len(non_jokers) < 2:
                return 0  # Can't determine without at least 2 regular cards

            # Sort non-jokers by rank value
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
            sorted_cards = sorted(non_jokers, key=lambda c: rank_to_value.get(c.rank, 0))

            # Check if joker is at the beginning, middle, or end
            joker_index = meld.cards.index(joker)
            if joker_index == 0:
                # At beginning, value is one less than the first non-joker
                first_value = rank_to_value.get(sorted_cards[0].rank, 0)
                return self.CARD_POINTS.get(sorted_cards[0].rank, 0) if first_value > 1 else 10  # A=10 points
            elif joker_index == len(meld.cards) - 1:
                # At end, value is one more than the last non-joker
                last_value = rank_to_value.get(sorted_cards[-1].rank, 0)
                rank_value = last_value + 1
                if rank_value > 13:  # Beyond King
                    return 10  # Assume Ace value
                for rank, value in rank_to_value.items():
                    if value == rank_value:
                        return self.CARD_POINTS.get(rank, 0)
            else:
                # In middle, try to determine the missing rank
                for i, card in enumerate(sorted_cards):
                    if i > 0 and rank_to_value.get(card.rank, 0) - rank_to_value.get(sorted_cards[i - 1].rank, 0) > 1:
                        # Found a gap between consecutive cards
                        missing_value = rank_to_value.get(sorted_cards[i - 1].rank, 0) + 1
                        for rank, value in rank_to_value.items():
                            if value == missing_value:
                                return self.CARD_POINTS.get(rank, 0)

        # Default if can't determine
        return self.JOKER_POINTS
