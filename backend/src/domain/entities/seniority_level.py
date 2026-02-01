"""Seniority Level enum and related business logic."""

from enum import Enum
from decimal import Decimal


class SeniorityLevel(str, Enum):
    """
    Seniority levels for project members.
    
    Each level has an associated capacity multiplier as defined in BR-ROLE-004.
    """
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"
    SPECIALIST = "Specialist"
    LEAD = "Lead"

    @property
    def capacity_multiplier(self) -> Decimal:
        """
        Returns the capacity multiplier for this seniority level.
        
        As per BR-ROLE-004:
        - Junior: 0.6x Base Capacity
        - Mid: 1.0x Base Capacity
        - Senior: 1.3x Base Capacity
        - Specialist: 1.2x Base Capacity
        - Lead: 1.1x Base Capacity
        """
        multipliers = {
            SeniorityLevel.JUNIOR: Decimal("0.6"),
            SeniorityLevel.MID: Decimal("1.0"),
            SeniorityLevel.SENIOR: Decimal("1.3"),
            SeniorityLevel.SPECIALIST: Decimal("1.2"),
            SeniorityLevel.LEAD: Decimal("1.1"),
        }
        return multipliers[self]
