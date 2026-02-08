from enum import Enum


class CaseStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

    def can_transition_to(self, new_status: "CaseStatus") -> bool:
        """Define transiciones válidas de estado"""
        transitions = {
            self.OPEN: [self.IN_PROGRESS, self.CLOSED],
            self.IN_PROGRESS: [self.RESOLVED, self.CLOSED],
            self.RESOLVED: [self.CLOSED],
            self.CLOSED: []
        }
        return new_status in transitions.get(self, [])
