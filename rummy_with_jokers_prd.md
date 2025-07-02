# Product Requirements Document (PRD)  
## Rummy With Jokers – CLI Game

---

## Overview

This product is a terminal-based multiplayer **Rummy With Jokers** game following a custom ruleset. The game is designed for local use on a single machine, where players take turns using the same terminal. It provides a structured and rule-enforced way to play the game with friends or family without needing physical cards.

Refer to the Appendix 1 - Detailed Game Rules chapter to understand how the game is played and what are the rules that need to be implemented

### Problem It Solves
- Eliminates the need for physical cards.
- Ensures fair rule enforcement.
- Enables quick and organized gameplay without manual tracking or scorekeeping.

### Target Users
- Casual players familiar with Rummy.
- Families or friends wanting to play a local game on a shared screen.
- Developers or hobbyists interested in card game implementations.

---

## Core Features

### 1. Game Setup
- Allows 2–6 players.
- Shuffles and deals 13 cards to each player.
- Initializes draw and discard piles.

### 2. Turn Management
- Tracks rounds and player turns.
- Enforces rule: declarations allowed only after Round 4.
- Allows card drawing, reviewing hand, and discarding.

### 3. Declaration System
- Validates initial declarations:
  - Minimum 48 points.
  - At least one pure sequence.
- Tracks if a player has declared.
- Allows follow-up melds and extensions only after first declaration.

### 4. Meld Extension
- Enables adding to existing melds on the table.
- Validates extension rules (e.g., sequences must remain valid, no wrapping over Ace).

### 5. Game Closure
- Allows a player to end the game if all cards are declared/extended and one card is left to close.
- Automatically triggers scoring.

### 6. Scoring System
- Applies penalties for undeclared players.
- Counts values for remaining cards.
- Special handling for jokers in hand vs. melds.

---

## User Experience

### User Personas
- **Tomas (Experienced Rummy player)**: Wants automation and rule validation.
- **Anna (Casual player)**: Needs clear prompts and guidance.
- **Lukas (Techie friend)**: Curious about CLI and rule logic.

### Key User Flows
- Start a new game → Enter player names → Deal cards → Play turns → Declare/meld → Close game → View scores.

### UI/UX Considerations
- Clear prompts for actions (draw, declare, discard).
- Show hand in readable format (suit, rank).
- Hide other players’ hands.
- Use text-based menus for clarity.

---

## Technical Architecture

### System Components
- **CLI Interface**: Handles input/output.
- **Game Engine**: Enforces rules, turn logic.
- **Card Engine**: Manages deck, shuffling, drawing.
- **Validator**: Ensures meld legality and turn validity.
- **Score Tracker**: Stores round and player scores.

### Data Models
- `Card`: suit, rank, joker flag.
- `Player`: name, hand, has_declared flag.
- `Meld`: type, cards.
- `GameState`: players, draw pile, discard pile, round counter, melds on table.

