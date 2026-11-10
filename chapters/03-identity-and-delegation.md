# Identity and delegated capability design

## Production question

Whose authority is the agent using, and how can it act without receiving more privilege than the user has?

## Learning objectives

After studying this chapter, a student should be able to:

1. **Explain** why an agent should use delegated, least-privilege authority instead of a broad service credential.
2. **Distinguish** authentication, authorization, delegation, access tokens, and MCP tool access.
3. **Trace** a remote MCP OAuth flow from user authorization to an MCP request.
4. **Describe** how a permission intersection is limited by user access, application permissions, resource scope, and enabled capabilities.
5. **Apply** the pattern by building a read-only identity step and extending it to a controlled issue-management action with approval.

## Core idea

Give the agent delegated authority. Do not give it a privileged service credential.

The application authenticates the user with an identity provider, obtains a delegated credential for a downstream resource, and limits each operation to the permissions that remain after several checks:

- what the user can access;
- what the application or resource provider allows;
- which resources the application is allowed to reach;
- what the current operation requires;
- what the user has approved.

The agent can select or propose a capability. The MCP server and downstream resource enforce authorization. A prompt cannot enforce an access policy.

## Why privileged access fails

A privileged service credential gives the agent more authority than the current user may have. That creates several problems:

- one compromised agent can access data for many users;
- the downstream resource may not know which user requested an action;
- revoking one user's access may not revoke the agent's access;
- audit records may identify only the service, not the human principal;
- prompt injection or an agent error can use authority unrelated to the user's task;
- testing and incident response become harder when the permission boundary is too broad.

Least privilege limits the authority available to a compromised or mistaken component. Delegation also preserves attribution and keeps access aligned with the requesting user's permissions.

Delegation is one control. The application still needs narrow capabilities, approval for consequential actions, token protection, and audit records.

## Zero trust context

Zero trust starts with a simple rule: the system must not trust a component merely because it runs inside the application or on the organization's network. Each request needs an authenticated principal, an intended resource, an allowed operation, and an enforcement point. NIST describes this model in [SP 800-207](https://doi.org/10.6028/NIST.SP.800-207).

In an agent integration:

- the user, application, agent, remote MCP server, and downstream resource are separate principals or trust boundaries;
- the application identifies the user before it invokes the agent;
- the MCP server exposes only the capabilities it is configured to provide;
- the downstream resource checks the user's access, application permissions, and resource scope;
- the agent receives data or a tool result, not a reusable downstream credential.

Zero trust does not mean adding a second login prompt to every request. It means refusing to treat location, application membership, or model instructions as proof of authority.

## Core vocabulary

- **Authentication:** establishing the identity of a user, service, or workload.
- **Authorization:** deciding whether that principal may perform an operation on a resource.
- **Delegation:** allowing an application to act with authority granted by a user while preserving attribution.
- **Least privilege:** granting only the authority required for the task, resource, and time period.
- **Permission intersection:** the shorthand used in this chapter for the access left after user access, application permissions, resource scope, policy, and operation constraints are combined.
- **Authorization code:** a short-lived value returned after the user authorizes an application; the server exchanges it for an access token.
- **User access token:** a provider-issued credential used by a service to call a resource on behalf of the authorized user.

## Tokens in two minutes

An access token is a credential presented to a resource server. The resource server, not the client or the model, decides whether to accept it.

A **JSON Web Token (JWT)** is a compact, URL-safe token format that carries signed claims as a header, payload, and signature. A resource can validate the signature and inspect claims such as `iss`, `aud`, and `exp`. A JWT is still only a credential. The receiving API must validate that it was issued by the expected authority, for the expected audience, and with the required permissions.

Not every access token is a JWT. Some providers issue opaque bearer tokens. The application must use the resource provider's validation and permission model rather than assume that it can parse token claims.

In any OAuth-based integration, the important credentials are:

- **Authorization code:** a short-lived code returned after the user authorizes the application. The server exchanges it for an access token.
- **User access token:** the credential used for downstream API calls on behalf of the user.
- **Refresh token:** an optional server-side credential used to obtain a new access token when the provider issues expiring tokens.

The model receives none of these credentials.

## Common mistakes

