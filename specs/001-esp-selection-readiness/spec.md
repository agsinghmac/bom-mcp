# Feature Specification: ESP Selection and BOM Readiness Assessment

**Feature Branch**: `001-add-esp-readiness-resource`  
**Created**: 2026-04-27  
**Status**: Draft  
**Input**: User description: "add a new resource type for the MCP server. The resource is basically an instruction that can be used as an agent skill for ESP Selection & BOM Readiness Assessment. Given an engineer's operational requirement (flow rate, power, frequency), select the best-fit ESP model and assess whether its BOM is field ready, flagging critical part density and surfacing part details for procurement review."

**Scope Clarification**: This feature creates a reusable MCP resource-based skill exposed through `skill://` URIs. Agents discover and read skill instructions from MCP resources (not from `SKILL.md`) and then execute existing MCP tools to produce ESP recommendations and BOM readiness outputs.

## User Scenarios & Manual Verification *(mandatory)*

### User Story 1 - Recommend Best-Fit ESP (Priority: P1)

A production engineer provides required flow, maximum available power, and operating frequency, then receives a ranked list of ESP model recommendations that best match those constraints.

**Why this priority**: Selecting a viable ESP model is the core decision needed before any downstream readiness or procurement work can start.

**Independent Verification**: Can be fully verified by submitting one valid operating requirement set and confirming that a ranked recommendation list is returned with clear ranking rationale.

**Acceptance Scenarios**:

1. **Given** valid flow, power, and frequency inputs, **When** the engineer requests a recommendation, **Then** the system returns at least one ranked ESP model that satisfies mandatory constraints.
2. **Given** multiple models satisfy constraints, **When** recommendations are generated, **Then** the output is ordered from best fit to lower fit using consistent ranking criteria.

---

### User Story 2 - Assess BOM Field Readiness (Priority: P2)

For each recommended ESP model, the engineer receives a BOM readiness report that quantifies critical-part density, highlights availability risk, and indicates whether the BOM is field ready.

**Why this priority**: A recommendation is not actionable unless the associated BOM readiness can support field deployment.

**Independent Verification**: Can be fully verified by selecting a recommended ESP and confirming the report includes critical-part percentage, readiness status, and availability flags.

**Acceptance Scenarios**:

1. **Given** a recommended ESP model with BOM data, **When** readiness is assessed, **Then** the report includes critical-part percentage and a field-readiness status.
2. **Given** BOM items with elevated risk indicators, **When** readiness is assessed, **Then** the report flags those items for attention.

---

### User Story 3 - Support Procurement Review (Priority: P3)

A procurement reviewer inspects the readiness output and sees part-level alerts and details needed to prioritize sourcing actions before field deployment.

**Why this priority**: Procurement visibility reduces deployment risk and prevents late-stage schedule delays.

**Independent Verification**: Can be fully verified by reviewing a generated report and confirming that flagged parts include enough detail to guide sourcing decisions.

**Acceptance Scenarios**:

1. **Given** a readiness report with flagged parts, **When** a procurement reviewer opens the report, **Then** each alert includes part identity, risk reason, and urgency classification.
2. **Given** no material BOM risk, **When** a procurement reviewer checks the report, **Then** the report clearly indicates no active procurement alerts.

### Edge Cases

