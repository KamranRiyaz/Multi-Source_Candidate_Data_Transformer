# Step 1: Technical Design

**Name:** Kamran Riyaz
**Email:** riyazkamran03@gmail.com
**Role:** Eightfold Engineering Intern (Jul-Dec 2026)

## 1. Pipeline Breakdown

The system uses a strict **Chain of Responsibility** pattern to ensure determinism:

1. **Extract**: Source-specific adapters parse inputs (CSV, ATS JSON, GitHub, Notes) and map them to a uniform `ExtractedCandidate` dictionary.
2. **Normalize**: Cleans data immediately after extraction. Applies RegEx and mappings (e.g., E.164 phone formats, lowercase emails).
3. **Merge (Conflict Resolution)**: Combines the normalized sources into a single `CanonicalProfile`. It tracks provenance (where a value came from) and calculates an overall confidence score.
4. **Project (Runtime Config)**: A dynamic layer that reshapes the `CanonicalProfile` into the user-defined JSON shape using dot-notation path resolution.
5. **Validate**: (Handled implicitly via Pydantic in FastAPI) Ensures the final output doesn't violate type constraints.

## 2. Canonical Schema & Normalization

- **Phone Numbers**: Strips whitespace/symbols. Formats to **E.164** (e.g., `+15550192834`). Defaults to adding `+1` for 10-digit numbers.
- **Dates**: Normalizes formats like "Jan 2020", "01/2020", or "2020-01-15" to **YYYY-MM**. Retains "Present" for current roles.
- **Location / Country**: Maps variations ("USA", "United States", "uk") to **ISO-3166 alpha-2** (e.g., "US", "GB").
- **Skills**: Canonicalizes variations (e.g., "reactjs" &rarr; "React", "python 3" &rarr; "Python") to prevent duplicate entries.
- **Output**: The canonical model utilizes Python data classes (Pydantic) mapping directly to the requested fields (`full_name`, `emails`, `location`, `experience`, `provenance`, etc.).

## 3. Merge & Conflict-Resolution Policy

- **Confidence Weights**: Every source is assigned a base reliability score (ATS = 0.95, CSV = 0.85, GitHub = 0.75, Notes = 0.50).
- **Single-Value Fields (Name, Headline, Location)**: The merger acts as a Priority Queue. It selects the value from the source with the highest confidence weight that provided a non-null value.
- **Array Fields (Emails, Phones, Skills)**: Values are unioned across all sources. Because they are normalized _before_ merging, exact matches naturally deduplicate using Set logic.
- **Confidence Assignment**: The `overall_confidence` score is an average of the confidence weights of the contributing sources, rewarding profiles corroborated by highly-structured data.

## 4. Handling Runtime Custom-Output Config

The `Projector` layer completely isolates internal logic from external requirements:

- **Path Resolution**: Supports dot-notation and array indices (e.g., `emails[0]`, `location.city`) to dynamically query the Canonical profile.
- **Field Mapping**: Reads the `path` and `from` keys in the config to construct the new output shape.
- **Missing Data Policy (`on_missing`)**: If a resolved path yields `None`:
  - `null`: Emits the field as `null`.
  - `omit`: Drops the key entirely from the output dictionary.
  - `error`: If the field has `required: true`, the pipeline aborts and throws a `ValueError`.

## 5. Edge Cases Handled

1.  **Missing/Garbage Sources**: The extractor catches malformed JSON or empty CSVs and simply returns an empty list for that source. The pipeline doesn't crash; it just operates on the valid sources.
2.  **Array Out-of-Bounds in Config**: If the config asks for `emails[0]` but the candidate has no emails, the projector gracefully catches the `IndexError` and falls back to the `on_missing` behavior.
3.  **Conflicting Names (e.g., "Jane Doe" vs "Jane H. Doe")**: By utilizing confidence-weight selection instead of string merging, we avoid generating corrupted names like "Jane Doe H. Doe". We pick the highest-authority string.
4.  **Inconsistent Date Formats**: The normalizer handles multiple variations (MM/YYYY, Month YYYY, YYYY-MM) using robust RegEx fallbacks.

## 6. Deliberate Omissions (Under Time Pressure)

- **LLM Extraction for Notes**: Extracting from raw text (`.txt`) is done via RegEx heuristics rather than a Generative LLM to guarantee deterministic outputs and fast local execution without external API keys.
- **Fuzzy Deduplication**: Experience deduplication requires exact company/title matches. Advanced fuzzy matching (e.g., treating "Acme" and "Acme Corp" as identical) was descoped to prioritize core architecture.