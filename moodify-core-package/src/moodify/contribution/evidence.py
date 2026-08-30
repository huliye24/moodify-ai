"""Evidence bundle management and verification."""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Iterator
from dataclasses import dataclass
from pathlib import Path

from .validate import ContributionValidator


@dataclass
class EvidenceItem:
    """A single piece of evidence."""
    evidence_id: str
    evidence_type: str
    observed_at: str
    verification: Dict[str, Any]
    uri: Optional[str] = None
    digest: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            'evidenceId': self.evidence_id,
            'type': self.evidence_type,
            'observedAt': self.observed_at,
            'verification': self.verification
        }
        if self.uri is not None:
            result['uri'] = self.uri
        if self.digest is not None:
            result['digest'] = self.digest
        if self.metadata is not None:
            result['metadata'] = self.metadata
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvidenceItem':
        """Create from dictionary representation."""
        return cls(
            evidence_id=data['evidenceId'],
            evidence_type=data['type'],
            observed_at=data['observedAt'],
            verification=data['verification'],
            uri=data.get('uri'),
            digest=data.get('digest'),
            metadata=data.get('metadata')
        )


class EvidenceBundle:
    """Collection and management of evidence items."""

    def __init__(self, evidence_items: List[Dict[str, Any]] = None):
        """Initialize with optional evidence items."""
        self.items = []
        if evidence_items:
            for item in evidence_items:
                self.add_evidence(item)

    def add_evidence(self, evidence_data: Dict[str, Any], validate: bool = True) -> None:
        """Add evidence to the bundle.

        Args:
            evidence_data: Evidence data to add
            validate: Whether to validate the evidence
        """
        if validate:
            validator = ContributionValidator()
            is_valid, errors = validator.validate_evidence_bundle([evidence_data])
            if not is_valid:
                raise ValueError(f"Invalid evidence: {'; '.join(errors)}")

        # Convert to EvidenceItem and add
        evidence_item = EvidenceItem.from_dict(evidence_data)
        self.items.append(evidence_item)

    def remove_evidence(self, evidence_id: str) -> bool:
        """Remove evidence by ID.

        Args:
            evidence_id: ID of evidence to remove

        Returns:
            True if removed, False if not found
        """
        for i, item in enumerate(self.items):
            if item.evidence_id == evidence_id:
                del self.items[i]
                return True
        return False

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceItem]:
        """Get evidence by ID.

        Args:
            evidence_id: ID of evidence to retrieve

        Returns:
            Evidence item or None if not found
        """
        for item in self.items:
            if item.evidence_id == evidence_id:
                return item
        return None

    def get_evidence_by_type(self, evidence_type: str) -> List[EvidenceItem]:
        """Get all evidence items of a specific type.

        Args:
            evidence_type: Type of evidence to retrieve

        Returns:
            List of evidence items
        """
        return [item for item in self.items if item.evidence_type == evidence_type]

    def verify_evidence(self, evidence_id: str, method: str, verified_by: str) -> None:
        """Mark evidence as verified.

        Args:
            evidence_id: ID of evidence to verify
            method: Method used for verification
            verified_by: Who performed the verification
        """
        item = self.get_evidence(evidence_id)
        if item:
            item.verification.update({
                'status': 'verified',
                'method': method,
                'verifiedAt': datetime.utcnow().isoformat(),
                'verifiedBy': verified_by
            })

    def reject_evidence(self, evidence_id: str, reason: str) -> None:
        """Mark evidence as rejected.

        Args:
            evidence_id: ID of evidence to reject
            reason: Reason for rejection
        """
        item = self.get_evidence(evidence_id)
        if item:
            item.verification.update({
                'status': 'rejected',
                'method': 'manual_review',
                'verifiedAt': datetime.utcnow().isoformat(),
                'verifiedBy': 'system',
                'reason': reason
            })

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert to list of dictionaries."""
        return [item.to_dict() for item in self.items]

    def __len__(self) -> int:
        """Return number of evidence items."""
        return len(self.items)

    def __iter__(self) -> Iterator[EvidenceItem]:
        """Iterate over evidence items."""
        return iter(self.items)


class EvidenceDuplicateDetector:
    """Detects duplicate and semantically similar evidence."""

    def __init__(self, threshold: float = 0.95):
        """Initialize with similarity threshold.

        Args:
            threshold: Similarity threshold for duplicate detection
        """
        self.threshold = threshold

    def find_duplicates(self, bundle: EvidenceBundle) -> Dict[str, List[str]]:
        """Find duplicate evidence items.

        Args:
            bundle: Evidence bundle to search

        Returns:
            Dictionary mapping evidence IDs to lists of duplicate IDs
        """
        duplicates = {}

        for i, item1 in enumerate(bundle.items):
            item_duplicates = []

            for j, item2 in enumerate(bundle.items):
                if i >= j:  # Skip self-comparisons and already checked pairs
                    continue

                similarity = self._calculate_similarity(item1, item2)
                if similarity >= self.threshold:
                    item_duplicates.append(item2.evidence_id)

            if item_duplicates:
                duplicates[item1.evidence_id] = item_duplicates

        return duplicates

    def _calculate_similarity(self, item1: EvidenceItem, item2: EvidenceItem) -> float:
        """Calculate similarity between two evidence items.

        Args:
            item1: First evidence item
            item2: Second evidence item

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Simple implementation: check type, URI, and digest matches
        score = 0.0
        factors = 3

        # Check type match
        if item1.evidence_type == item2.evidence_type:
            score += 1.0 / factors

        # Check URI match (if both have URIs)
        if (item1.uri and item2.uri and
            item1.uri == item2.uri):
            score += 1.0 / factors

        # Check digest match (if both have digests)
        if (item1.digest and item2.digest and
            item1.digest == item2.digest):
            score += 1.0 / factors

        return score