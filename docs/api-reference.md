# API Reference

This document provides detailed information about all functions, classes, and parameters in the Mantis AI library.

## Core Functions

### transcribe

```python
mantis.transcribe(
    audio_file: str, 
    raw_output: bool = False,
    clean_output: bool = False,
    model: str = "gemini-1.5-flash",
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
) -> Union[str, TranscriptionOutput]
```

Transcribes audio from a file or YouTube URL.

#### Parameters

- **audio_file** (`str`): Path to the audio file or YouTube URL.
- **raw_output** (`bool`, optional): If `True`, returns the full `TranscriptionOutput` object. If `False` (default), returns just the transcription string.
- **clean_output** (`bool`, optional): If `True`, removes disfluencies, repetitions, and other speech artifacts. If `False` (default), provides the verbatim transcription.
- **model** (`str`, optional): The Gemini model to use for transcription. Default is "gemini-1.5-flash".
- **progress_callback** (`Callable[[ProcessingProgress], None]`, optional): Optional callback function to report progress.

#### Returns

- If `raw_output` is `False` (default): A string containing the transcription.
- If `raw_output` is `True`: A `TranscriptionOutput` object.

#### Raises

- `MantisError`: Base class for all Mantis-specific errors.
- `AudioProcessingError`: If there's an error processing the audio.
- `YouTubeDownloadError`: If there's an error downloading a YouTube video.
- `ModelInferenceError`: If there's an error with the model inference.
- `ValidationError`: If there's a validation error.

#### Example

```python
# Basic usage
transcript = mantis.transcribe("interview.mp3")

# With clean output
clean_transcript = mantis.transcribe("interview.mp3", clean_output=True)

# Get the full output object
result = mantis.transcribe("interview.mp3", raw_output=True)
print(f"Transcription: {result.transcription}")
print(f"Confidence: {result.confidence}")
```

### summarize

```python
mantis.summarize(
    audio_file: str, 
    raw_output: bool = False,
    model: str = "gemini-1.5-flash",
    max_length: Optional[int] = None,
    language: str = "English",
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
) -> Union[str, SummarizeOutput]
```

Summarizes audio from a file or YouTube URL.

#### Parameters

- **audio_file** (`str`): Path to the audio file or YouTube URL.
- **raw_output** (`bool`, optional): If `True`, returns the full `SummarizeOutput` object. If `False` (default), returns just the summary string.
- **model** (`str`, optional): The Gemini model to use for summarization. Default is "gemini-1.5-flash".
- **max_length** (`int`, optional): Optional maximum length for the summary in characters.
- **language** (`str`, optional): Language for the summary output. Default is "English".
- **progress_callback** (`Callable[[ProcessingProgress], None]`, optional): Optional callback function to report progress.

#### Returns

- If `raw_output` is `False` (default): A string containing the summary.
- If `raw_output` is `True`: A `SummarizeOutput` object.

#### Raises

- `MantisError`: Base class for all Mantis-specific errors.
- `AudioProcessingError`: If there's an error processing the audio.
- `YouTubeDownloadError`: If there's an error downloading a YouTube video.
- `ModelInferenceError`: If there's an error with the model inference.
- `ValidationError`: If there's a validation error.

#### Example

```python
# Basic usage
summary = mantis.summarize("lecture.mp3")

# With maximum length
short_summary = mantis.summarize("lecture.mp3", max_length=200)

# In a different language
spanish_summary = mantis.summarize("lecture.mp3", language="Spanish")

# Get the full output object
result = mantis.summarize("lecture.mp3", raw_output=True)
print(f"Summary: {result.summary}")
print(f"Word count: {result.word_count}")
```

### extract

```python
mantis.extract(
    audio_file: str, 
    prompt: str, 
    raw_output: bool = False,
    model: str = "gemini-1.5-flash",
    structured_output: bool = False,
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None
) -> Union[str, ExtractOutput]
```

Extracts information from audio based on a custom prompt.

#### Parameters

- **audio_file** (`str`): Path to the audio file or YouTube URL.
- **prompt** (`str`): Custom prompt specifying what information to extract.
- **raw_output** (`bool`, optional): If `True`, returns the full `ExtractOutput` object. If `False` (default), returns just the extraction string.
- **model** (`str`, optional): The Gemini model to use for extraction. Default is "gemini-1.5-flash".
- **structured_output** (`bool`, optional): Whether to attempt to return structured data. Default is `False`.
- **progress_callback** (`Callable[[ProcessingProgress], None]`, optional): Optional callback function to report progress.

