# AI Rummy Games

A terminal-based multiplayer Rummy With Jokers card game using custom rules.

## Features

- **Multiplayer Support**: Play with 2-6 players on the same machine
- **Complete Rule Enforcement**: Game validates declarations, melds, and scoring
- **Rich Terminal UI**: Colorful interface with suit pictograms (♠, ♣, ♦, ♥)
- **Full Game Flow**: From game setup to scoring and winner determination

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai_rummy_games.git
cd ai_rummy_games

# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package and dependencies
pip install -e .
```

## Usage

Start the game:

```bash
python main.py start
```

Run the demo:

```bash
python main.py demo
```

## Game Rules

See the full game rules in [rummy_with_jokers_prd.md](rummy_with_jokers_prd.md).

### Basic Flow

1. Each player gets 13 cards
2. Take turns drawing and discarding cards
3. Create melds (sets or sequences) with at least 48 points and one pure sequence
4. Extend existing melds
5. Close the game when you're down to your last card
6. Lowest score wins!

## Card Display

Cards are displayed using their rank and suit symbol:
- Spades: ♠ (black)
- Clubs: ♣ (black)
- Hearts: ♥ (red)
- Diamonds: ♦ (red)

For example, Ace of Spades is displayed as "A♠", Ten of Hearts as "10♥".

## Development

### Running Tests

```bash
pytest
```

### Project Structure

- `ai_rummy_games/` - Core game logic
  - `models.py` - Card, Deck, Player, and GameState classes
  - `validator.py` - Rules validation logic
  - `scorer.py` - Scoring system
- `main.py` - CLI interface using Typer and Rich
- `tests/` - Unit and integration tests

## Terminal Compatibility

The suit pictograms (♠, ♣, ♦, ♥) should display correctly in most modern terminals. If you experience issues with symbol rendering, try:

1. Ensuring your terminal supports UTF-8
2. Using a font that includes card suit symbols
3. Updating to the latest terminal version

## License

[MIT License](LICENSE)
