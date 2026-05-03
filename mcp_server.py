"""
MCP Server for ESP Parts and BOM Database

Provides tools to query and manage Electric Submersible Pump parts,
assemblies, and bills of materials.
"""

from contextlib import contextmanager
from pathlib import Path
import threading
import time
from typing import Optional
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from esp_db import ESPDatabase, init_database, DatabasePath
from skill_resource_manager import SkillResourceManager
from version import APP_VERSION

# Initialize FastMCP server
mcp = FastMCP("ESP BOM Database")
SKILL_DIRECTORY_NAME = ".skills"
SKILL_DIRECTORY_PATH = Path(__file__).resolve().parent / SKILL_DIRECTORY_NAME
SKILL_INDEX_URI = "skill://index"
SKILL_REFRESH_INTERVAL_SECONDS = 30.0
_skill_manager = SkillResourceManager(
    skill_dir=SKILL_DIRECTORY_PATH,
    poll_interval_seconds=SKILL_REFRESH_INTERVAL_SECONDS,
)
_registered_skill_metadata: dict[str, tuple[str, str]] = {}
_registered_lock = threading.Lock()


# Context manager for database lifecycle
@contextmanager
def get_db():
    """Get database instance with proper lifecycle management."""
    db = ESPDatabase(DatabasePath.DEFAULT)
    try:
        yield db
    finally:
        db.close()


def _register_dynamic_skill_resource(uri: str, name: str, description: str) -> None:
    """Register one concrete skill resource URI with dynamic content lookup."""
    skill_name = uri.replace("skill://", "", 1)
    skill_key = skill_name

    def _read_dynamic_skill() -> str:
        _sync_skill_resources(mode="PERIODIC", force_refresh=False)
        try:
            return _skill_manager.get_skill_content(skill_key)
        except KeyError:
            return (
                "# Missing skill resource\n\n"
                f"Skill resource `{uri}` is not currently discoverable in `{SKILL_DIRECTORY_NAME}/`."
            )

    _read_dynamic_skill.__name__ = f"read_skill_{skill_name.replace('-', '_')}"
    mcp.resource(
        uri,
        name=name,
        description=description,
        mime_type="text/markdown",
    )(_read_dynamic_skill)
    _registered_skill_metadata[uri] = (name, description)


def _sync_skill_resources(mode: str, force_refresh: bool) -> None:
    """Refresh discovery cache and synchronize concrete skill resources."""
    with _registered_lock:
        if force_refresh:
            _skill_manager.refresh(mode=mode)
        else:
            _skill_manager.refresh_if_due()

        discovered = _skill_manager.list_skills(refresh_if_due=False)
        discovered_by_uri = {entry.uri: entry for entry in discovered}

        for uri in list(_registered_skill_metadata):
            if uri in discovered_by_uri:
                continue
            mcp._local_provider.remove_resource(uri)
            _registered_skill_metadata.pop(uri, None)

        for uri, entry in discovered_by_uri.items():
            previous = _registered_skill_metadata.get(uri)
            current = (entry.name, entry.description)
            if previous == current:
                continue
            if previous is not None:
                mcp._local_provider.remove_resource(uri)
            _register_dynamic_skill_resource(uri, entry.name, entry.description)


@mcp.resource(
    SKILL_INDEX_URI,
    name="Skill Index",
    description="Aggregated index of discoverable markdown skills.",
    mime_type="text/markdown",
)
def skill_index() -> str:
    """Return the current skill index with refresh diagnostics and status."""
    _sync_skill_resources(mode="PERIODIC", force_refresh=False)
    return _skill_manager.get_index_content()


def _start_skill_refresh_worker() -> None:
    """Start periodic refresh to keep resource listing synchronized at runtime."""

    def _worker() -> None:
        while True:
            time.sleep(SKILL_REFRESH_INTERVAL_SECONDS)
            try:
                _sync_skill_resources(mode="PERIODIC", force_refresh=True)
            except Exception:
                # Keep refresh loop alive even if one cycle fails unexpectedly.
                pass

    thread = threading.Thread(target=_worker, name="skill-refresh-worker", daemon=True)
    thread.start()


_sync_skill_resources(mode="STARTUP", force_refresh=True)
_start_skill_refresh_worker()


# ============ ESP Tools ============

@mcp.tool
def list_esps() -> list[dict]:
    """List all ESP pump models with their specifications."""
    with get_db() as db:
        return db.get_all_esps()


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



@mcp.tool
def get_bom_summary(esp_id: str) -> dict | None:
    """Get a BOM summary for an ESP (total parts, weight, critical count).

    Args:
        esp_id: ESP identifier (e.g., "ESP-001")
    """
    with get_db() as db:
        return db.get_bom_summary(esp_id)



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



@mcp.tool
def get_part(part_number: str) -> dict | None:
    """Get a specific part by part number.

    Args:
        part_number: Part identifier (e.g., "ESP-MTR-001")
    """
    with get_db() as db:
        return db.get_part(part_number)



@mcp.tool
def search_parts(query: str) -> list[dict]:
    """Search parts by name, category, or material.

    Args:
        query: Search query string
    """
    with get_db() as db:
        return db.search_parts(query)



@mcp.tool
def get_parts_by_category(category: str) -> list[dict]:
    """Get all parts in a given category.

    Args:
        category: Category name (e.g., "Motor", "Pump", "Seal", "Cable")
    """
    with get_db() as db:
        return db.get_parts_by_category(category)



