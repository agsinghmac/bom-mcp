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

    # MCP Protocol endpoint (/mcp)
    @app.route('/mcp', methods=['GET', 'POST'])
    def mcp_endpoint():
        """Handle MCP protocol JSON-RPC requests."""
        try:
            # Get the JSON-RPC request
            if request.method == 'POST':
                data = request.get_json() or {}
            else:
                # For GET requests, return server info
                return jsonify({
                    "name": "ESP BOM MCP Server",
                    "version": "1.0.0",
                    "description": "Electric Submersible Pump Parts and BOM Database"
                })

            jsonrpc_id = data.get('id')
            method = data.get('method')
            params = data.get('params', {})

            # Handle MCP methods
            if method == 'initialize':
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": jsonrpc_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "resources": {}
                        },
                        "serverInfo": {
                            "name": "ESP BOM MCP Server",
                            "version": "1.0.0"
                        }
                    }
                })

            elif method == 'tools/list':
                # Return list of available tools
                tools = [
                    {"name": "list_esps", "description": "List all ESP pump models", "inputSchema": {"type": "object", "properties": {}}},
                    {"name": "get_esp", "description": "Get a specific ESP", "inputSchema": {"type": "object", "properties": {"esp_id": {"type": "string"}}, "required": ["esp_id"]}},
                    {"name": "get_esp_bom", "description": "Get BOM for an ESP", "inputSchema": {"type": "object", "properties": {"esp_id": {"type": "string"}}, "required": ["esp_id"]}},
                    {"name": "get_bom_summary", "description": "Get BOM summary", "inputSchema": {"type": "object", "properties": {"esp_id": {"type": "string"}}, "required": ["esp_id"]}},
                    {"name": "list_parts", "description": "List all parts", "inputSchema": {"type": "object", "properties": {}}},
                    {"name": "get_part", "description": "Get a specific part", "inputSchema": {"type": "object", "properties": {"part_number": {"type": "string"}}, "required": ["part_number"]}},
                    {"name": "search_parts", "description": "Search parts", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
                    {"name": "get_stats", "description": "Get database statistics", "inputSchema": {"type": "object", "properties": {}}},
                    {"name": "view_dashboard", "description": "Show ESP dashboard", "inputSchema": {"type": "object", "properties": {}}},
                    {"name": "view_esp_catalogue", "description": "Show ESP catalogue", "inputSchema": {"type": "object", "properties": {}}},
                    {"name": "view_esp_bom", "description": "Show BOM for ESP", "inputSchema": {"type": "object", "properties": {"esp_id": {"type": "string"}}, "required": ["esp_id"]}},
                    {"name": "manage_parts", "description": "Manage parts", "inputSchema": {"type": "object", "properties": {}}},
                    {"name": "manage_assemblies", "description": "Manage assemblies", "inputSchema": {"type": "object", "properties": {}}},
                ]
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": jsonrpc_id,
                    "result": {"tools": tools}
                })

            elif method == 'tools/call':
                tool_name = params.get('name')
                tool_args = params.get('arguments', {})

                with get_db() as db:
                    # Map tool names to database methods
                    tool_map = {
                        'list_esps': lambda: db.get_all_esps(),
                        'get_esp': lambda: db.get_esp(tool_args.get('esp_id')),
                        'get_esp_bom': lambda: db.get_esp_bom_parts(tool_args.get('esp_id')),
                        'get_bom_summary': lambda: db.get_bom_summary(tool_args.get('esp_id')),
                        'list_parts': lambda: db.get_all_parts(),
                        'get_part': lambda: db.get_part(tool_args.get('part_number')),
                        'search_parts': lambda: db.search_parts(tool_args.get('query')),
                        'get_parts_by_category': lambda: db.get_parts_by_category(tool_args.get('category')),
                        'get_critical_parts': lambda: db.get_critical_parts(),
                        'list_assemblies': lambda: db.get_all_assemblies(),
                        'get_assembly': lambda: db.get_assembly(tool_args.get('assembly_code')),
                        'get_stats': lambda: {
                            "total_esps": len(db.get_all_esps()),
                            "total_parts": len(db.get_all_parts()),
                            "total_assemblies": len(db.get_all_assemblies()),
                            "critical_parts": len(db.get_critical_parts()),
                        },
                    }

                    if tool_name in tool_map:
                        result = tool_map[tool_name]()
                        return jsonify({
                            "jsonrpc": "2.0",
                            "id": jsonrpc_id,
                            "result": {
                                "content": [{"type": "text", "text": json.dumps(result)}]
                            }
                        })
                    else:
                        return jsonify({
                            "jsonrpc": "2.0",
                            "id": jsonrpc_id,
                            "error": {"code": -32601, "message": f"Method not found: {tool_name}"}
                        }), 404

            elif method == 'resources/list':
                # Return list of available resources (HTML views)
                resources = [
                    {"uri": "view-dashboard.html", "name": "Dashboard View", "description": "ESP Dashboard with stats and critical parts"},
                    {"uri": "view-esp-catalogue.html", "name": "ESP Catalogue View", "description": "ESP Catalogue with CRUD"},
                    {"uri": "view-esp-bom.html", "name": "BOM Viewer View", "description": "BOM Viewer with export"},
                    {"uri": "manage-parts.html", "name": "Parts Manager View", "description": "Parts Manager with CRUD"},
                    {"uri": "manage-assemblies.html", "name": "Assembly Manager View", "description": "Assembly Manager with CRUD"},
                ]
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": jsonrpc_id,
                    "result": {"resources": resources}
                })

            elif method == 'resources/read':
                resource_uri = params.get('uri', '')

                # Map URIs to HTML content
                html_contents = {
                    'view-dashboard.html': get_dashboard_html(),
                    'view-esp-catalogue.html': get_esp_catalogue_html(),
                    'view-esp-bom.html': get_esp_bom_html(),
                    'manage-parts.html': get_parts_html(),
                    'manage-assemblies.html': get_assemblies_html(),
                }

                if resource_uri in html_contents:
                    return jsonify({
                        "jsonrpc": "2.0",
                        "id": jsonrpc_id,
                        "result": {
                            "contents": [{
                                "uri": resource_uri,
                                "mimeType": "text/html;profile=mcp-app",
                                "text": html_contents[resource_uri]
                            }]
                        }
                    })
                else:
                    return jsonify({
                        "jsonrpc": "2.0",
                        "id": jsonrpc_id,
                        "error": {"code": -32602, "message": f"Invalid resource: {resource_uri}"}
                    }), 404

            else:
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": jsonrpc_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }), 404

        except Exception as e:
            return jsonify({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }), 500

    # Serve HTML resources directly
    @app.route('/resources/<resource_name>')
    def serve_resource(resource_name):
        """Serve MCP App HTML resources."""
        html_contents = {
            'view-dashboard.html': get_dashboard_html(),
            'view-esp-catalogue.html': get_esp_catalogue_html(),
            'view-esp-bom.html': get_esp_bom_html(),
            'manage-parts.html': get_parts_html(),
            'manage-assemblies.html': get_assemblies_html(),
        }

        if resource_name in html_contents:
            return html_contents[resource_name], 200, {'Content-Type': 'text/html'}
        return "Not found", 404

    return app


