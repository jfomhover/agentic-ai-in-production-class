# Policy engines and enforcement

## Production question

How is authority enforced before an agent can act?

## Learning objectives

After reading this chapter, students can:

1. **Explain** why delegated identity and downstream permissions do not remove the need for application policy around agent actions.
2. **Distinguish** the roles of the policy decision point, policy enforcement point, policy information point, and downstream resource server.
3. **Construct** an authorization request using the NIST ABAC vocabulary: subject, object, operation, and environment.
4. **Trace** a proposed MCP or tool call through policy evaluation, enforcement, downstream authorization, and application approval or error handling.

## Core idea

An agent proposes an action. A policy decision point evaluates a request built from authenticated and otherwise trusted attributes. A policy enforcement point blocks or permits the request, and the downstream resource server performs its own authorization check at the operation boundary.

The policy decision must be independent of the model's wording. A prompt such as "the user approved this" is evidence to consider, not proof of approval.

## Motivation

Previous chapters established that giving an agent its own broad credentials is bad practice. The agent should act on behalf of a user instead. That still leaves a problem: if the user's delegated permissions are broad, a tool-poisoning attack, model error, or mistaken tool call can use more authority than the current task needs. Policy must restrict what the agent may do on the user's behalf.

This decision should not be left to the model or solved by writing better instructions. For enterprise readiness, authorization needs a strict, deterministic policy layer that can be tested, reviewed, versioned, and enforced outside the model. An externalized policy service gives an organization a place to define, review, test, version, and enforce rules.

Zero trust provides the broader security frame: do not trust a component because it runs inside the application or network. Authenticate the principal, evaluate the requested object and operation, and enforce the result at the boundary where the operation occurs.

## Where the harness meets policy

The harness is the enforcement seam between a model's proposed tool call and the tool itself. A generic integration works like this:

1. The model proposes a tool call.
2. A pre-tool hook builds the authorization request from the subject, object, operation, and environment.
3. The hook sends that request to the policy decision point and receives a decision.
4. The harness either blocks the call or invokes the tool.

Approval can be one of the environment attributes. A human-review mechanism may pause the harness, collect a decision, and resume the run. It does not replace authorization at the downstream service.

A pre-tool hook is an application-level enforcement point, not a substitute for enforcement by the MCP server or downstream resource server. Every trust boundary must validate the request and its parameters. Otherwise a caller may bypass the hook or use a permitted tool against an unauthorized object.

The policy function can be local in a prototype or hosted by OPA, Cedar, or another policy service. The enforcement point remains in the harness or gateway, while GitHub or another downstream service performs its own authorization.

## Core vocabulary

- **Policy decision point (PDP):** evaluates a request and returns a decision.
- **Policy enforcement point (PEP):** intercepts an operation and enforces the decision.
- **Policy information point (PIP):** supplies facts used by a policy, such as identity, repository, approval, or data classification.
- **Identity provider (IdP):** authenticates a principal and provides identity information used by authorization.
- **Resource server:** protects an API, data store, or operation and enforces access to it.
- **Subject:** the user, agent, service, or workload requesting an operation.
- **Object:** the data, service, or system component affected by the operation.
- **Operation:** the requested action, such as reading issues or creating a comment.
- **Environment:** additional facts that affect the decision, such as tenant, time, approval, deployment environment, or purpose.
- **Obligation:** an instruction associated with a policy decision that the enforcement point must perform when applicable, such as logging, redaction, or approval recording.

## The authorization request

A policy decision should need four things:

| Element | Question | GitHub example |
| --- | --- | --- |
| Subject | Which authenticated principal and delegated client or workload are associated with the request? | User principal, OAuth client or app, MCP host, and, only if independently authenticated, the agent workload |
| Object | What would be affected? | Repository and issue |
| Operation | What should happen? | Create an issue comment |
| Environment | What other facts matter? | Repository access, app permission, approval, deployment environment |

