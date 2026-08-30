"""Contribution schema definitions."""

import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import hashlib
import jsonschema


@dataclass
class ScoreAdjustment:
    """Individual score adjustment."""
    type: str  # 'bonus' or 'penalty'
    value: float
    reason: str


@dataclass
class ReviewData:
    """Review data structure."""
    reviewer: str
    review_date: str
    score: Optional[int] = None
    feedback: Optional[str] = None
    strengths: Optional[List[str]] = None
    areas_for_improvement: Optional[List[str]] = None
    recommendation: Optional[str] = None
    appliedAt: Optional[str] = None


@dataclass
class FinalReviewData:
    """Final review data structure."""
    finalReviewer: str
    finalDate: str
    finalDecision: str
    appliedAt: Optional[str] = None


@dataclass
class EvidenceItemSchema:
    """Single evidence item schema."""
    evidence_id: str
    evidence_type: str
    observed_at: str
    verification: Dict[str, Any]
    uri: Optional[str] = None
    digest: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Metadata:
    """Metadata structure."""
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    immutable: bool = False
    review: Optional[Union[ReviewData, FinalReviewData]] = None


@dataclass
class ContributionSchema:
    """Schema for contribution records."""
    contribution_id: str
    schema_version: str
    policy_version: str
    status: str
    submitted_at: str
    contributor: Dict[str, str]
    category: str
    content: Dict[str, Any]
    content_fingerprint: str
    evidence: List[EvidenceItemSchema]
    metadata: Optional[Metadata] = None
    scores: Optional[Dict[str, Union[int, float]]] = None
    reputation_evidence: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContributionSchema':
        """Create schema from dictionary."""
        # Process evidence items
        evidence_items = []
        for evidence in data.get('evidence', []):
            evidence_items.append(EvidenceItemSchema(**evidence))

        # Process metadata
        metadata = None
        if data.get('metadata'):
            metadata_dict = data['metadata']
            review_data = None

            if metadata_dict.get('review'):
                review = metadata_dict['review']
                # Determine if it's a final review
                if all(k in review for k in ['finalReviewer', 'finalDate', 'finalDecision']):
                    review_data = FinalReviewData(
                        finalReviewer=review['finalReviewer'],
                        finalDate=review['finalDate'],
                        finalDecision=review['finalDecision'],
                        appliedAt=review.get('appliedAt')
                    )
                else:
                    review_data = ReviewData(
                        reviewer=review['reviewer'],
                        review_date=review.get('reviewDate', ''),
                        score=review.get('score'),
                        feedback=review.get('feedback'),
                        strengths=review.get('strengths'),
                        areas_for_improvement=review.get('areas_for_improvement'),
                        recommendation=review.get('recommendation'),
                        appliedAt=review.get('appliedAt')
                    )

            metadata = Metadata(
                created_by=metadata_dict.get('createdBy'),
                created_at=metadata_dict.get('createdAt'),
                immutable=metadata_dict.get('immutable', False),
                review=review_data
            )

        # Process scores
        scores = data.get('scores')

        return cls(
            contribution_id=data['contributionId'],
            schema_version=data['schemaVersion'],
            policy_version=data['policyVersion'],
            status=data['status'],
            submitted_at=data['submittedAt'],
            contributor=data['contributor'],
            category=data['category'],
            content=data['content'],
            content_fingerprint=data['contentFingerprint'],
            evidence=evidence_items,
            metadata=metadata,
            scores=scores,
            reputation_evidence=data.get('reputationEvidence')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            'contributionId': self.contribution_id,
            'schemaVersion': self.schema_version,
            'policyVersion': self.policy_version,
            'status': self.status,
            'submittedAt': self.submitted_at,
            'contributor': self.contributor,
            'category': self.category,
            'content': self.content,
            'contentFingerprint': self.content_fingerprint,
            'evidence': [
                {
                    'evidenceId': item.evidence_id,
                    'type': item.evidence_type,
                    'observedAt': item.observed_at,
                    'verification': item.verification,
                    'uri': item.uri,
                    'digest': item.digest,
                    'metadata': item.metadata
                }
                for item in self.evidence
            ],
            'scores': self.scores,
            'reputationEvidence': self.reputation_evidence
        }

        if self.metadata:
            metadata_dict = {
                'createdBy': self.metadata.created_by,
                'createdAt': self.metadata.created_at,
                'immutable': self.metadata.immutable
            }

            if self.metadata.review:
                review = self.metadata.review
                if isinstance(review, FinalReviewData):
                    metadata_dict['review'] = {
                        'finalReviewer': review.finalReviewer,
                        'finalDate': review.finalDate,
                        'finalDecision': review.finalDecision,
                        'appliedAt': review.appliedAt
                    }
                else:
                    review_dict = {
                        'reviewer': review.reviewer,
                        'reviewDate': review.review_date
                    }
                    if review.score is not None:
                        review_dict['score'] = review.score
                    if review.feedback is not None:
                        review_dict['feedback'] = review.feedback
                    if review.strengths is not None:
                        review_dict['strengths'] = review.strengths
                    if review.areas_for_improvement is not None:
                        review_dict['areas_for_improvement'] = review.areas_for_improvement
                    if review.recommendation is not None:
                        review_dict['recommendation'] = review.recommendation
                    if review.appliedAt is not None:
                        review_dict['appliedAt'] = review.appliedAt
                    metadata_dict['review'] = review_dict

            result['metadata'] = metadata_dict

        return result


