"""Sample contribution data for testing."""

# Sample valid contribution
SAMPLE_CONTRIBUTION = {
    'contributionId': 'mood-contrib-12345678',
    'schemaVersion': '1.0.0',
    'policyVersion': '002-draft-1',
    'status': 'draft',
    'submittedAt': '2026-08-29T10:00:00.000Z',
    'contributor': {
        'type': 'github',
        'id': 'user123'
    },
    'category': 'code',
    'content': {
        'title': 'Authentication API Implementation',
        'description': 'Implemented REST API endpoints for user authentication with JWT tokens',
        'technologies': ['Python', 'FastAPI', 'PostgreSQL'],
        'url': 'https://github.com/example/repo/pull/456',
        'files_changed': 12,
        'additions': 450,
        'deletions': 30,
        'review_comments': 8,
        'tests_passed': 100
    },
    'contentFingerprint': 'sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
    'evidence': [
        {
            'evidenceId': 'pr-456',
            'type': 'pull_request',
            'observedAt': '2026-08-29T10:00:00.000Z',
            'verification': {
                'status': 'verified',
                'method': 'github_api',
                'verifiedAt': '2026-08-29T10:00:00.000Z',
                'verifiedBy': 'system'
            },
            'uri': 'https://github.com/example/repo/pull/456',
            'digest': 'sha256:abc123def456',
            'metadata': {
                'branch': 'feature/auth-api',
                'reviewers': ['user456', 'user789']
            }
        }
    ],
    'metadata': {
        'createdBy': 'system',
        'createdAt': '2026-08-29T10:00:00.000Z'
    }
}

# Sample contribution with multiple evidence
SAMPLE_CONTRIBUTION_MULTIPLE_EVIDENCE = {
    'contributionId': 'mood-contrib-87654321',
    'schemaVersion': '1.0.0',
    'policyVersion': '002-draft-1',
    'status': 'submitted',
    'submittedAt': '2026-08-29T11:30:00.000Z',
    'contributor': {
        'type': 'github',
        'id': 'developer42'
    },
    'category': 'documentation',
    'content': {
        'title': 'API Documentation Enhancement',
        'description': 'Added comprehensive documentation for the public API endpoints',
        'technologies': ['Sphinx', 'reStructuredText'],
        'pages_added': 15,
        'diagrams_created': 3,
        'code_examples': 12
    },
    'contentFingerprint': 'sha256:fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321',
    'evidence': [
        {
            'evidenceId': 'doc-pr-123',
            'type': 'pull_request',
            'observedAt': '2026-08-29T11:30:00.000Z',
            'verification': {
                'status': 'verified',
                'method': 'github_api'
            },
            'uri': 'https://github.com/example/docs/pull/123',
            'metadata': {
                'files_modified': ['api.rst', 'auth.rst', 'examples.rst']
            }
        },
        {
            'evidenceId': 'issue-789',
            'type': 'issue',
            'observedAt': '2026-08-29T11:25:00.000Z',
            'verification': {
                'status': 'verified',
                'method': 'github_api'
            },
            'uri': 'https://github.com/example/docs/issues/789',
            'metadata': {
                'requested_by': 'user101',
                'priority': 'high'
            }
        }
    ],
    'metadata': {
        'createdBy': 'system',
        'createdAt': '2026-08-29T11:30:00.000Z'
    }
}

# Sample reputation evidence
SAMPLE_REPUTATION_EVIDENCE = {
    'contribution': 8,
    'impact': 7,
    'quality': 9,
    'persistence': 6,
    'early': 5,
    'adjustments': [
        {
            'type': 'bonus',
            'value': 1,
            'reason': 'Excellent documentation with comprehensive examples'
        },
        {
            'type': 'penalty',
            'value': -0.5,
            'reason': 'Minor formatting issues in some sections'
        }
    ]
}

# Sample review data
SAMPLE_REVIEW_DATA = {
    'reviewer': 'senior-developer',
    'reviewDate': '2026-08-29T14:00:00.000Z',
    'score': 8,
    'feedback': 'High quality implementation with good test coverage',
    'strengths': [
        'Clean code structure',
        'Comprehensive test suite',
        'Well-documented API'
    ],
    'areas_for_improvement': [
        'Add integration tests for edge cases',
        'Improve error handling in some endpoints'
    ],
    'recommendation': 'approve'
}