### Tools & Dependencies
- **Language**: Python 3.13
- **Package Manager**: [`uv`](https://github.com/astral-sh/uv)
- **Suggested Libraries**:
  - `rich` (for colorful terminal UI)
  - `typer` or `argparse` (optional for CLI organization)

---

## Development Roadmap

### MVP (Minimum Viable Product)
- Core card and deck engine.
- Game setup and player management.
- Basic turn system (draw, discard).
- Initial declaration enforcement (48 points + pure sequence).
- Game closure and scoring.

### Phase 2: Feature Enhancements
- Meld extension across players.
- In-terminal score summary after each round.
- Invalid action guidance (e.g., trying to declare too early).
- History of melds on table.

### Phase 3: UX Improvements
- Animated text for shuffling.
- Hints for possible melds (optional).
- Save/load game state.

---

## Logical Dependency Chain

1. **Card and Deck Models** → core foundation.
2. **Turn and Round Tracker** → minimal play loop.
3. **Validation Engine** → for enforcing declarations.
4. **Meld Table and Extension Logic** → to support advanced rules.
5. **Scoring System** → activated on game close.
6. **Game Closure & Win Conditions** → finalize each round.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Handling complex meld validation | Start with basic checks, expand using test cases |
| CLI interaction overload | Use guided prompts and clean formatting (e.g. via `rich`) |
| Player confusion about when extensions are allowed | Add helpful messages and flags per player |
| Shared terminal awkwardness | Assume social honesty and show only relevant views per player |

---

## Appendix 1 - Detailed Game Rules

Below are the rules of the game:

### Objective
The objective of the game is to be the first player to get rid of all cards in hand by declaring valid melds or adding to existing melds on the table. Other players are penalized based on cards left in their hand when the game ends.

---

### Players
- **2 to 6 players**
- Each player plays individually.

---

### Deck Composition
- **Two standard 52-card decks** (104 cards) plus **4 printed Jokers** – total 108 cards.
- No wild jokers are used.

---

### Game Setup
1. Shuffle the full deck and deal **13 cards** to each player.
2. Place the remaining cards face down to form the **draw pile**.
3. Flip the top card of the draw pile to start the **discard pile**.
4. Randomly select a starting player.
5. Track rounds: one **round** is complete once every player has taken one turn.

---

### Gameplay Overview

#### Rounds 1–3
- **No declarations allowed**.
- On their turn, each player:
  1. Draws a card (from draw pile).
  2. Reviews hand.
  3. Discards a card.

> 🚫 Players **may not declare or extend melds** during these rounds.

---

### Turn Structure (From Round 4 Onward)
From the 4th round, players may start declaring or extending melds during their turn.

Each player’s turn consists of:

1. **Draw Phase**
   - Draw **one card** from:
     - Top of the **draw pile**, or
     - Top of the **discard pile**, **only if the drawn card is used in a declaration or extension during the same turn**.

2. **Action Phase**
   - One or more of the following:
     - **Initial Declaration** (only once per game per player)
     - **Additional Declarations**
     - **Extend existing melds** (only if player has already made their initial declaration)
     - **Close the game** (if playing final card)

3. **Discard Phase**
   - Discard **one card** unless player is **closing the game**, in which case they place the final card **face down** on the draw pile to indicate closure.

---

### Declarations

#### Initial Declaration
- Allowed only from **Round 4 onward**.
- Must meet all of the following:
  1. Melds must sum to **at least 48 points** (based on card values).
  2. Must include **at least one pure sequence** (no jokers).
  3. Melds may include sets and/or sequences.
  4. All melds must follow the rules below.

#### Subsequent Declarations
- After the initial declaration, players may:
  - Declare additional **valid melds**.
  - **Extend** existing melds on the table (including those declared by others), as long as:
    - The meld being extended is valid.
    - Extensions are **sequential and valid** (see below).
    - The player has made at least one declaration already.

---

### Valid Melds

#### Sequences
- **Pure Sequence**: At least 3 consecutive cards of the same suit, no jokers.
  - Example: 3♣–4♣–5♣
- **Impure Sequence**: At least 3 cards of the same suit, with jokers substituting missing cards.
  - Example: 8♦–JOKER–10♦ (Joker represents 9♦)

#### Sets
- 3 or 4 cards of the **same rank**, all of **different suits**.
- Can include jokers.
  - Example: Q♣–Q♦–JOKER

#### Meld Extension Rules
- A player may add cards to **any existing meld** on the table, once they’ve made their own initial declaration.
- **Extensions** must preserve sequence or set structure:
  - A sequence can be extended by adding next/previous cards in same suit.
    - Example: Meld = 7♦–8♦–9♦ → Can add 6♦ or 10♦
  - A set cannot be extended beyond 4 cards.
- No wrap-around over Aces:
  - You **cannot** add K♦ before A♦–2♦–3♦.
  - You **cannot** add 2♦ after Q♦–K♦–A♦.

---

### Jokers
- Only the 4 printed jokers are used.
- Jokers:
  - Can be used in **impure sequences** or **sets**.
  - Are **not allowed in pure sequences**.
  - Count as **0 points in melds**, but **10 points in hand** (if left unplayed when game ends).

---

### Closing the Game
- A player may **close** the game on their turn if:
  - They have **used all cards** in valid declarations or extensions.
  - They place their **final card face down** on the draw pile instead of discarding it.

---

### Scoring

#### At Game End
- Player who closed the game: **0 points**
- All other players:
  - **100 points** if they **haven’t made an initial declaration** yet.
  - **+50 points** per **joker left in hand** (only applies if no initial declaration).
  - If a player **has declared**, their score is the **sum of all card values remaining** in hand:
    - Number cards: face value
    - Face cards (A, K, Q, J): 10 points
    - Jokers: 10 points

#### Card Values
- 2–10: Face value
- J, Q, K, A: 10 points
- Joker:
  - In hand (undeclared): **10 points**
  - In melds: same value as the card it substitutes in the meld (example: in meld 8♦–JOKER–10♦ Joker represents 9♦ and thus has value of 9)

---

### Optional Rules
- Play multiple rounds; the player with **lowest cumulative score** wins.
- Optional bonuses for:
  - "Perfect finish" (declaring all melds in a single turn).
  - Having multiple pure sequences.
