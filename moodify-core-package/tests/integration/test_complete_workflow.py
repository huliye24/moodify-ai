"""Integration tests for the complete contribution workflow."""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

from moodify.contribution import ContributionCore, EvidenceBundle, Scorer


class TestCompleteWorkflow:
    """Test the complete contribution workflow from creation to finalization."""

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

    def test_complete_workflow_from_draft_to_finalized(self, core):
        """Test the complete workflow from draft to finalized."""
        # Step 1: Create a new contribution
        contributor = {
            'type': 'github',
            'id': 'developer123'
        }

        content = {
            'title': 'User Authentication System',
            'description': 'Implemented secure JWT-based authentication',
            'technologies': ['Node.js', 'Express', 'PostgreSQL'],
            'features': ['Login', 'Logout', 'Token refresh', 'Password reset'],
            'security_measures': ['Password hashing', 'Rate limiting', 'CSRF protection']
        }

        contribution, errors = core.create_contribution(
            contributor=contributor,
            category='code',
            content=content
        )

        assert not errors
        assert contribution['status'] == 'draft'
        assert 'contributionId' in contribution
        original_id = contribution['contributionId']

        # Step 2: Submit the contribution
        contribution, errors = core.submit_contribution(original_id)
        assert not errors
        assert contribution['status'] == 'submitted'

        # Step 3: Review the contribution (verified)
        review_data = {
            'reviewer': 'tech-lead',
            'date': datetime.now(timezone.utc).isoformat(),
            'score': 9,
            'feedback': 'Excellent implementation with security best practices',
            'recommendation': 'approve'
        }

        contribution, errors = core.review_contribution(
            original_id,
            'verified',
            review_data
        )
        assert not errors
        assert contribution['status'] == 'verified'
        assert 'review' in contribution
        assert contribution['review']['feedback'] == review_data['feedback']

        # Step 4: Score the contribution
        reputation_evidence = {
            'contribution': 9,
            'impact': 8,
            'quality': 9,
            'persistence': 7,
            'early': 6,
            'adjustments': [
                {
                    'type': 'bonus',
                    'value': 1,
                    'reason': 'Outstanding security implementation'
                },
                {
                    'type': 'penalty',
                    'value': -0.3,
                    'reason': 'Minor documentation improvements needed'
                }
            ]
        }

        contribution, errors = core.score_contribution(
            original_id,
            reputation_evidence
        )
        assert not errors
        assert contribution['status'] == 'scored'
        assert 'scores' in contribution
        assert 'reputationEvidence' in contribution
        assert contribution['scores']['contribution'] == 9

        # Step 5: Finalize the contribution
        final_review = {
            'finalReviewer': 'senior-architect',
            'finalDate': datetime.now(timezone.utc).isoformat(),
            'finalDecision': 'Approved for production'
        }

        contribution, errors = core.finalize_contribution(
            original_id,
            final_review
        )
        assert not errors
        assert contribution['status'] == 'finalized'
        assert contribution['metadata']['immutable'] is True
        assert 'review' in contribution['metadata']
        assert contribution['metadata']['review']['finalDecision'] == final_review['finalDecision']

        # Verify contribution is stored
        stored_contribution = core.get_contribution(original_id)
        assert stored_contribution is not None
        assert stored_contribution['status'] == 'finalized'

        # Verify history is complete
        history = core.get_contribution_history(original_id)
        expected_statuses = ['draft', 'submitted', 'verified', 'scored', 'finalized']
        actual_statuses = [entry['status'] for entry in history]

        for status in expected_statuses:
            assert status in actual_statuses

    def test_workflow_with_evidence(self, core):
        """Test workflow with multiple evidence items."""
        # Create contribution
        contributor = {'type': 'github', 'id': 'contributor456'}
        content = {
            'title': 'API Documentation',
            'description': 'Complete REST API documentation',
            'sections': ['Authentication', 'Endpoints', 'Examples']
        }

        contribution, errors = core.create_contribution(
            contributor=contributor,
            category='documentation',
            content=content
        )
        contribution_id = contribution['contributionId']

        # Add evidence
        evidence1 = {
            'evidenceId': 'doc-pr-1',
            'type': 'pull_request',
            'observedAt': datetime.now(timezone.utc).isoformat(),
            'verification': {
                'status': 'verified',
                'method': 'github_api'
            },
            'uri': 'https://github.com/docs/repo/pull/1'
        }

        contribution, errors = core.add_evidence(contribution_id, evidence1)
        assert not errors
        assert len(contribution['evidence']) == 1

        evidence2 = {
            'evidenceId': 'doc-pr-2',
            'type': 'pull_request',
            'observedAt': datetime.now(timezone.utc).isoformat(),
            'verification': {
                'status': 'verified',
                'method': 'github_api'
            },
            'uri': 'https://github.com/docs/repo/pull/2'
        }

        contribution, errors = core.add_evidence(contribution_id, evidence2)
        assert not errors
        assert len(contribution['evidence']) == 2

        # Submit and verify
        core.submit_contribution(contribution_id)
        review_data = {'reviewer': 'doc-team', 'score': 8, 'feedback': 'Great docs'}
        core.review_contribution(contribution_id, 'verified', review_data)

        # Score and finalize
        reputation_evidence = {
            'contribution': 8,
            'impact': 7,
            'quality': 9,
            'persistence': 8,
            'early': 5
        }

        core.score_contribution(contribution_id, reputation_evidence)
        core.finalize_contribution(contribution_id)

        # Verify evidence detection
        duplicates = core.detect_duplicate_evidence(contribution_id)
        # Since these are different PRs, no duplicates expected
        assert len(duplicates) == 0

    def test_workflow_invalid_transitions(self, core):
        """Test that invalid transitions are prevented."""
        # Create a contribution
        contributor = {'type': 'github', 'id': 'user789'}
        content = {'title': 'Test', 'description': 'Test content'}

        contribution, errors = core.create_contribution(
            contributor=contributor,
            category='code',
            content=content
        )
        contribution_id = contribution['contributionId']

        # Try to skip submission (should fail)
        review_data = {'reviewer': 'system', 'feedback': 'Skip submission'}
        _, errors = core.review_contribution(contribution_id, 'verified', review_data)
        assert errors
        assert "Cannot transition" in errors[0]

        # Submit properly
        core.submit_contribution(contribution_id)

        # Try to score without verifying (should fail)
        reputation_evidence = {'contribution': 8, 'impact': 7}
        _, errors = core.score_contribution(contribution_id, reputation_evidence)
        assert errors
        assert "Cannot score" in errors[0]

        # Verify properly
        review_data = {'reviewer': 'system', 'score': 8}
        core.review_contribution(contribution_id, 'verified', review_data)

        # Now scoring should work
        core.score_contribution(contribution_id, reputation_evidence)

        # Try to reject after scoring (should fail as it's immutable)
        review_data = {'reviewer': 'system', 'feedback': 'Changed mind'}
        _, errors = core.review_contribution(contribution_id, 'rejected', review_data)
        assert errors
        assert "Cannot transition" in errors[0]

    def test_workflow_with_evidence_bundle(self, core):
        """Test workflow using EvidenceBundle directly."""
        # Create contribution
        contributor = {'type': 'github', 'id': 'bundle_user'}
        content = {
            'title': 'Test Bundle',
            'description': 'Testing evidence bundle functionality'
        }

        contribution, errors = core.create_contribution(
            contributor=contributor,
            category='code',
            content=content
        )
        contribution_id = contribution['contributionId']

        # Create evidence bundle manually
        evidence_items = [
            {
                'evidenceId': 'bundle-e1',
                'type': 'commit',
                'observedAt': datetime.now(timezone.utc).isoformat(),
                'verification': {'status': 'verified'}
            },
            {
                'evidenceId': 'bundle-e2',
                'type': 'issue',
                'observedAt': datetime.now(timezone.utc).isoformat(),
                'verification': {'status': 'verified'}
            }
        ]

        bundle = EvidenceBundle(evidence_items)

        # Add evidence through bundle
        for item in bundle:
            core.add_evidence(contribution_id, item.to_dict())

        # Verify evidence was added
        stored_contribution = core.get_contribution(contribution_id)
        assert len(stored_contribution['evidence']) == 2

        # Complete workflow
        core.submit_contribution(contribution_id)
        review_data = {'reviewer': 'system', 'score': 7, 'feedback': 'Good'}
        core.review_contribution(contribution_id, 'verified', review_data)

        # Test scoring factors (without explicit scores)
        reputation_evidence = {
            'code_changes': {'commits': 5, 'files': 3},
            'user_impact': {'feedback_positive': 0.9},
            'testing_coverage': {'percentage': 85}
        }

        scored, errors = core.score_contribution(contribution_id, reputation_evidence)
        assert not errors
        assert 'scores' in scored

    def test_workflow_state_machine_constraints(self, core):
        """Test state machine constraints throughout the workflow."""
        # Create contribution
        contributor = {'type': 'github', 'id': 'state_user'}
        content = {'title': 'State Test', 'description': 'State machine testing'}

        contribution, errors = core.create_contribution(
            contributor=contributor,
            category='code',
            content=content
        )
        contribution_id = contribution['contributionId']

        # Check allowed transitions from each state
        # Draft state
        transitions = core.get_allowed_transitions(contribution_id)
        assert 'submitted' in transitions
        assert 'under_review' not in transitions  # Can't jump directly to review

        # Submit
        core.submit_contribution(contribution_id)

        # Submitted state
        transitions = core.get_allowed_transitions(contribution_id)
        assert 'under_review' in transitions
        assert 'verified' not in transitions  # Can't jump directly to verified

        # Review (reject)
        review_data = {'reviewer': 'system', 'feedback': 'Not suitable', 'reasons': ['poor quality']}
        core.review_contribution(contribution_id, 'rejected', review_data)

        # Rejected state (immutable)
        transitions = core.get_allowed_transitions(contribution_id)
        assert len(transitions) == 0  # No allowed transitions from rejected

        # Create a new one to test full workflow
        contribution2, errors = core.create_contribution(
            contributor=contributor,
            category='code',
            content=content
        )
        contribution_id2 = contribution2['contributionId']

        # Submit, verify, score, finalize
        core.submit_contribution(contribution_id2)
        review_data2 = {'reviewer': 'system', 'score': 8, 'feedback': 'Good'}
        core.review_contribution(contribution_id2, 'verified', review_data2)

        reputation_evidence = {'contribution': 8, 'impact': 7, 'quality': 9, 'persistence': 6, 'early': 5}
        core.score_contribution(contribution_id2, reputation_evidence)
        core.finalize_contribution(contribution_id2)

        # Finalized state (immutable)
        transitions = core.get_allowed_transitions(contribution_id2)
        assert len(transitions) == 0  # No allowed transitions from finalized