"""Schema validation and business rule validation for contributions."""

import json
import jsonschema
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from .ids import generate_content_fingerprint, normalize_wallet_address
from .schema.contribution import ContributionSchema
from .schema.contribution import validate_contribution, CONTRIBUTION_JSON_SCHEMA, generate_content_fingerprint as schema_generate_content_fingerprint


class ValidationError(Exception):
    """Raised when contribution validation fails."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


class ContributionValidator:
    """Validates contribution records against schema and business rules."""

    def __init__(self, policy_path: Optional[str] = None):
        # Load schemas
        self.contribution_schema = CONTRIBUTION_JSON_SCHEMA

        # Load policy
        self.policy = self._load_policy(policy_path or
                                       Path(__file__).parent / 'config' / 'contribution-policy.json')

    def _load_schema(self, schema_path: Path) -> Dict:
        """Load a JSON schema from file."""
        # For now, return empty schema since we're using inline schema
        return {}

    def _load_policy(self, policy_path: Path) -> Dict:
        """Load the contribution policy from file."""
        with open(policy_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate_contribution(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a contribution record against schema and policy.

        Args:
            data: The contribution record to validate

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        # 1. Schema validation using our internal function
        is_valid, schema_errors = validate_contribution(data)
        if not is_valid:
            errors.extend(schema_errors)

        # 2. No economic fields check
        forbidden_fields = ['tokenAmount', 'payout', 'claimAmount', 'vesting']
        for field in forbidden_fields:
            if field in data:
                errors.append(f"Forbidden economic field: {field}")
                return False, errors

        # 3. Content fingerprint verification
        if 'contentFingerprint' in data:
            # Create the same structure as during creation
            fingerprint_data = {
                'contributor': data['contributor'],
                'category': data['category'],
                'content': data['content'],
                'evidence': data.get('evidence', []),
                'schemaVersion': data['schemaVersion']
            }
            expected_fingerprint = schema_generate_content_fingerprint(fingerprint_data)
            if data['contentFingerprint'] != expected_fingerprint:
                errors.append(f"Content fingerprint does not match calculated value: expected {expected_fingerprint}")
                return False, errors

        # 4. Contributor identity validation
        contributor_errors = self._validate_contributor(data.get('contributor', {}))
        errors.extend(contributor_errors)

        # 5. Evidence validation
        evidence_errors = self.validate_evidence_bundle(data.get('evidence', []))
        errors.extend(evidence_errors[1] if not evidence_errors[0] else [])

        # 6. Policy validation
        policy_errors = self._validate_policy(data)
        errors.extend(policy_errors)

        # 7. Status validation
        status_errors = self._validate_status(data)
        errors.extend(status_errors)

        return len(errors) == 0, errors

    def _validate_contributor(self, contributor: Dict) -> List[str]:
        """Validate contributor identity."""
        errors = []

        if not isinstance(contributor, dict):
            errors.append("Contributor must be an object")
            return errors

        required_fields = ['type', 'id']
        for field in required_fields:
            if field not in contributor:
                errors.append(f"Missing required contributor field: {field}")

        if 'type' in contributor:
            valid_types = ['wallet', 'github', 'protocol_id']
            if contributor['type'] not in valid_types:
                errors.append(f"Invalid contributor type: {contributor['type']}")

        if 'id' in contributor:
            if not isinstance(contributor['id'], str) or len(contributor['id'].strip()) == 0:
                errors.append("Contributor ID must be a non-empty string")

        return errors

    def _validate_evidence(self, evidence: List, category: str) -> List[str]:
        """Validate evidence items."""
        errors = []

        if not isinstance(evidence, list):
            errors.append("Evidence must be an array")
            return errors

        # Check minimum evidence requirement for category
        category_info = self.policy.get('categories', {}).get(category, {})
        min_evidence = category_info.get('minimumEvidence', 1)
        if len(evidence) < min_evidence:
            errors.append(f"Category '{category}' requires at least {min_evidence} evidence items")

        # Validate each evidence item
        for i, item in enumerate(evidence):
            try:
                self.evidence_validator.validate(item)
            except jsonschema.ValidationError as e:
                errors.append(f"Evidence item {i} validation failed: {e.message}")

        return errors

    def _validate_policy(self, data: Dict) -> List[str]:
        """Validate against policy requirements."""
        errors = []

        # Check policy version exists
        if 'policyVersion' not in data:
            errors.append("Missing policyVersion")
        else:
            # Check if policy version matches loaded policy
            if data['policyVersion'] != self.policy['policyVersion']:
                errors.append(f"Policy version mismatch: expected {self.policy['policyVersion']}")

        # Check category eligibility
        category = data.get('category')
        if category in self.policy.get('categories', {}):
            if not self.policy['categories'][category].get('eligible', False):
                errors.append(f"Category '{category}' is not eligible for scoring")

        return errors

    def _validate_status(self, data: Dict) -> List[str]:
        """Validate record status and associated fields."""
        errors = []
        status = data.get('status')

        # Status must be one of the allowed values
        valid_statuses = ['draft', 'submitted', 'under_review', 'needs_more_evidence',
                         'rejected', 'verified', 'scored', 'finalized']
        if status not in valid_statuses:
            errors.append(f"Invalid status: {status}")

        # Certain statuses imply certain fields
        if status in ['rejected', 'needs_more_evidence']:
            if not data.get('review'):
                errors.append(f"Status '{status}' requires review field")

        if status in ['scored', 'finalized']:
            if not data.get('scores'):
                errors.append(f"Status '{status}' requires scores field")

        return errors

    def validate_evidence_bundle(self, evidence: List[Dict]) -> Tuple[bool, List[str]]:
        """Validate a standalone evidence bundle."""
        errors = []

        if not isinstance(evidence, list):
            errors.append("Evidence must be an array")
            return False, errors

        # Simple validation for evidence items
        for i, item in enumerate(evidence):
            if not isinstance(item, dict):
                errors.append(f"Evidence item {i} must be an object")
                continue

            required_fields = ['evidenceId', 'type', 'observedAt', 'verification']
            for field in required_fields:
                if field not in item:
                    errors.append(f"Evidence item {i} missing required field: {field}")

            # Validate verification status
            if 'verification' in item and isinstance(item['verification'], dict):
                if 'status' not in item['verification']:
                    errors.append(f"Evidence item {i} verification missing status")

        return len(errors) == 0, errors