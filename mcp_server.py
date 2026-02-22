"""
MCP Server for ESP Parts and BOM Database

Provides tools to query and manage Electric Submersible Pump parts,
assemblies, and bills of materials.
"""

from contextlib import contextmanager
from typing import Optional
from fastmcp import FastMCP
from esp_db import ESPDatabase, init_database, DatabasePath

# Initialize FastMCP server
mcp = FastMCP("ESP BOM Database")


# Context manager for database lifecycle
@contextmanager
def get_db():
    """Get database instance with proper lifecycle management."""
    db = ESPDatabase(DatabasePath.DEFAULT)
    try:
        yield db
    finally:
        db.close()


# ============ ESP Tools ============

@mcp.tool
def list_esps() -> list[dict]:
    """List all ESP pump models with their specifications."""
    with get_db() as db:
        return db.get_all_esps()

# Register MCP App for list_esps tool
list_esps._meta = {"ui": {"resourceUri": "mcp_app/index.html"}}


@mcp.tool
def get_esp(esp_id: str) -> dict | None:
    """Get a complete ESP with all assemblies and parts.

    Args:
        esp_id: ESP identifier (e.g., "ESP-001")
    """
    with get_db() as db:
        esp = db.get_esp(esp_id)
        if esp:
            return esp
        return None


@mcp.tool
def get_esp_bom(esp_id: str) -> list[dict] | None:
    """Get the Bill of Materials (flat parts list) for an ESP.

    Args:
        esp_id: ESP identifier (e.g., "ESP-001")
    """
    with get_db() as db:
        return db.get_esp_bom_parts(esp_id)

get_esp_bom._meta = {"ui": {"resourceUri": "mcp_app/bom-table.html"}}


@mcp.tool
def get_bom_summary(esp_id: str) -> dict | None:
    """Get a BOM summary for an ESP (total parts, weight, critical count).

    Args:
        esp_id: ESP identifier (e.g., "ESP-001")
    """
    with get_db() as db:
        return db.get_bom_summary(esp_id)

get_bom_summary._meta = {"ui": {"resourceUri": "mcp_app/bom-summary.html"}}


@mcp.tool
def get_esps_by_series(series: str) -> list[dict]:
    """Get all ESPs in a given series.

    Args:
        series: Series name (e.g., "RedZone Pro", "AquaMax")
    """
    with get_db() as db:
        return db.get_esps_by_series(series)


@mcp.tool
def create_esp(
    esp_id: str,
    model_name: str,
    series: str,
    power_rating_kw: float,
    voltage_v: int,
    frequency_hz: float,
    flow_rate_m3d: float,
    stages: int,
    cable_length_m: float,
    assembly_codes: Optional[list[str]] = None,
) -> dict:
    """Create a new ESP pump model.

    Args:
        esp_id: Unique identifier (e.g., "ESP-011")
        model_name: Model name (e.g., "RedZone Pro 500")
        series: Series name (e.g., "RedZone Pro")
        power_rating_kw: Power rating in kilowatts
        voltage_v: Voltage in volts
        frequency_hz: Frequency in Hz
        flow_rate_m3d: Flow rate in m3/day
        stages: Number of pump stages
        cable_length_m: Cable length in meters
        assembly_codes: Optional list of assembly codes to include
    """
    with get_db() as db:
        return db.create_esp(
            esp_id=esp_id,
            model_name=model_name,
            series=series,
            power_rating_kw=power_rating_kw,
            voltage_v=voltage_v,
            frequency_hz=frequency_hz,
            flow_rate_m3d=flow_rate_m3d,
            stages=stages,
            cable_length_m=cable_length_m,
            assembly_codes=assembly_codes,
        )


