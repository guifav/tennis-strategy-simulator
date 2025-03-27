import gradio as gr
import random
import numpy as np

# Constants for shot types and positions
SHOT_TYPES = {
    # Ground Strokes
    "Forehand Cross-court": {"risk": 0.1, "base_success": 0.75},
    "Forehand Down-the-line": {"risk": 0.2, "base_success": 0.65},
    "Backhand Cross-court": {"risk": 0.15, "base_success": 0.7},
    "Backhand Down-the-line": {"risk": 0.25, "base_success": 0.6},
    
    # Special Shots
    "Drop Shot": {"risk": 0.35, "base_success": 0.55},
    "Lob": {"risk": 0.3, "base_success": 0.6},
    "Slice": {"risk": 0.15, "base_success": 0.7},
    
    # Net Play
    "Approach Shot": {"risk": 0.25, "base_success": 0.65},
    "Volley": {"risk": 0.2, "base_success": 0.7},
    
    # Serves
    "First Serve": {"risk": 0.25, "base_success": 0.65, "ace_chance": 0.15},
    "Second Serve": {"risk": 0.1, "base_success": 0.85, "ace_chance": 0.05}
}

PLAYER_POSITIONS = ["Baseline", "Mid-court", "Net"]
COURT_POSITIONS = ["Center", "Forehand Side", "Backhand Side"]

TENDENCY_TYPES = [
    "Aggressive Baseliner",
    "Defensive Baseliner",
    "Serve-and-Volleyer",
    "All-Court Player",
    "Forehand Dominant",
    "Backhand Dominant"
]

class Player:
    def __init__(self, is_user=False):
        self.is_user = is_user
        if is_user:
            # Fixed profile for user
            self.profile = {
                "Serve": 5,  # Average (scale 1-10)
                "Forehand": 8,  # Great
                "Backhand": 5,  # Average
                "Volley": 3,  # Bad
                "Drop Shot": 7,  # Good
                "Lob": 5,  # Average
                "Movement/Endurance": 5  # Average
            }
        else:
            # Randomly generated profile for AI opponent
            self.profile = self.generate_random_profile()
            self.tendency = random.choice(TENDENCY_TYPES)
            
        self.position = "Baseline"  # Starting position
        self.court_position = "Center"  # Starting court position
        self.fatigue = 0  # Starting fatigue level for the player
        self.max_fatigue = 100
        
    def generate_random_profile(self):
        """Generate a random skill profile for the AI opponent"""
        return {
            "Serve": random.randint(3, 9),
            "Forehand": random.randint(3, 9),
            "Backhand": random.randint(3, 9),
            "Volley": random.randint(3, 9),
            "Drop Shot": random.randint(3, 9),
            "Lob": random.randint(3, 9),
            "Movement/Endurance": random.randint(3, 9)
        }
    
    def profile_to_string(self):
        """Convert the profile to a readable string"""
        if self.is_user:
            return "Your Profile:\nServe: Average\nForehand: Great\nBackhand: Average\nVolley: Bad\nDrop Shot: Good\nMovement/Endurance: Average"
        else:
            skill_terms = {
                1: "Very Poor", 2: "Poor", 3: "Below Average", 
                4: "Slightly Below Average", 5: "Average", 
                6: "Slightly Above Average", 7: "Above Average", 
                8: "Good", 9: "Excellent", 10: "Outstanding"
            }
            
            profile_str = f"Opponent Profile (Tendency: {self.tendency}):\n"
            for skill, value in self.profile.items():
                profile_str += f"{skill}: {value}/10 ({skill_terms.get(value, 'Unknown')})\n"
            return profile_str
    
    def increase_fatigue(self, amount):
        """Increase the player's fatigue level"""
        if self.is_user:  # Only track fatigue for the user
            self.fatigue = min(self.max_fatigue, self.fatigue + amount)
    
    def get_fatigue_description(self):
        """Get a description of the current fatigue level"""
        if self.fatigue < 20:
            return "Fresh"
        elif self.fatigue < 40:
            return "Slightly Tired"
        elif self.fatigue < 60:
            return "Tiring"
        elif self.fatigue < 80:
            return "Very Tired"
        else:
            return "Exhausted"
    
    def reset_fatigue(self):
        """Reset fatigue between points"""
        if self.is_user:
            self.fatigue = max(0, self.fatigue - 30)  # Partial recovery between points
            
    def get_shot_skill(self, shot_type):
        """Get the player's skill level for a specific shot type"""
        if "Forehand" in shot_type and "Volley" not in shot_type:
            return self.profile["Forehand"]
        elif "Backhand" in shot_type and "Volley" not in shot_type:
            return self.profile["Backhand"]
        elif "Drop Shot" in shot_type:
            return self.profile["Drop Shot"]
        elif "Lob" in shot_type:
            return self.profile["Lob"]
        elif "Volley" in shot_type:
            return self.profile["Volley"]
        elif "Approach" in shot_type:
            # Approach shots are a mix of groundstroke skill and net play
            if "Forehand" in shot_type:
                return (self.profile["Forehand"] + self.profile["Volley"]) / 2
            else:
                return (self.profile["Backhand"] + self.profile["Volley"]) / 2
        elif "Slice" in shot_type:
            # Slice is often more related to backhand skill
            return (self.profile["Backhand"] + 5) / 2
        elif "Serve" in shot_type or shot_type in ["First Serve", "Second Serve"]:
            return self.profile["Serve"]
        else:
            return 5  # Default average skill

