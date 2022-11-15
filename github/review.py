from dataclasses import dataclass
from enum import Enum, auto


class ReviewState(Enum):
    REQUESTED = auto()
    APPROVED = auto()
    COMMENTED = auto()
    CHANGES_REQUESTED = auto()


def create_review_state(state: str) -> ReviewState:
    try:
        return ReviewState[state]
    except KeyError:
        return ReviewState.REQUESTED


REVIEW_STATE_TO_EMOJI = {
    ReviewState.REQUESTED: "⌛",
    ReviewState.APPROVED: "✅",
    ReviewState.COMMENTED: "💬",
    ReviewState.CHANGES_REQUESTED: "❌"
}


@dataclass
class Review:
    author: str
    state: ReviewState

    def __repr__(self):
        return f"{self.author} {REVIEW_STATE_TO_EMOJI[self.state]}"
