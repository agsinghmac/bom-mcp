#!/usr/bin/env python3
"""
HTTP Server wrapper for MCP Tools

Provides REST endpoints that the Node.js MCP App server can call.
This wraps the ESPDatabase to expose tools via HTTP.

Usage:
    python http_server.py           # Default port: 3001
    python http_server.py --port 3001
"""

import argparse
import json
from flask import Flask, jsonify, request
from esp_db import ESPDatabase, DatabasePath


def create_app():
    app = Flask(__name__)

    def get_db():
        return ESPDatabase(DatabasePath.DEFAULT)

    # Health check
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy"})

    # Tool proxy endpoint - calls a tool by name with args
    @app.route('/tool/<tool_name>', methods=['GET', 'POST'])
    def call_tool(tool_name):
        try:
            with get_db() as db:
                # Get args from query params or JSON body
                if request.method == 'POST':
                    args = request.get_json() or {}
                else:
                    args = {k: v for k, v in request.args.items()}

                # Map tool names to database methods
                tool_map = {
                    'list_esps': db.get_all_esps,
                    'get_esp': lambda: db.get_esp(args.get('esp_id')),
                    'get_esp_bom': lambda: db.get_esp_bom_parts(args.get('esp_id')),
                    'get_bom_summary': lambda: db.get_bom_summary(args.get('esp_id')),
                    'get_esps_by_series': lambda: db.get_esps_by_series(args.get('series')),
                    'list_parts': db.get_all_parts,
                    'get_part': lambda: db.get_part(args.get('part_number')),
                    'search_parts': lambda: db.search_parts(args.get('query')),
                    'get_parts_by_category': lambda: db.get_parts_by_category(args.get('category')),
                    'get_critical_parts': db.get_critical_parts,
                    'get_part_assemblies': lambda: db.get_assemblies_using_part(args.get('part_number')),
                    'list_assemblies': db.get_all_assemblies,
                    'get_assembly': lambda: db.get_assembly(args.get('assembly_code')),
                    'get_assembly_esps': lambda: db.get_esps_using_assembly(args.get('assembly_code')),
                    'get_stats': lambda: {
                        "total_esps": len(db.get_all_esps()),
                        "total_parts": len(db.get_all_parts()),
                        "total_assemblies": len(db.get_all_assemblies()),
                        "critical_parts": len(db.get_critical_parts()),
                    },
                    'create_esp': lambda: db.create_esp(
                        esp_id=args.get('esp_id'),
                        model_name=args.get('model_name'),
                        series=args.get('series'),
                        power_rating_kw=float(args.get('power_rating_kw', 0)),
                        voltage_v=int(args.get('voltage_v', 0)),
                        frequency_hz=float(args.get('frequency_hz', 0)),
                        flow_rate_m3d=float(args.get('flow_rate_m3d', 0)),
                        stages=int(args.get('stages', 0)),
                        cable_length_m=float(args.get('cable_length_m', 0)),
                    ),
                    'delete_esp': lambda: db.delete_esp(args.get('esp_id')),
                    'create_part': lambda: db.create_part(
                        part_number=args.get('part_number'),
                        name=args.get('name'),
                        category=args.get('category'),
                        material=args.get('material'),
                        weight_kg=float(args.get('weight_kg', 0)),
                        is_critical=args.get('is_critical', 'false').lower() == 'true',
                    ),
                    'update_part': lambda: db.update_part(
                        part_number=args.get('part_number'),
                        name=args.get('name'),
                        category=args.get('category'),
                        material=args.get('material'),
                        weight_kg=float(args.get('weight_kg', 0)) if args.get('weight_kg') else None,
                        is_critical=args.get('is_critical', '').lower() == 'true' if 'is_critical' in args else None,
                    ),
                    'delete_part': lambda: db.delete_part(args.get('part_number')),
                    'create_assembly': lambda: db.create_assembly(
                        assembly_code=args.get('assembly_code'),
                        name=args.get('name'),
                    ),
                    'delete_assembly': lambda: db.delete_assembly(args.get('assembly_code')),
                    'add_part_to_assembly': lambda: db.add_part_to_assembly(
                        args.get('assembly_code'),
                        args.get('part_number'),
                    ),
                    'remove_part_from_assembly': lambda: db.remove_part_from_assembly(
                        args.get('assembly_code'),
                        args.get('part_number'),
                    ),
                    'update_assembly_part_quantity': lambda: db.update_assembly_part_quantity(
                        args.get('assembly_code'),
                        args.get('part_number'),
                        int(args.get('quantity', 1)),
                    ),
                }

                if tool_name in tool_map:
                    result = tool_map[tool_name]()
                    return jsonify(result)
                else:
                    return jsonify({"error": f"Unknown tool: {tool_name}"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app


def main():
    parser = argparse.ArgumentParser(description="ESP BOM HTTP Server")
    parser.add_argument('--port', type=int, default=3001, help='Port to run server on')
    args = parser.parse_args()

    app = create_app()
    app.run(host='0.0.0.0', port=args.port, debug=False)


if __name__ == '__main__':
    main()