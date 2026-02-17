"""
Safety Validator
RUBRIC: Governance & Guardrails - Safety validator with Azure Content Safety (3 marks)

TASK: Implement safety validation using both local checks and Azure Content Safety
"""
import re
from typing import Dict, Any, List
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.contentsafety.models import AnalyzeTextOptions
from config import config
from guardrails.content_safety import ContentSafety


class SafetyValidator:
    """Validates content safety and detects adversarial attacks (jailbreaks)"""

    def __init__(self):
        # Initialize local content safety checker
        self.content_safety = ContentSafety()

        # Define prompt injection patterns
        self.injection_patterns = [
            r"ignore previous instructions",
            r"bypass safety",
            r"override guidelines",
            r"you are now in developer mode",
            r"delete all data",
            r"jailbreak mode",
        ]

        # Initialize Azure Content Safety client if credentials available
        self.client = None
        if config.content_safety.endpoint and config.content_safety.key:
            try:
                self.client = ContentSafetyClient(
                    endpoint=config.content_safety.endpoint,
                    credential=AzureKeyCredential(config.content_safety.key)
                )
            except Exception as e:
                print(f"Warning: Failed to init Azure Content Safety: {e}")

    def validate(self, text: str, severity_threshold: str = "high") -> Dict[str, Any]:
        """
        Validates the text for safety violations

        This method:
        1. Initializes flags list and is_safe boolean
        2. Runs local content safety check
        3. Checks for prompt injection patterns
        4. Runs Azure Content Safety check if client available
        5. Returns dict with safe, violations, severity
        """
        violations = []
        is_safe = True

        # 1. Local Content Safety Guardrail (Keywords & Regex)
        local_result = self.content_safety.check(text)
        if not local_result['safe']:
            is_safe = False
            for flag in local_result['flags']:
                violations.append(f"Unsafe Keyword ({flag['category']}): {flag['text']}")

        # 2. Specific Injection Checks
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                is_safe = False
                violations.append(f"Prompt Injection Detected: {pattern}")

        # 3. Azure Content Safety Check
        if self.client:
            try:
                request = AnalyzeTextOptions(text=text)
                response = self.client.analyze_text(request)

                # Check categories_analysis for high severity flags (severity > 2)
                if response.categories_analysis:
                    for analysis in response.categories_analysis:
                        if analysis.severity > 2:
                            is_safe = False
                            violations.append(
                                f"Azure Content Safety Violation: {analysis.category} (severity: {analysis.severity})")

            except HttpResponseError as e:
                print(f"Azure Content Safety check failed: {e}")

        return {
            'safe': is_safe,
            'violations': violations,
            'severity': 'high' if not is_safe else 'low'
        }