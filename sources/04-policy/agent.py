"""Demo code for putting a typed policy gate before agent tool execution.

This is not production security code. Authentication, policy storage, approval
storage, audit integrity, and downstream authorization are intentionally mocked.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class PolicyDecision(str, Enum):
    """Policy results used by this demo PDP."""

    PERMIT = "permit"
    DENY = "deny"
    INDETERMINATE = "indeterminate"


class AuthenticatedContext(BaseModel):
    """Mock trusted context supplied by the application, not the model.

    In a real system these values would come from authentication and
    authorization services. The important teaching boundary is that the
    model does not get to invent them in its tool arguments.
    """

    user: str
    agent: str
    request_id: str
    user_can_read: bool
    user_can_write: bool


class Subject(BaseModel):
    """The principal and agent associated with the request."""

    user: str
    agent: str
    request_id: str


class ObjectRef(BaseModel):
    """The downstream object that the requested operation would affect."""

    repository: str
    issue: int | None = None


class ApprovalRecord(BaseModel):
    """Request-bound approval captured by the application workflow.

    Approval is not a free-floating boolean. It is tied to the principal,
    operation, object, material parameters, and an expiry time.
    """

    approver: str
    subject: str
    operation: str
    repository: str
    issue: int | None
    parameter_hash: str
    expires_at: datetime


class Environment(BaseModel):
    """Request-time facts used by the prototype policy."""

    user_can_read: bool
    user_can_write: bool
    approval: ApprovalRecord | None = None


class ToolArguments(BaseModel):
    """Strict base model for model-produced tool arguments.

    The model proposes these values, so unknown fields and malformed input
    must not silently pass into policy evaluation or tool execution.
    """

    model_config = ConfigDict(extra="forbid")


class ReadIssueArguments(ToolArguments):
    repository: str = Field(min_length=1)
    issue_number: int = Field(gt=0)


class CreateIssueCommentArguments(ToolArguments):
    repository: str = Field(min_length=1)
    issue_number: int = Field(gt=0)
    body: str = Field(min_length=1, max_length=4000)


class AuthorizationRequest(BaseModel):
    """NIST ABAC-shaped request passed from the harness to the PDP."""

    subject: Subject
    object: ObjectRef
    operation: str
    environment: Environment
    parameter_hash: str


# Application workflow policy. This would normally come from a versioned policy service or action registry.
APPROVAL_REQUIRED_OPERATIONS = {
    "github.issue.comment.create",
}


def trace(message: str) -> None:
    """Print a small, readable execution trace for the teaching prototype."""

    print(f"[trace] {message}", flush=True)


def audit(event: str, **fields: Any) -> None:
    """Emit a small structured audit event without logging comment content.

    This is console output for teaching, not tamper-resistant audit storage.
    """

    payload = {"event": event, **fields}
    print(f"[audit] {json.dumps(payload, sort_keys=True)}", flush=True)


def operation_parameter_hash(
    repository: str,
    issue: int | None,
    body: str = "",
) -> str:
    """Bind approval to material parameters without logging their contents."""

    material = json.dumps(
        {"repository": repository, "issue": issue, "body": body},
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def approval_matches(request: AuthorizationRequest) -> bool:
    """Check exact approval binding and expiry before a write can proceed."""

    # No approval record means the application workflow must ask for one.
    approval = request.environment.approval
    if approval is None:
        return False

    # Every material authorization dimension must match the approved request.
    return (
        approval.approver == request.subject.user
        and approval.subject == request.subject.user
        and approval.operation == request.operation
        and approval.repository == request.object.repository
        and approval.issue == request.object.issue
        and approval.parameter_hash == request.parameter_hash
        and approval.expires_at > datetime.now(timezone.utc)
    )


def authorize(request: AuthorizationRequest) -> PolicyDecision:
    """Return a teaching policy decision for a typed ABAC request."""

    # Pydantic validates the shape. A real policy service must also validate
    # that the attributes came from trusted identity and authorization sources.
    operation = request.operation
    environment = request.environment
    trace(
        "PDP evaluating "
        f"operation={operation} repository={request.object.repository} "
        f"issue={request.object.issue} user={request.subject.user}"
    )
    audit(
        "pdp.evaluate",
        request_id=request.subject.request_id,
        operation=operation,
        repository=request.object.repository,
        issue=request.object.issue,
        approval_bound=request.environment.approval is not None,
    )

    if operation == "github.issue.read":
        # Reading is allowed only when the user's effective read permission
        # has already been established by the surrounding application.
        decision = (
            PolicyDecision.PERMIT if environment.user_can_read else PolicyDecision.DENY
        )
        trace(f"PDP result={decision.value} user_can_read={environment.user_can_read}")
        return decision
    if operation == "github.issue.comment.create":
        # A valid user write permission is still not enough for this example:
        # the application also requires an explicit approval signal.
        if not environment.user_can_write:
            trace("PDP result=deny user_can_write=False")
            return PolicyDecision.DENY
        if environment.approval is not None and not approval_matches(request):
            trace("PDP result=indeterminate approval_binding_invalid=true")
            return PolicyDecision.INDETERMINATE
        trace("PDP result=permit user_can_write=True")
        return PolicyDecision.PERMIT

    # Default deny is appropriate for an unknown operation in this teaching
    # example. A production policy must define its error and availability
    # behavior explicitly.
    trace(f"PDP result=deny unknown_operation={operation}")
    return PolicyDecision.DENY


@wrap_tool_call
async def policy_gate(
    request: Any,
    handler: Callable[[Any], Awaitable[ToolMessage | Command]],
) -> ToolMessage | Command:
    """Enforce the local policy decision before an async tool handler runs."""

    # The model chooses a Python tool name. The policy uses stable business
    # operation names instead of coupling policy to Python function names.
    tool_name = request.tool_call["name"]
    tool_args = request.tool_call.get("args", {})
    trace(f"PEP intercepted tool={tool_name} arg_keys={sorted(tool_args)}")
    action_names = {
        "read_issue": "github.issue.read",
        "create_issue_comment": "github.issue.comment.create",
    }
    # The action registry decouples stable policy names from Python tool names.
    argument_models = {
        "read_issue": ReadIssueArguments,
        "create_issue_comment": CreateIssueCommentArguments,
    }
    argument_model = argument_models.get(tool_name)
    if argument_model is None:
        trace(f"PEP result=indeterminate unregistered_tool={tool_name}")
        audit("pep.indeterminate", reason="unregistered_tool", tool=tool_name)
        return ToolMessage(
            content="Policy decision: indeterminate. The tool is not registered.",
            tool_call_id=request.tool_call["id"],
        )

    # Validate untrusted model arguments before constructing the ABAC request.
    try:
        parsed_args = argument_model.model_validate(tool_args)
    except ValidationError as error:
        trace(f"PEP result=indeterminate invalid_arguments={error.errors()[0]['type']}")
        audit("pep.indeterminate", reason="invalid_tool_arguments", tool=tool_name)
        return ToolMessage(
            content="Policy decision: indeterminate. Tool arguments were invalid.",
            tool_call_id=request.tool_call["id"],
        )

    # This context is application-supplied in the demo. In production it would
    # be assembled from authenticated identity and permission services.
    context = AuthenticatedContext(
        user="demo-user",
        agent="backlog-agent",
        request_id=request.tool_call["id"],
        user_can_read=True,
        user_can_write=True,
    )
    # Hash material parameters so approval cannot be replayed for a different
    # repository, issue, or comment body without exposing the body in logs.
    body = getattr(parsed_args, "body", "")
    parameter_hash = operation_parameter_hash(
        parsed_args.repository,
        parsed_args.issue_number,
        body,
    )
    # This is the handoff from the harness to the PDP. The demo context is
    # mocked, but its type makes the trusted-attribute boundary explicit.
    policy_request = AuthorizationRequest(
        subject=Subject(
            user=context.user,
            agent=context.agent,
            request_id=context.request_id,
        ),
        operation=action_names[tool_name],
        object=ObjectRef(
            repository=parsed_args.repository,
            issue=parsed_args.issue_number,
        ),
        environment=Environment(
            user_can_read=context.user_can_read,
            user_can_write=context.user_can_write,
            # Approval is collected by the application workflow below. Never
            # treat a model-supplied tool argument as proof of approval.
            approval=None,
        ),
        parameter_hash=parameter_hash,
    )
    trace(
        "PEP built request "
        f"subject={policy_request.subject.user} "
        f"operation={policy_request.operation} "
        f"object={policy_request.object.repository}#{policy_request.object.issue} "
        f"approval_bound={policy_request.environment.approval is not None}"
    )
    decision = authorize(policy_request)
    trace(f"PEP received decision={decision.value}")

    if decision is not PolicyDecision.PERMIT:
        # Do not call the handler for a policy denial or indeterminate result.
        return ToolMessage(
            content=f"Policy decision: {decision.value}. The tool was not executed.",
            tool_call_id=request.tool_call["id"],
        )

    if (
        policy_request.operation in APPROVAL_REQUIRED_OPERATIONS
        and policy_request.environment.approval is None
    ):
        trace(
            "WORKFLOW approval_required=true "
            "reason=write operation has no approval record"
        )
        print("\nApproval required before this write operation.")
        print(
            "  Action: create GitHub issue comment\n"
            f"  Repository: {policy_request.object.repository}\n"
            f"  Issue: #{policy_request.object.issue}"
        )
        answer = await asyncio.to_thread(input, "Approve this action? [y/N]: ")
        answer = answer.strip().lower()
        if answer not in {"y", "yes"}:
            trace("WORKFLOW approval_granted=false; tool will not execute")
            audit(
                "approval.denied",
                request_id=policy_request.subject.request_id,
                operation=policy_request.operation,
            )
            return ToolMessage(
                content="Application workflow: approval denied. The tool was not executed.",
                tool_call_id=request.tool_call["id"],
            )

        # Record approval against the exact request before resuming execution.
        approval = ApprovalRecord(
            approver=policy_request.subject.user,
            subject=policy_request.subject.user,
            operation=policy_request.operation,
            repository=policy_request.object.repository,
            issue=policy_request.object.issue,
            parameter_hash=policy_request.parameter_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        policy_request.environment.approval = approval
        audit(
            "approval.granted",
            request_id=policy_request.subject.request_id,
            operation=policy_request.operation,
            repository=policy_request.object.repository,
            issue=policy_request.object.issue,
            expires_at=approval.expires_at.isoformat(),
        )
        trace("WORKFLOW approval_granted=true; resuming execution")
        # Re-run the PDP after approval. The original permit was only policy
        # eligibility; this decision includes the newly bound approval record.
        decision = authorize(policy_request)
        trace(f"PEP re-evaluated after approval decision={decision.value}")
        if decision is not PolicyDecision.PERMIT:
            return ToolMessage(
                content=(
                    f"Policy decision after approval: {decision.value}. "
                    "The tool was not executed."
                ),
                tool_call_id=request.tool_call["id"],
            )

    # A local PEP permit does not replace authorization at the resource server.
    if not downstream_authorize(policy_request):
        trace("RESOURCE SERVER result=deny; tool will not execute")
        return ToolMessage(
            content="Downstream authorization denied. The tool was not executed.",
            tool_call_id=request.tool_call["id"],
        )

    # Only the permit path reaches the operation. This is the key PEP rule in
    # the example: the model proposes; the policy gate decides; the tool runs
    # only after the gate permits it.
    trace(f"PEP permit=true invoking tool={tool_name}")
    result = await handler(request)
    trace(f"PEP tool completed tool={tool_name}")
    return result


def downstream_authorize(request: AuthorizationRequest) -> bool:
    """Simulate an independent resource-server authorization check."""

    # This deliberately small resource server only exposes the demo object.
    # It demonstrates that a local policy permit is not the final authority.
    allowed = (
        request.object.repository == "example/repo"
        and request.object.issue == 42
    )
    audit(
        "resource_server.authorize",
        request_id=request.subject.request_id,
        operation=request.operation,
        repository=request.object.repository,
        issue=request.object.issue,
        result="permit" if allowed else "deny",
    )
    return allowed


def read_issue(repository: str, issue_number: int) -> str:
    """Stand in for a read-only downstream operation."""

    trace(f"TOOL read_issue repository={repository} issue={issue_number}")
    return f"Issue {repository}#{issue_number}: example issue data"


def create_issue_comment(
    repository: str,
    issue_number: int,
    body: str,
) -> str:
    """Stand in for a side-effecting downstream operation."""

    trace(f"TOOL create_issue_comment repository={repository} " f"issue={issue_number}")
    return f"Created comment on {repository}#{issue_number}: {body}"


def format_message_content(content: Any) -> str:
    """Render LangChain text content without dumping the raw message structure."""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                text_parts.append(part["text"])
        if text_parts:
            return "\n".join(text_parts)

    return str(content)


async def main() -> None:
    """Run a small interactive terminal UI around the policy-gated agent."""

    # Load local development settings without putting credentials in source
    # control. The .env.example file documents the expected variables.
    load_dotenv()
    required = {
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_DEPLOYMENT": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    }
    # Fail before constructing the model when the required Azure settings are
    # missing. This example uses Azure OpenAI by default for the model call.
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError("Missing Azure OpenAI settings: " + ", ".join(missing))

    # The deployment must support tool calling. The model proposes tool calls;
    # policy_gate remains responsible for deciding whether they execute.
    endpoint = required["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    base_url = endpoint if endpoint.endswith("/openai/v1") else f"{endpoint}/openai/v1/"
    model = ChatOpenAI(
        model=required["AZURE_OPENAI_DEPLOYMENT"],
        base_url=base_url,
        api_key=required["AZURE_OPENAI_API_KEY"],
        temperature=0,
    )
    # create_agent builds the agent loop on LangGraph. The middleware wraps
    # every tool call made by this agent.
    agent = create_agent(
        model,
        [read_issue, create_issue_comment],
        middleware=[policy_gate],
        system_prompt="Use tools only for the user's request. Never claim an action succeeded if policy blocked it.",
    )
    print("\nPolicy-gated agent demo")
    print("The model may propose tools; policy decides whether they execute.")
    print("Write actions pause for explicit terminal approval.")
    print("Try: Read issue 42 in example/repo, then comment that it needs review.")
    print("Type /quit to exit.\n")

    while True:
        try:
            user_input = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return

        if not user_input:
            continue
        if user_input.lower() in {"/quit", "/exit", "quit", "exit"}:
            print("Goodbye.")
            return

        print("\nCalling model; policy gate is active ...", flush=True)
        try:
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": user_input}]}
            )
        except Exception as exc:
            print(f"\nError: {exc}\n")
            continue

        messages = result.get("messages", [])
        if not messages:
            print("\nAgent: no response messages returned.\n")
            continue

        response = format_message_content(messages[-1].content)
        print(f"\nAgent > {response}\n")


if __name__ == "__main__":
    asyncio.run(main())
