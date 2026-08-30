"""Scoring system for reputation evidence across multiple dimensions."""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

from .validate import ValidationError


@dataclass
class ScoreDimension:
    """Represents a scoring dimension configuration."""
    name: str
    description: str
    weight: Optional[float] = None
    range_min: int = 1
    range_max: int = 10
    factors: Optional[List[str]] = None


@dataclass
class ScoreResult:
    """Represents a scoring result."""
    contribution_id: str
    scores: Dict[str, float]
    weighted_score: float
    final_score: float
    metadata: Dict[str, Any]


class Scorer:
    """Deterministic scoring system for contribution records."""

    # Define standard scoring dimensions
    STANDARD_DIMENSIONS = [
        ScoreDimension(
            name="contribution",
            description="Quantity and quality of the direct contribution",
            weight=0.25,
            range_min=1,
            range_max=10,
            factors=["code_changes", "documentation_additions", "data_contributions"]
        ),
        ScoreDimension(
            name="impact",
            description="Business value and impact on the ecosystem",
            weight=0.30,
            range_min=1,
            range_max=10,
            factors=["user_impact", "business_value", "ecosystem_effect"]
        ),
        ScoreDimension(
            name="quality",
            description="Technical excellence and maintainability",
            weight=0.20,
            range_min=1,
            range_max=10,
            factors=["testing_coverage", "code_quality", "documentation_quality"]
        ),
        ScoreDimension(
            name="persistence",
            description="Long-term value and sustainability",
            weight=0.15,
            range_min=1,
            range_max=10,
            factors=["maintenance_effort", "longevity", "community_ownership"]
        ),
        ScoreDimension(
            name="early",
            description="Early adoption and pioneering work",
            weight=0.10,
            range_min=1,
            range_max=10,
            factors=["pioneering_contribution", "early_adoption", "breaking_ground"]
        )
    ]

    def __init__(self, dimensions: List[ScoreDimension] = None, custom_weights: Dict[str, float] = None):
        """Initialize scorer with optional custom dimensions and weights.

        Args:
            dimensions: Custom scoring dimensions (defaults to STANDARD_DIMENSIONS)
            custom_weights: Custom weights for dimensions
        """
        self.dimensions = dimensions or self.STANDARD_DIMENSIONS
        self.custom_weights = custom_weights or {}
        # Schema validation will be handled by validate_contribution function

    def score_contribution(self, contribution_id: str, reputation_evidence: Dict[str, Any]) -> ScoreResult:
        """Score a contribution based on reputation evidence.

        Args:
            contribution_id: ID of the contribution being scored
            reputation_evidence: Reputation evidence data

        Returns:
            ScoreResult containing all dimension scores and final score
        """
        # Simple validation for reputation evidence fields
        required_fields = ['contribution', 'impact', 'quality', 'persistence', 'early']
        errors = []

        for field in required_fields:
            if field not in reputation_evidence:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(reputation_evidence[field], (int, float)) or not (1 <= reputation_evidence[field] <= 10):
                errors.append(f"Field '{field}' must be a number between 1 and 10")

        if errors:
            raise ValidationError(f"Invalid reputation evidence: {errors}")

        # Extract scores from evidence
        dimension_scores = self._extract_dimension_scores(reputation_evidence)

        # Apply weights and calculate weighted score
        weighted_score = self._calculate_weighted_score(dimension_scores)

        # Apply any adjustments based on evidence
        final_score = self._apply_evidence_adjustments(weighted_score, reputation_evidence)

        # Create result
        result = ScoreResult(
            contribution_id=contribution_id,
            scores=dimension_scores,
            weighted_score=weighted_score,
            final_score=final_score,
            metadata={
                'dimension_count': len(dimension_scores),
                'weighted': bool(self.custom_weights),
                'adjustments_applied': len(reputation_evidence.get('adjustments', []))
            }
        )

        return result

    def _extract_dimension_scores(self, reputation_evidence: Dict[str, Any]) -> Dict[str, float]:
        """Extract scores from reputation evidence.

        Args:
            reputation_evidence: Reputation evidence data

        Returns:
            Dictionary mapping dimension names to scores
        """
        scores = {}

        # Extract scores from evidence
        for dimension in self.dimensions:
            dimension_name = dimension.name

            if dimension_name in reputation_evidence:
                # Use explicit score if provided
                explicit_score = reputation_evidence[dimension_name]
                scores[dimension_name] = self._clamp_score(explicit_score, dimension)
            else:
                # Calculate score from evidence factors
                score = self._calculate_dimension_score(dimension, reputation_evidence)
                scores[dimension_name] = score

        return scores

    def _calculate_dimension_score(self, dimension: ScoreDimension, evidence: Dict[str, Any]) -> float:
        """Calculate score for a single dimension based on evidence factors.

        Args:
            dimension: The dimension to score
            evidence: Reputation evidence

        Returns:
            Calculated score (1.0 to 10.0)
        """
        if not dimension.factors:
            return 5.0  # Default middle score

        total_score = 0.0
        factor_count = 0

        for factor in dimension.factors:
            factor_score = self._extract_factor_score(factor, evidence)
            if factor_score is not None:
                total_score += factor_score
                factor_count += 1

        if factor_count == 0:
            return 5.0  # Default if no factors found

        return total_score / factor_count

    def _extract_factor_score(self, factor: str, evidence: Dict[str, Any]) -> Optional[float]:
        """Extract score for a specific factor from evidence.

        Args:
            factor: Factor name to extract
            evidence: Reputation evidence

        Returns:
            Score (1.0 to 10.0) or None if factor not found
        """
        # Common factor extraction patterns
        factor_path = factor.split('.')

        # Look for exact match
        if factor in evidence:
            return self._clamp_score(evidence[factor], None)

        # Look for nested paths
        current = evidence
        for key in factor_path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        if isinstance(current, (int, float)):
            return self._clamp_score(current, None)

        return None

    def _clamp_score(self, score: float, dimension: Optional[ScoreDimension] = None) -> float:
        """Clamp score to valid range.

        Args:
            score: Raw score value
            dimension: Optional dimension for custom range

        Returns:
            Clamped score
        """
        min_val = dimension.range_min if dimension else 1
        max_val = dimension.range_max if dimension else 10
        return max(min_val, min(max_val, float(score)))

    def _calculate_weighted_score(self, dimension_scores: Dict[str, float]) -> float:
        """Calculate weighted average of dimension scores.

        Args:
            dimension_scores: Dictionary of dimension scores

        Returns:
            Weighted average score
        """
        if not dimension_scores:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for dimension_name, score in dimension_scores.items():
            # Get weight (use custom weight if available, otherwise default)
            weight = self.custom_weights.get(dimension_name)
            if weight is None:
                # Find dimension to get default weight
                for dim in self.dimensions:
                    if dim.name == dimension_name:
                        weight = dim.weight or 0.2  # Default if no weight
                        break
                else:
                    weight = 0.2  # Fallback weight

            weighted_sum += score * weight
            total_weight += weight

        if total_weight == 0:
            return sum(dimension_scores.values()) / len(dimension_scores)

        return weighted_sum / total_weight

    def _apply_evidence_adjustments(self, base_score: float, evidence: Dict[str, Any]) -> float:
        """Apply adjustments based on additional evidence.

        Args:
            base_score: Base weighted score
            evidence: Full reputation evidence

        Returns:
            Final adjusted score
        """
        final_score = base_score

        # Apply positive adjustments
        for adjustment in evidence.get('adjustments', []):
            if adjustment.get('type') == 'bonus':
                final_score += adjustment.get('value', 0)
            elif adjustment.get('type') == 'penalty':
                final_score += adjustment.get('value', 0)  # Penalties are negative

        # Ensure final score is within bounds
        return self._clamp_score(final_score, None)

    def get_dimension_descriptions(self) -> Dict[str, str]:
        """Get descriptions for all scoring dimensions.

        Returns:
            Dictionary mapping dimension names to descriptions
        """
        return {dim.name: dim.description for dim in self.dimensions}

    def validate_score_consistency(self, result: ScoreResult) -> List[str]:
        """Validate that scores are consistent with evidence.

        Args:
            result: Score result to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check that all dimensions are scored
        dimension_names = {dim.name for dim in self.dimensions}
        scored_dimensions = set(result.scores.keys())
        missing_dimensions = dimension_names - scored_dimensions
        if missing_dimensions:
            errors.append(f"Missing scores for dimensions: {missing_dimensions}")

        # Check score bounds
        for dimension_name, score in result.scores.items():
            dimension = next((d for d in self.dimensions if d.name == dimension_name), None)
            if dimension:
                if score < dimension.range_min or score > dimension.range_max:
                    errors.append(
                        f"Score {score} for '{dimension_name}' outside allowed range "
                        f"[{dimension.range_min}, {dimension.range_max}]"
                    )
            else:
                # For unknown dimensions, use default bounds
                if score < 1 or score > 10:
                    errors.append(
                        f"Score {score} for unknown dimension '{dimension_name}' outside default range [1, 10]"
                    )

        # Check that weighted score matches calculation
        calculated_weighted = self._calculate_weighted_score(result.scores)
        if abs(calculated_weighted - result.weighted_score) > 0.001:
            errors.append(
                f"Weighted score mismatch: calculated {calculated_weighted}, "
                f"recorded {result.weighted_score}"
            )

        return errors