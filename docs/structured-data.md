# Structured Data Extraction

Extract typed, validated data from audio using Pydantic models.

## Basic Usage

```python
from pydantic import BaseModel
from typing import List, Optional

class MovieReview(BaseModel):
    title: str
    rating: float
    pros: List[str]
    cons: List[str]
    reviewer: Optional[str]

# Extract structured data from a movie review
review = mantis.extract_structured("movie_review.mp3", MovieReview)
print(f"Rating: {review.rating}/10")
print("Pros:", ", ".join(review.pros))
```

## Best Practices

1. **Define Clear Models**
   - Use descriptive field names
   - Add field descriptions using `Field(..., description="...")`
   - Use appropriate types (str, int, float, etc.)

2. **Handle Optional Data**
   - Use `Optional[Type]` for fields that might be missing
   - Provide default values where appropriate

3. **Validation Rules**
   - Add field validators using Pydantic's `@validator`
   - Set min/max values for numerical fields

## Examples

### Meeting Notes
```python
class MeetingNotes(BaseModel):
    title: str
    date: datetime
    attendees: List[str]
    action_items: List[dict[str, str]]
    key_decisions: List[str]

notes = mantis.extract_structured("meeting.mp3", MeetingNotes)
```

### Research Interview
```python
class ResearchInterview(BaseModel):
    participant_id: str
    demographics: dict[str, str]
    key_findings: List[str]
    quotes: List[str]

interview = mantis.extract_structured("interview.mp3", ResearchInterview)
```
```

</augment_code_snippet>

These updates will:
1. Document the new structured data extraction feature
2. Provide clear examples and best practices
3. Update navigation to include new sections
4. Keep the documentation in sync with the latest code changes

Would you like me to create any additional documentation sections or elaborate on any of these updates?