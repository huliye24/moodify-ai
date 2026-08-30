"""Deterministic contribution ID generation and content fingerprinting."""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional


def normalize_wallet_address(address: str) -> str:
    """Normalize a wallet address to its canonical form.

    Args:
        address: The wallet address (e.g., '0x...')

    Returns:
        Normalized lowercase address without leading '0x'
    """
    return address.lower().replace('0x', '')


def generate_contribution_id(
    schema_version: str,
    contributor_type: str,
    contributor_id: str,
    category: str,
    content_fingerprint: str,
    submitted_at: str
) -> str:
    """Generate a deterministic contribution ID.

    Args:
        schema_version: Schema version (e.g., '1.0.0')
        contributor_type: Type of contributor (wallet, github, protocol_id)
        contributor_id: Normalized contributor ID
        category: Contribution category
        content_fingerprint: SHA256 content fingerprint
        submitted_at: ISO8601 timestamp of submission

    Returns:
        Deterministic contribution ID
    """
    # Create deterministic input string
    input_data = f"{schema_version}:{contributor_type}:{contributor_id}:{category}:{content_fingerprint}:{submitted_at}"

    # Generate SHA256 hash
    hash_obj = hashlib.sha256(input_data.encode('utf-8'))
    return f"mood-contrib-{hash_obj.hexdigest()[:8]}"


def generate_content_fingerprint(data: Dict[str, Any]) -> str:
    """Generate a canonical SHA256 fingerprint of contribution data.

    The fingerprint excludes mutable review fields and preserves determinism
    regardless of key order in evidence arrays.

    Args:
        data: The contribution record data

    Returns:
        SHA256 fingerprint in format 'sha256:...'
    """
    # Create a copy to avoid modifying original
    normalized_data = data.copy()

    # Exclude mutable review fields from fingerprint
    normalized_data.pop('review', None)
    normalized_data.pop('scores', None)
    normalized_data.pop('reputationEvidence', None)
    normalized_data.pop('supersedes', None)

    # Normalize evidence arrays to be deterministic
    if 'evidence' in normalized_data:
        # Sort evidence by evidenceId to ensure deterministic ordering
        normalized_evidence = []
        for evidence in normalized_data['evidence']:
            if isinstance(evidence, dict):
                # Convert to sorted dict for consistent JSON
                sorted_evidence = dict(sorted(evidence.items()))
                normalized_evidence.append(sorted_evidence)
        normalized_data['evidence'] = sorted(normalized_evidence, key=lambda x: x.get('evidenceId', ''))

    # Create canonical JSON string (sorted keys, no whitespace)
    canonical_json = json.dumps(normalized_data, sort_keys=True, separators=(',', ':'))

    # Generate SHA256 hash
    hash_obj = hashlib.sha256(canonical_json.encode('utf-8'))
    return f"sha256:{hash_obj.hexdigest()}"


def verify_content_fingerprint(data: Dict[str, Any], expected_fingerprint: str) -> bool:
    """Verify that data matches expected content fingerprint.

    Args:
        data: The contribution record data
        expected_fingerprint: Expected SHA256 fingerprint

    Returns:
        True if fingerprints match
    """
    actual_fingerprint = generate_content_fingerprint(data)
    return actual_fingerprint == expected_fingerprint