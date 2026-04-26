---
description: "Implement a coding request by auto-selecting the right sub-agents and gstack/Superpowers skills"
argument-hint: "[feature-or-fix-request]"
---

# /develop

You are running in Develop mode for this invocation.

The user invoked:

```text
$ARGUMENTS
```

Treat this command as the user's explicit authorization to use relevant Codex sub-agents and installed skills for the requested coding work. Do not ask the user to name agents or skills unless the requirement itself is ambiguous enough that implementation would be risky.

## Goal

Turn a plain implementation request into a complete development workflow:

1. Infer the task type.
2. Infer the affected architectural layer or layers: interface/API, application/service, domain, infrastructure/adapters, persistence, jobs/pipelines, configuration, tests, or docs.
3. Infer the domain and asset scope without assuming it is stock-only. The request may involve equities, crypto assets, accounts, market data, trading indicators, external broker/exchange APIs, or future asset classes.
4. Select the minimal useful skill set from AGENTS.md, gstack, and Superpowers.
5. Select the minimal useful sub-agent set.
6. Implement the code using the repository's existing conventions.
7. Verify with focused tests or checks.
8. Summarize what changed and what was verified.

## Required Context

Before choosing agents or editing code:

1. Read repository guidance files if present: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`.
2. Inspect the relevant application structure with `rg --files`, then read nearby files that define the local pattern.
3. Prefer existing project architecture, naming, dependency injection, tests, schemas, interfaces, services, domain models, infrastructure adapters, and persistence boundaries.
4. Identify the narrowest module ownership implied by the request instead of defaulting to any one package, asset class, or layer.

For this repository, currently expect a Python backend with layered modules. Existing names may include examples like:

- `*/interface` for controllers, routes, schemas, request/response contracts, or presentation adapters.
- `*/service` or equivalent application layer modules for use cases and orchestration.
- `*/domain` for business entities, value objects, policies, indicators, and domain rules.
- `*/infra` or equivalent infrastructure modules for external APIs, broker/exchange clients, token managers, repositories, schedulers, and adapters.
- `tests`

Treat names such as `stock` as current module names, not as permanent domain limits. If a requested feature is broader, such as crypto, multiple asset classes, or a generic market-data abstraction, choose or introduce names that fit the wider domain while preserving existing compatibility.

## Skill Routing

Always follow normal skill trigger rules. In addition, use this routing table when it applies.

Use these Superpowers skills:

- `superpowers:using-superpowers`: always, as the first process check.
- `superpowers:brainstorming`: for new behavior, new APIs, or non-trivial feature shape. Keep it lightweight; do not turn small implementation requests into long product discovery.
- `superpowers:test-driven-development`: for feature work and bug fixes. Add or update a focused failing test first when practical.
- `superpowers:systematic-debugging`: for failures, regressions, broken tests, or unclear bugs.
- `superpowers:writing-plans`: for broad multi-file changes where a short written plan will reduce mistakes.
- `superpowers:subagent-driven-development`: when two or more independent implementation or review tasks can run in parallel.
- `superpowers:requesting-code-review`: before finishing substantial changes.
- `superpowers:verification-before-completion`: before claiming the work is complete.
- `superpowers:finishing-a-development-branch`: only when the user asks to finish, merge, PR, or ship.

Use these gstack skills:

- `investigate`: for root-cause debugging or unexplained behavior.
- `plan-eng-review`: for architecture, data flow, layer boundaries, migration, external integration, or failure-mode decisions.
- `review`: before landing risky or multi-file changes, especially changes that could pass CI but fail in production.
- `qa` or `qa-only`: for web/app behavior testing when the task includes UI or end-to-end behavior.
- `cso`: for auth, secrets, permissions, input trust boundaries, sensitive financial flows, broker/exchange credentials, or external integrations.
- `ship`: only when the user asks to create a PR, push, deploy, or ship.

## Sub-Agent Routing

Spawn sub-agents only when they materially help and can work in parallel with your local critical path. Do not spawn agents just to look busy. Use disjoint ownership and tell each worker they are not alone in the codebase and must not revert others' edits.

Default mappings:

- `python-pro`: Python implementation across API/interface, service, domain, infrastructure, tests, packaging, typing, and framework integration.
- `refactoring-specialist`: multi-file cleanup, preserving behavior, aligning new code with local structure.
- `sql-pro`: SQL queries, schemas, migrations, repositories, database constraints, transaction behavior.
- `data-engineer`: ingestion, ETL, market data pipelines, scheduled jobs, transformations, data quality, and replay/idempotency behavior.
- `fintech-engineer`: accounts, orders, balances, portfolios, brokerage/exchange integration, reconciliation, settlement, and compliance-sensitive transaction flows.
- `quant-analyst`: indicators, trading signals, backtests, numeric thresholds, strategy logic, simulations, and market-data assumptions.
- `security-auditor`: auth, secrets, token handling, permissions, SSRF, input validation, external API trust boundaries.
- `risk-manager`: financial, operational, product, or architecture risk tradeoffs, especially real-money behavior.
- `machine-learning-engineer`: model training, inference, feature pipelines, model serving.
- `code-reviewer`: final review for correctness, maintainability, missing tests, and risky implementation choices.

Suggested bundles:

- Interface/API request: `python-pro`, optionally `security-auditor` for trust boundaries, optionally `code-reviewer`.
- Service/application use case: `python-pro`, optionally `refactoring-specialist`, optionally `code-reviewer`.
- Domain model, policy, indicator, or signal: `python-pro`, `quant-analyst` when numeric or strategy semantics matter, optionally `code-reviewer`.
- Infrastructure adapter for broker, exchange, market data, auth/token, or external API: `python-pro`, `security-auditor`, optionally `fintech-engineer`, optionally `risk-manager`.
- Persistence, repository, schema, migration, or query behavior: `python-pro`, `sql-pro`, optionally `data-engineer`, optionally `code-reviewer`.
- Market data ingestion, scheduled fetch, backfill, or replay pipeline: `python-pro`, `data-engineer`, optionally `sql-pro`.
- Account, portfolio, order, balance, or real-money flow: `python-pro`, `fintech-engineer`, `security-auditor`, optionally `risk-manager`.
- Multi-asset abstraction or asset-class expansion such as equities plus crypto: `python-pro`, `refactoring-specialist`, optionally `fintech-engineer`, `quant-analyst`, or `data-engineer` depending on the affected behavior.
- Bug or failing test: use debugging skills first; add `python-pro` only if implementation can proceed independently.
- Refactor request: `refactoring-specialist`, `python-pro`, `code-reviewer`.

## Execution Rules

1. Start with a short note naming the selected skills and agents.
2. If the task is small, keep the plan to 2-4 bullets and implement directly.
3. If the task is broad, write a concise plan and break work into independently verifiable pieces.
4. Do local critical-path work yourself. Delegate sidecar implementation/review tasks only when they can proceed independently.
5. Use `apply_patch` for manual edits.
6. Add focused tests near the changed behavior. If a failing test first is impractical, explain why briefly and still verify behavior.
7. Run the narrowest meaningful verification first, then broader checks when risk warrants it.
8. Never revert unrelated user changes.
9. Do not run `ship`, push, create PRs, or deploy unless the user explicitly asks.

## Final Response

Keep the final response concise and include:

- Files changed.
- Sub-agents and skills actually used.
- Verification commands and results.
- Any known limitations or follow-up work.
