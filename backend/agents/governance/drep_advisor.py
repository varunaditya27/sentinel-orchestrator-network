import logging
from typing import Dict, List, Any
import asyncio

logger = logging.getLogger(__name__)

class DRepAdvisor:
    """DRep recommendation system that analyzes voting history and matches users to compatible DReps."""

    def __init__(self):
        """Initialize with demo DRep data."""
        self.drep_data = {
            "drep1cardanofoundation": {
                "name": "Cardano Foundation DRep",
                "description": "Official foundation delegate focused on ecosystem growth",
                "voting_style": "Progressive",
                "voting_record": {"total_votes": 127, "yes_rate": 73.2},
                "alignment_ranges": {"progressive": (70, 100), "balanced": (40, 70), "conservative": (0, 30)}
            },
            "drep1iog": {
                "name": "IOG DRep",
                "description": "Input Output Global delegate prioritizing technical excellence",
                "voting_style": "Balanced",
                "voting_record": {"total_votes": 89, "yes_rate": 56.2},
                "alignment_ranges": {"progressive": (40, 70), "balanced": (40, 70), "conservative": (30, 50)}
            },
            "drep1emurgo": {
                "name": "Emurgo DRep",
                "description": "Emurgo delegate supporting adoption and education initiatives",
                "voting_style": "Progressive",
                "description": "Emurgo delegate supporting adoption and education initiatives",
                "voting_style": "Progressive",
                "voting_record": {"total_votes": 156, "yes_rate": 78.9},
                "alignment_ranges": {"progressive": (70, 100), "balanced": (50, 80), "conservative": (20, 40)}
            },
            "drep1communitywatchdog": {
                "name": "Community Watchdog DRep",
                "description": "Community-focused delegate ensuring protocol stability",
                "voting_style": "Conservative",
                "voting_record": {"total_votes": 98, "yes_rate": 23.5},
                "alignment_ranges": {"progressive": (0, 30), "balanced": (20, 50), "conservative": (0, 40)}
            }
        }

    def _calculate_alignment_score(self, drep_id: str, preference: str) -> float:
        """Calculate alignment score based on voting history and user preference."""
        drep = self.drep_data[drep_id]
        yes_rate = drep["voting_record"]["yes_rate"]

        # Define preference ranges
        ranges = {
            "progressive": (70.0, 100.0),
            "balanced": (40.0, 70.0),
            "conservative": (0.0, 30.0)
        }

        target_min, target_max = ranges[preference]
        drep_min, drep_max = drep["alignment_ranges"][preference]

        # Calculate score based on how well the DRep's voting aligns with preference
        if target_min <= yes_rate <= target_max:
            score = 100.0
        elif drep_min <= yes_rate <= drep_max:
            score = 80.0
        else:
            # Calculate distance from target range
            if yes_rate < target_min:
                distance = target_min - yes_rate
            else:
                distance = yes_rate - target_max
            score = max(0.0, 100.0 - (distance * 2))

        return round(score, 1)

    async def recommend_dreps(self, preference: str = "balanced") -> Dict[str, Any]:
        """Recommend DReps sorted by alignment with user preference."""
        try:
            if preference not in ["progressive", "balanced", "conservative"]:
                preference = "balanced"

            recommendations = []
            for drep_id, drep_info in self.drep_data.items():
                alignment_score = self._calculate_alignment_score(drep_id, preference)
                voting_style = drep_info["voting_style"]

                recommendation = {
                    "drep_id": drep_id,
                    "name": drep_info["name"],
                    "alignment_score": alignment_score,
                    "voting_style": voting_style,
                    "voting_record": drep_info["voting_record"],
                    "description": drep_info["description"],
                    "recommended": alignment_score >= 70.0
                }
                recommendations.append(recommendation)

            # Sort by alignment score descending
            recommendations.sort(key=lambda x: x["alignment_score"], reverse=True)

            logger.info(f"Generated {len(recommendations)} DRep recommendations for {preference} preference")

            return {
                "success": True,
                "preference": preference,
                "recommendations": recommendations,
                "total_dreps": len(recommendations),
                "timestamp": asyncio.get_event_loop().time()
            }

        except Exception as e:
            logger.error(f"Error in recommend_dreps: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": [],
                "total_dreps": 0
            }

    async def analyze_drep(self, drep_id: str) -> Dict[str, Any]:
        """Analyze a specific DRep's voting history."""
        try:
            if drep_id not in self.drep_data:
                return {
                    "success": False,
                    "error": f"DRep {drep_id} not found",
                    "drep_id": drep_id
                }

            drep_info = self.drep_data[drep_id]

            # Calculate voting statistics
            voting_record = drep_info["voting_record"]
            yes_rate = voting_record["yes_rate"]
            total_votes = voting_record["total_votes"]

            # Determine primary voting style
            if yes_rate >= 70:
                primary_style = "Progressive"
            elif yes_rate >= 40:
                primary_style = "Balanced"
            else:
                primary_style = "Conservative"

            analysis = {
                "drep_id": drep_id,
                "name": drep_info["name"],
                "description": drep_info["description"],
                "voting_style": drep_info["voting_style"],
                "voting_record": voting_record,
                "primary_style": primary_style,
                "consistency_score": min(100.0, yes_rate * 1.2),  # Mock consistency score
                "active_period": "6 months",  # Mock data
                "governance_participation": f"{total_votes} votes cast",
                "alignment_analysis": {
                    "progressive_alignment": self._calculate_alignment_score(drep_id, "progressive"),
                    "balanced_alignment": self._calculate_alignment_score(drep_id, "balanced"),
                    "conservative_alignment": self._calculate_alignment_score(drep_id, "conservative")
                }
            }

            logger.info(f"Analyzed DRep {drep_id}: {drep_info['name']}")

            return {
                "success": True,
                "drep": analysis,
                "timestamp": asyncio.get_event_loop().time()
            }

        except Exception as e:
            logger.error(f"Error in analyze_drep: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "drep_id": drep_id
            }
