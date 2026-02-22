"""Command-line interface for ESP BOM queries."""

import argparse
import json
import sys
from esp_db import ESPDatabase, init_database


def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))


def cmd_list_esps(args):
    """List all ESPs."""
    with init_database() as db:
        print_json({"esps": db.get_all_esps()})


def cmd_get_esp(args):
    """Get ESP details with full BOM."""
    with init_database() as db:
        esp = db.get_esp(args.esp_id)
        if esp:
            print_json({"esp": esp})
        else:
            print(f"ESP {args.esp_id} not found", file=sys.stderr)
            sys.exit(1)


def cmd_create_esp(args):
    """Create a new ESP."""
    with init_database() as db:
        try:
            esp = db.create_esp(
                esp_id=args.esp_id,
                model_name=args.model_name,
                series=args.series,
                power_rating_kw=args.power,
                voltage_v=args.voltage,
                frequency_hz=args.frequency,
                flow_rate_m3d=args.flow_rate,
                stages=args.stages,
                cable_length_m=args.cable_length,
                assembly_codes=args.assemblies if args.assemblies else None
            )
            print_json({"esp": esp, "message": "ESP created successfully"})
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_delete_esp(args):
    """Delete an ESP."""
    with init_database() as db:
        deleted = db.delete_esp(args.esp_id)
        if deleted:
            print(f"ESP {args.esp_id} deleted successfully")
        else:
            print(f"ESP {args.esp_id} not found", file=sys.stderr)
            sys.exit(1)


def cmd_get_bom(args):
    """Get BOM parts for an ESP."""
    with init_database() as db:
        bom = db.get_esp_bom_parts(args.esp_id)
        if bom:
            print_json({"esp_id": args.esp_id, "bom_parts": bom})
        else:
            print(f"ESP {args.esp_id} not found", file=sys.stderr)
            sys.exit(1)


def cmd_bom_summary(args):
    """Get BOM summary for an ESP."""
    with init_database() as db:
        summary = db.get_bom_summary(args.esp_id)
        if summary:
            print_json({"summary": summary})
        else:
            print(f"ESP {args.esp_id} not found", file=sys.stderr)
            sys.exit(1)


def cmd_list_parts(args):
    """List all parts."""
    with init_database() as db:
        print_json({"parts": db.get_all_parts()})


def cmd_get_part(args):
    """Get a specific part."""
    with init_database() as db:
        part = db.get_part(args.part_number)
        if part:
            print_json({"part": part})
        else:
            print(f"Part {args.part_number} not found", file=sys.stderr)
            sys.exit(1)


def cmd_create_part(args):
    """Create a new part."""
    with init_database() as db:
        try:
            part = db.create_part(
                part_number=args.part_number,
                name=args.name,
                category=args.category,
                material=args.material,
                weight_kg=args.weight,
                is_critical=args.critical
            )
            print_json({"part": part, "message": "Part created successfully"})
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_update_part(args):
    """Update a part."""
    with init_database() as db:
        updates = {}
        if args.name:
            updates["name"] = args.name
        if args.category:
            updates["category"] = args.category
        if args.material:
            updates["material"] = args.material
        if args.weight:
            updates["weight_kg"] = args.weight
        if args.critical is not None:
            updates["is_critical"] = args.critical

        part = db.update_part(args.part_number, **updates)
        if part:
            print_json({"part": part, "message": "Part updated successfully"})
        else:
            print(f"Part {args.part_number} not found", file=sys.stderr)
            sys.exit(1)


def cmd_delete_part(args):
    """Delete a part."""
    with init_database() as db:
        if args.force:
            deleted = db.force_delete_part(args.part_number)
            action = "force deleted"
        else:
            deleted = db.delete_part(args.part_number)
            action = "deleted"
        if deleted:
            print(f"Part {args.part_number} {action} successfully")
        else:
            print(f"Part {args.part_number} not found or is in use (use --force to force delete)", file=sys.stderr)
            sys.exit(1)