@mcp.tool
def get_critical_parts() -> list[dict]:
    """List all critical parts (components marked as critical)."""
    with get_db() as db:
        return db.get_critical_parts()



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
        "version": APP_VERSION,
        "capabilities": {
            "esp_management": True,
            "part_management": True,
            "assembly_management": True,
            "bom_queries": True,
        },
    }


# ============ Custom HTTP Routes ============

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for Cloud Run and load balancers."""
    return JSONResponse({"status": "healthy", "version": APP_VERSION})


@mcp.custom_route("/api/health", methods=["GET"])
async def api_health_check(request: Request) -> JSONResponse:
    """API health check alias."""
    return JSONResponse({"status": "healthy", "version": APP_VERSION})


@mcp.custom_route("/version", methods=["GET"])
async def version_info(request: Request) -> JSONResponse:
    """Return deployed version information."""
    return JSONResponse({"version": APP_VERSION})


@mcp.custom_route("/api/version", methods=["GET"])
async def api_version_info(request: Request) -> JSONResponse:
    """API version alias."""
    return JSONResponse({"version": APP_VERSION})


@mcp.custom_route("/tool/{tool_name}", methods=["GET", "POST"])
async def tool_proxy(request: Request) -> JSONResponse:
    """HTTP proxy for MCP tools — used by the Node.js MCP Apps UI server."""
    tool_name = request.path_params["tool_name"]
    if request.method == "POST":
        try:
            args = await request.json()
        except Exception:
            args = {}
    else:
        args = dict(request.query_params)

    try:
        with get_db() as db:
            tool_map = {
                # ESP tools
                "list_esps": db.get_all_esps,
                "get_esp": lambda: db.get_esp(args.get("esp_id")),
                "get_esp_bom": lambda: db.get_esp_bom_parts(args.get("esp_id")),
                "get_bom_summary": lambda: db.get_bom_summary(args.get("esp_id")),
                "get_esps_by_series": lambda: db.get_esps_by_series(args.get("series")),
                "create_esp": lambda: db.create_esp(
                    esp_id=args.get("esp_id"),
                    model_name=args.get("model_name"),
                    series=args.get("series"),
                    power_rating_kw=float(args.get("power_rating_kw", 0)),
                    voltage_v=int(args.get("voltage_v", 0)),
                    frequency_hz=float(args.get("frequency_hz", 0)),
                    flow_rate_m3d=float(args.get("flow_rate_m3d", 0)),
                    stages=int(args.get("stages", 0)),
                    cable_length_m=float(args.get("cable_length_m", 0)),
                ),
                "delete_esp": lambda: db.delete_esp(args.get("esp_id")),
                # Part tools
                "list_parts": db.get_all_parts,
                "get_part": lambda: db.get_part(args.get("part_number")),
                "search_parts": lambda: db.search_parts(args.get("query")),
                "get_parts_by_category": lambda: db.get_parts_by_category(args.get("category")),
                "get_critical_parts": db.get_critical_parts,
                "get_part_assemblies": lambda: db.get_assemblies_using_part(args.get("part_number")),
                "create_part": lambda: db.create_part(
                    part_number=args.get("part_number"),
                    name=args.get("name"),
                    category=args.get("category"),
                    material=args.get("material"),
                    weight_kg=float(args.get("weight_kg", 0)),
                    is_critical=args.get("is_critical", False),
                ),
                "update_part": lambda: db.update_part(
                    part_number=args.get("part_number"),
                    name=args.get("name"),
                    category=args.get("category"),
                    material=args.get("material"),
                    weight_kg=float(args.get("weight_kg", 0)) if args.get("weight_kg") else None,
                    is_critical=args.get("is_critical"),
                ),
                "delete_part": lambda: db.delete_part(args.get("part_number")),
                # Assembly tools
                "list_assemblies": db.get_all_assemblies,
                "get_assembly": lambda: db.get_assembly(args.get("assembly_code")),
                "get_assembly_esps": lambda: db.get_esps_using_assembly(args.get("assembly_code")),
                "create_assembly": lambda: db.create_assembly(
                    assembly_code=args.get("assembly_code"),
                    name=args.get("name"),
                ),
                "delete_assembly": lambda: db.delete_assembly(args.get("assembly_code")),
                "add_part_to_assembly": lambda: db.add_part_to_assembly(
                    args.get("assembly_code"),
                    args.get("part_number"),
                ),
                "remove_part_from_assembly": lambda: db.remove_part_from_assembly(
                    args.get("assembly_code"),
                    args.get("part_number"),
                ),
                "update_assembly_part_quantity": lambda: db.update_assembly_part_quantity(
                    args.get("assembly_code"),
                    args.get("part_number"),
                    int(args.get("quantity", 1)),
                ),
                # Stats / view tools
                "get_stats": lambda: {
                    "total_esps": len(db.get_all_esps()),
                    "total_parts": len(db.get_all_parts()),
                    "total_assemblies": len(db.get_all_assemblies()),
                    "critical_parts": len(db.get_critical_parts()),
                },
                "view_dashboard": lambda: {
                    "total_esps": len(db.get_all_esps()),
                    "total_parts": len(db.get_all_parts()),
                    "total_assemblies": len(db.get_all_assemblies()),
                    "critical_parts": len(db.get_critical_parts()),
                },
                "view_esp_catalogue": db.get_all_esps,
                "view_esp_bom": lambda: db.get_esp_bom_parts(args.get("esp_id")),
                "manage_parts": db.get_all_parts,
                "manage_assemblies": db.get_all_assemblies,
            }

            if tool_name in tool_map:
                result = tool_map[tool_name]()
                return JSONResponse(result)
            return JSONResponse({"error": f"Unknown tool: {tool_name}"}, status_code=404)

    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)