def main():
    parser = argparse.ArgumentParser(description="ESP BOM HTTP Server")
    parser.add_argument('--port', type=int, default=3001, help='Port to run server on')
    args = parser.parse_args()

    app = create_app()
    app.run(host='0.0.0.0', port=args.port, debug=False)


if __name__ == '__main__':
    main()

# HTML content generators for MCP Apps UI views
def get_dashboard_html():
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>ESP Dashboard</title></head>
<body><h1>ESP Dashboard</h1><p>Loading...</p>
<script type="module">
import { App } from 'https://cdn.jsdelivr.net/npm/@modelcontextprotocol/ext-apps@1.0.1/dist/src/app-with-deps.js';
const app = new App({ name: 'ESP Dashboard', version: '1.0.0' });
app.onhostcontextchanged = (ctx) => { if (ctx.styles?.variables) { Object.entries(ctx.styles.variables).forEach(([k,v]) => document.documentElement.style.setProperty('--'+k, v)); }};
app.ontoolresult = (r) => { const d=r?.data||r; if(d?.total_esps){ document.body.innerHTML='<h1>ESP Dashboard</h1><p>Total ESPs: '+d.total_esps+'</p><p>Total Parts: '+d.total_parts+'</p><p>Critical Parts: '+d.critical_parts+'</p>'; }};
app.onteardown = async () => ({});
await app.connect();
app.callTool('get_stats', {});
</script></body></html>"""

def get_esp_catalogue_html():
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>ESP Catalogue</title></head>
<body><h1>ESP Catalogue</h1><p>Loading...</p>
<script type="module">
import { App } from 'https://cdn.jsdelivr.net/npm/@modelcontextprotocol/ext-apps@1.0.1/dist/src/app-with-deps.js';
const app = new App({ name: 'ESP Catalogue', version: '1.0.0' });
app.onhostcontextchanged = (ctx) => { if (ctx.styles?.variables) { Object.entries(ctx.styles.variables).forEach(([k,v]) => document.documentElement.style.setProperty('--'+k, v)); }};
app.ontoolresult = (r) => { const d=r?.data||r; if(Array.isArray(d)&&d[0]?.esp_id){ document.body.innerHTML='<h1>ESP Catalogue</h1><ul>'+d.map(e=>'<li>'+e.esp_id+' - '+e.model_name+' ('+e.series+')</li>').join('')+'</ul>'; }};
app.onteardown = async () => ({});
await app.connect();
app.callTool('list_esps', {});
</script></body></html>"""