def cmd_parts_by_category(args):
    """List parts by category."""
    with init_database() as db:
        print_json({"category": args.category, "parts": db.get_parts_by_category(args.category)})


def cmd_search_parts(args):
    """Search parts."""
    with init_database() as db:
        print_json({"query": args.query, "parts": db.search_parts(args.query)})


def cmd_critical_parts(args):
    """List critical parts."""
    with init_database() as db:
        print_json({"critical_parts": db.get_critical_parts()})


def cmd_list_assemblies(args):
    """List all assemblies."""
    with init_database() as db:
        print_json({"assemblies": db.get_all_assemblies()})


def cmd_get_assembly(args):
    """Get a specific assembly."""
    with init_database() as db:
        assembly = db.get_assembly(args.assembly_code)
        if assembly:
            print_json({"assembly": assembly})
        else:
            print(f"Assembly {args.assembly_code} not found", file=sys.stderr)
            sys.exit(1)


def cmd_create_assembly(args):
    """Create a new assembly."""
    with init_database() as db:
        try:
            assembly = db.create_assembly(
                assembly_code=args.assembly_code,
                name=args.name,
                part_numbers=args.parts if args.parts else None
            )
            print_json({"assembly": assembly, "message": "Assembly created successfully"})
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_delete_assembly(args):
    """Delete an assembly."""
    with init_database() as db:
        if args.force:
            deleted = db.force_delete_assembly(args.assembly_code)
            action = "force deleted"
        else:
            deleted = db.delete_assembly(args.assembly_code)
            action = "deleted"
        if deleted:
            print(f"Assembly {args.assembly_code} {action} successfully")
        else:
            print(f"Assembly {args.assembly_code} not found or is in use (use --force to force delete)", file=sys.stderr)
            sys.exit(1)


def cmd_add_part_to_assembly(args):
    """Add a part to an assembly."""
    with init_database() as db:
        assembly = db.add_part_to_assembly(args.assembly_code, args.part_number)
        if assembly:
            print_json({"assembly": assembly, "message": f"Part {args.part_number} added to assembly"})
        else:
            print(f"Assembly {args.assembly_code} or part {args.part_number} not found", file=sys.stderr)
            sys.exit(1)


def cmd_remove_part_from_assembly(args):
    """Remove a part from an assembly."""
    with init_database() as db:
        assembly = db.remove_part_from_assembly(args.assembly_code, args.part_number)
        if assembly:
            print_json({"assembly": assembly, "message": f"Part {args.part_number} removed from assembly"})
        else:
            print(f"Assembly {args.assembly_code} not found", file=sys.stderr)
            sys.exit(1)


def cmd_update_part_quantity(args):
    """Update the quantity of a part in an assembly."""
    with init_database() as db:
        try:
            assembly = db.update_assembly_part_quantity(args.assembly_code, args.part_number, args.quantity)
            if assembly:
                print_json({"assembly": assembly, "message": f"Quantity updated to {args.quantity}"})
            else:
                print(f"Assembly {args.assembly_code} or part {args.part_number} not found in assembly", file=sys.stderr)
                sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_add_assembly_to_esp(args):
    """Add an assembly to an ESP."""
    with init_database() as db:
        esp = db.add_assembly_to_esp(args.esp_id, args.assembly_code)
        if esp:
            print_json({"esp": esp, "message": f"Assembly {args.assembly_code} added to ESP"})
        else:
            print(f"ESP {args.esp_id} or assembly {args.assembly_code} not found", file=sys.stderr)
            sys.exit(1)


def cmd_remove_assembly_from_esp(args):
    """Remove an assembly from an ESP."""
    with init_database() as db:
        esp = db.remove_assembly_from_esp(args.esp_id, args.assembly_code)
        if esp:
            print_json({"esp": esp, "message": f"Assembly {args.assembly_code} removed from ESP"})
        else:
            print(f"ESP {args.esp_id} not found", file=sys.stderr)
            sys.exit(1)