class TennisGame:
    def __init__(self):
        self.player = Player(is_user=True)
        self.opponent = Player(is_user=False)
        
        # Point scoring
        self.player_point_score = 0
        self.opponent_point_score = 0
        
        # Game scoring
        self.player_games = 0
        self.opponent_games = 0
        
        # Set scoring
        self.player_sets = 0
        self.opponent_sets = 0
        self.sets_to_win = 2  # Best of 3 sets
        
        # Deuce tracking
        self.deuce = False  # Track if the game is in deuce
        
        self.rally_count = 0
        self.last_shot = None
        self.player_turn = True  # Whether it's the player's turn to hit
        self.game_state = "Ready to serve"  # Current state of the game
        self.game_history = []  # Log of game events
        self.is_serving = True  # Whether the current shot is a serve
        self.server = "player"  # Who's serving this game: "player" or "opponent"
        self.second_serve = False  # Whether this is the second serve (after first serve fault)
        
    def start_new_game(self):
        """Start a new game with a new opponent"""
        # Don't reset sets/games when just starting a new game
        self.player_point_score = 0
        self.opponent_point_score = 0
        self.deuce = False
        
        # Determine server based on tennis rules
        if self.player_games + self.opponent_games == 0:
            # First game of the set, randomize server
            self.server = random.choice(["player", "opponent"])
        elif (self.player_games + self.opponent_games) % 2 == 1:
            # Switch servers after odd-numbered games
            self.server = "opponent" if self.server == "player" else "player"
        
        self.reset_rally()
        self.game_state = f"New game started. {self.server.capitalize()} is serving."
        self.game_history = [f"New game started. {self.server.capitalize()} is serving."]
        return self.get_game_status()
        
    def start_new_match(self):
        """Start a completely new match"""
        self.opponent = Player(is_user=False)
        self.player_point_score = 0
        self.opponent_point_score = 0
        self.player_games = 0
        self.opponent_games = 0
        self.player_sets = 0
        self.opponent_sets = 0
        self.deuce = False
        
        # Randomize who serves first
        self.server = random.choice(["player", "opponent"])
        
        self.reset_rally()
        self.game_state = f"New match started. {self.server.capitalize()} is serving."
        self.game_history = [f"New match started against a new opponent. {self.server.capitalize()} is serving."]
        return self.get_game_status()
        
    def reset_rally(self):
        """Reset for a new rally/point"""
        self.rally_count = 0
        self.last_shot = None
        self.is_serving = True  # Start with a serve
        self.second_serve = False  # Reset to first serve
        self.player_turn = self.server == "player"  # Serving player starts
        self.player.position = "Baseline"
        self.opponent.position = "Baseline"
        self.player.court_position = "Center"
        self.opponent.court_position = "Center"
        self.player.reset_fatigue()
        
        # Update game state to indicate who's serving
        if self.player_turn:
            self.game_state = "Your serve. Select 'First Serve'."
        else:
            self.game_state = "Opponent's serve. Click 'Continue Rally' to see their serve."
    
    def get_score_string(self):
        """Get the current score as a string"""
        # Tennis point scoring: 0, 15, 30, 40, Ad
        point_names = {0: "0", 1: "15", 2: "30", 3: "40"}
        
        # Current point score
        if not self.deuce:
            if self.player_point_score <= 3 and self.opponent_point_score <= 3:
                # Regular scoring (before deuce)
                point_score = f"{point_names.get(self.player_point_score, '40')} - {point_names.get(self.opponent_point_score, '40')}"
                
                # Check for deuce
                if self.player_point_score == 3 and self.opponent_point_score == 3:
                    point_score = "Deuce"
                    self.deuce = True
            else:
                # Someone scores game point
                if self.player_point_score > 3:
                    self.player_games += 1
                    self.game_history.append(f"Game won by player! Score: {self.player_games}-{self.opponent_games}")
                    self.check_set_winner()
                    self.player_point_score = 0
                    self.opponent_point_score = 0
                    # Switch server
                    self.server = "opponent" if self.server == "player" else "player"
                    self.deuce = False
                elif self.opponent_point_score > 3:
                    self.opponent_games += 1
                    self.game_history.append(f"Game won by opponent! Score: {self.player_games}-{self.opponent_games}")
                    self.check_set_winner()
                    self.player_point_score = 0
                    self.opponent_point_score = 0
                    # Switch server
                    self.server = "opponent" if self.server == "player" else "player"
                    self.deuce = False
                
                point_score = f"{point_names.get(self.player_point_score, '40')} - {point_names.get(self.opponent_point_score, '40')}"
        else:
            # After deuce
            if self.player_point_score == self.opponent_point_score:
                point_score = "Deuce"
            elif self.player_point_score > self.opponent_point_score:
                point_score = "Ad - 40"
            elif self.opponent_point_score > self.player_point_score:
                point_score = "40 - Ad"
            
            # Check for game win after advantage
            if self.player_point_score >= self.opponent_point_score + 2:
                self.player_games += 1
                self.game_history.append(f"Game won by player! Score: {self.player_games}-{self.opponent_games}")
                self.check_set_winner()
                self.player_point_score = 0
                self.opponent_point_score = 0
                self.deuce = False
                # Switch server
                self.server = "opponent" if self.server == "player" else "player"
            elif self.opponent_point_score >= self.player_point_score + 2:
                self.opponent_games += 1
                self.game_history.append(f"Game won by opponent! Score: {self.player_games}-{self.opponent_games}")
                self.check_set_winner()
                self.player_point_score = 0
                self.opponent_point_score = 0
                self.deuce = False
                # Switch server
                self.server = "opponent" if self.server == "player" else "player"
            
        # Full score including games and sets
        return f"Sets: {self.player_sets}-{self.opponent_sets} | Games: {self.player_games}-{self.opponent_games} | Points: {point_score}"
    
    def get_court_display(self):
        """Generate a simpler, clearer representation of tennis court"""
        court = [
            "┌─────────────────────────────┐",
            "│                             │",
            "│                             │",
            "│            O                │", # Opponent position
            "│                             │",
            "│                             │",
            "│                             │",
            "│─────────────────────────────│", # Service line
            "│                             │",
            "│                             │",
            "│                             │",
            "├─────────────┼───────────────┤", # Center line
            "│                             │",
            "│                             │",
            "│             •               │", # Ball position (center)
            "│                             │",
            "│─────────────────────────────│", # Service line
            "│                             │",
            "│                             │",
            "│                             │",
            "│            P                │", # Player position
            "│                             │",
            "└─────────────────────────────┘"
        ]
        
        # Update player positions based on game state
        player_row = 20  # Default position (baseline)
        if self.player.position == "Mid-court":
            player_row = 17
        elif self.player.position == "Net":
            player_row = 14
            
        opponent_row = 3  # Default position (baseline)
        if self.opponent.position == "Mid-court":
            opponent_row = 6
        elif self.opponent.position == "Net":
            opponent_row = 9
            
        # Update player column based on court position
        player_col = 14  # Default center
        if self.player.court_position == "Forehand Side":
            player_col = 8
        elif self.player.court_position == "Backhand Side":
            player_col = 20
            
        opponent_col = 14  # Default center
        if self.opponent.court_position == "Forehand Side":
            opponent_col = 8
        elif self.opponent.court_position == "Backhand Side":
            opponent_col = 20
        
        # Clear old positions and set new ones
        # Clear player line
        court[20] = "│                             │"
        # Add player at new position
        court_line = list(court[player_row])
        court_line[player_col] = 'P'
        court[player_row] = ''.join(court_line)
        
        # Clear opponent line
        court[3] = "│                             │"
        # Add opponent at new position
        court_line = list(court[opponent_row])
        court_line[opponent_col] = 'O'
        court[opponent_row] = ''.join(court_line)
        
        # Add ball position if in play
        if self.rally_count > 0 or self.is_serving:
            # Ball is roughly between the players
            ball_row = (player_row + opponent_row) // 2
            
            if self.player_turn:
                # Ball is closer to opponent
                ball_row = (ball_row + opponent_row) // 2
            else:
                # Ball is closer to player
                ball_row = (ball_row + player_row) // 2
                
            ball_col = 14  # Default center
            
            # For cross-court shots, angle the ball
            if self.last_shot and "Cross-court" in self.last_shot:
                if self.player_turn:
                    ball_col = (opponent_col + 14) // 2
                else:
                    ball_col = (player_col + 14) // 2
                    
            # Clear ball line and add ball
            if 1 < ball_row < 22:
                court_line = list(court[ball_row])
                court_line[ball_col] = '●'
                court[ball_row] = ''.join(court_line)
        
        # Add court legends
        court.append("P: Player, O: Opponent, ●: Ball")
        court.append("Player Positions: Baseline, Mid-court, Net")
        
        return "\n".join(court)
    
    def get_game_status(self):
        """Get the current game status information"""
        # Determine which shot buttons should be enabled
        available_shot_types = []
        if self.player_turn:
            if self.is_serving and self.server == "player":
                if self.second_serve:
                    # Second serve
                    available_shot_types = ["second_serve"]
                else:
                    # First serve
                    available_shot_types = ["first_serve"]
            elif self.player.position == "Baseline":
                available_shot_types = ["ground_strokes", "special"]
            elif self.player.position == "Mid-court":
                available_shot_types = ["ground_strokes", "special"]
            elif self.player.position == "Net":
                available_shot_types = ["special"]  # Only volleys, etc.
        
        # Create a properly formatted game history
        game_history_text = "\n".join(self.game_history[-8:])  # Show only most recent events
        
        # Generate court display
        court_display = self.get_court_display()
        
        status = {
            "player_profile": self.player.profile_to_string(),
            "opponent_profile": self.opponent.profile_to_string(),
            "score": self.get_score_string(),
            "rally_status": self.game_state,
            "fatigue": f"Fatigue: {self.player.fatigue}/100 ({self.player.get_fatigue_description()})",
            "game_history": game_history_text,
            "court_display": court_display,
            "available_shots": available_shot_types
        }
        return status
    
    def player_won_point(self):
        """Handle scoring when player wins a point"""
        self.game_history.append("Point won by player!")
        
        # Update point score
        if not self.deuce:
            # Regular scoring (before deuce)
            self.player_point_score += 1
            
            # Check for deuce situation
            if self.player_point_score == 3 and self.opponent_point_score == 3:
                self.deuce = True
                self.game_history.append("Deuce!")
        else:
            # After deuce
            if self.player_point_score == self.opponent_point_score:
                # From deuce
                self.player_point_score += 1
                self.game_history.append("Advantage player!")
            elif self.player_point_score > self.opponent_point_score:
                # From advantage
                self.player_point_score += 1  # This will trigger game win in get_score_string
            else:
                # From opponent advantage, back to deuce
                self.player_point_score = self.opponent_point_score
                self.game_history.append("Back to deuce!")
            
    def opponent_won_point(self):
        """Handle scoring when opponent wins a point"""
        self.game_history.append("Point won by opponent!")
        
        # Update point score
        if not self.deuce:
            # Regular scoring (before deuce)
            self.opponent_point_score += 1
            
            # Check for deuce situation
            if self.player_point_score == 3 and self.opponent_point_score == 3:
                self.deuce = True
                self.game_history.append("Deuce!")
        else:
            # After deuce
            if self.player_point_score == self.opponent_point_score:
                # From deuce
                self.opponent_point_score += 1
                self.game_history.append("Advantage opponent!")
            elif self.opponent_point_score > self.player_point_score:
                # From advantage
                self.opponent_point_score += 1  # This will trigger game win in get_score_string
            else:
                # From player advantage, back to deuce
                self.opponent_point_score = self.player_point_score
                self.game_history.append("Back to deuce!")
            
    def check_set_winner(self):
        """Check if a set has been won"""
        # Standard set is won by first to 6 games with a 2-game lead
        if self.player_games >= 6 and self.player_games >= self.opponent_games + 2:
            self.player_sets += 1
            self.game_history.append(f"Set won by player! Sets: {self.player_sets}-{self.opponent_sets}")
            self.player_games = 0
            self.opponent_games = 0
            self.check_match_winner()
        elif self.opponent_games >= 6 and self.opponent_games >= self.player_games + 2:
            self.opponent_sets += 1
            self.game_history.append(f"Set won by opponent! Sets: {self.player_sets}-{self.opponent_sets}")
            self.player_games = 0
            self.opponent_games = 0
            self.check_match_winner()
            
    def check_match_winner(self):
        """Check if the match has been won"""
        if self.player_sets >= self.sets_to_win:
            self.game_history.append("Match won by player!")
            self.game_state = "Match won by player!"
        elif self.opponent_sets >= self.sets_to_win:
            self.game_history.append("Match won by opponent!")
            self.game_state = "Match won by opponent!"
    
    def calculate_shot_outcome(self, shot_type, hitter, receiver, is_serve=False, skill_override=None):
        """Calculate the outcome of a shot based on player skills, shot risk, and fatigue"""
        # Get base probabilities - use shot type if available, otherwise default values
        shot_info = SHOT_TYPES.get(shot_type, {"risk": 0.2, "base_success": 0.7})
        base_success = shot_info["base_success"]
        risk = shot_info["risk"]
        
        # Apply skill modifier
        if skill_override is not None:
            # Use provided skill override (for serves)
            skill_modifier = skill_override * 0.05  # Each skill point above/below 5 is ±5%
        else:
            # Calculate based on player's skill for this shot type
            skill_modifier = (hitter.get_shot_skill(shot_type) - 5) * 0.05
            
        success_prob = base_success + skill_modifier
        
        # Adjust for receiver's relevant skills
        if not is_serve:  # These adjustments don't apply to serves
            if "Drop Shot" in shot_type:
                # Drop shots effectiveness depends on receiver's movement
                defense_modifier = (receiver.profile["Movement/Endurance"] - 5) * 0.03
                success_prob -= defense_modifier  # Better movement makes drop shots less effective
                
            elif "Lob" in shot_type:
                # Lobs effectiveness depends on receiver's position
                if receiver.position == "Net":
                    success_prob += 0.15  # Lobs are more effective against net players
            
            # Context of previous shot affects outcome
            if self.last_shot:
                if "Drop Shot" in self.last_shot and "Lob" in shot_type:
                    success_prob += 0.1  # Easier to lob after a drop shot
                elif "Lob" in self.last_shot and "Volley" in shot_type:
                    success_prob += 0.1  # Easier to volley after a lob
        
        # Adjust for court positioning
        if hitter.court_position != "Center":
            success_prob -= 0.05  # Slightly harder to hit good shots from off-center
            
        # Fatigue effect (only for player)
        if hitter.is_user:
            fatigue_modifier = hitter.fatigue * 0.002  # Each fatigue point reduces success by 0.2%
            success_prob -= fatigue_modifier
            
        # Rally momentum factor
        if self.rally_count > 3:
            # As rallies get longer, there's a slight bias toward continuation
            momentum_factor = min(0.05, self.rally_count * 0.01)
            success_prob += momentum_factor
            
        # Random element for rally dynamics
        random_factor = random.uniform(-0.05, 0.05)
        success_prob += random_factor
        
        # Ensure probability stays within valid range
        success_prob = max(0.1, min(0.95, success_prob))
        
        # For serves, use special logic
        if is_serve:
            # Check if serve is good (in)
            serve_in_roll = random.random()
            if serve_in_roll > success_prob:
                # Serve fault
                return "Fault"
                
            # If serve is in, determine if it's an ace
            ace_chance = shot_info.get("ace_chance", 0.1)  # Default 10% ace chance
            # Adjust ace chance based on server skill
            skill_ace_modifier = (hitter.profile["Serve"] - 5) * 0.02
            ace_chance += skill_ace_modifier
            
            ace_roll = random.random()
            if ace_roll < ace_chance:
                # Ace
                return "Ace"
            else:
                # Returnable serve
                return "Returnable"
        else:
            # For normal shots
            # Strongly favor returnable shots to create longer rallies
            outcome_roll = random.random()
            
            if outcome_roll > success_prob:
                # Error
                return "Error"
            elif outcome_roll > success_prob * 0.85:
                # Winner (rarer to create longer rallies)
                return "Winner"
            else:
                # Returnable shot (most common outcome)
                return "Returnable"
            
    def update_positions(self, shot_type, hitter):
        """Update player positions based on the shot played"""
        # Update hitter position
        if "Approach" in shot_type or "Volley" in shot_type:
            hitter.position = "Net"
        elif "Drop Shot" in shot_type:
            hitter.position = "Mid-court"
            
        # Update receiver position based on shot type
        receiver = self.opponent if hitter is self.player else self.player
        
        if "Drop Shot" in shot_type:
            receiver.position = "Mid-court"
        elif "Lob" in shot_type and receiver.position == "Net":
            receiver.position = "Baseline"
            
        # Randomize court position slightly
        court_positions = ["Center", "Forehand Side", "Backhand Side"]
        weights = [0.6, 0.2, 0.2] if hitter.court_position == "Center" else [0.4, 0.3, 0.3]
        hitter.court_position = random.choices(court_positions, weights=weights)[0]
        
    def ai_choose_shot(self):
        """Have the AI opponent choose their next shot based on their profile and tendencies"""
        # Filter shots based on current context
        available_shots = []
        
        if self.opponent.position == "Baseline":
            # From baseline, can hit groundstrokes, drop shots, lobs, approach shots
            available_shots.extend([
                "Forehand Cross-court", "Forehand Down-the-line", 
                "Backhand Cross-court", "Backhand Down-the-line",
                "Drop Shot", "Lob", "Slice", "Approach Shot"
            ])
        elif self.opponent.position == "Mid-court":
            # From mid-court, can hit groundstrokes, approach shots, drop shots
            available_shots.extend([
                "Forehand Cross-court", "Forehand Down-the-line", 
                "Backhand Cross-court", "Backhand Down-the-line",
                "Drop Shot", "Approach Shot", "Slice"
            ])
        elif self.opponent.position == "Net":
            # From net, can hit volleys
            available_shots.extend(["Volley", "Drop Shot"])
        
        # Default if somehow no shots are available
        if not available_shots:
            available_shots = ["Forehand Cross-court", "Backhand Cross-court"]
        
        weights = []
        
        for shot in available_shots:
            weight = 1.0  # Base weight
            
            # Adjust weight based on AI skill for this shot
            skill = self.opponent.get_shot_skill(shot)
            weight *= (skill / 5.0) ** 2  # Square to emphasize skills
            
            # Context based on last shot from player
            if self.last_shot:
                if "Cross-court" in self.last_shot and "Down-the-line" in shot:
                    weight *= 1.3  # Slightly more likely to change direction
            
            # Adjust based on tendency
            if self.opponent.tendency == "Aggressive Baseliner":
                if "Down-the-line" in shot:
                    weight *= 1.5
                if "Drop Shot" in shot:
                    weight *= 0.7
                    
            elif self.opponent.tendency == "Defensive Baseliner":
                if "Cross-court" in shot:
                    weight *= 1.5
                if "Approach" in shot or "Volley" in shot:
                    weight *= 0.5
                    
            elif self.opponent.tendency == "Serve-and-Volleyer":
                if "Approach" in shot or "Volley" in shot:
                    weight *= 2.0
                    
            elif self.opponent.tendency == "Forehand Dominant":
                if "Forehand" in shot:
                    weight *= 1.8
                    
            elif self.opponent.tendency == "Backhand Dominant":
                if "Backhand" in shot:
                    weight *= 1.8
                    
            elif self.opponent.tendency == "All-Court Player":
                # More balanced shot selection
                weight *= 1.0
            
            # Position-based adjustments
            if self.opponent.position == "Net":
                if "Volley" in shot:
                    weight *= 3.0  # Much more likely to hit volleys at net
                else:
                    weight *= 0.2  # Less likely to hit groundstrokes from net
                
            # If player is at net, more likely to hit lobs
            if self.player.position == "Net" and "Lob" in shot:
                weight *= 2.0
                
            # Rally length impacts shot selection
            if self.rally_count > 6:
                # In long rallies, more aggressive players get impatient
                if self.opponent.tendency in ["Aggressive Baseliner", "Forehand Dominant"]:
                    if "Down-the-line" in shot or "Drop Shot" in shot:
                        weight *= 1.0 + (self.rally_count - 6) * 0.1  # Increasing weight with rally length
                
            weights.append(weight)
            
        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:  # Avoid division by zero
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(available_shots)] * len(available_shots)
        
        # Choose a shot
        return random.choices(available_shots, weights=weights)[0]
    
    def player_hit(self, shot_type):
        """Process the player's shot"""
        # Ensure it's the player's turn
        if not self.player_turn:
            return self.get_game_status()
            
        # Handle serve vs. regular shot
        if self.is_serving:
            if self.second_serve and shot_type != "Second Serve":
                # Force second serve if it's second serve time
                shot_type = "Second Serve"
                
            self.game_history.append(f"You serve: {shot_type}")
            
            # Calculate shot fatigue cost
            fatigue_cost = 3  # Base fatigue cost for serves
            self.player.increase_fatigue(fatigue_cost)
            
            # Calculate outcome with serve skill
            skill_modifier = self.player.profile["Serve"] - 5  # Adjust based on serve skill
            
            # Calculate outcome for serve
            outcome = self.calculate_shot_outcome(shot_type, self.player, self.opponent, 
                                                is_serve=True, skill_override=skill_modifier)
            
            if outcome == "Fault":
                # Handle first serve fault
                if not self.second_serve:
                    self.second_serve = True
                    self.game_history.append("Fault! Second serve needed.")
                    self.game_state = "Fault on first serve. Select 'Second Serve'."
                else:
                    # Double fault
                    self.game_history.append("Double fault!")
                    self.opponent_won_point()
                    self.game_state = "Point lost. You made a double fault."
                    self.reset_rally()
            elif outcome == "Ace":
                # Serve is an ace
                self.game_history.append("Ace!")
                self.player_won_point()
                self.game_state = "Point won! You hit an ace!"
                self.reset_rally()
            else:  # Returnable serve
                # Turn off serving mode and let rally continue
                self.is_serving = False
                self.last_shot = shot_type
                self.player_turn = False
                
                # Update player positions for visualization
                self.update_positions(shot_type, self.player)
                
                # Start the rally with opponent's return
                self.game_state = f"You served a {shot_type}. Opponent will return the serve."
        else:
            # Regular shot during rally
            self.rally_count += 1
            self.game_history.append(f"Rally #{self.rally_count}: You hit {shot_type}")
            
            # Calculate shot fatigue cost
            fatigue_cost = 5  # Base fatigue cost
            if "Drop Shot" in shot_type or "Lob" in shot_type:
                fatigue_cost += 2  # Special shots cost more energy
            
            if self.rally_count > 4:
                fatigue_cost += (self.rally_count - 4)  # Longer rallies increase fatigue
                
            self.player.increase_fatigue(fatigue_cost)
            
            # Calculate outcome
            outcome = self.calculate_shot_outcome(shot_type, self.player, self.opponent)
            
            # Update positions
            self.update_positions(shot_type, self.player)
            
            # Process outcome
            if outcome == "Error":
                self.game_history.append(f"You made an error with your {shot_type}.")
                self.opponent_won_point()
                self.game_state = f"Point lost. You made an error with your {shot_type}."
                self.reset_rally()
            elif outcome == "Winner":
                self.game_history.append(f"You hit a winner with your {shot_type}!")
                self.player_won_point()
                self.game_state = f"Point won! You hit a winner with your {shot_type}!"
                self.reset_rally()
            else:  # Returnable
                self.last_shot = shot_type
                self.player_turn = False
                self.game_state = f"You hit a {shot_type}. Opponent's turn."
                
        return self.get_game_status()
    
    def opponent_hit(self):
        """Process the opponent's shot"""
        # Handle serving vs. regular shots
        if self.is_serving:
            # Handle serving
            if self.second_serve:
                shot_type = "Second Serve"
                self.game_history.append(f"Opponent serves: Second Serve")
            else:
                shot_type = "First Serve"
                self.game_history.append(f"Opponent serves: First Serve")
                
            # Calculate outcome with serve skill
            skill_modifier = self.opponent.profile["Serve"] - 5  # Adjust based on serve skill
            
            # Calculate outcome for serve
            outcome = self.calculate_shot_outcome(shot_type, self.opponent, self.player, 
                                                is_serve=True, skill_override=skill_modifier)
            
            if outcome == "Fault":
                # Handle first serve fault
                if not self.second_serve:
                    self.second_serve = True
                    self.game_history.append("Fault! Second serve needed.")
                    self.game_state = "Opponent faulted on first serve. Waiting for second serve."
                    return self.get_game_status()  # Don't continue to second serve automatically
                else:
                    # Double fault
                    self.game_history.append("Double fault!")
                    self.player_won_point()
                    self.game_state = "Point won! Opponent made a double fault."
                    self.reset_rally()
            elif outcome == "Ace":
                # Serve is an ace
                self.game_history.append("Ace!")
                self.opponent_won_point()
                self.game_state = "Point lost. Opponent hit an ace!"
                self.reset_rally()
            else:  # Returnable serve
                # Turn off serving mode and let rally continue
                self.is_serving = False
                self.last_shot = shot_type
                self.player_turn = True
                
                # Update positions for visualization
                self.update_positions(shot_type, self.opponent)
                
                self.game_state = f"Opponent served a {shot_type}. Your turn to return."
        else:
            # Regular shot during rally
            shot_type = self.ai_choose_shot()
            self.rally_count += 1
            self.game_history.append(f"Rally #{self.rally_count}: Opponent hits {shot_type}")
            
            # Calculate outcome for regular shot
            outcome = self.calculate_shot_outcome(shot_type, self.opponent, self.player)
            
            # Update positions
            self.update_positions(shot_type, self.opponent)
            
            # Process outcome
            if outcome == "Error":
                self.game_history.append(f"Opponent made an error with their {shot_type}.")
                self.player_won_point()
                self.game_state = f"Point won! Opponent made an error with their {shot_type}."
                self.reset_rally()
            elif outcome == "Winner":
                self.game_history.append(f"Opponent hit a winner with their {shot_type}!")
                self.opponent_won_point()
                self.game_state = f"Point lost. Opponent hit a winner with their {shot_type}!"
                self.reset_rally()
            else:  # Returnable
                self.last_shot = shot_type
                self.player_turn = True
                self.game_state = f"Opponent hit a {shot_type}. Your turn."
            
        return self.get_game_status()

