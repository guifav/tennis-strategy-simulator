# Tennis Strategy Simulator

## Overview

The Tennis Strategy Simulator is an interactive turn-based tennis game that allows players to make strategic shot decisions based on their skills, opponent characteristics, and match situation. This simulator focuses on the tactical aspect of tennis, helping players understand how different shots affect rally dynamics.

## Features

- **Complete Tennis Scoring System**: Points, games, sets with proper deuce and advantage rules
- **Visual Court Representation**: ASCII visualization showing player positions and ball movement
- **Strategic Shot Selection**: Various shot types including serves, groundstrokes, and specialty shots
- **Realistic Player Movement**: Players' court positions change based on shot selection
- **Dynamic Opponent AI**: Computer opponent with different playing styles and tendencies
- **Fatigue System**: Longer rallies increase player fatigue, affecting shot success rates
- **Two-Serve System**: First and second serves with different risk/reward profiles

## How to Play

1. **Start a Match**: Click "New Match" to begin playing against a randomly generated opponent
2. **Serving**: Select "First Serve" when it's your turn to serve
3. **Shot Selection**: Choose from various shots during rallies:
   - Ground strokes: Forehand/Backhand Cross-court or Down-the-line
   - Special shots: Drop Shot, Lob, Slice, Approach Shot, Volley
4. **Continue Rally**: Click "Continue Rally" when it's the opponent's turn
5. **Watch the Court**: Observe how player positions (P = Player, O = Opponent) change based on shots
6. **Track Scoring**: Game follows standard tennis scoring with points, games, and sets

## Tactical Tips

- **Use the Right Shot for the Situation**: 
  - Cross-court shots are safer but less aggressive
  - Down-the-line shots are riskier but more likely to be winners
  - Drop shots are effective when the opponent is at the baseline
  - Lobs work well against opponents at the net

- **Consider Your Strengths**: Your player has particular strengths (great forehand, good drop shot) that affect shot success rates

- **Manage Fatigue**: Long rallies increase fatigue, affecting your shot accuracy

- **Read Your Opponent**: Each opponent has different tendencies and strengths that influence their shot selection

## Technical Requirements

- Python 3.7+
- Gradio 3.50.2+
- NumPy 1.24.0+

## Installation

```bash
# Clone the repository
git clone https://github.com/guifav/tennis-strategy-simulator.git
cd tennis-strategy-simulator

# Install required packages
pip install -r requirements.txt

# Run the simulator
python app.py
```

## Contributing

Contributions are welcome! Some potential areas for improvement:

- Enhanced graphics or visual representation
- Additional shot types
- More sophisticated AI behavior
- Statistical tracking of matches
- Multiplayer support

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by real tennis strategy and tactics
- Thanks to the Gradio team for their excellent UI framework

---

Enjoy playing and developing your tennis strategy!

---

Developer: wwww.guilhermefavaron.com.br