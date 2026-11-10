# Agentic AI in Production

Public materials for a master's-level class on building and governing agentic AI in production.

## Slide deck

**[Download the complete PDF slide deck](dist/agentic-ai-in-production-2026.pdf)**

## Class philosophy

Implementation details are abundant. Tutorials, frameworks, papers, examples, and generated code can answer almost any question about calling a model, building an agent, or connecting a tool.

The scarce skill is knowing what to build, why it matters, and where it must be constrained. This class is a steering prompt: it helps students challenge the promise of an AI system before they commit to its implementation.

The class uses four production questions:

1. **Agent fit:** What is an agent actually good at, and where should simpler software take over?
2. **User data:** What user data does the system capture, create, store, transmit, and expose?
3. **Identity and delegation:** Whose authority is the agent using, and what can it do?
4. **Policy enforcement:** How is policy enforced before an agent can act?

These are review questions, not implementation phases. They expose the scope, data, identity, and authority boundaries that model demonstrations often hide.

## Chapters

- [01 - Agent fit and bounded autonomy](chapters/01-agent-fit-and-enterprise-concerns.md)
- [02 - User-data management](chapters/02-user-data-management.md)
- [03 - Identity and delegation](chapters/03-identity-and-delegation.md)
- [04 - Policy engines and enforcement](chapters/04-policy-engines-and-enforcement.md)

## Chapter 4 source example

The policy chapter includes a small typed policy-gate prototype:

- [Source README](sources/04-policy/README.md)
- [Policy-gate agent](sources/04-policy/agent.py)
- [Python dependencies](sources/04-policy/requirements.txt)

The prototype is teaching material, not production security code. Authentication, token validation, durable approval storage, audit integrity, and downstream authorization are intentionally simplified or mocked.

## License

This material is available under [CC BY-SA 4.0](LICENSE).

The hour is for direction, not implementation coverage.
