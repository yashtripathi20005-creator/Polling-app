# Data models for the polling app
# This file contains the data structures and business logic

class Poll:
    """Poll model representing a voting question"""
    def __init__(self, id, question, created_at):
        self.id = id
        self.question = question
        self.created_at = created_at
        self.options = []
        self.total_votes = 0
    
    def add_option(self, option):
        """Add an option to this poll"""
        self.options.append(option)
    
    def get_total_votes(self):
        """Calculate total votes for this poll"""
        return sum(option.votes for option in self.options)
    
    def get_winner(self):
        """Get the option with the most votes"""
        if not self.options:
            return None
        return max(self.options, key=lambda o: o.votes)
    
    def to_dict(self):
        """Convert poll to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'question': self.question,
            'created_at': self.created_at,
            'options': [opt.to_dict() for opt in self.options],
            'total_votes': self.get_total_votes()
        }

class Option:
    """Option model representing a choice in a poll"""
    def __init__(self, id, poll_id, text):
        self.id = id
        self.poll_id = poll_id
        self.text = text
        self.votes = 0
    
    def add_vote(self):
        """Increment vote count for this option"""
        self.votes += 1
    
    def get_percentage(self, total_votes):
        """Calculate percentage of votes for this option"""
        if total_votes == 0:
            return 0
        return round((self.votes / total_votes) * 100, 1)
    
    def to_dict(self):
        """Convert option to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'poll_id': self.poll_id,
            'text': self.text,
            'votes': self.votes
        }

class Vote:
    """Vote model representing a single vote"""
    def __init__(self, id, poll_id, option_id, voted_at):
        self.id = id
        self.poll_id = poll_id
        self.option_id = option_id
        self.voted_at = voted_at
    
    def to_dict(self):
        """Convert vote to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'poll_id': self.poll_id,
            'option_id': self.option_id,
            'voted_at': self.voted_at
        }