def get_esp_bom_html():
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>BOM Viewer</title></head>
<body><h1>BOM Viewer</h1><p>Loading...</p>
<script type="module">
import { App } from 'https://cdn.jsdelivr.net/npm/@modelcontextprotocol/ext-apps@1.0.1/dist/src/app-with-deps.js';
const app = new App({ name: 'BOM Viewer', version: '1.0.0' });
app.onhostcontextchanged = (ctx) => { if (ctx.styles?.variables) { Object.entries(ctx.styles.variables).forEach(([k,v]) => document.documentElement.style.setProperty('--'+k, v)); }};
const params = new URLSearchParams(window.location.search);
const espId = params.get('esp_id') || 'ESP-001';
app.ontoolresult = (r) => { const d=r?.data||r; if(Array.isArray(d)){ document.body.innerHTML='<h1>BOM for '+espId+'</h1><p>Total parts: '+d.length+'</p><table border="1"><tr><th>Part #</th><th>Name</th><th>Qty</th></tr>'+d.map(p=>'<tr><td>'+p.part_number+'</td><td>'+p.name+'</td><td>'+(p.quantity||1)+'</td></tr>').join('')+'</table>'; }};
app.onteardown = async () => ({});
await app.connect();
app.callTool('get_esp_bom', { esp_id: espId });
</script></body></html>"""

def get_parts_html():
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Parts Manager</title></head>
<body><h1>Parts Manager</h1><p>Loading...</p>
<script type="module">
import { App } from 'https://cdn.jsdelivr.net/npm/@modelcontextprotocol/ext-apps@1.0.1/dist/src/app-with-deps.js';
const app = new App({ name: 'Parts Manager', version: '1.0.0' });
app.onhostcontextchanged = (ctx) => { if (ctx.styles?.variables) { Object.entries(ctx.styles.variables).forEach(([k,v]) => document.documentElement.style.setProperty('--'+k, v)); }};
app.ontoolresult = (r) => { const d=r?.data||r; if(Array.isArray(d)){ document.body.innerHTML='<h1>Parts Manager</h1><p>Total parts: '+d.length+'</p><table border="1"><tr><th>Part #</th><th>Name</th><th>Category</th></tr>'+d.map(p=>'<tr><td>'+p.part_number+'</td><td>'+p.name+'</td><td>'+p.category+'</td></tr>').join('')+'</table>'; }};
app.onteardown = async () => ({});
await app.connect();
app.callTool('list_parts', {});
</script></body></html>"""

def get_assemblies_html():
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Assembly Manager</title></head>
<body><h1>Assembly Manager</h1><p>Loading...</p>
<script type="module">
import { App } from 'https://cdn.jsdelivr.net/npm/@modelcontextprotocol/ext-apps@1.0.1/dist/src/app-with-deps.js';
const app = new App({ name: 'Assembly Manager', version: '1.0.0' });
app.onhostcontextchanged = (ctx) => { if (ctx.styles?.variables) { Object.entries(ctx.styles.variables).forEach(([k,v]) => document.documentElement.style.setProperty('--'+k, v)); }};
app.ontoolresult = (r) => { const d=r?.data||r; if(Array.isArray(d)){ document.body.innerHTML='<h1>Assembly Manager</h1><ul>'+d.map(a=>'<li>'+a.assembly_code+' - '+a.name+'</li>').join('')+'</ul>'; }};
app.onteardown = async () => ({});
await app.connect();
app.callTool('list_assemblies', {});
</script></body></html>"""
