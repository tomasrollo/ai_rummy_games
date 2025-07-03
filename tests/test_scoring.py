"""Unit tests for the scoring functionality."""

import pytest
from ai_rummy_games.models import Card, Meld, Player, GameState
from ai_rummy_games.scorer import Scorer


class TestScoring:
    """Test cases for the scoring functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scorer = Scorer()
        self.game_state = GameState()
        self.players = [
            Player(name="Player1"),
            Player(name="Player2"),
            Player(name="Player3"),
        ]
        for player in self.players:
            self.game_state.add_player(player)

    def test_calculate_hand_points(self):
        """Test point calculation for cards left in hand."""
        # Create a hand with mixed cards
        hand = [
            Card(suit="Hearts", rank="2"),  # 2 points
            Card(suit="Spades", rank="5"),  # 5 points
            Card(suit="Clubs", rank="K"),  # 10 points
            Card(suit="", rank="", is_joker=True),  # 10 points (joker in hand)
        ]

        # Calculate points
        points = self.scorer._calculate_hand_points(hand)

        # Expected: 2 + 5 + 10 + 10 = 27
        assert points == 27

    def test_winner_score(self):
        """Test that the winner (closer) gets 0 points."""
        # Set up players with cards
        self.players[0].add_card(Card(suit="Hearts", rank="K"))
        self.players[1].add_card(Card(suit="Hearts", rank="Q"))
        self.players[2].add_card(Card(suit="Hearts", rank="J"))

        # Mark players as having declared
        self.players[0].has_declared = True
        self.players[1].has_declared = True
        self.players[2].has_declared = True

        # Set player 1 as the winner/closer
        scores = self.scorer.calculate_scores(self.game_state, "Player1")

        assert scores["Player1"] == 0  # Winner gets 0 points
        assert scores["Player2"] == 10  # Player has a Q = 10 points
        assert scores["Player3"] == 10  # Player has a J = 10 points

    def test_undeclared_player_score(self):
        """Test that undeclared players get penalty scores."""
        # Set up players
        self.players[0].has_declared = True
        self.players[1].has_declared = False  # Undeclared player
        self.players[2].has_declared = True

        # Add cards to players' hands
        self.players[1].add_card(Card(suit="Hearts", rank="2"))
        self.players[1].add_card(Card(suit="", rank="", is_joker=True))  # Joker

        # Calculate scores (Player3 is the closer)
        scores = self.scorer.calculate_scores(self.game_state, "Player3")

        # Player1 has no cards = 0 points
        assert scores["Player1"] == 0

        # Player2 is undeclared = 100 + 50 (one joker) = 150 points
        assert scores["Player2"] == 150

        # Player3 is the closer = 0 points
        assert scores["Player3"] == 0

    def test_joker_points_in_hand(self):
        """Test scoring jokers left in hand."""
        # Set up players
        self.players[0].has_declared = True
        self.players[1].has_declared = True

        # Add cards with jokers
        joker1 = Card(suit="", rank="", is_joker=True)
        joker2 = Card(suit="", rank="", is_joker=True)

        self.players[0].add_card(joker1)
        self.players[0].add_card(Card(suit="Hearts", rank="2"))

        self.players[1].add_card(joker2)

        # Calculate scores (Player2 is the closer)
        scores = self.scorer.calculate_scores(self.game_state, "Player2")

        # Player1: 1 joker (10 pts) + 1 card (2 pts) = 12 points
        assert scores["Player1"] == 12

        # Player2 is the closer = 0 points
        assert scores["Player2"] == 0

    def test_game_state_close_method(self):
        """Test the game closure functionality in GameState."""
        # Setup
        player1 = self.players[0]
        player1.has_declared = True

        # Player 1 has no cards left
        result = self.game_state.close_game(player1.name)

        # Verify game closure was successful
        assert result is True
        assert self.game_state.is_game_closed is True
        assert self.game_state.closer_name == player1.name
        assert player1.name in self.game_state.scores
        assert self.game_state.scores[player1.name] == 0

    def test_can_player_close(self):
        """Test the can_player_close method."""
        # Player must have declared and have 0 or 1 card left

        # Player1: declared, no cards
        self.players[0].has_declared = True

        # Player2: declared, 2 cards
        self.players[1].has_declared = True
        self.players[1].add_card(Card(suit="Hearts", rank="2"))
        self.players[1].add_card(Card(suit="Hearts", rank="3"))

        # Player3: not declared, 1 card
        self.players[2].has_declared = False
        self.players[2].add_card(Card(suit="Hearts", rank="4"))

        # Verify
        assert self.game_state.can_player_close(self.players[0]) is True  # Can close
        assert self.game_state.can_player_close(self.players[1]) is False  # Too many cards
        assert self.game_state.can_player_close(self.players[2]) is False  # Not declared


if __name__ == "__main__":
    pytest.main([__file__])
