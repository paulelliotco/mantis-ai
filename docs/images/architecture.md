# Mantis AI Architecture Diagram

This file contains instructions for generating the architecture diagram for Mantis AI documentation.

## Diagram Description

The architecture diagram should illustrate the following components and flow:

1. **Input Layer**:
   - Local Audio Files
   - YouTube URLs

2. **Processing Layer**:
   - Input Handler (validates and prepares audio)
   - Audio Processor (processes audio with Gemini AI)
   - Gemini API (external service)

3. **Output Layer**:
   - Result Formatter
   - Result Output (transcription, summary, extraction)

4. **Core Functions**:
   - transcribe()
   - summarize()
   - extract()

## Diagram Generation

You can generate this diagram using any diagramming tool such as:
- [Mermaid](https://mermaid.js.org/)
- [Draw.io](https://app.diagrams.net/)
- [Lucidchart](https://www.lucidchart.com/)

## Mermaid Code

Here's a Mermaid code snippet that can be used to generate the diagram:

```mermaid
flowchart TD
    A[Audio Source] --> B[Input Handler]
    B --> C[Audio Processor]
    C --> D[Gemini API]
    D --> E[Result Formatter]
    E --> F[Result Output]
    
    subgraph Input Types
        G[Local Audio Files]
        H[YouTube URLs]
    end
    
    subgraph Core Functions
        I[transcribe()]
        J[summarize()]
        K[extract()]
    end
    
    subgraph Output Types
        L[Transcription Text]
        M[Summary Text]
        N[Extraction Results]
    end
    
    G --> A
    H --> A
    C --> I
    C --> J
    C --> K
    I --> E
    J --> E
    K --> E
    E --> L
    E --> M
    E --> N
```

## Placeholder Image

Until the diagram is generated, you can use the ASCII art version in `architecture.txt` as a reference. 