"""Reusable structured response schemas for common audio intelligence tasks."""
from __future__ import annotations

from typing import Dict, List, Optional, Type

from pydantic import BaseModel, Field


class BaseSchemaModel(BaseModel):
    """Shared configuration for reusable schema models."""

    model_config = {
        "extra": "forbid",
        "frozen": True,
    }


class ActionItem(BaseSchemaModel):
    """Represents a follow-up task discovered in the conversation."""

    description: str = Field(..., description="Plain-language description of the action item.")
    owner: Optional[str] = Field(
        None,
        description="Person or team responsible for completing the action item if mentioned.",
    )
    due_date: Optional[str] = Field(
        None,
        description="Due date in ISO-8601 format or natural language if explicitly stated.",
    )
    priority: Optional[str] = Field(
        None,
        description="Priority or urgency label if available (e.g., high, medium, low).",
    )


class EntityMention(BaseSchemaModel):
    """Key entity referenced in the audio."""

    name: str = Field(..., description="Canonical name or label for the entity.")
    type: Optional[str] = Field(
        None,
        description="Entity type such as person, company, product, metric, etc.",
    )
    context: Optional[str] = Field(
        None,
        description="Short explanation of how the entity was referenced in the audio.",
    )


class SpeakerInsight(BaseSchemaModel):
    """Highlights for a single speaker."""

    speaker: str = Field(..., description="Name or label associated with the speaker.")
    highlights: List[str] = Field(
        default_factory=list,
        description="Key points or themes discussed by this speaker.",
    )
    sentiment: Optional[str] = Field(
        None,
        description="Overall sentiment expressed by the speaker (positive, neutral, negative).",
    )


class SentimentSnapshot(BaseSchemaModel):
    """Overall emotional tone of the audio."""

    overall: str = Field(..., description="Overall sentiment such as positive, neutral, or negative.")
    confidence: Optional[str] = Field(
        None,
        description="Model-provided confidence or justification for the sentiment classification.",
    )
    supporting_evidence: Optional[str] = Field(
        None,
        description="Relevant quotes or paraphrased evidence supporting the sentiment judgment.",
    )


class AudioInsightsSchema(BaseSchemaModel):
    """Default schema combining several common audio intelligence signals."""

    summary: Optional[str] = Field(
        None,
        description="Brief summary capturing the main outcome of the audio segment.",
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="Bullet-friendly list of the most important discussion points.",
    )
    action_items: List[ActionItem] = Field(
        default_factory=list,
        description="Collection of follow-up tasks mentioned in the audio.",
    )
    speakers: List[SpeakerInsight] = Field(
        default_factory=list,
        description="Insights grouped by speaker or participant.",
    )
    entities: List[EntityMention] = Field(
        default_factory=list,
        description="Important entities or concepts referenced in the audio.",
    )
    sentiment: Optional[SentimentSnapshot] = Field(
        None,
        description="High-level sentiment assessment for the entire audio clip.",
    )


class ActionItemListSchema(BaseSchemaModel):
    """Focused schema that only returns action items."""

    action_items: List[ActionItem] = Field(
        default_factory=list,
        description="Action items extracted from the audio.",
    )


class SpeakerSummarySchema(BaseSchemaModel):
    """Focused schema for summarising each speaker's contribution."""

    speakers: List[SpeakerInsight] = Field(
        default_factory=list,
        description="List of speakers with associated highlights and sentiment.",
    )


COMMON_RESPONSE_SCHEMAS: Dict[str, Type[BaseSchemaModel]] = {
    "audio_insights": AudioInsightsSchema,
    "action_items": ActionItemListSchema,
    "speaker_summary": SpeakerSummarySchema,
}

__all__ = [
    "ActionItem",
    "EntityMention",
    "SpeakerInsight",
    "SentimentSnapshot",
    "AudioInsightsSchema",
    "ActionItemListSchema",
    "SpeakerSummarySchema",
    "COMMON_RESPONSE_SCHEMAS",
]
