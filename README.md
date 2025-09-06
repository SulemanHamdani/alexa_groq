**Overview**
- **Purpose:** Alexa skill backend (AWS Lambda) that routes free‑form questions to Groq via the OpenAI‑compatible API and returns concise, voice‑friendly answers.
- **Design:** Minimal, testable modules with a thin entrypoint. Safe timeouts and short responses to fit Alexa’s ~8s budget.

**Highlights**
- **Free‑form intent:** Uses a single `FreeFormIntent` with `AMAZON.SearchQuery` slot for natural questions.
- **Tight budget:** Caps request time and tokens; short, PlainText responses for broad device support.
- **Separation of concerns:** Config, responses, client, and handlers in small, focused modules.
- **Operational clarity:** Simple logging with latency and categorized error messages.

**Repository Layout**
- `alexa_groq/lambda_function.py`:1 — Lambda entrypoint (`lambda_function.lambda_handler`).
- `alexa_groq/app_config.py`:1 — Environment‑driven `Config` dataclass and loader.
- `alexa_groq/alexa_responses.py`:1 — Alexa response builders (`speak`, `end_session`).
- `alexa_groq/utils.py`:1 — Helpers (`get_slot`, `get_remaining_ms`).
- `alexa_groq/groq_client.py`:1 — `GroqChatClient` wrapper using OpenAI‑compatible SDK.
- `alexa_groq/handlers.py`:1 — Request routing, `FreeFormIntent`, and built‑ins.

**How It Works**
- Launch opens a session and prompts the user to speak a question.
- `FreeFormIntent` captures `utterance` and calls Groq (`chat.completions.create`).
- Handler enforces a remaining‑time guard (< 2500 ms short‑circuits with a friendly message).
- Responses are PlainText to maximize Alexa device compatibility.

**Prerequisites**
- AWS account with permission to create and invoke Lambdas.
- Alexa Developer Console access for custom skills.
- Groq API key with access to your chosen model.
- Python 3.11+ locally for packaging; choose an AWS Lambda runtime that matches (e.g., Python 3.11 or 3.12 when available in your region).

**Configuration**
- Set these environment variables on the Lambda function:
  - `GROQ_API_KEY` (required): Groq API key.
  - `GROQ_MODEL` (default: `openai/gpt-oss-120b`): Model identifier.
  - `GROQ_BASE_URL` (default: `https://api.groq.com/openai/v1`): OpenAI‑compatible base URL.
  - `GROQ_TIMEOUT_S` (default: `5.0`): HTTP client timeout seconds.
  - `GROQ_MAX_TOKENS` (default: `220`): Max tokens for completion

**Local Smoke Test**
- Create a quick driver script to exercise the handler:
  - Example event (FreeFormIntent):
    - Save as `event.json`:
      - `{ "request": { "type": "IntentRequest", "intent": { "name": "FreeFormIntent", "slots": { "utterance": { "name": "utterance", "value": "explain quantum computing" } } } } }`
  - Example runner `run_local.py`:
    - `from alexa_groq.lambda_function import lambda_handler; import json; class Ctx: get_remaining_time_in_millis=lambda self:8000; print(json.dumps(lambda_handler(json.load(open('event.json')), Ctx()), indent=2))`

**Build and Package (Makefile)**
- At the repository root, use the provided Makefile:
  - `make help` — lists available targets.
  - `make check` — byte‑compiles sources to catch syntax errors early.
  - `make package` — creates `alexa_groq.zip` from `alexa_groq/` (excludes caches).
  - `make tree` — prints the contents of the existing zip archive.
  - `make clean` — removes the zip and local caches.

**Deploy (AWS Lambda)**
- Create or update the Lambda function using the generated `alexa_groq.zip`:
  - Runtime: Python 3.11 (or 3.12 where supported by your region).
  - Handler: `lambda_function.lambda_handler`.
  - Memory: 256–512 MB (start with 256 MB; increase if needed).
  - Timeout: 8 seconds (align with Alexa request budget).
  - Upload `alexa_groq.zip` and set environment variables.

**Wire Up the Alexa Skill**
- In Alexa Developer Console:
  - Create a Custom skill (e.g., “Hello Chat”).
  - Invocation name: choose a short, pronounceable phrase.
  - Intents: add `FreeFormIntent` with slot `utterance` of type `AMAZON.SearchQuery`.
  - Built‑ins: include `AMAZON.HelpIntent`, `AMAZON.CancelIntent`, `AMAZON.StopIntent`, `AMAZON.FallbackIntent`.
  - Sample utterances for `FreeFormIntent`: `"{utterance}"` (single slot capture pattern).
  - Endpoint: AWS Lambda ARN (default region) and account linking not required.
  - Build the interaction model, then test in the simulator.

**Operational Notes**
- The client is lazily initialized and reused across invocations to reduce cold‑start overhead.
- The handler logs request metadata and basic latency/error categories to CloudWatch.
- Answers are truncated to ~600 characters for TTS comfort.
- Keep `GROQ_TIMEOUT_S` conservative so the overall skill stays below ~8 seconds.

**Security**
- Store `GROQ_API_KEY` as an encrypted Lambda environment variable; enable helpers like KMS encryption at rest.
- Apply least‑privilege IAM (no AWS services beyond CloudWatch Logs are required).
- Do not log user content or secrets; current logs are minimal and avoid PII by design.
- Rotate API keys on a regular cadence and monitor error rates.

**Troubleshooting**
- 401 Unauthorized: invalid or missing `GROQ_API_KEY`.
- 403 Forbidden: model/key not permitted; switch models or check access.
- Timeout: increase `GROQ_TIMEOUT_S` slightly or reduce `GROQ_MAX_TOKENS`.
- Unexpected request type: verify the skill’s endpoint configuration and intent schema.

**Extending**
- Add a second intent (e.g., `SummarizeIntent`) by implementing a new handler in `alexa_groq/handlers.py`:1 and wiring it into the router.
- Swap models by changing `GROQ_MODEL` without code changes.
- Update prompts or voice UX strings in `alexa_groq/app_config.py`:1.

**License**
- MIT
