# User-data management for AI systems

> **Legal disclaimer:** This chapter is for educational purposes only. It is not legal advice and does not determine an organization's compliance obligations. Those obligations depend on jurisdiction, controller or processor role, purpose, data subjects, sector, contract, and system classification. Obtain qualified legal and privacy advice for real systems.

## Production question

What data does the system handle, where does it go, and what controls does each step require?

## Learning objectives

After reading this chapter, students can:

1. **Explain** why user data is broader than PII.
2. **Trace** data through an agent workflow, including prompts, tools, outputs, memory, and traces.
3. **Draft** a small inventory showing what is collected, why, where it is stored, who can access it, and when it is deleted.

## Core idea

An agent creates a data flow, not just a response. A request may pass through a browser, application, model provider, retrieval system, MCP server, downstream API, memory store, log system, cache, and backup.

Every step can create another copy or another derived record. The team needs to know what each record contains, why it exists, who can access it, and how long it remains available.

## Motivation

Teams often treat user data as if it meant only direct identifiers such as names, phone numbers, or government IDs. In an AI system, user data can include:

- prompts and uploaded files;
- conversation history and feedback;
- retrieved context;
- tool arguments and results;
- model responses and action proposals;
- memory and preferences;
- approvals and corrections;
- traces, logs, caches, and backups.

Some of these records may be personal data. Others may be confidential, proprietary, regulated, public, or system metadata. The classification depends on the record and its context.

## Core vocabulary

- **User data:** information supplied by, associated with, or produced through a user's interaction with the system.
- **Personal data:** information relating to an identified or identifiable natural person, directly or indirectly, as defined by GDPR Article 4(1). Whether a record qualifies depends on its content, available means of identification, and context.
- **Sensitive information:** a policy category that may include GDPR special-category data, criminal-offence data, confidential business information, security secrets, or other regulated information. It is not a single legal category.
- **Derived data:** information summarized, inferred, classified, or generated from other data.
- **Telemetry:** records about system operation, such as latency, errors, token counts, and tool calls.
- **Data inventory:** a short record of what data exists, why it is processed, which storage or processing systems hold it, who can access it, and when it is deleted.

## Recommendation 1 : Three distinctions to keep straight

### User data is broader than PII

A prompt about a confidential business negotiation may be user data without containing personal data, although the surrounding context may change that classification. A prompt about an employee's health condition may be both.

An identifier such as a user ID, object ID, tenant ID, or correlation ID may be personal data if the organization can link it to a person. Pseudonymized or opaque identifiers are not automatically anonymous.

### Outputs need their own classification

An LLM output does not automatically inherit the legal status of every input. It may still reproduce, relate to, infer, or be derived from personal data. Classify the output according to its content, linkability, purpose, and context.

### Traces are data too

Calling something telemetry does not make it safe. A trace containing a prompt, retrieved document, tool argument, output, or linkable identifier may need safeguards appropriate to its content, access, retention, and risk. Those safeguards need not be identical to the source record's controls.

## Recommendation 2: Build a data inventory

This matters because the inventory gives the team something it can inspect and audit. By linking each data flow to its purpose, storage, access, retention, and transfers, the team can review whether the system's actual handling is consistent with applicable regulations, internal policies, contracts, and user agreements. The inventory does not prove compliance on its own; it makes gaps, undocumented processing, and conflicting commitments visible.

The inventory does not need to start as a large catalog. For each important data flow, record seven practical fields:

| Field | Question |
| --- | --- |
| Data | What is captured, created, or transmitted? |
| Classification | Is it user content, personal data, sensitive data, confidential data, secret, telemetry, derived data, or audit data? |
| Purpose | Why does the system need it? |
| Storage | Which application, provider, database, vector store, memory store, log, cache, or backup holds it? |
| Access | Which user, service, MCP server, vendor, or team can read or change it? |
| Retention | When is it deleted, and what happens to backups or provider copies? |
| Transfer | Does it cross a team, vendor, country, or trust boundary? |

Add provenance, legal basis, rights handling, and detailed controls when the use case requires them.

IMPORTANT: Talk to a legal team to assess the need for a DPIA, especially where processing is likely to result in a risk to people’s rights and freedoms (see GDPR).

## Recommendation 3: LLM-as-a-judge is another processing flow

WARNING: An evaluation model may process user data and may consume or produce personal data.

Consider a simple scope check for an agent that manages GitHub issues.

**Judge input:**

```text
Agent scope: read and summarize issues in repositories the user can access.
User request: "Find the open issues labeled competitive-analysis that mention Project Nightfall in the Acme/product-platform repository."
```

**Judge output 1, the grade:**

```text
in_scope
```

**Judge output 2, the reason:**

```text
The request asks the agent to search and summarize issues in an accessible repository. "competitive-analysis" and "Project Nightfall" are filters for issue retrieval; the request does not ask the agent to modify an issue or access another repository.
```

The grade is simple. But the reason is a verbose generated record that can repeat personal data, confidential project information, secret product names, repository names, issue labels, or the user's original request.

The same analysis applies when the judge evaluates relevance, safety, policy compliance, or tool selection. A judge creates a distinct processing flow with its own purpose, data, access, retention, and risk analysis. Evaluation data may create privacy obligations where it contains or relates to personal data; it may also raise confidentiality, security, intellectual-property, or contractual obligations.

Useful controls include redaction, gated content capture, separate retention periods, access controls, and deletion across the judge, application logs, caches, backups, and providers.

## Bibliography

1. European Parliament and Council. [Regulation (EU) 2016/679, General Data Protection Regulation](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679), especially Articles 5, 25, 30, 32, and 35. **Regulation.** Primary source for personal-data definition, minimization, transparency, processing records, security, and DPIAs.
2. Information Commissioner's Office. [How do we ensure individual rights in our AI systems?](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/how-do-we-ensure-individual-rights-in-our-ai-systems/). **Supervisory-authority guidance.** Addresses prompts, outputs, model results, logs, rights requests, and monitoring.
3. Information Commissioner's Office. [How should we assess security and data minimisation in AI?](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/how-should-we-assess-security-and-data-minimisation-in-ai/). **Supervisory-authority guidance.** Covers data movement, intermediate files, de-identification, query monitoring, and audit trails.
4. European Union. [Regulation (EU) 2024/1689, Artificial Intelligence Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng), especially Articles 10, 12, 13, 14, 17, 19, and 26. **Regulation.** Relevant primarily to providers and deployers of applicable high-risk AI systems, including requirements concerning data governance, logging, transparency, human oversight, and monitoring.
5. NIST. [Privacy Framework](https://www.nist.gov/privacy-framework). **Government framework.** Provides a structure for identifying, governing, controlling, communicating, and protecting privacy risk.
6. NIST. [Protecting the Confidentiality of Personally Identifiable Information (PII), SP 800-122](https://csrc.nist.gov/pubs/sp/800/122/final). **Government guidance.** Useful for PII identification and confidentiality impact; PII is narrower than all user data.
7. ISO/IEC. [ISO/IEC 27701:2025](https://www.iso.org/standard/27701). **International standard.** Optional depth for privacy information management and controller/processor accountability. The 2019 edition is withdrawn.
