"""Card and Deck models for the AI Rummy Games."""

from dataclasses import dataclass, field
from typing import List, Optional, Literal, Dict, Any, Tuple
import random


@dataclass
class Card:
    """Represents a playing card with suit, rank, and joker status.

    Cards are displayed with pictogram symbols for suits:
    - Spades: ♠
    - Clubs: ♣
    - Diamonds: ♦
    - Hearts: ♥

    Example string representation: "A♠" (Ace of Spades), "10♥" (Ten of Hearts)
    """

    suit: str
    rank: str
    is_joker: bool = False

    # Suit pictogram mapping (Unicode symbols for standard playing card suits)
    # These symbols should render correctly in all modern UTF-8 compatible terminals
    SUIT_SYMBOLS = {
        "Spades": "♠",  # U+2660 BLACK SPADE SUIT
        "Clubs": "♣",  # U+2663 BLACK CLUB SUIT
        "Diamonds": "♦",  # U+2666 BLACK DIAMOND SUIT
        "Hearts": "♥",  # U+2665 BLACK HEART SUIT
    }

    def __str__(self) -> str:
        """String representation of the card."""
        if self.is_joker:
            return "Joker"
        # Use pictogram for suit if available, otherwise use the original suit name
        suit_symbol = self.SUIT_SYMBOLS.get(self.suit, self.suit)
        return f"{self.rank}{suit_symbol}"

    def __repr__(self) -> str:
        """Detailed representation of the card."""
        return f"Card(suit='{self.suit}', rank='{self.rank}', is_joker={self.is_joker})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary for serialization."""
        return {"suit": self.suit, "rank": self.rank, "is_joker": self.is_joker}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Card":
        """Create Card instance from dictionary."""
        return cls(suit=data["suit"], rank=data["rank"], is_joker=data["is_joker"])


class Deck:
    """Represents a deck of cards for Rummy with two standard decks plus jokers.

    While suits are stored as string names internally, they are displayed
    using Unicode pictogram symbols (♥, ♦, ♣, ♠) in the user interface.
    """

    # Use suit names for internal representation, but display as pictograms
    SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
    # Suit pictograms in display: Hearts (♥), Diamonds (♦), Clubs (♣), Spades (♠)
    RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    def __init__(self):
        """Initialize a deck with 108 cards: two standard decks + 4 jokers."""
        self.draw_pile: List[Card] = []
        self.discard_pile: List[Card] = []
        self._build_deck()

    def _build_deck(self):
        """Build the complete deck with 108 cards."""
        # Add two standard decks (52 cards each = 104 cards)
        for _ in range(2):
            for suit in self.SUITS:
                for rank in self.RANKS:
                    self.draw_pile.append(Card(suit=suit, rank=rank))

        # Add 4 printed jokers
        for _ in range(4):
            self.draw_pile.append(Card(suit="", rank="", is_joker=True))

    def shuffle(self):
        """Shuffle the draw pile using random.shuffle."""
        random.shuffle(self.draw_pile)

    def draw(self) -> Optional[Card]:
        """Draw a card from the draw pile.

        Returns:
            Card if available, None if draw pile is empty.
        """
        if not self.draw_pile:
            return None
        return self.draw_pile.pop()

    def discard(self, card: Card):
        """Add a card to the discard pile.

        Args:
            card: The card to discard.
        """
        self.discard_pile.append(card)

    def cards_remaining(self) -> int:
        """Get the number of cards remaining in the draw pile."""
        return len(self.draw_pile)

    def discard_pile_size(self) -> int:
        """Get the number of cards in the discard pile."""
        return len(self.discard_pile)

    def peek_top_discard(self) -> Optional[Card]:
        """Peek at the top card of the discard pile without removing it.

        Returns:
            Top card of discard pile if available, None if empty.
        """
        if not self.discard_pile:
            return None
        return self.discard_pile[-1]