@mcp.tool
def update_esp(
    esp_id: str,
    model_name: Optional[str] = None,
    series: Optional[str] = None,
    power_rating_kw: Optional[float] = None,
    voltage_v: Optional[int] = None,
    frequency_hz: Optional[float] = None,
    flow_rate_m3d: Optional[float] = None,
    stages: Optional[int] = None,
    cable_length_m: Optional[float] = None,
) -> dict | None:
    """Update an ESP's specifications.

    Args:
        esp_id: ESP identifier to update
        model_name: New model name (optional)
        series: New series name (optional)
        power_rating_kw: New power rating (optional)
        voltage_v: New voltage (optional)
        frequency_hz: New frequency (optional)
        flow_rate_m3d: New flow rate (optional)
        stages: New stages count (optional)
        cable_length_m: New cable length (optional)
    """
    with get_db() as db:
        return db.update_esp(
            esp_id=esp_id,
            model_name=model_name,
            series=series,
            power_rating_kw=power_rating_kw,
            voltage_v=voltage_v,
            frequency_hz=frequency_hz,
            flow_rate_m3d=flow_rate_m3d,
            stages=stages,
            cable_length_m=cable_length_m,
        )


@mcp.tool
def delete_esp(esp_id: str) -> bool:
    """Delete an ESP pump model.

    Args:
        esp_id: ESP identifier to delete
    """
    with get_db() as db:
        return db.delete_esp(esp_id)


@mcp.tool
def add_assembly_to_esp(esp_id: str, assembly_code: str) -> dict | None:
    """Add an assembly to an ESP.

    Args:
        esp_id: ESP identifier
        assembly_code: Assembly code to add
    """
    with get_db() as db:
        return db.add_assembly_to_esp(esp_id, assembly_code)


@mcp.tool
def remove_assembly_from_esp(esp_id: str, assembly_code: str) -> dict | None:
    """Remove an assembly from an ESP.

    Args:
        esp_id: ESP identifier
        assembly_code: Assembly code to remove
    """
    with get_db() as db:
        return db.remove_assembly_from_esp(esp_id, assembly_code)


# ============ Part Tools ============

@mcp.tool
def list_parts() -> list[dict]:
    """List all parts in the database."""
    with get_db() as db:
        return db.get_all_parts()

list_parts._meta = {"ui": {"resourceUri": "mcp_app/parts-table.html"}}


@mcp.tool
def get_part(part_number: str) -> dict | None:
    """Get a specific part by part number.

    Args:
        part_number: Part identifier (e.g., "ESP-MTR-001")
    """
    with get_db() as db:
        return db.get_part(part_number)

get_part._meta = {"ui": {"resourceUri": "mcp_app/part-detail.html"}}


@mcp.tool
def search_parts(query: str) -> list[dict]:
    """Search parts by name, category, or material.

    Args:
        query: Search query string
    """
    with get_db() as db:
        return db.search_parts(query)

search_parts._meta = {"ui": {"resourceUri": "mcp_app/parts-table.html"}}


@mcp.tool
def get_parts_by_category(category: str) -> list[dict]:
    """Get all parts in a given category.

    Args:
        category: Category name (e.g., "Motor", "Pump", "Seal", "Cable")
    """
    with get_db() as db:
        return db.get_parts_by_category(category)

get_parts_by_category._meta = {"ui": {"resourceUri": "mcp_app/parts-table.html"}}


@mcp.tool
def get_critical_parts() -> list[dict]:
    """List all critical parts (components marked as critical)."""
    with get_db() as db:
        return db.get_critical_parts()

get_critical_parts._meta = {"ui": {"resourceUri": "mcp_app/parts-table.html"}}


@mcp.tool
def create_part(
    part_number: str,
    name: str,
    category: str,
    material: str,
    weight_kg: float,
    is_critical: bool = False,
) -> dict:
    """Create a new part.

    Args:
        part_number: Unique identifier (e.g., "ESP-NEW-001")
        name: Part name
        category: Category (e.g., "Motor", "Pump", "Seal", "Cable", "Sensor")
        material: Material composition
        weight_kg: Weight in kilograms
        is_critical: Whether this is a critical part
    """
    with get_db() as db:
        return db.create_part(
            part_number=part_number,
            name=name,
            category=category,
            material=material,
            weight_kg=weight_kg,
            is_critical=is_critical,
        )


@mcp.tool
def update_part(
    part_number: str,
    name: Optional[str] = None,
    category: Optional[str] = None,
    material: Optional[str] = None,
    weight_kg: Optional[float] = None,
    is_critical: Optional[bool] = None,
) -> dict | None:
    """Update an existing part.

    Args:
        part_number: Part number to update
        name: New name (optional)
        category: New category (optional)
        material: New material (optional)
        weight_kg: New weight (optional)
        is_critical: New critical flag (optional)
    """
    with get_db() as db:
        return db.update_part(
            part_number=part_number,
            name=name,
            category=category,
            material=material,
            weight_kg=weight_kg,
            is_critical=is_critical,
        )