# JSON Schema for validation
CONTRIBUTION_JSON_SCHEMA = {
    'type': 'object',
    'required': [
        'contributionId',
        'schemaVersion',
        'policyVersion',
        'status',
        'submittedAt',
        'contributor',
        'category',
        'content',
        'contentFingerprint',
        'evidence',
        'metadata'
    ],
    'properties': {
        'contributionId': {
            'type': 'string',
            'pattern': '^mood-contrib-[a-f0-9]{8}$'
        },
        'schemaVersion': {
            'type': 'string',
            'pattern': '^[0-9]+\\.[0-9]+\\.[0-9]+$'
        },
        'policyVersion': {
            'type': 'string',
            'pattern': '^002-draft-[0-9]+$'
        },
        'status': {
            'type': 'string',
            'enum': ['draft', 'submitted', 'under_review', 'verified', 'rejected', 'scored', 'finalized']
        },
        'submittedAt': {
            'type': 'string',
            'format': 'date-time'
        },
        'contributor': {
            'type': 'object',
            'required': ['type', 'id'],
            'properties': {
                'type': {
                    'type': 'string',
                    'enum': ['github', 'wallet', 'protocol_id']
                },
                'id': {
                    'type': 'string'
                }
            }
        },
        'category': {
            'type': 'string',
            'enum': ['code', 'documentation', 'data', 'compute', 'community', 'research']
        },
        'content': {
            'type': 'object',
            'minProperties': 1
        },
        'contentFingerprint': {
            'type': 'string',
            'pattern': '^sha256:[a-f0-9]{64}$'
        },
        'evidence': {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['evidenceId', 'evidenceType', 'observedAt', 'verification'],
                'properties': {
                    'evidenceId': {
                        'type': 'string'
                    },
                    'evidenceType': {
                        'type': 'string',
                        'enum': ['pull_request', 'commit', 'issue', 'merge_request', 'code_review']
                    },
                    'observedAt': {
                        'type': 'string',
                        'format': 'date-time'
                    },
                    'verification': {
                        'type': 'object',
                        'properties': {
                            'status': {
                                'type': 'string',
                                'enum': ['pending', 'verified', 'rejected', 'needs_verification']
                            },
                            'method': {
                                'type': 'string'
                            },
                            'verifiedAt': {
                                'type': 'string',
                                'format': 'date-time'
                            },
                            'verifiedBy': {
                                'type': 'string'
                            }
                        },
                        'required': ['status']
                    },
                    'uri': {
                        'type': 'string',
                        'format': 'uri'
                    },
                    'digest': {
                        'type': 'string',
                        'pattern': '^[a-f0-9]+$'
                    },
                    'metadata': {
                        'type': 'object'
                    }
                }
            }
        },
        'metadata': {
            'type': 'object',
            'properties': {
                'createdBy': {
                    'type': 'string'
                },
                'createdAt': {
                    'type': 'string',
                    'format': 'date-time'
                },
                'immutable': {
                    'type': 'boolean'
                },
                'review': {
                    'oneOf': [
                        {
                            'type': 'object',
                            'properties': {
                                'reviewer': {'type': 'string'},
                                'reviewDate': {'type': 'string', 'format': 'date-time'},
                                'score': {'type': 'integer', 'minimum': 1, 'maximum': 10},
                                'feedback': {'type': 'string'},
                                'strengths': {'type': 'array', 'items': {'type': 'string'}},
                                'areas_for_improvement': {'type': 'array', 'items': {'type': 'string'}},
                                'recommendation': {'type': 'string', 'enum': ['approve', 'reject', 'needs_more']},
                                'appliedAt': {'type': 'string', 'format': 'date-time'}
                            },
                            'required': ['reviewer', 'reviewDate']
                        },
                        {
                            'type': 'object',
                            'properties': {
                                'finalReviewer': {'type': 'string'},
                                'finalDate': {'type': 'string', 'format': 'date-time'},
                                'finalDecision': {'type': 'string', 'enum': ['approved', 'rejected']},
                                'appliedAt': {'type': 'string', 'format': 'date-time'}
                            },
                            'required': ['finalReviewer', 'finalDate', 'finalDecision']
                        }
                    ]
                }
            }
        },
        'scores': {
            'type': 'object',
            'properties': {
                'contribution': {'type': 'number', 'minimum': 0, 'maximum': 10},
                'impact': {'type': 'number', 'minimum': 0, 'maximum': 10},
                'quality': {'type': 'number', 'minimum': 0, 'maximum': 10},
                'persistence': {'type': 'number', 'minimum': 0, 'maximum': 10},
                'early': {'type': 'number', 'minimum': 0, 'maximum': 10}
            }
        },
        'reputationEvidence': {
            'type': 'object',
            'properties': {
                'contribution': {'type': 'number', 'minimum': 0, 'maximum': 10},
                'impact': {'type': 'number', 'minimum': 0, 'maximum': 10},
                'quality': {'type': 'number', 'minimum': 0, 'maximum': 10},
                'persistence': {'type': 'number', 'minimum': 0, 'maximum': 10},
                'early': {'type': 'number', 'minimum': 0, 'maximum': 10},
                'adjustments': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'type': {'type': 'string', 'enum': ['bonus', 'penalty']},
                            'value': {'type': 'number'},
                            'reason': {'type': 'string'}
                        },
                        'required': ['type', 'value', 'reason']
                    }
                }
            }
        }
    },
    'additionalProperties': False
}