- **Give the agent a personal access token or broad service credential.** One leaked or misused credential can expose every repository that it can reach, across many users.
- **Put tokens in prompts, memory, client-side state, or ordinary logs.** Those surfaces have more readers and longer retention than the authorization flow requires.
- **Let the model choose the token or repository.** The MCP host and server must derive access from the authenticated session and their permission checks.
- **Request write access before the prototype needs it.** Early write permissions expand the blast radius before the read path and approval experience have been tested.

## Practice assignment

Using the official documentation and a vibe-coding tool, build a minimal LangGraph agent with GitHub's hosted remote MCP server.

### Sequence 1: identify the user

Use OAuth and expose only `get_me`. Explain the browser flow, token handling, and which GitHub user the application is acting for.

Read: [GitHub remote MCP server](https://github.com/github/github-mcp-server#remote-github-mcp-server), [host integration](https://github.com/github/github-mcp-server/blob/main/docs/host-integration.md), [MCP authorization](https://modelcontextprotocol.io/specification/latest/basic/authorization), and [creating a GitHub OAuth App](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app).

### Sequence 2: access issues

Add read-only issue access. Test an inaccessible repository, then optionally add one approved issue comment and identify which component enforces each boundary.

Read: [GitHub MCP toolsets](https://github.com/github/github-mcp-server#available-toolsets), [server configuration](https://github.com/github/github-mcp-server/blob/main/docs/server-configuration.md), and [GitHub issue permissions](https://docs.github.com/en/rest/authentication/permissions-required-for-github-apps).

Deliverable: a short trace of the flow, permissions, token handling, and one failed boundary test. Never give the model a token or commit client secrets.

## Optional enterprise extension: Entra ID and OBO

The local GitHub example teaches delegation without introducing a second identity provider. In an enterprise application, Microsoft Entra ID may authenticate the user and protect the application's API. Microsoft Entra's on-behalf-of flow can then obtain a token for another Entra-protected API.

That token exchange does not produce a GitHub token. GitHub remains a separate authorization domain and requires its own authorization flow or credential. The enterprise application must deliberately link the Entra principal to the verified GitHub user and keep the provider-specific tokens separate.

## Bibliography

1. [OAuth 2.0 Token Exchange, RFC 8693](https://datatracker.ietf.org/doc/html/rfc8693). **IETF standard.** Defines token exchange, delegation, impersonation, actor context, and resource targeting.
2. [OAuth 2.0 Security Best Current Practice, RFC 9700](https://datatracker.ietf.org/doc/html/rfc9700). **IETF best current practice.** Current security guidance for OAuth deployments, token handling, and narrow authorization.
3. NIST. [Zero Trust Architecture, SP 800-207](https://doi.org/10.6028/NIST.SP.800-207). **Government architecture guidance.** Grounds per-request authorization, policy decision points, and policy enforcement points.
4. NIST. [Security and Privacy Controls, SP 800-53 Rev. 5](https://doi.org/10.6028/NIST.SP.800-53r5), especially AC-6 Least Privilege and AC-5 Separation of Duties. **Government control catalog.** Provides institutional control language for privilege and accountability.
5. [Model Context Protocol specification](https://modelcontextprotocol.io/specification/latest). **Protocol specification.** Defines how the agent invokes an MCP capability; it does not define resource authorization or replace policy enforcement.
6. [MCP authorization](https://modelcontextprotocol.io/specification/latest/basic/authorization). **Protocol specification.** Defines the authorization flow for protected MCP resources and the separation between MCP client and server.
7. GitHub. [Remote MCP host integration](https://github.com/github/github-mcp-server/blob/main/docs/host-integration.md). **Platform guidance.** Describes the remote server as a protected resource and places token acquisition in the host application.
8. Microsoft. [Microsoft identity platform and OAuth 2.0 On-Behalf-Of flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow). **Optional enterprise extension.** Defines Entra OBO for downstream APIs that trust Microsoft Entra; it does not produce a GitHub token.
9. GitHub. [Creating an OAuth App](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app). **Platform documentation.** Describes registration, client credentials, homepage URL, and authorization callback URL.
10. GitHub. [Authorizing OAuth Apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps). **Platform documentation.** Describes the authorization-code flow, state, PKCE, callback, and access-token exchange.
