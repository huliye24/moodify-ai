"""Comprehensive test suite for the contribution core module."""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from moodify.contribution import (
    ContributionCore,
    ContributionValidator,
    EvidenceBundle,
    EvidenceItem,
    Scorer,
    StateMachine
)


class TestContributionCore:
    """Test the core contribution engine."""

    @pytest.fixture
    def storage_dir(self):
        """Create a temporary storage directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def core(self, storage_dir):
        """Create a contribution core with storage."""
        return ContributionCore(storage_path=str(storage_dir))

    @pytest.fixture
    def sample_contributor(self):
        """Sample contributor data."""
        return {
            'type': 'github',
            'id': 'user123'
        }

    @pytest.fixture
    def sample_content(self):
        """Sample content data."""
        return {
            'title': 'Feature enhancement',
            'description': 'Added new API endpoint for user authentication',
            'url': 'https://github.com/example/repo/pull/123',
            'files_changed': 5,
            'additions': 100,
            'deletions': 20
        }

    @pytest.fixture
    def sample_evidence(self):
        """Sample evidence data."""
        return [
            {
                'evidenceId': 'pr-123',
                'type': 'pull_request',
                'observedAt': '2026-08-29T10:00:00.000Z',
                'verification': {
                    'status': 'verified',
                    'method': 'github_api',
                    'verifiedAt': '2026-08-29T10:00:00.000Z',
                    'verifiedBy': 'system'
                },
                'uri': 'https://github.com/example/repo/pull/123',
                'digest': 'sha256:abc123'
            }
        ]

    def test_create_contribution(self, core, sample_contributor, sample_content):
        """Test creating a new contribution."""
        contribution, errors = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content
        )

        assert not errors
        assert contribution is not None
        assert 'contributionId' in contribution
        assert contribution['contributor'] == sample_contributor
        assert contribution['category'] == 'code'
        assert contribution['content'] == sample_content
        assert contribution['status'] == 'draft'
        assert 'contentFingerprint' in contribution

    def test_create_contribution_with_evidence(self, core, sample_contributor, sample_content, sample_evidence):
        """Test creating a contribution with evidence."""
        contribution, errors = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content,
            evidence=sample_evidence
        )

        assert not errors
        assert contribution is not None
        assert len(contribution['evidence']) == 1
        assert contribution['evidence'][0] == sample_evidence[0]

    def test_create_contribution_invalid_data(self, core):
        """Test creating a contribution with invalid data."""
        # Missing required fields
        contribution, errors = core.create_contribution(
            contributor={},
            category='',
            content={}
        )

        assert errors
        assert "Missing required contributor field" in errors[0]
        assert contribution == {}

    def test_submit_contribution(self, core, sample_contributor, sample_content):
        """Test submitting a contribution."""
        # Create first
        contribution, _ = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content
        )

        # Submit
        updated, errors = core.submit_contribution(contribution['contributionId'])

        assert not errors
        assert updated['status'] == 'submitted'

    def test_submit_nonexistent_contribution(self, core):
        """Test submitting a non-existent contribution."""
        _, errors = core.submit_contribution('nonexistent-id')

        assert errors
        assert "not found" in errors[0]

    def test_review_contribution(self, core, sample_contributor, sample_content):
        """Test reviewing a contribution."""
        # Create and submit
        contribution, _ = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content
        )
        core.submit_contribution(contribution['contributionId'])

        # Review as verified
        review_data = {
            'reviewer': 'system',
            'feedback': 'Excellent contribution',
            'score': 8
        }

        updated, errors = core.review_contribution(
            contribution['contributionId'],
            'verified',
            review_data
        )

        assert not errors
        assert updated['status'] == 'verified'
        assert 'review' in updated
        assert updated['review']['feedback'] == 'Excellent contribution'

    def test_reject_contribution(self, core, sample_contributor, sample_content):
        """Test rejecting a contribution."""
        # Create and submit
        contribution, _ = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content
        )
        core.submit_contribution(contribution['contributionId'])

        # Reject
        review_data = {
            'reviewer': 'system',
            'feedback': 'Does not meet quality standards',
            'reasons': ['insufficient testing', 'documentation incomplete']
        }

        updated, errors = core.review_contribution(
            contribution['contributionId'],
            'rejected',
            review_data
        )

        assert not errors
        assert updated['status'] == 'rejected'
        assert 'review' in updated
        assert updated['review']['reasons'] == ['insufficient testing', 'documentation incomplete']

    def test_add_evidence(self, core, sample_contributor, sample_content, sample_evidence):
        """Test adding evidence to a contribution."""
        # Create and submit
        contribution, _ = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content
        )
        core.submit_contribution(contribution['contributionId'])

        # Add evidence
        new_evidence = {
            'evidenceId': 'issue-456',
            'type': 'issue',
            'observedAt': '2026-08-29T11:00:00.000Z',
            'verification': {
                'status': 'verified',
                'method': 'github_api'
            },
            'uri': 'https://github.com/example/repo/issues/456'
        }

        updated, errors = core.add_evidence(
            contribution['contributionId'],
            new_evidence
        )

        assert not errors
        assert len(updated['evidence']) == 2
        assert new_evidence in updated['evidence']

    def test_score_contribution(self, core, sample_contributor, sample_content):
        """Test scoring a contribution."""
        # Create, submit, and verify
        contribution, _ = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content
        )
        core.submit_contribution(contribution['contributionId'])

        review_data = {'reviewer': 'system', 'feedback': 'Good work'}
        core.review_contribution(contribution['contributionId'], 'verified', review_data)

        # Score
        reputation_evidence = {
            'contribution': 8,
            'impact': 7,
            'quality': 9,
            'persistence': 6,
            'early': 5,
            'adjustments': [
                {'type': 'bonus', 'value': 1, 'reason': 'Excellent documentation'},
                {'type': 'penalty', 'value': -0.5, 'reason': 'Minor performance issue'}
            ]
        }

        scored, errors = core.score_contribution(
            contribution['contributionId'],
            reputation_evidence
        )

        assert not errors
        assert scored['status'] == 'scored'
        assert 'scores' in scored
        assert 'reputationEvidence' in scored
        assert scored['scores']['contribution'] == 8
        assert scored['scores']['impact'] == 7

    def test_score_unverified_contribution(self, core, sample_contributor, sample_content):
        """Test scoring an unverified contribution (should fail)."""
        # Create but don't submit/verify
        contribution, _ = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content
        )

        # Try to score
        reputation_evidence = {'contribution': 8, 'impact': 7}
        _, errors = core.score_contribution(contribution['contributionId'], reputation_evidence)

        assert errors
        assert "Cannot score" in errors[0]

    def test_finalize_contribution(self, core, sample_contributor, sample_content):
        """Test finalizing a contribution."""
        # Create, submit, verify, and score
        contribution, _ = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content
        )
        core.submit_contribution(contribution['contributionId'])

        review_data = {'reviewer': 'system', 'feedback': 'Good work'}
        core.review_contribution(contribution['contributionId'], 'verified', review_data)

        reputation_evidence = {'contribution': 8, 'impact': 7}
        core.score_contribution(contribution['contributionId'], reputation_evidence)

        # Finalize
        finalized, errors = core.finalize_contribution(contribution['contributionId'])

        assert not errors
        assert finalized['status'] == 'finalized'
        assert finalized['metadata']['immutable'] is True

    def test_get_contribution(self, core, sample_contributor, sample_content):
        """Test retrieving a contribution."""
        # Create
        contribution, _ = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content
        )

        # Get
        retrieved = core.get_contribution(contribution['contributionId'])

        assert retrieved is not None
        assert retrieved['contributionId'] == contribution['contributionId']

    def test_get_nonexistent_contribution(self, core):
        """Test retrieving a non-existent contribution."""
        retrieved = core.get_contribution('nonexistent-id')
        assert retrieved is None

    def test_get_history(self, core, sample_contributor, sample_content):
        """Test retrieving contribution history."""
        # Create, submit, and verify
        contribution, _ = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content
        )
        core.submit_contribution(contribution['contributionId'])

        review_data = {'reviewer': 'system', 'feedback': 'Good work'}
        core.review_contribution(contribution['contributionId'], 'verified', review_data)

        # Get history
        history = core.get_contribution_history(contribution['contributionId'])

        assert len(history) >= 3  # created, submitted, reviewed
        assert history[0]['status'] == 'draft'
        assert history[1]['status'] == 'submitted'
        assert history[2]['status'] == 'verified'

    def test_detect_duplicates(self, core, sample_contributor, sample_content, sample_evidence):
        """Test detecting duplicate evidence."""
        # Create with evidence
        contribution, _ = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content,
            evidence=sample_evidence
        )

        # Add duplicate evidence
        duplicate_evidence = {
            'evidenceId': 'pr-123-duplicate',
            'type': 'pull_request',
            'observedAt': '2026-08-29T10:00:00.000Z',
            'verification': {'status': 'verified', 'method': 'github_api'},
            'uri': 'https://github.com/example/repo/pull/123',
            'digest': 'sha256:abc123'
        }

        core.add_evidence(contribution['contributionId'], duplicate_evidence)

        # Detect duplicates
        duplicates = core.detect_duplicate_evidence(contribution['contributionId'])

        assert len(duplicates) > 0
        assert any('pr-123' in key for key in duplicates.keys())

    def test_get_allowed_transitions(self, core, sample_contributor, sample_content):
        """Test getting allowed state transitions."""
        # Create
        contribution, _ = core.create_contribution(
            contributor=sample_contributor,
            category='code',
            content=sample_content
        )

        # From draft
        transitions = core.get_allowed_transitions(contribution['contributionId'])
        assert 'submitted' in transitions

        # Submit
        core.submit_contribution(contribution['contributionId'])

        # From submitted
        transitions = core.get_allowed_transitions(contribution['contributionId'])
        assert 'under_review' in transitions


class TestContributionValidator:
    """Test the contribution validator."""

    @pytest.fixture
    def validator(self):
        """Create a contribution validator."""
        return ContributionValidator()

    def test_valid_contribution(self, validator):
        """Test validating a valid contribution."""
        data = {
            'contributionId': 'mood-contrib-12345678',
            'schemaVersion': '1.0.0',
            'policyVersion': '002-draft-1',
            'status': 'draft',
            'submittedAt': '2026-08-29T10:00:00.000Z',
            'contributor': {'type': 'github', 'id': 'user123'},
            'category': 'code',
            'content': {'title': 'Feature', 'description': 'New feature'},
            'contentFingerprint': 'sha256:abcdef',
            'evidence': [],
            'metadata': {}
        }

        is_valid, errors = validator.validate_contribution(data)
        assert is_valid
        assert len(errors) == 0

    def test_invalid_contributor(self, validator):
        """Test validating invalid contributor data."""
        data = {
            'contributionId': 'mood-contrib-12345678',
            'schemaVersion': '1.0.0',
            'status': 'draft',
            'submittedAt': '2026-08-29T10:00:00.000Z',
            'contributor': {'id': ''},  # Missing type
            'category': 'code',
            'content': {},
            'contentFingerprint': 'sha256:abcdef',
            'evidence': [],
            'metadata': {}
        }

        is_valid, errors = validator.validate_contribution(data)
        assert not is_valid
        assert any("Missing required contributor field" in e for e in errors)

    def test_forbidden_economic_fields(self, validator):
        """Test detection of forbidden economic fields."""
        data = {
            'contributionId': 'mood-contrib-12345678',
            'schemaVersion': '1.0.0',
            'status': 'draft',
            'submittedAt': '2026-08-29T10:00:00.000Z',
            'contributor': {'type': 'github', 'id': 'user123'},
            'category': 'code',
            'content': {},
            'contentFingerprint': 'sha256:abcdef',
            'evidence': [],
            'metadata': {},
            'tokenAmount': 100  # Forbidden field
        }

        is_valid, errors = validator.validate_contribution(data)
        assert not is_valid
        assert any("Forbidden economic field" in e for e in errors)

    def test_invalid_content_fingerprint(self, validator):
        """Test content fingerprint verification."""
        data = {
            'contributionId': 'mood-contrib-12345678',
            'schemaVersion': '1.0.0',
            'status': 'draft',
            'submittedAt': '2026-08-29T10:00:00.000Z',
            'contributor': {'type': 'github', 'id': 'user123'},
            'category': 'code',
            'content': {'title': 'Feature', 'description': 'New feature'},
            'contentFingerprint': 'sha256:wrong',  # Wrong fingerprint
            'evidence': [],
            'metadata': {}
        }

        is_valid, errors = validator.validate_contribution(data)
        assert not is_valid
        assert any("Content fingerprint does not match" in e for e in errors)


class TestEvidenceBundle:
    """Test the evidence bundle functionality."""

    @pytest.fixture
    def sample_evidence(self):
        """Sample evidence data."""
        return [
            {
                'evidenceId': 'e1',
                'type': 'pull_request',
                'observedAt': '2026-08-29T10:00:00.000Z',
                'verification': {'status': 'verified'}
            },
            {
                'evidenceId': 'e2',
                'type': 'issue',
                'observedAt': '2026-08-29T11:00:00.000Z',
                'verification': {'status': 'verified'}
            }
        ]

    def test_evidence_bundle_creation(self, sample_evidence):
        """Test creating an evidence bundle."""
        bundle = EvidenceBundle(sample_evidence)

        assert len(bundle) == 2
        assert bundle.get_evidence('e1') is not None
        assert bundle.get_evidence('e2') is not None

    def test_add_evidence(self, sample_evidence):
        """Test adding evidence to bundle."""
        bundle = EvidenceBundle()
        bundle.add_evidence(sample_evidence[0])

        assert len(bundle) == 1
        assert bundle.get_evidence('e1') is not None

    def test_remove_evidence(self, sample_evidence):
        """Test removing evidence from bundle."""
        bundle = EvidenceBundle(sample_evidence)
        assert bundle.remove_evidence('e1') is True
        assert bundle.remove_evidence('nonexistent') is False
        assert len(bundle) == 1

    def test_get_evidence_by_type(self, sample_evidence):
        """Test getting evidence by type."""
        bundle = EvidenceBundle(sample_evidence)

        pr_evidence = bundle.get_evidence_by_type('pull_request')
        assert len(pr_evidence) == 1
        assert pr_evidence[0].evidence_id == 'e1'

        issue_evidence = bundle.get_evidence_by_type('issue')
        assert len(issue_evidence) == 1
        assert issue_evidence[0].evidence_id == 'e2'

    def test_verify_evidence(self, sample_evidence):
        """Test verifying evidence."""
        bundle = EvidenceBundle(sample_evidence)

        bundle.verify_evidence('e1', 'manual_review', 'reviewer1')
        evidence = bundle.get_evidence('e1')

        assert evidence.verification['status'] == 'verified'
        assert evidence.verification['method'] == 'manual_review'
        assert evidence.verification['verifiedBy'] == 'reviewer1'

    def test_reject_evidence(self, sample_evidence):
        """Test rejecting evidence."""
        bundle = EvidenceBundle(sample_evidence)

        bundle.reject_evidence('e1', 'Does not meet requirements')
        evidence = bundle.get_evidence('e1')

        assert evidence.verification['status'] == 'rejected'
        assert evidence.verification['reason'] == 'Does not meet requirements'


class TestScorer:
    """Test the scoring system."""

    @pytest.fixture
    def scorer(self):
        """Create a scorer."""
        return Scorer()

    @pytest.fixture
    def sample_reputation_evidence(self):
        """Sample reputation evidence."""
        return {
            'contribution': 8,
            'impact': 7,
            'quality': 9,
            'persistence': 6,
            'early': 5,
            'adjustments': [
                {'type': 'bonus', 'value': 1, 'reason': 'Excellent documentation'},
                {'type': 'penalty', 'value': -0.5, 'reason': 'Minor issue'}
            ]
        }

    def test_score_contribution(self, scorer, sample_reputation_evidence):
        """Test scoring a contribution."""
        result = scorer.score_contribution('test-id', sample_reputation_evidence)

        assert result.contribution_id == 'test-id'
        assert len(result.scores) == 5
        assert result.scores['contribution'] == 8
        assert result.scores['impact'] == 7
        assert result.scores['quality'] == 9
        assert result.scores['persistence'] == 6
        assert result.scores['early'] == 5
        assert result.weighted_score > 0

    def test_score_with_factors(self, scorer):
        """Test scoring using evidence factors."""
        evidence = {
            'code_changes': {'commits': 5, 'files': 3},
            'user_impact': {'users_affected': 1000, 'feedback_positive': 0.95},
            'testing_coverage': {'percentage': 85, 'integration_tests': True}
        }

        result = scorer.score_contribution('test-id', evidence)

        assert result.contribution_id == 'test-id'
        assert 'contribution' in result.scores
        assert 'impact' in result.scores
        assert 'quality' in result.scores

    def test_clamp_score(self, scorer):
        """Test score clamping."""
        # Test with default range (1-10)
        assert scorer._clamp_score(0) == 1
        assert scorer._clamp_score(5) == 5
        assert scorer._clamp_score(15) == 10

        # Test with custom dimension
        dimension = scorer.STANDARD_DIMENSIONS[0]  # contribution (1-10)
        assert scorer._clamp_score(-1, dimension) == 1
        assert scorer._clamp_score(5, dimension) == 5
        assert scorer._clamp_score(12, dimension) == 10

    def test_validate_score_consistency(self, scorer, sample_reputation_evidence):
        """Test score consistency validation."""
        result = scorer.score_contribution('test-id', sample_reputation_evidence)

        # Valid result should have no errors
        errors = scorer.validate_score_consistency(result)
        assert len(errors) == 0

        # Test with inconsistent scores
        result.scores['unknown_dimension'] = 15  # Out of bounds
        errors = scorer.validate_score_consistency(result)
        # Check that at least one error is about score range
        range_errors = [e for e in errors if "outside" in e and "range" in e]
        assert len(range_errors) > 0


class TestStateMachine:
    """Test the state machine."""

    @pytest.fixture
    def state_machine(self):
        """Create a state machine."""
        return StateMachine()

    def test_can_transition(self, state_machine):
        """Test transition validation."""
        # Valid transitions
        assert state_machine.can_transition('draft', 'submitted')
        assert state_machine.can_transition('submitted', 'under_review')
        assert state_machine.can_transition('under_review', 'verified')
        assert state_machine.can_transition('verified', 'scored')
        assert state_machine.can_transition('scored', 'finalized')

        # Invalid transitions
        assert not state_machine.can_transition('draft', 'under_review')
        assert not state_machine.can_transition('verified', 'submitted')
        assert not state_machine.can_transition('finalized', 'scored')

    def test_get_allowed_transitions(self, state_machine):
        """Test getting allowed transitions."""
        transitions = state_machine.get_allowed_transitions('under_review')
        assert 'rejected' in transitions
        assert 'needs_more_evidence' in transitions
        assert 'verified' in transitions
        assert len(transitions) == 3

    def test_is_terminal_state(self, state_machine):
        """Test terminal state detection."""
        assert state_machine.is_terminal_state('rejected')
        assert state_machine.is_terminal_state('finalized')
        assert not state_machine.is_terminal_state('draft')
        assert not state_machine.is_terminal_state('verified')

    def test_apply_transition(self, state_machine):
        """Test applying state transitions."""
        contribution = {
            'contributionId': 'test-id',
            'status': 'draft',
            'metadata': {}
        }

        # Submit
        updated = state_machine.apply_transition(contribution, 'submitted')
        assert updated['status'] == 'submitted'
        assert 'review' not in updated['metadata']

        # Go to under_review first
        review_data = {'reviewer': 'system', 'feedback': 'Good work'}
        updated = state_machine.apply_transition(updated, 'under_review', review_data)
        assert updated['status'] == 'under_review'

        # Then verify
        updated = state_machine.apply_transition(updated, 'verified', review_data)
        assert updated['status'] == 'verified'
        assert 'review' in updated['metadata']

        # Try invalid transition
        with pytest.raises(Exception):
            state_machine.apply_transition(updated, 'submitted')