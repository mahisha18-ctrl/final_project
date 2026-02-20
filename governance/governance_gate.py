"""
Governance Gate
RUBRIC: Governance & Guardrails - GovernanceGate orchestrates safety checks (3 marks)
TASK: Implement main governance orchestrator with audit logging
"""
from typing import Dict, Any
import datetime
from governance.safety_validator import SafetyValidator
from governance.compliance_checker import ComplianceChecker

class GovernanceGate:
    """The main orchestrator that coordinates all governance checks"""
    
    def __init__(self):
        self.safety_validator = SafetyValidator()
        self.compliance_checker = ComplianceChecker()
        self.audit_log = []

    def validate_input(self, text: str) -> Dict[str, Any]:
        """Validates user input before processing"""
        safety_result = self.safety_validator.validate(text)
        compliance_result = self.compliance_checker.check_compliance(text, compliance_standards=["GDPR"])
        passed = safety_result['safe'] and compliance_result['compliant']
        violations = safety_result['violations'] + compliance_result['violations']
        result = {
            'passed': passed,
            'violations': violations,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self._log_audit("validate_input", result)
        return result

    def validate_output(self, text: str) -> Dict[str, Any]:
        """
        Validates LLM output before returning to user.
        Output validation is lenient - only blocks profanity and hate speech,
        NOT travel policy terms like weapon, illegal, bomb (these appear in baggage rules)
        """
        # Only check for profanity and hate speech in output
        # Travel policy documents naturally contain words like weapon, illegal, bomb
        text_lower = text.lower()
        violations = []
        
        strict_patterns = ['fuck', 'shit', 'bitch', 'racist', 'nazi', 'supremacist']
        for word in strict_patterns:
            if word in text_lower:
                violations.append(f"Inappropriate language in response: {word}")

        passed = len(violations) == 0
        result = {
            'passed': passed,
            'violations': violations,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self._log_audit("validate_output", result)
        return result

    def get_audit_log(self):
        return self.audit_log

    def _log_audit(self, action: str, result: Dict[str, Any]):
        entry = {
            'action': action,
            'result': "PASS" if result['passed'] else "FAIL",
            'details': result,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.audit_log.append(entry)
