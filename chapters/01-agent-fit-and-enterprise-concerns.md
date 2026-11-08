# Agent fit: deflating the unlimited-agent assumption

## Production question

What is an agent actually good at, and where should simpler software take over?

## Learning objectives

After reading this chapter, students can:

1. **Explain** why a single agent has a bounded envelope of reliable goals, tools, context, and operating conditions.
2. **Assess** why broad agent scope makes evaluation, monitoring, and alignment harder.
3. **Distinguish** adaptive work that benefits from an agent from deterministic work that belongs in a script or workflow.
4. **Decompose** a mixed process so deterministic control remains deterministic and agentic interaction is used only where it adds value.

## Core idea

An agent is not a general-purpose employee in software form. It is a probabilistic system that interprets context, selects actions, and uses tools under constraints. Its reliable capability has an envelope: a bounded set of goals, inputs, tools, permissions, state, and operating conditions in which its behavior is acceptable.

That envelope is limited by the model's context capacity, incomplete or stale information, variable outputs, confabulation, ambiguous instructions, retrieval failures, tool inaccuracies, state and memory errors, latency, cost, and the consequences of a wrong action. The model may be able to discuss many topics, but that does not mean one agent can reliably pursue many unrelated goals in production.

The practical response is not automatically “use more agents.” Improve the reliable scope with better context engineering, dependable tools and data, explicit policy controls, evaluation, monitoring, and recovery. The design question is where a narrow agent adds adaptive value and where ordinary software should remain in control.

## Insight 1: Every agent has a practical scope limit

### Scope is constrained by competing forces

An agent's possible behavior is limited by more than the model's training. Model capability, context engineering, dependable tools and data, policy controls, and evaluation can expand the reliable scope. Other forces limit it: the context window constrains how much of the task can remain available at once; requests may be ambiguous; generated content can be unsupported; and tools can return incomplete, stale, malformed, or unauthorized data. A long chain of calls creates more opportunities for error and state drift.

The system also has a reliability envelope. Within a narrow task, a team may be able to test representative inputs and constrain the available operations. As goals, tools, data sources, permissions, and side effects expand, the number of interactions and failure modes grows. A capability that is acceptable for drafting a response may not be acceptable for making a financial, security, or production change.

### Specialization can be a control, not only an optimization

Separate agents may be useful when each has a clearly bounded purpose, capability set, context, and evaluation suite. For example, one component can retrieve approved product information, another can draft a customer explanation, and a deterministic service can commit an approved change. The boundaries make it possible to restrict data and authority.

Do not treat a multi-agent design as automatically safer. Coordination can introduce new failures: one agent may misunderstand another's output, shared memory may leak context, and the overall system may be harder to debug. Decompose only when the separation creates a clearer contract and a smaller testable surface.

## Insight 2: Broad scope makes evaluation and monitoring harder

### Alignment is relative to a defined goal

An evaluation needs a target: what should the system do, for which inputs, under which constraints, and with what acceptable failure behavior? A broad agent with many goals and tools has many more combinations of:

- user intents and ambiguity levels;
- context and retrieval conditions;
- tool choices and tool failures;
- permissions and resource states;
- success criteria and harmful side effects.

The evaluation surface can grow combinatorially as these dimensions interact. Monitoring also becomes harder because a plausible answer is not evidence that the right goal was pursued, the right data was used, or the right action was authorized. A single aggregate success score can hide failures concentrated in a particular user group, repository, tool, or operating condition.

Narrow goals do not make evaluation easy, but they make the expected behavior and the failure boundary more explicit. A bounded agent can have representative test cases, adversarial cases, tool-contract tests, approval tests, and production signals tied to a defined outcome. It is easier to review its alignment when the team can say what it is allowed to accomplish and what it must never do.

## Insight 3: Deterministic repetition belongs in scripts and workflows

Agents are useful when the work requires interpretation, adaptation, or communication across varied situations. They are a poor substitute for a script when the requirement is to repeat the same steps, apply the same predicates, and produce an auditable result every time.

### Example: product-release gates