- What happens when no ESP model satisfies all required operating constraints?
- How does the system handle missing or incomplete BOM data for an otherwise valid ESP candidate?
- How does the system respond when flow, power, or frequency inputs are out of valid engineering ranges?
- What happens when two or more ESP models have identical fit scores?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose an MCP skill resource under a `skill://` URI for ESP Selection and BOM Readiness Assessment.
- **FR-002**: The `skill://` resource MUST define required inputs: required flow, maximum power, and operating frequency, including validation rules, engineering bounds, and corrective guidance for invalid or missing values.
- **FR-003**: The `skill://` resource MUST define recommendation ranking logic: flow match (primary) → power headroom, favoring candidates with sufficient power and the smallest acceptable excess → frequency compatibility as the third ranking criterion rather than a hard pre-filter.
- **FR-004**: The `skill://` resource MUST define an explainable fit-summary format indicating the primary constraint (flow) and whether power/frequency are within margin or at/beyond limits.
- **FR-005**: The `skill://` resource MUST define the BOM readiness assessment process for each recommended ESP model.
- **FR-006**: The `skill://` resource MUST define how to calculate and report critical-part density as a percentage of BOM line items.
- **FR-007**: The `skill://` resource MUST define the four-level availability taxonomy (GREEN/YELLOW/RED/BLOCKED), including mapping rules and readiness impact of RED/BLOCKED critical parts.
- **FR-008**: The `skill://` resource MUST define procurement alert rules for BOM conditions that may block or delay field readiness, including urgency classification.
- **FR-009**: The `skill://` resource MUST define how agents retrieve and include part-level details for all flagged BOM items for procurement review.
- **FR-010**: The `skill://` resource MUST define the final combined output format: ranked ESP recommendations plus BOM readiness report (critical parts %, availability flags, procurement alerts).
- **FR-011**: System MUST make the skill resource discoverable by agents through MCP resource listing and readable via MCP resource retrieval.
- **FR-012**: The skill guidance MUST instruct agents to orchestrate existing MCP tools to gather ESP, BOM, and part data; the feature MUST NOT require creating a new assessment tool endpoint.

### Key Entities *(include if feature involves data)*

- **Operational Requirement**: Input record containing required flow, maximum power, and operating frequency used to evaluate candidate ESP models.
- **ESP Recommendation**: Ranked candidate model with fit score, ranking position, and fit rationale including which constraint is primary and whether power/frequency have margin.
- **BOM Readiness Report**: Assessment output for a recommended model including critical-part percentage, field-ready status (based on ≥ 80% critical-part availability), and aggregated risk indicators.
- **Part Readiness Alert**: Part-level alert item containing part identity, availability flag (GREEN/YELLOW/RED/BLOCKED), risk reason, and procurement urgency. RED/BLOCKED flags on critical parts trigger high-risk alerts.
- **Availability Flag**: Four-level taxonomy mapping supply status: GREEN (≤ 4 weeks), YELLOW (5–12 weeks, confirmed), RED (>12 weeks or uncertain), BLOCKED (obsolete/no source). RED/BLOCKED parts are flagged as high-risk; RED/BLOCKED critical parts block field-ready status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Agents can discover and read the `skill://` resource and execute a full assessment workflow without additional instruction.
- **SC-002**: At least 90% of pilot engineers report that the skill's ranking methodology (flow → power → frequency) is clear enough to support ESP selection without additional interpretation.
- **SC-003**: At least 90% of pilot assessments produce a BOM readiness report that correctly identifies critical-part availability, applies the 80% threshold, and classifies field-ready status without errors.
- **SC-004**: At least 90% of flagged BOM risks in pilot runs include sufficient part-level detail and urgency classification to guide procurement decisions without additional data requests.

## Clarifications

### Session 2026-04-27

- Q: How should "field ready" and "readiness status" be quantified for acceptance criteria? → A: A BOM is field ready if critical-part availability is ≥ 80% (i.e., ≤ 20% critical parts flagged as unavailable or high-risk). Non-critical parts can have lower availability without affecting field-ready status.
- Q: What are the explicit ranking criteria for ESP model recommendations? → A: Rank by flow match (primary) → power headroom, favoring sufficient power with the smallest acceptable excess → frequency compatibility as a ranking criterion, not a hard exclusion filter; explainable fit summary should state which constraint is primary (flow) and whether power/frequency have margin or are at/beyond limits.
- Q: What is the standardized availability flag taxonomy and how does it map to readiness alerts? → A: Four-level taxonomy (GREEN ≤4wks / YELLOW 5-12wks / RED >12wks / BLOCKED obsolete); RED/BLOCKED flags are high-risk; critical parts with RED/BLOCKED status block field-ready status (count against 80% threshold).
- Q: Should this be an MCP tool/parameterized resource or a static skill instruction? → A: Expose the skill as an MCP resource using the `skill://` scheme so agents discover/read instructions from MCP resources, then execute existing MCP tools; do not use `SKILL.md`-based instructions for this feature.

## Assumptions

- Existing ESP model and BOM datasets are available and maintained with sufficient quality for recommendation and readiness assessment.
- Availability flags required for readiness reporting are already present in the accessible BOM/part data sources.
- This feature focuses on recommendation and readiness assessment output; final procurement execution workflows remain outside scope.
- Users invoking this feature already understand engineering units for flow, power, and frequency.