# Create the Gradio interface
def create_interface():
    game = TennisGame()
    
    with gr.Blocks(title="Tennis Strategy Simulator", css="button { min-height: 30px; }") as interface:
        gr.Markdown("# Turn-Based Tennis Strategy Simulator")
        
        with gr.Row():
            with gr.Column(scale=1):
                court_display = gr.Textbox(label="Tennis Court", value=game.get_court_display(), lines=24)
                score_display = gr.Textbox(label="Score", value=game.get_score_string())
                rally_status = gr.Textbox(label="Rally Status", value="Ready to start")
                fatigue_indicator = gr.Textbox(label="Fatigue", value="Fatigue: 0/100 (Fresh)")
                
            with gr.Column(scale=1):
                game_history = gr.Textbox(label="Game History", lines=10, value="Game will start when you choose an option.")
                
                with gr.Row():
                    player_profile = gr.Textbox(label="Your Profile", value=game.player.profile_to_string(), lines=6, scale=1)
                    opponent_profile = gr.Textbox(label="Opponent Profile", value=game.opponent.profile_to_string(), lines=6, scale=1)
                
                # Compact buttons in a grid layout
                gr.Markdown("### Shots")
                with gr.Row():
                    # Serving buttons
                    with gr.Column(scale=1, min_width=100):
                        first_serve = gr.Button("First Serve", size="sm")
                        second_serve = gr.Button("Second Serve", size="sm")
                    
                    # Ground strokes
                    with gr.Column(scale=2, min_width=200):
                        with gr.Row():
                            forehand_cc = gr.Button("FH Cross", size="sm")
                            forehand_dtl = gr.Button("FH Down Line", size="sm")
                        with gr.Row():
                            backhand_cc = gr.Button("BH Cross", size="sm")
                            backhand_dtl = gr.Button("BH Down Line", size="sm")
                        with gr.Row():
                            drop_shot = gr.Button("Drop Shot", size="sm")
                            slice_shot = gr.Button("Slice", size="sm")
                        with gr.Row():
                            lob = gr.Button("Lob", size="sm")
                            approach = gr.Button("Approach", size="sm")
                            volley = gr.Button("Volley", size="sm")
                
                # Game control buttons
                with gr.Row():
                    continue_rally = gr.Button("Continue Rally (Opponent's Turn)", size="sm")
                    new_game = gr.Button("New Game", size="sm")
                    new_match = gr.Button("New Match", size="sm")
        
        # Define update function
        def update_ui(status):
            return [
                status["court_display"],
                status["score"],
                status["rally_status"],
                status["fatigue"],
                status["game_history"],
                status["player_profile"],
                status["opponent_profile"]
            ]
            
        # Button click handlers for serves
        first_serve.click(lambda: update_ui(game.player_hit("First Serve")),
                       outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        second_serve.click(lambda: update_ui(game.player_hit("Second Serve")),
                        outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        
        # Button click handlers for ground strokes
        forehand_cc.click(lambda: update_ui(game.player_hit("Forehand Cross-court")),
                         outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        forehand_dtl.click(lambda: update_ui(game.player_hit("Forehand Down-the-line")),
                          outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        backhand_cc.click(lambda: update_ui(game.player_hit("Backhand Cross-court")),
                         outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        backhand_dtl.click(lambda: update_ui(game.player_hit("Backhand Down-the-line")),
                          outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        
        # Button click handlers for special shots
        drop_shot.click(lambda: update_ui(game.player_hit("Drop Shot")),
                       outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        lob.click(lambda: update_ui(game.player_hit("Lob")),
                 outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        slice_shot.click(lambda: update_ui(game.player_hit("Slice")),
                       outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        approach.click(lambda: update_ui(game.player_hit("Approach Shot")),
                     outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        volley.click(lambda: update_ui(game.player_hit("Volley")),
                   outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        
        # Continue rally and new game buttons
        continue_rally.click(lambda: update_ui(game.opponent_hit()),
                           outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        new_game.click(lambda: update_ui(game.start_new_game()),
                      outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        new_match.click(lambda: update_ui(game.start_new_match()),
                      outputs=[court_display, score_display, rally_status, fatigue_indicator, game_history, player_profile, opponent_profile])
        
    return interface

# Launch the app when the script is run
if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=True)