"""
PII Detection using regex patterns
RUBRIC: Governance & Guardrails - PII detection (2 marks)

TASK: Implement PII detection for common personally identifiable information
"""
import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class PIIDetector:
    """Detects Personally Identifiable Information"""

    def __init__(self):
        # Define regex patterns for common PII types
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b(?:\d{4}[\s-]?){3}\d{4}\b',
            'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
            'zip_code': r'\b\d{5}(?:-\d{4})?\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        }

    def detect(self, text: str) -> Dict:
        """
        Detect PII in text

        This method:
        1. Initializes empty entities list
        2. Loops through self.patterns
        3. Uses re.finditer to find all matches
        4. For each match, appends dict with type, value, start, end
        5. Returns dict with detected (bool), entities (list), count (int)
        """
        entities = []

        # Loop through each pattern type and pattern
        for entity_type, pattern in self.patterns.items():
            # Use re.finditer to find all matches
            matches = re.finditer(pattern, text)

            for match in matches:
                # Append entity info to entities list
                entities.append({
                    'type': entity_type,
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })

        return {
            'detected': len(entities) > 0,
            'entities': entities,
            'count': len(entities)
        }

    def redact(self, text: str) -> str:
        """
        Redact PII from text

        Uses re.sub to replace each pattern with [TYPE_REDACTED]
        """
        redacted_text = text

        # Loop through patterns and redact each type
        for entity_type, pattern in self.patterns.items():
            if entity_type == 'email':
                redacted_text = re.sub(pattern, '[EMAIL_REDACTED]', redacted_text)
            elif entity_type == 'phone':
                redacted_text = re.sub(pattern, '[PHONE_REDACTED]', redacted_text)
            elif entity_type == 'passport':
                redacted_text = re.sub(pattern, '[PASSPORT_REDACTED]', redacted_text)
            elif entity_type == 'credit_card':
                redacted_text = re.sub(pattern, '[CREDIT_CARD_REDACTED]', redacted_text)
            else:
                # Use f-string to create dynamic redaction message
                redacted_text = re.sub(pattern, f'[{entity_type.upper()}_REDACTED]', redacted_text)

        return redacted_text