There is no universal policy-request schema. This chapter uses the NIST ABAC model of subject, object, operation, and environment attributes as its organizing vocabulary. The lesson is to make the decision inputs explicit and inspectable. See [NIST SP 800-162](https://doi.org/10.6028/NIST.SP.800-162).

## Apply it to the GitHub MCP example

The user asks the agent to create a comment on an issue. The agent proposes a GitHub MCP operation. The request passes through several roles:

During the authorization flow, GitHub authenticates the user and obtains the user's authorization according to the selected OAuth or GitHub App flow. It then issues a credential representing a scoped grant to the client. Token possession alone does not prove current user intent or authorize operations outside that grant. The local application is the OAuth client and MCP host. The application policy layer acts as the PDP and PEP for application-specific rules. GitHub's API is the resource server that performs the downstream authorization check and executes the operation.

The model is not automatically an authenticated subject. Treat its output as an untrusted proposal unless the application independently establishes the identity and attributes used for authorization.

Separate the checks made by GitHub from the application policy:

**GitHub is authoritative for:**

- which user is represented by the delegated credential;
- whether that user can access the repository and issue;
- whether the GitHub authorization permits the operation;
- which repositories and permissions the GitHub App or OAuth configuration covers.

**Application policy is responsible for:**

- whether this application exposes the MCP tool and permits this particular operation and parameter set;
- whether the current operation is allowed for this purpose and environment;
- whether approval is required and the approval is bound to the authenticated principal, exact operation, object, material parameters, policy context, authorized approver, and time window;
- which audit event must be recorded.

An exposed MCP tool is available to call; that does not authorize the operation. Tool discovery or exposure is availability, not authorization. Application policy can narrow or block the call, and the downstream service remains authoritative for its own permissions. Delegated access lets the downstream service enforce the user's authority, while application policy adds task-specific limits and approval rules.

## Decision outcomes

Separate policy results from application workflow states:

- **Permit:** policy evaluation authorizes the operation.
- **Deny:** policy evaluation rejects the operation.
- **Indeterminate:** policy evaluation could not produce a reliable result, for example because a required fact was missing.
- **Not applicable:** no policy applies, where the policy model exposes this result.

An application may map these results to workflow states such as **require approval**, retry, or user-visible error. `Require approval` is an application outcome, not a universal policy-engine result.

For authorization enforcement, a missing, stale, contradictory, or unverifiable required fact should normally result in no execution, typically `Deny` or a fail-closed `Indeterminate` handling path. Any fail-open exception must be explicit, narrowly scoped, and justified by the operation's risk and availability requirements. An approval record is one policy input; it does not replace identity, object access, least privilege, or downstream authorization.

## Bibliography

1. NIST. [Zero Trust Architecture, SP 800-207](https://doi.org/10.6028/NIST.SP.800-207). **Government architecture guidance.** Defines the policy decision and enforcement model and grounds per-request authorization.
2. NIST. [Guide to Attribute Based Access Control, SP 800-162](https://doi.org/10.6028/NIST.SP.800-162). **Government guidance.** Defines subject, object, operation, and environment attributes for authorization decisions.
3. NIST. [Security and Privacy Controls, SP 800-53 Rev. 5](https://doi.org/10.6028/NIST.SP.800-53r5), especially AC-3, AC-5, and AC-6. **Government control catalog.** Provides language for access enforcement, separation of duties, and least privilege.
4. OASIS. [eXtensible Access Control Markup Language (XACML) Version 3.0](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html). **Technical standard.** Defines policy decision points, enforcement points, information points, authorization results, obligations, and advice. Its standard results include Permit, Deny, Indeterminate, and NotApplicable; approval is an application workflow outcome.
5. Pang et al. [Zanzibar: Google’s Consistent, Global Authorization System](https://www.usenix.org/conference/atc19/presentation/pang), USENIX ATC 2019. **Systems research.** Shows relationship-based authorization at large scale.
6. [Open Policy Agent documentation](https://www.openpolicyagent.org/docs/latest/). **Open-source implementation guidance.** Useful for externalized policy, testing, and policy APIs; it is not a universal standard.
7. [Cedar policy language and documentation](https://docs.cedarpolicy.com/). **Authorization language and implementation ecosystem.** Useful for explicit entities, actions, resources, and policy validation.
