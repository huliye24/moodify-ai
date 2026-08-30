"""Core contribution engine that orchestrates all components."""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from .ids import generate_contribution_id
from .schema.contribution import generate_content_fingerprint as schema_generate_content_fingerprint
from .validate import ContributionValidator, ValidationError
from .state_machine import StateMachine, TransitionNotAllowedError
from .evidence import EvidenceBundle, EvidenceItem, EvidenceDuplicateDetector
from .scorer import Scorer, ScoreResult
from .schema.contribution import ContributionSchema


class ContributionCore:
    """Core contribution management engine."""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize the contribution core.

        Args:
            storage_path: Path to storage directory (optional)
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.validator = ContributionValidator()
        self.state_machine = StateMachine()
        self.scorer = Scorer()
        self.duplicate_detector = EvidenceDuplicateDetector()

        # Ensure storage directory exists
        if self.storage_path:
            self.storage_path.mkdir(parents=True, exist_ok=True)

    def create_contribution(
        self,
        contributor: Dict[str, str],
        category: str,
        content: Dict[str, Any],
        evidence: List[Dict[str, Any]] = None,
        schema_version: str = "1.0.0"
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Create a new contribution record.

        Args:
            contributor: Contributor identity {'type': str, 'id': str}
            category: Contribution category
            content: Contribution content
            evidence: Optional list of evidence items
            schema_version: Schema version

        Returns:
            Tuple of (contribution_record, errors)
        """
        # Generate deterministic values
        submitted_at = datetime.utcnow().isoformat()
        content_fingerprint = schema_generate_content_fingerprint({
            'contributor': contributor,
            'category': category,
            'content': content,
            'evidence': evidence or [],
            'schemaVersion': schema_version
        })
        contribution_id = generate_contribution_id(
            schema_version,
            contributor['type'],
            contributor['id'],
            category,
            content_fingerprint,
            submitted_at
        )

        # Build contribution record
        contribution = {
            'contributionId': contribution_id,
            'schemaVersion': schema_version,
            'policyVersion': '002-draft-1',
            'status': 'draft',
            'submittedAt': submitted_at,
            'contributor': contributor,
            'category': category,
            'content': content,
            'contentFingerprint': content_fingerprint,
            'evidence': evidence or [],
            'metadata': {
                'createdBy': 'system',
                'createdAt': datetime.utcnow().isoformat()
            }
        }

        # Validate the contribution
        is_valid, errors = self.validator.validate_contribution(contribution)
        if not is_valid:
            return {}, errors

        # Store contribution if storage path is provided
        if self.storage_path:
            self._store_contribution(contribution)

        return contribution, []

    def submit_contribution(self, contribution_id: str, review_data: Optional[Dict] = None) -> Tuple[Dict[str, Any], List[str]]:
        """Submit a draft contribution.

        Args:
            contribution_id: ID of contribution to submit
            review_data: Optional initial review data

        Returns:
            Tuple of (updated_contribution, errors)
        """
        # Load contribution
        contribution = self._load_contribution(contribution_id)
        if not contribution:
            return {}, [f"Contribution {contribution_id} not found"]

        # Apply transition
        try:
            updated_contribution = self.state_machine.apply_transition(
                contribution,
                'submitted',
                review_data
            )

            # Validate after transition
            is_valid, errors = self.validator.validate_contribution(updated_contribution)
            if not is_valid:
                return {}, errors

            # Store updated contribution
            if self.storage_path:
                self._store_contribution(updated_contribution)

            return updated_contribution, []

        except TransitionNotAllowedError as e:
            return {}, [str(e)]

    def review_contribution(
        self,
        contribution_id: str,
        decision: str,
        review_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[str]]:
        """Review a submitted contribution.

        Args:
            contribution_id: ID of contribution to review
            decision: Review decision ('verified', 'rejected', 'needs_more_evidence')
            review_data: Review details

        Returns:
            Tuple of (updated_contribution, errors)
        """
        # Load contribution
        contribution = self._load_contribution(contribution_id)
        if not contribution:
            return {}, [f"Contribution {contribution_id} not found"]

        # Apply transition
        try:
            updated_contribution = self.state_machine.apply_transition(
                contribution,
                decision,
                review_data
            )

            # Validate after transition
            is_valid, errors = self.validator.validate_contribution(updated_contribution)
            if not is_valid:
                return {}, errors

            # Store updated contribution
            if self.storage_path:
                self._store_contribution(updated_contribution)

            return updated_contribution, []

        except TransitionNotAllowedError as e:
            return {}, [str(e)]

    def add_evidence(self, contribution_id: str, evidence: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Add evidence to a contribution.

        Args:
            contribution_id: ID of contribution to add evidence to
            evidence: Evidence item to add

        Returns:
            Tuple of (updated_contribution, errors)
        """
        # Load contribution
        contribution = self._load_contribution(contribution_id)
        if not contribution:
            return {}, [f"Contribution {contribution_id} not found"]

        # Validate evidence
        is_valid, errors = self.validator.validate_evidence_bundle([evidence])
        if not is_valid:
            return contribution, errors

        # Add evidence
        contribution['evidence'].append(evidence)

        # Update content fingerprint
        content_fingerprint = schema_generate_content_fingerprint({
            'contributor': contribution['contributor'],
            'category': contribution['category'],
            'content': contribution['content'],
            'evidence': contribution['evidence'],
            'schemaVersion': contribution['schemaVersion']
        })
        contribution['contentFingerprint'] = content_fingerprint

        # Validate after adding evidence
        is_valid, errors = self.validator.validate_contribution(contribution)
        if not is_valid:
            return {}, errors

        # Store updated contribution
        if self.storage_path:
            self._store_contribution(contribution)

        return contribution, []

    def score_contribution(self, contribution_id: str, reputation_evidence: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Score a verified contribution.

        Args:
            contribution_id: ID of contribution to score
            reputation_evidence: Reputation evidence for scoring

        Returns:
            Tuple of (updated_contribution, errors)
        """
        # Load contribution
        contribution = self._load_contribution(contribution_id)
        if not contribution:
            return {}, [f"Contribution {contribution_id} not found"]

        # Check status requirements
        if contribution['status'] != 'verified':
            return {}, [f"Cannot score contribution in '{contribution['status']}' state"]

        # Score contribution
        try:
            score_result = self.scorer.score_contribution(contribution_id, reputation_evidence)

            # Validate scoring result
            consistency_errors = self.scorer.validate_score_consistency(score_result)
            if consistency_errors:
                return {}, consistency_errors

            # Apply score to contribution
            contribution['scores'] = score_result.scores
            contribution['reputationEvidence'] = reputation_evidence
            contribution['status'] = 'scored'

            # Validate after scoring
            is_valid, errors = self.validator.validate_contribution(contribution)
            if not is_valid:
                return {}, errors

            # Store updated contribution
            if self.storage_path:
                self._store_contribution(contribution)

            return contribution, []

        except ValidationError as e:
            return {}, [str(e)]

    def finalize_contribution(self, contribution_id: str, review_data: Optional[Dict] = None) -> Tuple[Dict[str, Any], List[str]]:
        """Finalize a scored contribution.

        Args:
            contribution_id: ID of contribution to finalize
            review_data: Optional final review data

        Returns:
            Tuple of (updated_contribution, errors)
        """
        # Load contribution
        contribution = self._load_contribution(contribution_id)
        if not contribution:
            return {}, [f"Contribution {contribution_id} not found"]

        # Apply transition
        try:
            updated_contribution = self.state_machine.apply_transition(
                contribution,
                'finalized',
                review_data
            )

            # Validate after transition
            is_valid, errors = self.validator.validate_contribution(updated_contribution)
            if not is_valid:
                return {}, errors

            # Store updated contribution
            if self.storage_path:
                self._store_contribution(updated_contribution)

            return updated_contribution, []

        except TransitionNotAllowedError as e:
            return {}, [str(e)]

    def get_contribution(self, contribution_id: str) -> Optional[Dict[str, Any]]:
        """Get a contribution by ID.

        Args:
            contribution_id: ID of contribution to retrieve

        Returns:
            Contribution record or None if not found
        """
        return self._load_contribution(contribution_id)

    def get_contribution_status(self, contribution_id: str) -> Optional[str]:
        """Get the status of a contribution.

        Args:
            contribution_id: ID of contribution

        Returns:
            Status or None if not found
        """
        contribution = self._load_contribution(contribution_id)
        return contribution.get('status') if contribution else None

    def get_contribution_history(self, contribution_id: str) -> List[Dict[str, Any]]:
        """Get the complete history of a contribution.

        Args:
            contribution_id: ID of contribution

        Returns:
            List of historical states
        """
        contribution = self._load_contribution(contribution_id)
        if not contribution:
            return []

        history = []
        current_state = contribution.copy()

        # Add initial state
        history.append({
            'status': current_state['status'],
            'timestamp': current_state.get('submittedAt'),
            'metadata': {
                'action': 'created',
                'metadata': current_state.get('metadata', {})
            }
        })

        # Add transition points
        if 'review' in current_state:
            history.append({
                'status': current_state['status'],
                'timestamp': current_state['review'].get('appliedAt'),
                'metadata': {
                    'action': 'reviewed',
                    'review': current_state['review']
                }
            })

        return history

    def detect_duplicate_evidence(self, contribution_id: str) -> Dict[str, List[str]]:
        """Detect duplicate evidence in a contribution.

        Args:
            contribution_id: ID of contribution to check

        Returns:
            Dictionary mapping evidence IDs to lists of duplicate IDs
        """
        contribution = self._load_contribution(contribution_id)
        if not contribution:
            return {}

        evidence_bundle = EvidenceBundle(contribution['evidence'])
        return self.duplicate_detector.find_duplicates(evidence_bundle)

    def get_allowed_transitions(self, contribution_id: str) -> List[str]:
        """Get allowed state transitions for a contribution.

        Args:
            contribution_id: ID of contribution

        Returns:
            List of allowed target statuses
        """
        contribution = self._load_contribution(contribution_id)
        if not contribution:
            return []

        return self.state_machine.get_allowed_transitions(contribution['status'])

    def _load_contribution(self, contribution_id: str) -> Optional[Dict[str, Any]]:
        """Load a contribution from storage.

        Args:
            contribution_id: ID of contribution to load

        Returns:
            Contribution record or None if not found
        """
        if not self.storage_path:
            # If no storage, return mock data for demo
            return self._get_mock_contribution(contribution_id)

        contribution_path = self.storage_path / f"{contribution_id}.json"
        if not contribution_path.exists():
            return None

        with open(contribution_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _store_contribution(self, contribution: Dict[str, Any]) -> None:
        """Store a contribution to filesystem.

        Args:
            contribution: Contribution record to store
        """
        if not self.storage_path:
            return

        contribution_path = self.storage_path / f"{contribution['contributionId']}.json"
        with open(contribution_path, 'w', encoding='utf-8') as f:
            json.dump(contribution, f, indent=2, ensure_ascii=False)

    def _get_mock_contribution(self, contribution_id: str) -> Optional[Dict[str, Any]]:
        """Get mock contribution for demo purposes.

        Args:
            contribution_id: ID to get mock data for

        Returns:
            Mock contribution or None
        """
        # Mock data for demonstration
        mock_contributions = {
            'mood-contrib-12345678': {
                'contributionId': 'mood-contrib-12345678',
                'schemaVersion': '1.0.0',
                'policyVersion': '002-draft-1',
                'status': 'verified',
                'submittedAt': '2026-08-29T10:00:00.000Z',
                'contributor': {
                    'type': 'github',
                    'id': 'user123'
                },
                'category': 'code',
                'content': {
                    'title': 'Feature enhancement',
                    'description': 'Added new API endpoint',
                    'url': 'https://github.com/example/repo/pull/123'
                },
                'contentFingerprint': 'sha256:abcdef1234567890',
                'evidence': [
                    {
                        'evidenceId': 'evidence-001',
                        'type': 'pull_request',
                        'observedAt': '2026-08-29T10:00:00.000Z',
                        'verification': {'status': 'verified', 'method': 'github_api'}
                    }
                ],
                'metadata': {
                    'createdBy': 'system',
                    'createdAt': '2026-08-29T10:00:00.000Z'
                }
            }
        }

        return mock_contributions.get(contribution_id)