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
        # Initialize safety validator and compliance checker
        self.safety_validator = SafetyValidator()
        self.compliance_checker = ComplianceChecker()
        self.audit_log = []

    def validate_input(self, text: str) -> Dict[str, Any]:
        """
        Validates user input before processing

        This method:
        1. Runs safety validation
        2. Runs compliance check with GDPR standard
        3. Combines results (passed if both safe and compliant)
        4. Logs audit entry
        5. Returns result dict
        """
        # 1. Safety Check
        safety_result = self.safety_validator.validate(text)

        # 2. Compliance Check (ensure no PII in query if strict)
        compliance_result = self.compliance_checker.check_compliance(text, compliance_standards=["GDPR"])

        # Combine results - passed only if both checks pass
        passed = safety_result['safe'] and compliance_result['compliant']
        violations = safety_result['violations'] + compliance_result['violations']

        result = {
            'passed': passed,
            'violations': violations,
            'timestamp': datetime.datetime.now().isoformat()
        }

        # Log audit entry
        self._log_audit("validate_input", result)
        return result

    def validate_output(self, text: str) -> Dict[str, Any]:
        """
        Validates LLM output before returning to user

        Similar to validate_input - runs both safety and compliance checks
        """
        # Similar checks for output
        safety_result = self.safety_validator.validate(text)
        compliance_result = self.compliance_checker.check_compliance(text, compliance_standards=["GDPR"])

        passed = safety_result['safe'] and compliance_result['compliant']
        violations = safety_result['violations'] + compliance_result['violations']

        result = {
            'passed': passed,
            'violations': violations,
            'timestamp': datetime.datetime.now().isoformat()
        }

        self._log_audit("validate_output", result)
        return result

    def get_audit_log(self):
        """Return the audit log"""
        return self.audit_log

    def _log_audit(self, action: str, result: Dict[str, Any]):
        """
        Log audit entry

        Creates entry dict with action, result status, details, timestamp
        """
        entry = {
            'action': action,
            'result': "PASS" if result['passed'] else "FAIL",
            'details': result,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.audit_log.append(entry)