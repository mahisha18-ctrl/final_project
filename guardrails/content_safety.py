"""
Content Safety Checker
RUBRIC: Governance & Guardrails - Content safety checks (2 marks)

TASK: Implement keyword-based content safety checking
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ContentSafety:
    """Checks content for safety violations"""

    def __init__(self):
        # Define unsafe keyword patterns for different categories
        self.unsafe_patterns = {
            'violence': ['kill', 'attack', 'murder', 'assault', 'shoot', 'stab', 'bomb', 'terrorist', 'weapon', 'gun'],
            'hate_speech': ['racist', 'sexist', 'nazi', 'supremacist', 'slur', 'bigot', 'discriminate', 'hatred'],
            'profanity': ['fuck', 'shit', 'bitch', 'damn', 'ass', 'bastard', 'crap', 'hell'],
            'personal_attack': ['stupid', 'idiot', 'moron', 'dumb', 'loser', 'pathetic', 'worthless', 'useless']
        }

        # Define travel-specific red flags
        self.travel_red_flags = ['fraud', 'fake booking', 'scam', 'steal', 'smuggle', 'illegal', 'counterfeit',
                                 'forged', 'fake passport', 'fake visa', 'bypass security', 'avoid customs']

    def check(self, text: str) -> Dict:
        """
        Check text for safety violations

        This method:
        1. Converts text to lowercase
        2. Initializes empty flags list
        3. Checks text against unsafe_patterns
        4. Checks text against travel_red_flags
        5. Returns dict with safe, flags, severity
        """
        text_lower = text.lower()
        flags = []

        # Check general unsafe patterns
        for category, keywords in self.unsafe_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Determine severity based on category
                    if category in ['violence', 'hate_speech']:
                        severity = 'high'
                    elif category == 'profanity':
                        severity = 'medium'
                    else:  # personal_attack
                        severity = 'low'

                    flags.append({
                        'category': category,
                        'text': keyword,
                        'severity': severity
                    })

        # Check travel-specific red flags
        for red_flag in self.travel_red_flags:
            if red_flag in text_lower:
                flags.append({
                    'category': 'travel_violation',
                    'text': red_flag,
                    'severity': 'high'
                })

        return {
            'safe': len(flags) == 0,
            'flags': flags,
            'severity': 'high' if any(f['severity'] == 'high' for f in flags) else ('medium' if flags else 'low')
        }

    def get_safety_score(self, text: str) -> float:
        """
        Calculate safety score (0-1)

        Returns 1.0 if safe, otherwise reduces by 0.2 per flag (minimum 0.0)
        """
        result = self.check(text)

        if result['safe']:
            return 1.0

        # Reduce score based on violations
        penalty = 0.2 * len(result['flags'])
        return max(0.0, 1.0 - penalty)