def cmd_stats(args):
    """Show database statistics."""
    with init_database() as db:
        print_json({
            "total_parts": len(db.get_all_parts()),
            "total_assemblies": len(db.get_all_assemblies()),
            "total_esps": len(db.get_all_esps()),
            "critical_parts": len(db.get_critical_parts())
        })


def main():
    parser = argparse.ArgumentParser(description="ESP BOM Database CLI")
    parser.add_argument("--db", default="esp_database.db", help="Database file path")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ESP commands
    esp_parser = subparsers.add_parser("esp", help="ESP commands")
    esp_sub = esp_parser.add_subparsers(dest="esp_command")

    p = esp_sub.add_parser("list", help="List all ESPs")
    p.set_defaults(cmd=cmd_list_esps)

    p = esp_sub.add_parser("get", help="Get ESP with full BOM")
    p.add_argument("esp_id", help="ESP ID (e.g., ESP-001)")
    p.set_defaults(cmd=cmd_get_esp)

    p = esp_sub.add_parser("create", help="Create a new ESP")
    p.add_argument("esp_id", help="ESP ID (e.g., ESP-011)")
    p.add_argument("model_name", help="Model name")
    p.add_argument("series", help="Series name")
    p.add_argument("power", type=float, help="Power rating (kW)")
    p.add_argument("voltage", type=int, help="Voltage (V)")
    p.add_argument("frequency", type=float, help="Frequency (Hz)")
    p.add_argument("flow_rate", type=float, help="Flow rate (m3/day)")
    p.add_argument("stages", type=int, help="Number of stages")
    p.add_argument("cable_length", type=float, help="Cable length (m)")
    p.add_argument("--assemblies", nargs="+", help="Assembly codes to include")
    p.set_defaults(cmd=cmd_create_esp)

    p = esp_sub.add_parser("delete", help="Delete an ESP")
    p.add_argument("esp_id", help="ESP ID to delete")
    p.set_defaults(cmd=cmd_delete_esp)

    p = esp_sub.add_parser("bom", help="Get BOM parts for an ESP")
    p.add_argument("esp_id", help="ESP ID (e.g., ESP-001)")
    p.set_defaults(cmd=cmd_get_bom)

    p = esp_sub.add_parser("summary", help="Get BOM summary for an ESP")
    p.add_argument("esp_id", help="ESP ID (e.g., ESP-001)")
    p.set_defaults(cmd=cmd_bom_summary)

    p = esp_sub.add_parser("series", help="Get ESPs by series")
    p.add_argument("series", help="Series name (e.g., RedZone Pro)")
    p.set_defaults(cmd=lambda a: print_json({"series": a.series, "esps": ESPDatabase(a.db).get_esps_by_series(a.series)}))

    p = esp_sub.add_parser("add-assembly", help="Add an assembly to an ESP")
    p.add_argument("esp_id", help="ESP ID")
    p.add_argument("assembly_code", help="Assembly code to add")
    p.set_defaults(cmd=cmd_add_assembly_to_esp)

    p = esp_sub.add_parser("remove-assembly", help="Remove an assembly from an ESP")
    p.add_argument("esp_id", help="ESP ID")
    p.add_argument("assembly_code", help="Assembly code to remove")
    p.set_defaults(cmd=cmd_remove_assembly_from_esp)

    # Parts commands
    parts_parser = subparsers.add_parser("parts", help="Parts commands")
    parts_sub = parts_parser.add_subparsers(dest="parts_command")

    p = parts_sub.add_parser("list", help="List all parts")
    p.set_defaults(cmd=cmd_list_parts)

    p = parts_sub.add_parser("get", help="Get a specific part")
    p.add_argument("part_number", help="Part number (e.g., ESP-MTR-001)")
    p.set_defaults(cmd=cmd_get_part)

    p = parts_sub.add_parser("create", help="Create a new part")
    p.add_argument("part_number", help="Part number (e.g., ESP-NEW-001)")
    p.add_argument("name", help="Part name")
    p.add_argument("category", help="Category (e.g., Motor, Pump, Seal, Cable, Sensor, Valve, Fitting, Bearing)")
    p.add_argument("material", help="Material composition")
    p.add_argument("weight", type=float, help="Weight in kg")
    p.add_argument("--critical", action="store_true", help="Mark as critical part")
    p.set_defaults(cmd=cmd_create_part)

    p = parts_sub.add_parser("update", help="Update a part")
    p.add_argument("part_number", help="Part number to update")
    p.add_argument("--name", help="New name")
    p.add_argument("--category", help="New category")
    p.add_argument("--material", help="New material")
    p.add_argument("--weight", type=float, help="New weight in kg")
    p.add_argument("--critical", action="store_true", help="Mark as critical")
    p.add_argument("--not-critical", dest="critical", action="store_false", help="Mark as not critical")
    p.set_defaults(cmd=cmd_update_part)

    p = parts_sub.add_parser("delete", help="Delete a part")
    p.add_argument("part_number", help="Part number to delete")
    p.add_argument("--force", action="store_true", help="Force delete (remove from assemblies first)")
    p.set_defaults(cmd=cmd_delete_part)

    p = parts_sub.add_parser("category", help="List parts by category")
    p.add_argument("category", help="Category (e.g., Motor, Pump)")
    p.set_defaults(cmd=cmd_parts_by_category)

    p = parts_sub.add_parser("search", help="Search parts")
    p.add_argument("query", help="Search query")
    p.set_defaults(cmd=cmd_search_parts)

    p = parts_sub.add_parser("critical", help="List critical parts")
    p.set_defaults(cmd=cmd_critical_parts)

    # Assembly commands
    asm_parser = subparsers.add_parser("assemblies", help="Assembly commands")
    asm_sub = asm_parser.add_subparsers(dest="asm_command")

    p = asm_sub.add_parser("list", help="List all assemblies")
    p.set_defaults(cmd=cmd_list_assemblies)

    p = asm_sub.add_parser("get", help="Get an assembly with its parts")
    p.add_argument("assembly_code", help="Assembly code (e.g., ASM-MTR-001)")
    p.set_defaults(cmd=cmd_get_assembly)

    p = asm_sub.add_parser("create", help="Create a new assembly")
    p.add_argument("assembly_code", help="Assembly code (e.g., ASM-NEW-001)")
    p.add_argument("name", help="Assembly name")
    p.add_argument("--parts", nargs="+", help="Part numbers to include")
    p.set_defaults(cmd=cmd_create_assembly)

    p = asm_sub.add_parser("delete", help="Delete an assembly")
    p.add_argument("assembly_code", help="Assembly code to delete")
    p.add_argument("--force", action="store_true", help="Force delete (remove from ESPs first)")
    p.set_defaults(cmd=cmd_delete_assembly)

    p = asm_sub.add_parser("add-part", help="Add a part to an assembly")
    p.add_argument("assembly_code", help="Target assembly")
    p.add_argument("part_number", help="Part number to add")
    p.set_defaults(cmd=cmd_add_part_to_assembly)

    p = asm_sub.add_parser("remove-part", help="Remove a part from an assembly")
    p.add_argument("assembly_code", help="Target assembly")
    p.add_argument("part_number", help="Part number to remove")
    p.set_defaults(cmd=cmd_remove_part_from_assembly)

    p = asm_sub.add_parser("update-quantity", help="Update the quantity of a part in an assembly")
    p.add_argument("assembly_code", help="Target assembly")
    p.add_argument("part_number", help="Part number to update")
    p.add_argument("quantity", type=int, help="New quantity value")
    p.set_defaults(cmd=cmd_update_part_quantity)

    # Stats command
    p = subparsers.add_parser("stats", help="Show database statistics")
    p.set_defaults(cmd=cmd_stats)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Initialize database with specified path
    ESPDatabase.db_path = args.db
    args.cmd(args)


if __name__ == "__main__":
    main()
