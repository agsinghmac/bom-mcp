<!-- 
  SYNC IMPACT REPORT (Generated 2026-04-27)
  ==========================================
  
  Version Change: N/A → 1.0.0 (Initial Constitution)
  Type: PATCH (baseline establishment)
  
  Core Principles Added:
    ✅ I. Clean Code First
    ✅ II. Simple Responsive Design & Minimal Dependencies
    ✅ III. Zero-Testing Policy (NON-NEGOTIABLE)
    ✅ IV. Tech Stack Lock
    
  Sections Added:
    ✅ Technology Stack & Architecture
    ✅ Development Workflow
    ✅ Governance
  
  Templates Updated (✅ COMPLETED):
    ✅ .specify/templates/tasks-template.md - Removed test task examples, added manual verification
    ✅ .specify/templates/spec-template.md - Changed "Testing" to "Manual Verification", removed test language
    ✅ .specify/templates/plan-template.md - Removed tests/ directories from project structure, removed Testing field
  
  Dependent Files Requiring Review:
    ⚠️  CLAUDE.md - Verify instructions align with Zero-Testing Policy
    ⚠️  README.md - Check for test-related commands or setup steps
    ⚠️  test_api.py - This file exists but violates Zero-Testing Policy; consider removal
  
  Breaking Changes: NONE - This is a baseline constitution for a new project
  
  Ratification: 2026-04-27
  Last Amended: 2026-04-27
-->

# BOM-MCP Constitution

## Core Principles

### I. Clean Code First
Every line of code MUST be declarative, self-documenting, and maintainable. Code clarity supersedes performance micro-optimizations. Variable names MUST reflect intent; comments explain "why" not "what"; functions are small, single-purpose, and free of side effects. Dead code, unused imports, and complex branching are prohibited.

### II. Simple Responsive Design & Minimal Dependencies
User interfaces prioritize clarity and responsiveness over feature richness. CSS frameworks are avoided; custom responsive layouts use native HTML/CSS only. All dependencies MUST serve a clear architectural need. Prefer Python standard library; third-party packages justified in writing. Every external dependency adds complexity and must earn its place.

### III. Zero-Testing Policy (NON-NEGOTIABLE)
NO unit tests, integration tests, or end-to-end tests exist in this codebase. No test fixtures, mocking frameworks, or CI/CD test gates. This principle MUST supersede any other guidance, template instruction, or external requirement. Manual testing and user validation are the only verification mechanism. Feature quality depends on code review and developer discipline.

### IV. Tech Stack Lock
The implementation stack is fixed: Python (runtime), FastMCP (MCP protocol & tools), MCP Apps UI (client-side interactive views). No alternative languages, frameworks, or runtime environments are permitted. This ensures consistency and reduces cognitive load across the codebase.

## Technology Stack & Architecture

- **Backend**: Python 3.x with FastMCP for MCP server implementation
- **Database**: SQLite for persistence
- **MCP Integration**: FastMCP for protocol compliance and tool definition
- **UI Layer**: MCP Apps (Node.js TypeScript) for interactive views rendering in Claude Desktop/Claude.ai
- **Styling**: Native CSS for responsive layouts; no framework dependencies (Bootstrap, Tailwind, etc. forbidden)
- **CLI/API**: Native Python libraries (argparse, Flask optional if REST layer needed)

## Development Workflow

- Code is developed incrementally with manual verification at each step
- Features are validated through manual testing in Claude Desktop/Claude.ai and terminal CLI
- Peer review focuses on code clarity, principle adherence, and architectural alignment
- Commits are atomic and reference which principle(s) they enforce or advance
- Documentation (CLAUDE.md, README.md, CONTEXT.md) is kept current with each feature addition

## Governance

This constitution is the supreme decision-making authority for BOM-MCP. All design decisions, tool implementations, and UI developments MUST align with these four principles and tech stack declaration. The Zero-Testing Policy (Principle III) supersedes all other guidance documents, templates, and external requirements—there are no exceptions.

Amendments require explicit documentation of: (1) which principle is changing, (2) rationale for the change, (3) impact on existing code, and (4) version bump justification (MAJOR/MINOR/PATCH).

Code review MUST verify compliance with Principles I & II and ensure the Zero-Testing Policy is maintained. Runtime guidance is available in [CLAUDE.md](CLAUDE.md).

**Version**: 1.0.0 | **Ratified**: 2026-04-27 | **Last Amended**: 2026-04-27