@dataclass
class Player:
    """Represents a player in the Rummy game."""

    name: str
    hand: List[Card] = field(default_factory=list)
    has_declared: bool = False
    score: int = 0  # Added score field for tracking

    def add_card(self, card: Card) -> None:
        """Add a card to the player's hand.

        Args:
            card: The card to add to the hand.
        """
        self.hand.append(card)

    def remove_card(self, card: Card) -> None:
        """Remove a card from the player's hand.

        Args:
            card: The card to remove from the hand.

        Raises:
            ValueError: If the card is not in the player's hand.
        """
        try:
            self.hand.remove(card)
        except ValueError:
            raise ValueError(f"Card {card} not found in {self.name}'s hand")

    def declare(self) -> None:
        """Set the player's declaration status to True."""
        self.has_declared = True

    def add_score(self, points: int) -> None:
        """Add points to player's score.

        Args:
            points: The points to add to the player's score.
        """
        self.score += points

    def hand_size(self) -> int:
        """Get the number of cards in the player's hand."""
        return len(self.hand)

    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for serialization."""
        return {"name": self.name, "hand": [card.to_dict() for card in self.hand], "has_declared": self.has_declared}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """Create Player instance from dictionary."""
        player = cls(name=data["name"], has_declared=data["has_declared"])
        player.hand = [Card.from_dict(card_data) for card_data in data["hand"]]
        return player


@dataclass
class Meld:
    """Represents a meld (sequence or set) of cards."""

    cards: List[Card] = field(default_factory=list)
    type: Literal["sequence", "set"] = "set"

    def is_valid(self) -> bool:
        """Check if the meld is valid according to Rummy rules.

        Returns:
            True if meld is valid, False otherwise.
        """
        if len(self.cards) < 3:
            return False

        if self.type == "set":
            return self._is_valid_set()
        elif self.type == "sequence":
            return self._is_valid_sequence()

        return False

    def _is_valid_set(self) -> bool:
        """Check if cards form a valid set (same rank, different suits)."""
        # All cards must have the same rank
        if not self.cards:
            return False

        # Get the rank of the first non-joker card
        base_rank = None
        for card in self.cards:
            if not card.is_joker:
                base_rank = card.rank
                break

        if base_rank is None:
            # All jokers - valid set
            return True

        # Check all non-joker cards have the same rank
        suits_used = set()
        for card in self.cards:
            if not card.is_joker:
                if card.rank != base_rank:
                    return False
                if card.suit in suits_used:
                    return False  # Duplicate suit
                suits_used.add(card.suit)

        return True

    def _is_valid_sequence(self) -> bool:
        """Check if cards form a valid sequence (consecutive ranks, same suit)."""
        if not self.cards:
            return False

        # Get the suit from the first non-joker card
        base_suit = None
        for card in self.cards:
            if not card.is_joker:
                base_suit = card.suit
                break

        if base_suit is None:
            # All jokers - not a valid sequence without knowing the intended suit
            return False

        # Check all non-joker cards have the same suit
        for card in self.cards:
            if not card.is_joker and card.suit != base_suit:
                return False

        # Sort cards by rank and check for consecutive sequence
        rank_values = {
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

        # Get positions of non-joker cards
        non_joker_positions = []
        for i, card in enumerate(self.cards):
            if not card.is_joker:
                non_joker_positions.append((i, rank_values[card.rank]))

        if len(non_joker_positions) < 2:
            # Need at least 2 non-joker cards to determine sequence
            return len(self.cards) >= 3  # Assume jokers fill gaps

        # Sort by position and check if ranks can form a sequence
        non_joker_positions.sort()
        for i in range(1, len(non_joker_positions)):
            pos_diff = non_joker_positions[i][0] - non_joker_positions[i - 1][0]
            rank_diff = non_joker_positions[i][1] - non_joker_positions[i - 1][1]
            if rank_diff != pos_diff:
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert meld to dictionary for serialization."""
        return {"type": self.type, "cards": [card.to_dict() for card in self.cards]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Meld":
        """Create Meld instance from dictionary."""
        meld = cls(type=data["type"])
        meld.cards = [Card.from_dict(card_data) for card_data in data["cards"]]
        return meld


@dataclass
class GameState:
    """Represents the current state of a Rummy game."""

    players: List[Player] = field(default_factory=list)
    draw_pile: List[Card] = field(default_factory=list)
    discard_pile: List[Card] = field(default_factory=list)
    melds_on_table: List[Meld] = field(default_factory=list)
    current_round: int = 1
    current_player_index: int = 0
    is_game_closed: bool = False
    closer_name: Optional[str] = None
    scores: Dict[str, int] = field(default_factory=dict)

    def add_player(self, player: Player) -> None:
        """Add a player to the game.

        Args:
            player: The player to add.
        """
        self.players.append(player)

    def remove_player(self, player_name: str) -> None:
        """Remove a player from the game by name.

        Args:
            player_name: The name of the player to remove.

        Raises:
            ValueError: If player is not found.
        """
        for i, player in enumerate(self.players):
            if player.name == player_name:
                self.players.pop(i)
                # Adjust current_player_index if necessary
                if self.current_player_index >= len(self.players) and self.players:
                    self.current_player_index = 0
                elif self.current_player_index > i:
                    self.current_player_index -= 1
                return

        raise ValueError(f"Player '{player_name}' not found")

    def next_turn(self) -> None:
        """Advance to the next player's turn."""
        if not self.players:
            return

        self.current_player_index += 1
        if self.current_player_index >= len(self.players):
            self.current_player_index = 0
            self.current_round += 1

    def current_player(self) -> Optional[Player]:
        """Get the current player.

        Returns:
            Current player or None if no players.
        """
        if not self.players or self.current_player_index >= len(self.players):
            return None
        return self.players[self.current_player_index]

    def add_meld_to_table(self, meld: Meld) -> None:
        """Add a meld to the table.

        Args:
            meld: The meld to add to the table.
        """
        self.melds_on_table.append(meld)

    def validate_and_process_declaration(self, player_name: str, melds: List[Meld]) -> bool:
        """
        Validate a player's initial declaration and process it if valid.

        Args:
            player_name: Name of the player making the declaration
            melds: List of melds the player wants to declare

        Returns:
            bool: True if declaration was valid and processed, False otherwise
        """
        # Import here to avoid circular imports
        from .validator import Validator

        # Find the player
        player = None
        for p in self.players:
            if p.name == player_name:
                player = p
                break

        if not player:
            raise ValueError(f"Player '{player_name}' not found")

        if player.has_declared:
            return False  # Player has already declared

        # Validate the declaration
        validator = Validator()
        if not validator.validate_initial_declaration(player.hand, melds):
            return False

        # Process the valid declaration
        player.declare()

        # Remove meld cards from player's hand
        for meld in melds:
            for card in meld.cards:
                player.remove_card(card)

        # Add melds to the table
        for meld in melds:
            self.add_meld_to_table(meld)

        return True

    def close_game(self, player_name: str) -> bool:
        """
        Close the game when a player has used all cards.

        Args:
            player_name: Name of the player closing the game

        Returns:
            bool: True if game was closed successfully, False otherwise
        """
        # Find the player
        player = None
        for p in self.players:
            if p.name == player_name:
                player = p
                break

        if not player:
            raise ValueError(f"Player '{player_name}' not found")

        # Verify player has no cards left in hand
        if player.hand_size() > 0:
            return False

        # Import here to avoid circular imports
        from .scorer import Scorer

        # Close the game and calculate scores
        self.is_game_closed = True
        self.closer_name = player_name

        # Calculate scores
        scorer = Scorer()
        self.scores = scorer.calculate_scores(self, player_name)

        # Update player scores
        for p in self.players:
            p.add_score(self.scores.get(p.name, 0))

        return True

    def can_player_close(self, player: Player) -> bool:
        """
        Check if a player can close the game.

        Args:
            player: The player to check

        Returns:
            bool: True if player can close the game
        """
        # Player must have declared and have only one card left to be able to close
        return player.has_declared and player.hand_size() <= 1

    def end_game(self) -> None:
        """End the game and determine the winner."""
        if self.is_game_closed:
            return

        self.is_game_closed = True

        # Calculate scores based on remaining cards
        for player in self.players:
            # Example scoring: 10 points for each card remaining
            player.add_score(len(player.hand) * 10)

    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for serialization."""
        return {
            "players": [player.to_dict() for player in self.players],
            "draw_pile": [card.to_dict() for card in self.draw_pile],
            "discard_pile": [card.to_dict() for card in self.discard_pile],
            "melds_on_table": [meld.to_dict() for meld in self.melds_on_table],
            "current_round": self.current_round,
            "current_player_index": self.current_player_index,
            "is_game_closed": self.is_game_closed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        """Create GameState instance from dictionary."""
        game_state = cls(current_round=data["current_round"], current_player_index=data["current_player_index"])
        game_state.players = [Player.from_dict(player_data) for player_data in data["players"]]
        game_state.draw_pile = [Card.from_dict(card_data) for card_data in data["draw_pile"]]
        game_state.discard_pile = [Card.from_dict(card_data) for card_data in data["discard_pile"]]
        game_state.melds_on_table = [Meld.from_dict(meld_data) for meld_data in data["melds_on_table"]]
        return game_state