Suppose an organization follows every product launch and requires product managers to pass 15 release gates. Each gate is evidenced by a work item being marked complete and linked to the required artifact. The organization wants to know which launches are compliant.

This process has two different jobs:

1. **Determine compliance:** inspect the release record, check the 15 required gates, validate the evidence and state transitions, identify missing or contradictory items, and apply the policy.
2. **Restore compliance:** contact the responsible product manager, explain which gates are missing, answer questions about the evidence, and help coordinate the next steps.

The first job should be a deterministic script or workflow. It can enumerate every launch, evaluate every gate with explicit rules, produce the same result for the same state, and record an audit trail. A policy engine can express exceptions and required conditions. An agent should not be asked to “look at the release and decide” when the organization already knows the 15 predicates that define compliance.

The second job may justify an agent. The agent can explain a deterministic finding in context, answer questions, adapt the conversation to the product manager, draft reminders, and route unresolved cases. Its authority should remain bounded: it should not mark gates complete, alter evidence, or declare a release compliant unless a separate controlled workflow permits that action.

This split is the agent-fit decision in concrete form:

```text
release state -> deterministic gate checks -> policy result and evidence
                                          -> agent-assisted explanation and follow-up
```

Use an agent for the variable human interaction around a trusted result, not for replacing the trusted result with an untestable judgment.

## A practical fit test

Before proposing an agent, ask:

1. **Variation:** Does the work require interpretation or adaptation, or are the steps already known?
2. **Boundary:** Can the goal, data, tools, permissions, and unacceptable actions be stated clearly?
3. **Evaluation:** Can representative, adversarial, tool-failure, and authorization tests be defined?
4. **Consequence:** What happens when the agent is wrong, incomplete, delayed, or overconfident?
5. **Alternative:** Would a script, rule, workflow, search system, or conventional service meet the need more reliably?
6. **Decomposition:** Can deterministic checks and adaptive interaction be separated into explicit components?

If the work is deterministic, choose deterministic automation. If it is adaptive but bounded and testable, an agent may help. If the goal, authority, or evaluation boundary remains unclear, narrow the proposal before adding autonomy.

## Core vocabulary

- **Reliable scope:** the practical combination of goals, inputs, tools, permissions, state, and conditions in which an agent is expected to behave acceptably.
- **Bounded goal:** a goal with explicit success criteria, scope, constraints, and unacceptable outcomes.
- **Deterministic automation:** a script, rule, or workflow that applies explicit logic predictably to the same state.
- **Evaluation surface:** the combinations of inputs, contexts, tools, permissions, states, and outcomes that need to be tested.
- **Confabulation:** generated content presented as if grounded when it is unsupported or false; teams often call this hallucination.
- **Permission boundary:** the resources and operations an agent or component is allowed to use.

## Decision

Choose a narrow agent, deterministic automation, a composed design, or no automation. The decision should be justified by the task's variation, authority, consequences, evaluation surface, and simpler alternatives—not by the breadth of the model's conversational capability.

## Bibliography

1. NIST. [Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile](https://doi.org/10.6028/NIST.AI.600-1), 2024. **Government framework.** Useful for confabulation, information integrity, testing, monitoring, and risk controls for generative AI systems.
2. NIST. [Artificial Intelligence Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework). **Government framework.** Provides language for valid and reliable performance, testing, monitoring, and risk management; it does not define a universal agent-fit test.
3. U.S. Government Accountability Office. [Artificial Intelligence: An Accountability Framework](https://www.gao.gov/products/gao-21-519sp), GAO-21-519SP, 2021. **Government framework.** Useful for accountability, data, performance, and monitoring considerations; it predates current agent architectures.
4. Anthropic. [Building effective agents](https://www.anthropic.com/research/building-effective-agents), 2024. **Vendor engineering guidance.** Useful for the teaching distinction between workflows, agents, tool use, and task decomposition; treat it as implementation guidance, not independent evidence.
5. OWASP. [Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/). **Community security guidance.** Useful for prompt injection, insecure output handling, excessive agency, and other failure modes relevant to tool-using agents.
