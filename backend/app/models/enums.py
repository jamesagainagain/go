from enum import Enum


class ComfortLevel(str, Enum):
    SOLO_OK = "solo_ok"
    PREFER_OTHERS = "prefer_others"
    NEED_FAMILIAR = "need_familiar"


class ActivationStage(str, Enum):
    SUGGEST = "suggest"
    RECOMMEND = "recommend"
    PRECOMMIT = "precommit"
    ACTIVATE = "activate"


class OpportunityTier(str, Enum):
    STRUCTURED = "structured"
    RECURRING_PATTERN = "recurring_pattern"
    MICRO_COORDINATION = "micro_coordination"
    SOLO_NUDGE = "solo_nudge"


class ActivationResponse(str, Enum):
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    EXPIRED = "expired"
    SNOOZED = "snoozed"