#### Returns

- If `raw_output` is `False` (default): A string containing the extracted information.
- If `raw_output` is `True`: An `ExtractOutput` object.

#### Raises

- `MantisError`: Base class for all Mantis-specific errors.
- `AudioProcessingError`: If there's an error processing the audio.
- `YouTubeDownloadError`: If there's an error downloading a YouTube video.
- `ModelInferenceError`: If there's an error with the model inference.
- `ValidationError`: If there's a validation error.

#### Example

```python
# Basic usage
key_points = mantis.extract("meeting.mp3", "What are the main action items?")

# Request structured output
structured_data = mantis.extract(
    "interview.mp3", 
    "Extract the speaker's name, age, and occupation", 
    structured_output=True
)

# Get the full output object
result = mantis.extract("meeting.mp3", "List all decisions made", raw_output=True)
print(f"Extraction: {result.extraction}")
```

## Logging Functions

### enable_verbose_logging

```python
mantis.enable_verbose_logging()
```

Enables verbose (INFO level) logging for the Mantis package. This is useful for debugging or understanding the processing flow.

#### Example

```python
import mantis

# Enable verbose logging
mantis.enable_verbose_logging()

# Now function calls will produce informational logs
transcript = mantis.transcribe("interview.mp3")
```

### enable_debug_logging

```python
mantis.enable_debug_logging()
```

Enables debug-level logging for the Mantis package. This provides the most detailed logging for troubleshooting issues.

#### Example

```python
import mantis

# Enable debug logging
mantis.enable_debug_logging()

# Now function calls will produce detailed debug logs
transcript = mantis.transcribe("interview.mp3")
```

### enable_warning_logging

```python
mantis.enable_warning_logging()
```

Enables warning-level logging for the Mantis package. This provides only warning and error messages.

#### Example

```python
import mantis

# Enable warning logging
mantis.enable_warning_logging()

# Now function calls will only log warnings and errors
transcript = mantis.transcribe("interview.mp3")
```

## Data Models

### TranscriptionOutput

```python
class TranscriptionOutput(MantisBaseModel):
    transcription: str
    confidence: Optional[float] = None
    duration_seconds: Optional[float] = None
```

Model for the output data after transcription.

#### Attributes

- **transcription** (`str`): The transcribed text from the audio source.
- **confidence** (`float`, optional): Confidence score of the transcription if available.
- **duration_seconds** (`float`, optional): Duration of the audio in seconds if available.

### SummarizeOutput

```python
class SummarizeOutput(MantisBaseModel):
    summary: str
    word_count: int = 0
```

Model for the output data after summarization.

#### Attributes

- **summary** (`str`): The generated summary of the audio content.
- **word_count** (`int`): The word count of the summary.

### ExtractOutput

```python
class ExtractOutput(MantisBaseModel):
    extraction: str
    structured_data: Optional[Dict[str, Any]] = None
```

Model for the output data after extraction.

#### Attributes

- **extraction** (`str`): The extracted information from the audio.
- **structured_data** (`Dict[str, Any]`, optional): Structured data if available.

### ProcessingProgress

```python
class ProcessingProgress(MantisBaseModel):
    stage: str
    progress: float
```

Model for reporting processing progress.

#### Attributes

- **stage** (`str`): The current processing stage (e.g., "Downloading YouTube audio", "Processing with AI model").
- **progress** (`float`): The progress value between 0.0 and 1.0.

## Exception Classes

### MantisError

```python
class MantisError(Exception):
    pass
```

Base class for all Mantis-specific errors.

### AudioProcessingError

```python
class AudioProcessingError(MantisError):
    pass
```

Raised when there's an error processing the audio.

### YouTubeDownloadError

```python
class YouTubeDownloadError(MantisError):
    pass
```

Raised when there's an error downloading a YouTube video.

### ModelInferenceError

```python
class ModelInferenceError(MantisError):
    pass
```

Raised when there's an error with the model inference.

### ValidationError

```python
class ValidationError(MantisError):
    pass
```

Raised when there's a validation error. 