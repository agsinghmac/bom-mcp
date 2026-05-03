# Quickstart: ESP Selection and BOM Readiness Skill Resource

## Goal

Manually verify that the MCP server exposes and serves `skill://esp-selection-bom-readiness` and that an agent can follow it using existing tools.

## Prerequisites

- Python dependencies installed from `requirements.txt`
- MCP server runnable via `python run_mcp.py`
- Existing ESP/BOM sample data present

## Manual Verification Steps

1. Start MCP server.
2. List MCP resources from host/client and confirm `skill://esp-selection-bom-readiness` appears.
3. Read resource content and verify it includes:
   - Required inputs (`required_flow_m3d`, `max_power_kw`, `frequency_hz`)
   - Ranking rules (flow -> power -> frequency)
   - Readiness rule (critical availability >= 80%)
   - Availability taxonomy (GREEN/YELLOW/RED/BLOCKED)
   - Procurement alert rules
   - Output template
4. Execute a manual walkthrough using existing tools:
   - Retrieve candidate ESPs and model details
   - Retrieve BOM summary and BOM parts
   - Retrieve part details for flagged items
5. Produce final output from walkthrough and confirm it includes:
   - Ranked ESP recommendations
   - Critical part percentage
   - Field-ready status
   - Availability flags
   - Procurement alerts with urgency

## Expected Outcome

- Resource is discoverable via `skill://` URI.
- Resource instructions are sufficient for complete assessment without extra assumptions.
- Existing MCP tools provide all required data inputs for the workflow.
