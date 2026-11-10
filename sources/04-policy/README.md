# Policy gate demo code

This example shows where policy evaluation fits into a LangChain agent running on LangGraph:

```text
model tool call -> wrap_tool_call -> policy decision -> tool execution or denial
```

`authorize()` is a local policy-decision-point stand-in and returns `permit`, `deny`, or `indeterminate`. `AuthorizationRequest` uses the NIST ABAC vocabulary: subject, object, operation, and environment. `policy_gate` is the policy-enforcement point. Approval is handled separately as an application workflow state. A production version could call OPA, Cedar, or another policy service.

The example uses Azure OpenAI's v1-compatible endpoint through LangChain's generic `ChatOpenAI` client. `AZURE_OPENAI_ENDPOINT` should be the resource endpoint; the code appends `/openai/v1/`. This v1 path does not use an `api_version` setting.

Run it with:

```text
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
python agent.py
```

The tools use placeholder results. The purpose is to make the harness boundary visible, not to call GitHub.

The program opens a small interactive terminal prompt. Enter a request, watch the model propose tool calls, and inspect the policy trace. Before a write operation, the policy gate displays the repository and issue and asks for explicit approval. Use `/quit` or press `Ctrl+C` to exit.

## What this demonstrates

- typed application context separate from model-produced tool arguments;
- strict tool-argument validation;
- permit, deny, and indeterminate policy paths;
- request-bound approval followed by policy re-evaluation;
- a second simulated resource-server authorization check;
- human-readable traces plus structured audit events.

## What this does not prove

Authentication, token validation, durable approval storage, audit integrity, real MCP authorization, and real GitHub permissions remain mocked. The example demonstrates the PDP/PEP and workflow boundaries; it is not production security code.