def validate_contribution(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate contribution data against schema.

    Args:
        data: Contribution data to validate

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []

    try:
        # Basic structure validation
        jsonschema.validate(instance=data, schema=CONTRIBUTION_JSON_SCHEMA)

        # Custom validations
        if data.get('status') == 'finalized' and not data.get('metadata', {}).get('immutable'):
            errors.append("Finalized contributions must be immutable")

        if data.get('status') in ['verified', 'rejected', 'finalized']:
            if 'review' not in data.get('metadata', {}):
                errors.append("Reviewed contributions must have review data")

        if 'scores' in data and data['status'] not in ['verified', 'scored', 'finalized']:
            errors.append("Scores only allowed for verified or scored contributions")

        # Check for forbidden fields
        forbidden_fields = ['tokenAmount', 'tokenValue', 'reward', 'payment']
        for field in forbidden_fields:
            if field in data or any(field in item for item in data.get('evidence', [])):
                errors.append(f"Forbidden economic field: {field}")

    except jsonschema.ValidationError as e:
        errors.append(f"Schema validation error: {e.message}")
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")

    return len(errors) == 0, errors


def generate_content_fingerprint(data: Dict[str, Any]) -> str:
    """Generate SHA256 fingerprint for content.

    Args:
        data: Data to fingerprint

    Returns:
        SHA256 fingerprint
    """
    # Sort keys for deterministic fingerprinting
    sorted_data = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return f"sha256:{hashlib.sha256(sorted_data.encode('utf-8')).hexdigest()}"