# Sample invalid contribution (missing required fields)
INVALID_CONTRIBUTION_MISSING_FIELDS = {
    'contributionId': 'mood-invalid-00000000',
    'schemaVersion': '1.0.0',
    'status': 'draft',
    'submittedAt': '2026-08-29T10:00:00.000Z',
    # Missing contributor, category, content
    'contentFingerprint': 'sha256:invalid',
    'evidence': [],
    'metadata': {}
}

# Sample invalid contribution (forbidden economic field)
INVALID_CONTRIBUTION_ECONOMIC = {
    'contributionId': 'mood-invalid-11111111',
    'schemaVersion': '1.0.0',
    'policyVersion': '002-draft-1',
    'status': 'draft',
    'submittedAt': '2026-08-29T10:00:00.000Z',
    'contributor': {
        'type': 'github',
        'id': 'user123'
    },
    'category': 'code',
    'content': {'title': 'Bad', 'description': 'Has economic data'},
    'contentFingerprint': 'sha256:invalid',
    'evidence': [],
    'metadata': {},
    # Forbidden field
    'tokenAmount': 1000
}

# Sample duplicate evidence
DUPLICATE_EVIDENCE = [
    {
        'evidenceId': 'duplicate-1',
        'type': 'pull_request',
        'observedAt': '2026-08-29T10:00:00.000Z',
        'verification': {
            'status': 'verified',
            'method': 'github_api'
        },
        'uri': 'https://github.com/example/repo/pull/123',
        'digest': 'sha256:common_digest'
    },
    {
        'evidenceId': 'duplicate-2',
        'type': 'pull_request',
        'observedAt': '2026-08-29T10:00:00.000Z',
        'verification': {
            'status': 'verified',
            'method': 'github_api'
        },
        'uri': 'https://github.com/example/repo/pull/123',  # Same URI
        'digest': 'sha256:common_digest'  # Same digest
    }
]

# Test cases
TEST_CASES = {
    'valid_code_contribution': {
        'contributor': {'type': 'github', 'id': 'dev123'},
        'category': 'code',
        'content': {
            'title': 'New Feature',
            'description': 'Added new user preferences feature',
            'implementation': 'Python backend',
            'tests': '24 unit tests'
        },
        'expected_id_prefix': 'mood-contrib'
    },
    'documentation_contribution': {
        'contributor': {'type': 'github', 'id': 'doc_writer'},
        'category': 'documentation',
        'content': {
            'title': 'Getting Started Guide',
            'description': 'Comprehensive guide for new users',
            'sections': 8,
            'examples': 15
        },
        'expected_id_prefix': 'mood-contrib'
    },
    'data_contribution': {
        'contributor': {'type': 'protocol_id', 'id': 'data_contributor_01'},
        'category': 'data',
        'content': {
            'title': 'Dataset Enhancement',
            'description': 'Added 1000 new training samples',
            'dataset_size': '1.2GB',
            'quality_score': 9.5
        },
        'expected_id_prefix': 'mood-contrib'
    },
    'compute_contribution': {
        'contributor': {'type': 'wallet', 'id': '0x123456789abcdef'},
        'category': 'compute',
        'content': {
            'title': 'Model Optimization',
            'description': 'Optimized neural network inference by 40%',
            'performance_gain': '40%',
            'memory_reduction': '25%'
        },
        'expected_id_prefix': 'mood-contrib'
    }
}

# CLI test scenarios
CLI_SCENARIOS = {
    'create_workflow': {
        'commands': [
            'cli.py create --contributor fixtures/sample_contributor.json '
            '--category code --content fixtures/sample_content.json --output temp_contribution.json',
            'cli.py submit temp_contribution.json',
            'cli.py review temp_contribution.json verified fixtures/review_data.json',
            'cli.py score temp_contribution.json fixtures/reputation_evidence.json'
        ]
    },
    'validation_workflow': {
        'commands': [
            'cli.py validate fixtures/valid_contribution.json',
            'cli.py validate fixtures/invalid_contribution.json'
        ]
    },
    'evidence_workflow': {
        'commands': [
            'cli.py get test-id',
            'cli.py evidence test-id fixtures/new_evidence.json',
            'cli.py evidence test-id fixtures/duplicate_evidence.json',
            'cli.py duplicates test-id'
        ]
    }
}