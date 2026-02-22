"""
REST API for ESP Parts and BOM Database

Provides endpoints to query part numbers and Bill of Materials
for Electric Submersible Pumps.
"""

from flask import Flask, jsonify, request
from esp_db import ESPDatabase, init_database, DatabasePath
from typing import Optional

app = Flask(__name__)
_db: Optional[ESPDatabase] = None


def get_db() -> ESPDatabase:
    """Get database instance, initializing if necessary."""
    global _db
    if _db is None:
        _db = init_database()
    return _db


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "ESP BOM API"})


# ============ Parts Endpoints ============

@app.route("/api/parts", methods=["GET"])
def get_all_parts():
    """Get all parts in the database."""
    db = get_db()
    return jsonify({"parts": db.get_all_parts()})


@app.route("/api/parts/<part_number>", methods=["GET"])
def get_part(part_number: str):
    """Get a single part by part number."""
    db = get_db()
    part = db.get_part(part_number)
    if part:
        return jsonify({"part": part})
    return jsonify({"error": f"Part {part_number} not found"}), 404


@app.route("/api/parts", methods=["POST"])
def create_part():
    """Create a new part.

    Request body:
    {
        "part_number": "ESP-NEW-001",
        "name": "New Part Name",
        "category": "Motor",
        "material": "Steel",
        "weight_kg": 10.5,
        "is_critical": false
    }
    """
    data = request.get_json()
    required = ["part_number", "name", "category", "material", "weight_kg"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    db = get_db()
    try:
        part = db.create_part(
            part_number=data["part_number"],
            name=data["name"],
            category=data["category"],
            material=data["material"],
            weight_kg=data["weight_kg"],
            is_critical=data.get("is_critical", False)
        )
        return jsonify({"part": part, "message": "Part created successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/parts/<part_number>", methods=["PUT"])
def update_part(part_number: str):
    """Update an existing part.

    Request body (any combination of fields):
    {
        "name": "Updated Name",
        "category": "Pump",
        "material": "Aluminum",
        "weight_kg": 8.0,
        "is_critical": true
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    db = get_db()
    part = db.update_part(
        part_number=part_number,
        name=data.get("name"),
        category=data.get("category"),
        material=data.get("material"),
        weight_kg=data.get("weight_kg"),
        is_critical=data.get("is_critical")
    )
    if part:
        return jsonify({"part": part, "message": "Part updated successfully"})
    return jsonify({"error": f"Part {part_number} not found"}), 404


@app.route("/api/parts/<part_number>", methods=["DELETE"])
def delete_part(part_number: str):
    """Delete a part.

    Use ?force=true to remove from all assemblies first.
    """
    force = request.args.get("force", "false").lower() == "true"
    db = get_db()

    if force:
        deleted = db.force_delete_part(part_number)
    else:
        deleted = db.delete_part(part_number)

    if deleted:
        return jsonify({"message": f"Part {part_number} deleted successfully"})
    return jsonify({"error": f"Part {part_number} not found or is in use (use ?force=true to force delete)"}), 404


@app.route("/api/parts/<part_number>/assemblies", methods=["GET"])
def get_part_assemblies(part_number: str):
    """Find all assemblies that contain a specific part."""
    db = get_db()
    assemblies = db.get_assemblies_using_part(part_number)
    return jsonify({"part_number": part_number, "assemblies": assemblies})


@app.route("/api/parts/category/<category>", methods=["GET"])
def get_parts_by_category(category: str):
    """Get all parts in a given category."""
    db = get_db()
    return jsonify({"category": category, "parts": db.get_parts_by_category(category)})


@app.route("/api/parts/search", methods=["GET"])
def search_parts():
    """Search parts by name, category, or material."""
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    db = get_db()
    return jsonify({"query": query, "parts": db.search_parts(query)})


@app.route("/api/parts/critical", methods=["GET"])
def get_critical_parts():
    """Get all critical parts."""
    db = get_db()
    return jsonify({"critical_parts": db.get_critical_parts()})


# ============ Assemblies Endpoints ============

@app.route("/api/assemblies", methods=["GET"])
def get_all_assemblies():
    """Get all assemblies in the database."""
    db = get_db()
    return jsonify({"assemblies": db.get_all_assemblies()})


@app.route("/api/assemblies/<assembly_code>", methods=["GET"])
def get_assembly(assembly_code: str):
    """Get an assembly with its parts."""
    db = get_db()
    assembly = db.get_assembly(assembly_code)
    if assembly:
        return jsonify({"assembly": assembly})
    return jsonify({"error": f"Assembly {assembly_code} not found"}), 404


@app.route("/api/assemblies", methods=["POST"])
def create_assembly():
    """Create a new assembly.

    Request body:
    {
        "assembly_code": "ASM-NEW-001",
        "name": "New Assembly",
        "part_numbers": ["ESP-MTR-001", "ESP-MTR-002"]
    }
    """
    data = request.get_json()
    required = ["assembly_code", "name"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    db = get_db()
    try:
        assembly = db.create_assembly(
            assembly_code=data["assembly_code"],
            name=data["name"],
            part_numbers=data.get("part_numbers")
        )
        return jsonify({"assembly": assembly, "message": "Assembly created successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/assemblies/<assembly_code>", methods=["PUT"])
def update_assembly(assembly_code: str):
    """Update an assembly's name."""
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Name field required"}), 400

    db = get_db()
    assembly = db.update_assembly(assembly_code, name=data["name"])
    if assembly:
        return jsonify({"assembly": assembly, "message": "Assembly updated successfully"})
    return jsonify({"error": f"Assembly {assembly_code} not found"}), 404


@app.route("/api/assemblies/<assembly_code>", methods=["DELETE"])
def delete_assembly(assembly_code: str):
    """Delete an assembly.

    Use ?force=true to remove from all ESPs first.
    """
    force = request.args.get("force", "false").lower() == "true"
    db = get_db()

    if force:
        deleted = db.force_delete_assembly(assembly_code)
    else:
        deleted = db.delete_assembly(assembly_code)

    if deleted:
        return jsonify({"message": f"Assembly {assembly_code} deleted successfully"})
    return jsonify({"error": f"Assembly {assembly_code} not found or is in use (use ?force=true to force delete)"}), 404


@app.route("/api/assemblies/<assembly_code>/parts/<part_number>", methods=["POST"])
def add_part_to_assembly(assembly_code: str, part_number: str):
    """Add a part to an assembly's BOM."""
    db = get_db()
    try:
        assembly = db.add_part_to_assembly(assembly_code, part_number)
        if assembly:
            return jsonify({"assembly": assembly, "message": f"Part {part_number} added to assembly"})
        return jsonify({"error": f"Assembly {assembly_code} or part {part_number} not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/assemblies/<assembly_code>/parts/<part_number>", methods=["DELETE"])
def remove_part_from_assembly(assembly_code: str, part_number: str):
    """Remove a part from an assembly's BOM."""
    db = get_db()
    assembly = db.remove_part_from_assembly(assembly_code, part_number)
    if assembly:
        return jsonify({"assembly": assembly, "message": f"Part {part_number} removed from assembly"})
    return jsonify({"error": f"Assembly {assembly_code} not found"}), 404


@app.route("/api/assemblies/<assembly_code>/esps", methods=["GET"])
def get_assembly_esps(assembly_code: str):
    """Find all ESPs that use a specific assembly."""
    db = get_db()
    esps = db.get_esps_using_assembly(assembly_code)
    return jsonify({"assembly_code": assembly_code, "esps": esps})


# ============ ESP Endpoints ============

@app.route("/api/esp", methods=["GET"])
def get_all_esps():
    """Get all top-level ESPs."""
    db = get_db()
    return jsonify({"esps": db.get_all_esps()})


@app.route("/api/esp/<esp_id>", methods=["GET"])
def get_esp(esp_id: str):
    """Get a complete ESP with all assemblies and parts."""
    db = get_db()
    esp = db.get_esp(esp_id)
    if esp:
        return jsonify({"esp": esp})
    return jsonify({"error": f"ESP {esp_id} not found"}), 404


@app.route("/api/esp", methods=["POST"])
def create_esp():
    """Create a new ESP.

    Request body:
    {
        "esp_id": "ESP-011",
        "model_name": "Test Pump 100",
        "series": "TestSeries",
        "power_rating_kw": 25,
        "voltage_v": 2400,
        "frequency_hz": 60,
        "flow_rate_m3d": 400,
        "stages": 30,
        "cable_length_m": 50,
        "assembly_codes": ["ASM-MTR-001", "ASM-PMP-001"]
    }
    """
    data = request.get_json()
    required = ["esp_id", "model_name", "series", "power_rating_kw", "voltage_v",
                "frequency_hz", "flow_rate_m3d", "stages", "cable_length_m"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    db = get_db()
    try:
        esp = db.create_esp(
            esp_id=data["esp_id"],
            model_name=data["model_name"],
            series=data["series"],
            power_rating_kw=data["power_rating_kw"],
            voltage_v=data["voltage_v"],
            frequency_hz=data["frequency_hz"],
            flow_rate_m3d=data["flow_rate_m3d"],
            stages=data["stages"],
            cable_length_m=data["cable_length_m"],
            assembly_codes=data.get("assembly_codes")
        )
        return jsonify({"esp": esp, "message": "ESP created successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/esp/<esp_id>", methods=["PUT"])
def update_esp(esp_id: str):
    """Update an ESP's specifications.

    Request body (any combination of fields):
    {
        "model_name": "Updated Name",
        "power_rating_kw": 75,
        "stages": 50
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    db = get_db()
    esp = db.update_esp(
        esp_id=esp_id,
        model_name=data.get("model_name"),
        series=data.get("series"),
        power_rating_kw=data.get("power_rating_kw"),
        voltage_v=data.get("voltage_v"),
        frequency_hz=data.get("frequency_hz"),
        flow_rate_m3d=data.get("flow_rate_m3d"),
        stages=data.get("stages"),
        cable_length_m=data.get("cable_length_m")
    )
    if esp:
        return jsonify({"esp": esp, "message": "ESP updated successfully"})
    return jsonify({"error": f"ESP {esp_id} not found"}), 404


@app.route("/api/esp/<esp_id>", methods=["DELETE"])
def delete_esp(esp_id: str):
    """Delete an ESP."""
    db = get_db()
    deleted = db.delete_esp(esp_id)
    if deleted:
        return jsonify({"message": f"ESP {esp_id} deleted successfully"})
    return jsonify({"error": f"ESP {esp_id} not found"}), 404


@app.route("/api/esp/<esp_id>/bom", methods=["GET"])
def get_esp_bom(esp_id: str):
    """Get the Bill of Materials for an ESP (all parts, no assembly hierarchy)."""
    db = get_db()
    bom_parts = db.get_esp_bom_parts(esp_id)
    if bom_parts is not None:
        return jsonify({"esp_id": esp_id, "bom_parts": bom_parts})
    return jsonify({"error": f"ESP {esp_id} not found"}), 404


@app.route("/api/esp/<esp_id>/assemblies", methods=["GET"])
def get_esp_assemblies(esp_id: str):
    """Get the assemblies for an ESP (without nested parts)."""
    db = get_db()
    esp = db.get_esp_assemblies(esp_id)
    if esp:
        return jsonify({"esp": esp})
    return jsonify({"error": f"ESP {esp_id} not found"}), 404


@app.route("/api/esp/<esp_id>/assemblies/<assembly_code>", methods=["POST"])
def add_assembly_to_esp(esp_id: str, assembly_code: str):
    """Add an assembly to an ESP."""
    db = get_db()
    try:
        esp = db.add_assembly_to_esp(esp_id, assembly_code)
        if esp:
            return jsonify({"esp": esp, "message": f"Assembly {assembly_code} added to ESP"})
        return jsonify({"error": f"ESP {esp_id} or assembly {assembly_code} not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/esp/<esp_id>/assemblies/<assembly_code>", methods=["DELETE"])
def remove_assembly_from_esp(esp_id: str, assembly_code: str):
    """Remove an assembly from an ESP."""
    db = get_db()
    esp = db.remove_assembly_from_esp(esp_id, assembly_code)
    if esp:
        return jsonify({"esp": esp, "message": f"Assembly {assembly_code} removed from ESP"})
    return jsonify({"error": f"ESP {esp_id} not found"}), 404


@app.route("/api/esp/<esp_id>/summary", methods=["GET"])
def get_esp_summary(esp_id: str):
    """Get a BOM summary for an ESP (counts, weights, etc.)."""
    db = get_db()
    summary = db.get_bom_summary(esp_id)
    if summary:
        return jsonify({"summary": summary})
    return jsonify({"error": f"ESP {esp_id} not found"}), 404


@app.route("/api/esp/series/<series>", methods=["GET"])
def get_esps_by_series(series: str):
    """Get all ESPs in a given series."""
    db = get_db()
    return jsonify({"series": series, "esps": db.get_esps_by_series(series)})


# ============ Utility Endpoints ============

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get database statistics."""
    db = get_db()
    return jsonify({
        "total_parts": len(db.get_all_parts()),
        "total_assemblies": len(db.get_all_assemblies()),
        "total_esps": len(db.get_all_esps()),
        "critical_parts": len(db.get_critical_parts())
    })


def create_api(db_path: str = DatabasePath.DEFAULT) -> Flask:
    """Create and configure the Flask API app."""
    global _db
    _db = init_database(db_path)
    return app


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f"Starting ESP BOM API server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
