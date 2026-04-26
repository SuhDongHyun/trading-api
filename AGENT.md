# Agent Skill Index

This project has local skill packs installed for agent-assisted development. Use this file as the quick routing table before choosing a skill.

Sources:
- gstack README: https://github.com/garrytan/gstack
- Superpowers README: https://github.com/obra/superpowers

## gstack

gstack is a sprint workflow for product, engineering, design, QA, security, release, and operations work. Its normal flow is:

1. Think
2. Plan
3. Build
4. Review
5. Test
6. Ship
7. Reflect

### Product And Planning

- `/office-hours` - YC-style product interrogation. Uses six forcing questions to clarify pain, reframe the request, challenge premises, and produce a design doc.
- `/plan-ceo-review` - Founder/CEO plan review. Rethinks scope and product strategy with expansion, selective expansion, hold-scope, or reduction modes.
- `/autoplan` - Runs the plan review pipeline automatically, including CEO, design, engineering, and DX review when relevant.

### Architecture And Engineering Review

- `/plan-eng-review` - Engineering manager review for architecture, data flow, diagrams, edge cases, tests, and failure modes.
- `/review` - Staff engineer code review for bugs that can pass CI but fail in production. Flags completeness gaps and may auto-fix obvious issues.
- `/investigate` - Root-cause debugging workflow. Investigates before fixing and avoids guessing.

### Design

- `/plan-design-review` - Design plan critique. Scores design dimensions, explains what a better version needs, and revises the plan.
- `/design-consultation` - Creates a design system from scratch, including aesthetic direction, typography, color, layout, spacing, and motion.
- `/design-shotgun` - Generates multiple visual directions, opens a comparison board, collects feedback, and iterates.
- `/design-html` - Converts an approved design or prompt into production-quality HTML/CSS.
- `/design-review` - Live visual QA and source-code fixes for design issues, using screenshots and before/after verification.

### Developer Experience

- `/plan-devex-review` - Interactive DX plan review for developer personas, competitor benchmarking, time-to-hello-world, magical moments, and friction.
- `/devex-review` - Live DX audit that actually tests docs, setup, onboarding, CLI help, and error states.

### Browser, QA, And Testing

- `/browse` - Headless Chromium control for navigation, screenshots, interaction, responsive checks, forms, dialogs, and bug evidence.
- `/open-gstack-browser` - Launches the visible GStack Browser with sidebar, stealth, screenshots, cookie import, and agent handoff.
- `/qa` - Tests a web app, fixes bugs found, commits fixes atomically, re-verifies, and generates regression tests.
- `/qa-only` - Same QA method as `/qa`, but report-only with no code changes.
- `/setup-browser-cookies` - Imports cookies from a real browser so authenticated flows can be tested.
- `/benchmark` - Captures performance baselines, Core Web Vitals, resource sizes, and before/after comparisons.
- `/canary` - Post-deploy monitoring for console errors, regressions, page failures, and visual anomalies.

### Security

- `/cso` - Chief Security Officer audit. Uses OWASP Top 10, STRIDE threat modeling, supply-chain checks, and concrete exploit scenarios.

### Release And Operations

- `/ship` - Release engineer workflow: sync base, run tests, review diff, update docs/changelog/version as needed, push, and open a PR.
- `/land-and-deploy` - Merge an approved PR, wait for CI/deploy, and verify production health.
- `/setup-deploy` - One-time deploy configuration detection for `/land-and-deploy`.
- `/document-release` - Updates docs after shipping so README, architecture docs, contributing docs, changelogs, and TODOs match reality.
- `/gstack-upgrade` - Updates gstack and reports what changed.

### Collaboration, Memory, And Safety

- `/pair-agent` - Shares a browser session with another AI agent using scoped tokens and tab isolation.
- `/learn` - Reviews, searches, prunes, and exports persistent project learnings.
- `/retro` - Engineering retrospective across commits, contributors, test health, shipping patterns, and growth areas.
- `/careful` - Warns before destructive commands such as `rm -rf`, `DROP TABLE`, or force-push.
- `/freeze` - Restricts edits to one directory.
- `/guard` - Combines `/careful` and `/freeze`.
- `/unfreeze` - Clears an active edit boundary.

### gstack Binaries

- `gstack-model-benchmark` - Runs the same prompt across Claude, GPT via Codex CLI, and Gemini, then compares latency, tokens, cost, and optional quality scores.
- `gstack-taste-update` - Updates persistent design taste memory from design approvals and rejections.

## Superpowers

Superpowers is a software development methodology for coding agents. It emphasizes Socratic design clarification, written plans, isolated workspaces, TDD, code review, and evidence before completion.

### Basic Workflow

1. `brainstorming` - Use before building or changing behavior. Refines rough ideas through questions, explores alternatives, presents the design in readable sections, and saves a design document.
2. `using-git-worktrees` - Use after design approval when isolated feature work is useful. Creates a separate workspace and verifies a clean baseline.
3. `writing-plans` - Use with an approved design. Produces small implementation tasks with exact files, code, and verification steps.
4. `subagent-driven-development` or `executing-plans` - Use with a plan. Either dispatches subagents with review loops or executes batches with checkpoints.
5. `test-driven-development` - Use during implementation. Enforces red, green, refactor: failing test first, minimal implementation, passing verification, then cleanup.
6. `requesting-code-review` - Use between tasks or before completion. Reviews against the plan and reports issues by severity.
7. `finishing-a-development-branch` - Use when work is complete. Verifies tests and presents merge, PR, keep, or discard options.

### Testing

- `test-driven-development` - Red, green, refactor cycle and testing anti-pattern guidance.

### Debugging

- `systematic-debugging` - Four-phase root-cause process with tracing, defense-in-depth, and condition-based waiting techniques.
- `verification-before-completion` - Requires concrete verification before claiming work is fixed or complete.

### Collaboration

- `brainstorming` - Socratic design refinement before implementation.
- `writing-plans` - Detailed implementation plans.
- `executing-plans` - Batch execution with human checkpoints.
- `dispatching-parallel-agents` - Concurrent subagent workflows for independent tasks.
- `requesting-code-review` - Pre-review checklist and review workflow.
- `receiving-code-review` - Structured response to code review feedback.
- `using-git-worktrees` - Parallel development branch workflow.
- `finishing-a-development-branch` - Merge/PR decision workflow.
- `subagent-driven-development` - Fast iteration with fresh subagents and two-stage review.

### Meta

- `using-superpowers` - Skill-system entrypoint and routing discipline.
- `writing-skills` - Create and test new skills following Superpowers practices.

### Philosophy

- Prefer test-driven development.
- Prefer systematic process over ad-hoc guessing.
- Reduce complexity before adding machinery.
- Verify with evidence before making completion claims.