@mcp.tool
def delete_part(part_number: str, force: bool = False) -> bool:
    """Delete a part.

    Args:
        part_number: Part number to delete
        force: If True, removes from all assemblies first
    """
    with get_db() as db:
        if force:
            return db.force_delete_part(part_number)
        return db.delete_part(part_number)


@mcp.tool
def get_part_assemblies(part_number: str) -> list[dict]:
    """Find all assemblies that contain a specific part.

    Args:
        part_number: Part to search for
    """
    with get_db() as db:
        return db.get_assemblies_using_part(part_number)


# ============ Assembly Tools ============

@mcp.tool
def list_assemblies() -> list[dict]:
    """List all assemblies with their parts."""
    with get_db() as db:
        return db.get_all_assemblies()


@mcp.tool
def get_assembly(assembly_code: str) -> dict | None:
    """Get an assembly with its parts.

    Args:
        assembly_code: Assembly identifier (e.g., "ASM-MTR-001")
    """
    with get_db() as db:
        return db.get_assembly(assembly_code)


@mcp.tool
def create_assembly(
    assembly_code: str,
    name: str,
    part_numbers: Optional[list[str]] = None,
) -> dict:
    """Create a new assembly.

    Args:
        assembly_code: Unique identifier (e.g., "ASM-NEW-001")
        name: Assembly name
        part_numbers: Optional list of part numbers to include
    """
    with get_db() as db:
        return db.create_assembly(
            assembly_code=assembly_code,
            name=name,
            part_numbers=part_numbers,
        )


@mcp.tool
def delete_assembly(assembly_code: str, force: bool = False) -> bool:
    """Delete an assembly.

    Args:
        assembly_code: Assembly code to delete
        force: If True, removes from all ESPs first
    """
    with get_db() as db:
        if force:
            return db.force_delete_assembly(assembly_code)
        return db.delete_assembly(assembly_code)


@mcp.tool
def add_part_to_assembly(assembly_code: str, part_number: str) -> dict | None:
    """Add a part to an assembly's BOM.

    Args:
        assembly_code: Target assembly
        part_number: Part to add
    """
    with get_db() as db:
        return db.add_part_to_assembly(assembly_code, part_number)


@mcp.tool
def remove_part_from_assembly(assembly_code: str, part_number: str) -> dict | None:
    """Remove a part from an assembly's BOM.

    Args:
        assembly_code: Target assembly
        part_number: Part to remove
    """
    with get_db() as db:
        return db.remove_part_from_assembly(assembly_code, part_number)


@mcp.tool
def update_assembly_part_quantity(assembly_code: str, part_number: str, quantity: int) -> dict | None:
    """Update the quantity of a part in an assembly's BOM.

    Args:
        assembly_code: Target assembly
        part_number: Part to update
        quantity: New quantity (must be a positive integer)
    """
    with get_db() as db:
        try:
            return db.update_assembly_part_quantity(assembly_code, part_number, quantity)
        except ValueError as e:
            return {"error": str(e)}


@mcp.tool
def get_assembly_esps(assembly_code: str) -> list[dict]:
    """Find all ESPs that use a specific assembly.

    Args:
        assembly_code: Assembly to search for
    """
    with get_db() as db:
        return db.get_esps_using_assembly(assembly_code)


# ============ Utility Tools ============

@mcp.tool
def get_stats() -> dict:
    """Get database statistics."""
    with get_db() as db:
        return {
            "total_parts": len(db.get_all_parts()),
            "total_assemblies": len(db.get_all_assemblies()),
            "total_esps": len(db.get_all_esps()),
            "critical_parts": len(db.get_critical_parts()),
        }


@mcp.tool
def get_server_info() -> dict:
    """Get information about this MCP server."""
    return {
        "name": "ESP BOM MCP Server",
        "description": "Electric Submersible Pump Parts and Bill of Materials database",
        "version": "1.0.0",
        "capabilities": {
            "esp_management": True,
            "part_management": True,
            "assembly_management": True,
            "bom_queries": True,
        },
    }
