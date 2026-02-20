import json
import os
from datetime import datetime
from pathlib import Path

class HighscoreManager:
    """Manages highscores with persistent JSON storage"""
    
    def __init__(self):
        # Create highscores file in the game directory
        self.highscores_path = Path(__file__).parent / "highscores.json"
        self.max_scores = 10
        self.scores = self.load_scores()
    
    def load_scores(self):
        """Load scores from JSON file, create if doesn't exist"""
        if self.highscores_path.exists():
            try:
                with open(self.highscores_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_scores(self):
        """Save scores to JSON file"""
        try:
            with open(self.highscores_path, 'w') as f:
                json.dump(self.scores, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving highscores: {e}")
            return False
    
    def add_score(self, name, score, level):
        """Add a new score and keep top 10"""
        new_entry = {
            "name": name[:15],  # Limit name to 15 characters
            "score": int(score),
            "level": int(level),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.scores.append(new_entry)
        # Sort by score (descending) then keep top 10
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:self.max_scores]
        
        self.save_scores()
        
        # Return ranking (1-based)
        return self.scores.index(new_entry) + 1
    
    def get_rank(self, score):
        """Get what rank a score would be"""
        if not self.scores:
            return 1
        
        rank = 1
        for entry in self.scores:
            if score > entry["score"]:
                return rank
            rank += 1
        
        if len(self.scores) < self.max_scores:
            return rank
        
        return None  # Score doesn't make top 10
    
    def is_highscore(self, score):
        """Check if score qualifies for top 10"""
        if len(self.scores) < self.max_scores:
            return True
        return score > self.scores[-1]["score"]
    
    def get_formatted_scores(self):
        """Get formatted string for display"""
        if not self.scores:
            return "No highscores yet!"
        
        lines = []
        lines.append("=" * 60)
        lines.append(f"{'RANK':<6} {'NAME':<15} {'SCORE':<10} {'LEVEL':<6} {'DATE':<20}")
        lines.append("=" * 60)
        
        for i, entry in enumerate(self.scores, 1):
            lines.append(
                f"{i:<6} {entry['name']:<15} {entry['score']:<10} "
                f"{entry['level']:<6} {entry['date']:<20}"
            )
        
        lines.append("=" * 60)
        return "\n".join(lines)
