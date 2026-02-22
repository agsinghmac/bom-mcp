"""
Electric Submersible Pump (ESP) Parts and BOM Database

A self-contained SQLite database storing part numbers and Bill of Materials
for fake Electric Submersible Pumps.
"""

import sqlite3
import os
import os



from typing import Optional
from dataclasses import dataclass
from enum import Enum


class DatabasePath:
    """Database file path constant."""
    DEFAULT = os.path.join(os.path.dirname(__file__), "esp_database.db")


@dataclass
class ESPPart:
    """Represents a single part in the ESP system."""
    part_number: str
    name: str
    category: str
    material: str
    weight_kg: float
    is_critical: bool


@dataclass
class ESPAssembly:
    """Represents an ESP assembly/sub-assembly."""
    assembly_code: str
    name: str
    parts: list[str]  # List of part numbers in this assembly


@dataclass
class ESPTopLevel:
    """Represents a top-level ESP unit."""
    esp_id: str
    model_name: str
    series: str
    power_rating_kw: float
    voltage_v: int
    frequency_hz: float
    flow_rate_m3d: float
    stages: int
    cable_length_m: float
    assemblies: list[str]  # List of assembly codes


# ESP Categories
class PartCategory(Enum):
    MOTOR = "Motor"
    PUMP = "Pump"
    SEAL = "Seal"
    CABLE = "Cable"
    SENSOR = "Sensor"
    VALVE = "Valve"
    FITTING = "Fitting"
    BEARING = "Bearing"


# Sample Part Data
SAMPLE_PARTS = [
    # Motor Parts
    ("ESP-MTR-001", "Main Motor Housing", "Motor", "Stainless Steel 316", 45.0, True, "ea"),
    ("ESP-MTR-002", "Rotor Assembly", "Motor", "Copper/Steel", 28.5, True, "ea"),
    ("ESP-MTR-003", "Stator Winding", "Motor", "Copper", 15.0, True, "ea"),
    ("ESP-MTR-004", "Motor Bearings", "Motor", "Chrome Steel", 5.2, True, "set"),
    ("ESP-MTR-005", "Thrust Bearing", "Motor", "Carbon Composite", 8.0, True, "ea"),
    ("ESP-MTR-006", "Motor Head", "Motor", "Cast Iron", 22.0, True, "ea"),
    ("ESP-MTR-007", "Shaft Coupling", "Motor", "Alloy Steel", 3.5, False, "ea"),

    # Pump Parts
    ("ESP-PMP-001", "Pump Housing", "Pump", "Cast Iron D2", 55.0, True, "ea"),
    ("ESP-PMP-002", "Impeller Assembly", "Pump", "Bronze C86300", 12.0, True, "set"),
    ("ESP-PMP-003", "Diffuser", "Pump", "Cast Iron", 18.5, True, "ea"),
    ("ESP-PMP-004", "Pump Shaft", "Pump", "Stainless Steel 17-4PH", 8.5, True, "ea"),
    ("ESP-PMP-005", "Pump Bearings", "Bearing", "Tungsten Carbide", 2.8, True, "set"),
    ("ESP-PMP-006", "Wear Rings", "Pump", "Bronze C93200", 1.5, False, "set"),
    ("ESP-PMP-007", "Stage Assembly", "Pump", "Multiple Materials", 35.0, True, "ea"),

    # Seal Parts
    ("ESP-SEL-001", "Mechanical Seal", "Seal", "Silicon Carbide", 2.5, True, "ea"),
    ("ESP-SEL-002", "Oil Chamber", "Seal", "Stainless Steel 304", 8.0, True, "ea"),
    ("ESP-SEL-003", "Seal Flush Line", "Seal", "Inconel 718", 1.2, False, "ea"),
    ("ESP-SEL-004", "Check Valve", "Valve", "Stainless Steel 316", 3.0, True, "ea"),

    # Cable Parts
    ("ESP-CBL-001", "Power Cable 50m", "Cable", "Copper/EPDM", 25.0, True, "m"),
    ("ESP-CBL-002", "Power Cable 100m", "Cable", "Copper/EPDM", 50.0, True, "m"),
    ("ESP-CBL-003", "Cable Guard", "Cable", "Rubber/Steel", 5.0, False, "ea"),
    ("ESP-CBL-004", "Cable Spacer", "Cable", "Nylon", 0.5, False, "ea"),

    # Sensor Parts
    ("ESP-SNS-001", "Temperature Sensor", "Sensor", "PT100/SS316", 0.3, True, "ea"),
    ("ESP-SNS-002", "Pressure Sensor", "Sensor", "SS316/Diaphragm", 0.8, True, "ea"),
    ("ESP-SNS-003", "Vibration Sensor", "Sensor", "Accelerometer", 0.2, True, "ea"),
    ("ESP-SNS-004", "Winding Protection", "Sensor", "Electronic/SS", 0.5, True, "ea"),

    # Fitting Parts
    ("ESP-FIT-001", "Intake Screen", "Fitting", "Stainless Steel 304", 6.5, True, "ea"),
    ("ESP-FIT-002", "Discharge Head", "Fitting", "Cast Iron", 15.0, True, "ea"),
    ("ESP-FIT-003", "Check Valve Retainer", "Fitting", "Stainless Steel 316", 2.0, False, "ea"),
    ("ESP-FIT-004", "Tie Bolt Assembly", "Fitting", "Alloy Steel", 4.5, False, "set"),
]

# Sample Assembly Data
SAMPLE_ASSEMBLIES = [
    ("ASM-MTR-001", "Main Motor Assembly", ["ESP-MTR-001", "ESP-MTR-002", "ESP-MTR-003", "ESP-MTR-004", "ESP-MTR-005", "ESP-MTR-006", "ESP-MTR-007"]),
    ("ASM-MTR-002", "Motor Seal Chamber", ["ESP-SEL-001", "ESP-SEL-002", "ESP-SEL-003"]),
    ("ASM-PMP-001", "Pump Section Assembly", ["ESP-PMP-001", "ESP-PMP-002", "ESP-PMP-003", "ESP-PMP-004", "ESP-PMP-005", "ESP-PMP-006"]),
    ("ASM-PMP-002", "Multi-Stage Assembly", ["ESP-PMP-007"]),
    ("ASM-CBL-001", "Cable Assembly 50m", ["ESP-CBL-001", "ESP-CBL-003", "ESP-CBL-004"]),
    ("ASM-CBL-002", "Cable Assembly 100m", ["ESP-CBL-002", "ESP-CBL-003", "ESP-CBL-004"]),
    ("ASM-SNS-001", "Monitoring Package", ["ESP-SNS-001", "ESP-SNS-002", "ESP-SNS-003", "ESP-SNS-004"]),
    ("ASM-VLV-001", "Valve Assembly", ["ESP-SEL-004", "ESP-FIT-003"]),
    ("ASM-FIT-001", "Intake Assembly", ["ESP-FIT-001", "ESP-FIT-004"]),
    ("ASM-FIT-002", "Discharge Assembly", ["ESP-FIT-002", "ESP-FIT-004"]),
]

# Sample Top-Level ESP Data
SAMPLE_ESPS = [
    ("ESP-001", "RedZone Pro 500", "RedZone Pro", 55, 2400, 60, 800, 45, 100, ["ASM-MTR-001", "ASM-MTR-002", "ASM-PMP-001", "ASM-PMP-002", "ASM-CBL-001", "ASM-SNS-001", "ASM-VLV-001", "ASM-FIT-001", "ASM-FIT-002"]),
    ("ESP-002", "RedZone Pro 750", "RedZone Pro", 75, 2400, 60, 1200, 50, 120, ["ASM-MTR-001", "ASM-MTR-002", "ASM-PMP-001", "ASM-PMP-002", "ASM-CBL-002", "ASM-SNS-001", "ASM-VLV-001", "ASM-FIT-001", "ASM-FIT-002"]),
    ("ESP-003", "RedZone Pro 1000", "RedZone Pro", 110, 2400, 60, 1600, 55, 150, ["ASM-MTR-001", "ASM-MTR-002", "ASM-PMP-001", "ASM-PMP-002", "ASM-CBL-002", "ASM-SNS-001", "ASM-VLV-001", "ASM-FIT-001", "ASM-FIT-002"]),
    ("ESP-004", "AquaMax 300", "AquaMax", 37, 2400, 60, 500, 40, 80, ["ASM-MTR-001", "ASM-MTR-002", "ASM-PMP-001", "ASM-PMP-002", "ASM-CBL-001", "ASM-SNS-001", "ASM-VLV-001", "ASM-FIT-001", "ASM-FIT-002"]),
    ("ESP-005", "AquaMax 600", "AquaMax", 55, 2400, 60, 950, 45, 100, ["ASM-MTR-001", "ASM-MTR-002", "ASM-PMP-001", "ASM-PMP-002", "ASM-CBL-001", "ASM-SNS-001", "ASM-VLV-001", "ASM-FIT-001", "ASM-FIT-002"]),
    ("ESP-006", "HydroLift 400", "HydroLift", 45, 2400, 50, 650, 42, 90, ["ASM-MTR-001", "ASM-MTR-002", "ASM-PMP-001", "ASM-PMP-002", "ASM-CBL-001", "ASM-SNS-001", "ASM-VLV-001", "ASM-FIT-001", "ASM-FIT-002"]),
    ("ESP-007", "HydroLift 800", "HydroLift", 90, 2400, 50, 1400, 52, 130, ["ASM-MTR-001", "ASM-MTR-002", "ASM-PMP-001", "ASM-PMP-002", "ASM-CBL-002", "ASM-SNS-001", "ASM-VLV-001", "ASM-FIT-001", "ASM-FIT-002"]),
    ("ESP-008", "PowerPump 200", "PowerPump", 22, 2400, 60, 300, 35, 70, ["ASM-MTR-001", "ASM-MTR-002", "ASM-PMP-001", "ASM-PMP-002", "ASM-CBL-001", "ASM-SNS-001", "ASM-VLV-001", "ASM-FIT-001", "ASM-FIT-002"]),
    ("ESP-009", "PowerPump 500", "PowerPump", 55, 2400, 60, 900, 48, 100, ["ASM-MTR-001", "ASM-MTR-002", "ASM-PMP-001", "ASM-PMP-002", "ASM-CBL-001", "ASM-SNS-001", "ASM-VLV-001", "ASM-FIT-001", "ASM-FIT-002"]),
    ("ESP-010", "DeepWell 1500", "DeepWell", 150, 2400, 60, 2500, 65, 200, ["ASM-MTR-001", "ASM-MTR-002", "ASM-PMP-001", "ASM-PMP-002", "ASM-CBL-002", "ASM-SNS-001", "ASM-VLV-001", "ASM-FIT-001", "ASM-FIT-002"]),
]


class ESPDatabase:
    """Self-contained SQLite database for ESP parts and BOMs."""

    def __init__(self, db_path: str = DatabasePath.DEFAULT):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database tables and indexes."""
        cursor = self.conn.cursor()

        # Create parts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parts (
                part_number TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                material TEXT NOT NULL,
                weight_kg REAL NOT NULL,
                is_critical INTEGER NOT NULL,
                uom TEXT NOT NULL DEFAULT 'ea'
            )
        """)

        # Create assemblies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assemblies (
                assembly_code TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)

        # Create assembly-parts junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assembly_parts (
                assembly_code TEXT NOT NULL,
                part_number TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                bom_level INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (assembly_code, part_number),
                FOREIGN KEY (assembly_code) REFERENCES assemblies(assembly_code),
                FOREIGN KEY (part_number) REFERENCES parts(part_number)
            )
        """)

        # Create top-level ESP table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS esp_units (
                esp_id TEXT PRIMARY KEY,
                model_name TEXT NOT NULL,
                series TEXT NOT NULL,
                power_rating_kw REAL NOT NULL,
                voltage_v INTEGER NOT NULL,
                frequency_hz REAL NOT NULL,
                flow_rate_m3d REAL NOT NULL,
                stages INTEGER NOT NULL,
                cable_length_m REAL NOT NULL
            )
        """)

        # Create ESP-assemblies junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS esp_assemblies (
                esp_id TEXT NOT NULL,
                assembly_code TEXT NOT NULL,
                PRIMARY KEY (esp_id, assembly_code),
                FOREIGN KEY (esp_id) REFERENCES esp_units(esp_id),
                FOREIGN KEY (assembly_code) REFERENCES assemblies(assembly_code)
            )
        """)

        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()

    def populate_sample_data(self) -> None:
        """Populate database with sample ESP data."""
        cursor = self.conn.cursor()

        # Insert parts
        for part in SAMPLE_PARTS:
            cursor.execute("""
                INSERT OR REPLACE INTO parts (part_number, name, category, material, weight_kg, is_critical, uom)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, part)

        # Insert assemblies
        for assembly in SAMPLE_ASSEMBLIES:
            cursor.execute("""
                INSERT OR REPLACE INTO assemblies (assembly_code, name)
                VALUES (?, ?)
            """, (assembly[0], assembly[1]))

            # Insert assembly-part relationships
            for part_number in assembly[2]:
                cursor.execute("""
                    INSERT OR IGNORE INTO assembly_parts (assembly_code, part_number)
                    VALUES (?, ?)
                """, (assembly[0], part_number))

        # Insert top-level ESPs
        for esp in SAMPLE_ESPS:
            cursor.execute("""
                INSERT OR REPLACE INTO esp_units
                (esp_id, model_name, series, power_rating_kw, voltage_v, frequency_hz, flow_rate_m3d, stages, cable_length_m)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, esp[:9])

            # Insert ESP-assembly relationships
            for assembly_code in esp[9]:
                cursor.execute("""
                    INSERT OR IGNORE INTO esp_assemblies (esp_id, assembly_code)
                    VALUES (?, ?)
                """, (esp[0], assembly_code))

        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()

    def get_part(self, part_number: str) -> Optional[dict]:
        """Get a single part by part number."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM parts WHERE part_number = ?", (part_number,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_parts_by_category(self, category: str) -> list[dict]:
        """Get all parts in a given category."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM parts WHERE category = ? ORDER BY part_number", (category,))
        return [dict(row) for row in cursor.fetchall()]

    def get_all_parts(self) -> list[dict]:
        """Get all parts in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM parts ORDER BY part_number")
        return [dict(row) for row in cursor.fetchall()]

    def get_assembly(self, assembly_code: str) -> Optional[dict]:
        """Get assembly details including parts."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM assemblies WHERE assembly_code = ?", (assembly_code,))
        row = cursor.fetchone()
        if not row:
            return None

        result = dict(row)

        # Get parts for this assembly
        cursor.execute("""
            SELECT p.*, ap.quantity, ap.bom_level FROM parts p
            JOIN assembly_parts ap ON p.part_number = ap.part_number
            WHERE ap.assembly_code = ?
            ORDER BY p.category, p.part_number
        """, (assembly_code,))
        result["parts"] = [dict(row) for row in cursor.fetchall()]

        return result

    def get_all_assemblies(self) -> list[dict]:
        """Get all assemblies in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM assemblies ORDER BY assembly_code")
        assemblies = []
        for row in cursor.fetchall():
            assembly = dict(row)
            cursor.execute("""
                SELECT p.*, ap.quantity, ap.bom_level FROM parts p
                JOIN assembly_parts ap ON p.part_number = ap.part_number
                WHERE ap.assembly_code = ?
            """, (assembly["assembly_code"],))
            assembly["parts"] = [dict(r) for r in cursor.fetchall()]
            assemblies.append(assembly)
        return assemblies

    def get_esp(self, esp_id: str) -> Optional[dict]:
        """Get top-level ESP with full BOM (all assemblies and their parts)."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM esp_units WHERE esp_id = ?", (esp_id,))
        row = cursor.fetchone()
        if not row:
            return None

        result = dict(row)

        # Get assemblies for this ESP
        cursor.execute("""
            SELECT a.* FROM assemblies a
            JOIN esp_assemblies ea ON a.assembly_code = ea.assembly_code
            WHERE ea.esp_id = ?
            ORDER BY a.assembly_code
        """, (esp_id,))
        assemblies = []
        for asm_row in cursor.fetchall():
            assembly = dict(asm_row)

            # Get parts for each assembly
            cursor.execute("""
                SELECT p.*, ap.quantity, ap.bom_level FROM parts p
                JOIN assembly_parts ap ON p.part_number = ap.part_number
                WHERE ap.assembly_code = ?
                ORDER BY p.category, p.part_number
            """, (assembly["assembly_code"],))
            assembly["parts"] = [dict(r) for r in cursor.fetchall()]
            assemblies.append(assembly)

        result["assemblies"] = assemblies

        # Flatten to get all parts for the complete BOM
        all_parts = []
        seen_parts = set()
        for assembly in assemblies:
            for part in assembly["parts"]:
                if part["part_number"] not in seen_parts:
                    seen_parts.add(part["part_number"])
                    all_parts.append(part)
        result["bom_parts"] = all_parts

        return result

    def get_esp_bom_parts(self, esp_id: str) -> Optional[list[dict]]:
        """Get just the BOM parts list for an ESP (no assembly hierarchy)."""
        esp = self.get_esp(esp_id)
        if esp:
            return esp.get("bom_parts")
        return None

    def get_esp_assemblies(self, esp_id: str) -> Optional[list[dict]]:
        """Get just the assemblies for an ESP (without nested parts)."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM esp_units WHERE esp_id = ?", (esp_id,))
        row = cursor.fetchone()
        if not row:
            return None

        result = dict(row)

        cursor.execute("""
            SELECT a.* FROM assemblies a
            JOIN esp_assemblies ea ON a.assembly_code = ea.assembly_code
            WHERE ea.esp_id = ?
            ORDER BY a.assembly_code
        """, (esp_id,))
        result["assemblies"] = [dict(row) for row in cursor.fetchall()]

        return result

    def get_all_esps(self) -> list[dict]:
        """Get all top-level ESPs with their specifications."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM esp_units ORDER BY esp_id")
        return [dict(row) for row in cursor.fetchall()]

    def get_esps_by_series(self, series: str) -> list[dict]:
        """Get all ESPs in a given series."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM esp_units WHERE series = ? ORDER BY power_rating_kw", (series,))
        return [dict(row) for row in cursor.fetchall()]

    def search_parts(self, query: str) -> list[dict]:
        """Search parts by name or category."""
        cursor = self.conn.cursor()
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT * FROM parts
            WHERE name LIKE ? OR category LIKE ? OR material LIKE ?
            ORDER BY category, part_number
        """, (search_term, search_term, search_term))
        return [dict(row) for row in cursor.fetchall()]

    def get_critical_parts(self) -> list[dict]:
        """Get all critical parts."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM parts WHERE is_critical = 1 ORDER BY category, part_number")
        return [dict(row) for row in cursor.fetchall()]

    def get_bom_summary(self, esp_id: str) -> Optional[dict]:
        """Get a summary of the BOM for an ESP."""
        esp = self.get_esp(esp_id)
        if not esp:
            return None

        parts = esp.get("bom_parts", [])

        # Count by category
        by_category = {}
        for part in parts:
            cat = part["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(part["part_number"])

        # Calculate total weight
        total_weight = sum(p["weight_kg"] for p in parts)
        critical_count = sum(1 for p in parts if p["is_critical"])

        return {
            "esp_id": esp_id,
            "model_name": esp["model_name"],
            "total_parts": len(parts),
            "total_weight_kg": round(total_weight, 2),
            "critical_parts_count": critical_count,
            "parts_by_category": {k: len(v) for k, v in by_category.items()},
            "assembly_count": len(esp["assemblies"])
        }

    # ============ Part CRUD Operations ============

    def create_part(self, part_number: str, name: str, category: str, material: str,
                    weight_kg: float, is_critical: bool = False) -> dict:
        """Create a new part in the database.

        Args:
            part_number: Unique identifier for the part
            name: Human-readable name
            category: Part category (e.g., Motor, Pump)
            material: Material composition
            weight_kg: Weight in kilograms
            is_critical: Whether this is a critical part

        Returns:
            The created part as a dict

        Raises:
            ValueError: If part already exists
        """
        cursor = self.conn.cursor()

        # Check if part already exists
        cursor.execute("SELECT 1 FROM parts WHERE part_number = ?", (part_number,))
        if cursor.fetchone():
            raise ValueError(f"Part {part_number} already exists")

        cursor.execute("""
            INSERT INTO parts (part_number, name, category, material, weight_kg, is_critical)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (part_number, name, category, material, weight_kg, 1 if is_critical else 0))
        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()

        return self.get_part(part_number)

    def update_part(self, part_number: str, name: str = None, category: str = None,
                    material: str = None, weight_kg: float = None,
                    is_critical: bool = None) -> Optional[dict]:
        """Update an existing part.

        Args:
            part_number: Part to update
            name: New name (optional)
            category: New category (optional)
            material: New material (optional)
            weight_kg: New weight (optional)
            is_critical: New critical flag (optional)

        Returns:
            Updated part as dict, or None if part doesn't exist
        """
        # Check part exists
        existing = self.get_part(part_number)
        if not existing:
            return None

        cursor = self.conn.cursor()

        # Build dynamic update
        updates = []
        params = []
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        if material is not None:
            updates.append("material = ?")
            params.append(material)
        if weight_kg is not None:
            updates.append("weight_kg = ?")
            params.append(weight_kg)
        if is_critical is not None:
            updates.append("is_critical = ?")
            params.append(1 if is_critical else 0)

        if not updates:
            return existing

        params.append(part_number)
        cursor.execute(f"""
            UPDATE parts SET {', '.join(updates)} WHERE part_number = ?
        """, params)
        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()

        return self.get_part(part_number)

    def delete_part(self, part_number: str) -> bool:
        """Delete a part from the database.

        Note: This will fail if the part is used in any assembly due to foreign key constraints.

        Args:
            part_number: Part to delete

        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM parts WHERE part_number = ?", (part_number,))
        deleted = cursor.rowcount > 0
        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()
        return deleted

    def force_delete_part(self, part_number: str) -> bool:
        """Force delete a part, removing it from all assemblies first.

        Args:
            part_number: Part to delete

        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()

        # Check if part exists
        cursor.execute("SELECT 1 FROM parts WHERE part_number = ?", (part_number,))
        if not cursor.fetchone():
            return False

        # Remove from all assemblies first
        cursor.execute("DELETE FROM assembly_parts WHERE part_number = ?", (part_number,))

        # Delete the part
        cursor.execute("DELETE FROM parts WHERE part_number = ?", (part_number,))
        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()
        return True

    # ============ Assembly CRUD Operations ============

    def create_assembly(self, assembly_code: str, name: str, part_numbers: list[str] = None) -> dict:
        """Create a new assembly.

        Args:
            assembly_code: Unique identifier for the assembly
            name: Human-readable name
            part_numbers: List of part numbers to include (optional)

        Returns:
            The created assembly as a dict

        Raises:
            ValueError: If assembly already exists or if any part doesn't exist
        """
        cursor = self.conn.cursor()

        # Check if assembly already exists
        cursor.execute("SELECT 1 FROM assemblies WHERE assembly_code = ?", (assembly_code,))
        if cursor.fetchone():
            raise ValueError(f"Assembly {assembly_code} already exists")

        # Create the assembly
        cursor.execute("""
            INSERT INTO assemblies (assembly_code, name)
            VALUES (?, ?)
        """, (assembly_code, name))

        # Add parts if provided
        if part_numbers:
            for pn in part_numbers:
                cursor.execute("SELECT 1 FROM parts WHERE part_number = ?", (pn,))
                if not cursor.fetchone():
                    # Rollback and raise error
                    self.conn.rollback()
                    raise ValueError(f"Part {pn} does not exist")
                cursor.execute("""
                    INSERT INTO assembly_parts (assembly_code, part_number)
                    VALUES (?, ?)
                """, (assembly_code, pn))

        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()
        return self.get_assembly(assembly_code)

    def update_assembly(self, assembly_code: str, name: str = None) -> Optional[dict]:
        """Update an assembly's name.

        Args:
            assembly_code: Assembly to update
            name: New name (optional)

        Returns:
            Updated assembly as dict, or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM assemblies WHERE assembly_code = ?", (assembly_code,))
        if not cursor.fetchone():
            return None

        if name is not None:
            cursor.execute("UPDATE assemblies SET name = ? WHERE assembly_code = ?", (name, assembly_code))
            self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()

        return self.get_assembly(assembly_code)

    def delete_assembly(self, assembly_code: str) -> bool:
        """Delete an assembly.

        Note: This will fail if the assembly is used in any ESP due to foreign key constraints.

        Args:
            assembly_code: Assembly to delete

        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM assemblies WHERE assembly_code = ?", (assembly_code,))
        deleted = cursor.rowcount > 0
        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()
        return deleted

    def force_delete_assembly(self, assembly_code: str) -> bool:
        """Force delete an assembly, removing ESP references first.

        Args:
            assembly_code: Assembly to delete

        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()

        # Check if assembly exists
        cursor.execute("SELECT 1 FROM assemblies WHERE assembly_code = ?", (assembly_code,))
        if not cursor.fetchone():
            return False

        # Remove ESP references
        cursor.execute("DELETE FROM esp_assemblies WHERE assembly_code = ?", (assembly_code,))

        # Remove part references
        cursor.execute("DELETE FROM assembly_parts WHERE assembly_code = ?", (assembly_code,))

        # Delete the assembly
        cursor.execute("DELETE FROM assemblies WHERE assembly_code = ?", (assembly_code,))
        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()
        return True

    # ============ BOM (Assembly Parts) Operations ============

    def add_part_to_assembly(self, assembly_code: str, part_number: str) -> Optional[dict]:
        """Add a part to an assembly's BOM.

        Args:
            assembly_code: Target assembly
            part_number: Part to add

        Returns:
            Updated assembly, or None if assembly or part doesn't exist

        Raises:
            ValueError: If part is already in the assembly
        """
        cursor = self.conn.cursor()

        # Verify assembly exists
        cursor.execute("SELECT 1 FROM assemblies WHERE assembly_code = ?", (assembly_code,))
        if not cursor.fetchone():
            return None

        # Verify part exists
        cursor.execute("SELECT 1 FROM parts WHERE part_number = ?", (part_number,))
        if not cursor.fetchone():
            return None

        # Check if already in assembly
        cursor.execute("""
            SELECT 1 FROM assembly_parts
            WHERE assembly_code = ? AND part_number = ?
        """, (assembly_code, part_number))
        if cursor.fetchone():
            raise ValueError(f"Part {part_number} is already in assembly {assembly_code}")

        # Add the part
        cursor.execute("""
            INSERT INTO assembly_parts (assembly_code, part_number)
            VALUES (?, ?)
        """, (assembly_code, part_number))
        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()

        return self.get_assembly(assembly_code)

    def remove_part_from_assembly(self, assembly_code: str, part_number: str) -> Optional[dict]:
        """Remove a part from an assembly's BOM.

        Args:
            assembly_code: Target assembly
            part_number: Part to remove

        Returns:
            Updated assembly, or None if assembly doesn't exist (part may not have been in assembly)
        """
        cursor = self.conn.cursor()

        # Verify assembly exists
        cursor.execute("SELECT 1 FROM assemblies WHERE assembly_code = ?", (assembly_code,))
        if not cursor.fetchone():
            return None

        # Remove the part
        cursor.execute("""
            DELETE FROM assembly_parts
            WHERE assembly_code = ? AND part_number = ?
        """, (assembly_code, part_number))
        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()

        return self.get_assembly(assembly_code)

    def update_assembly_part_quantity(self, assembly_code: str, part_number: str, quantity: int) -> Optional[dict]:
        """Update the quantity of a part in an assembly's BOM.

        Args:
            assembly_code: Target assembly
            part_number: Part to update
            quantity: New quantity value (must be positive integer)

        Returns:
            Updated assembly, or None if assembly or part not found in assembly

        Raises:
            ValueError: If quantity is not a positive integer
        """
        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError("Quantity must be a positive integer")

        cursor = self.conn.cursor()

        # Verify assembly exists
        cursor.execute("SELECT 1 FROM assemblies WHERE assembly_code = ?", (assembly_code,))
        if not cursor.fetchone():
            return None

        # Check if part is in assembly
        cursor.execute("""
            SELECT 1 FROM assembly_parts
            WHERE assembly_code = ? AND part_number = ?
        """, (assembly_code, part_number))
        if not cursor.fetchone():
            return None

        # Update the quantity
        cursor.execute("""
            UPDATE assembly_parts
            SET quantity = ?
            WHERE assembly_code = ? AND part_number = ?
        """, (quantity, assembly_code, part_number))
        self.conn.commit()

        return self.get_assembly(assembly_code)

    def get_assemblies_using_part(self, part_number: str) -> list[dict]:
        """Find all assemblies that contain a specific part.

        Args:
            part_number: Part to search for

        Returns:
            List of assemblies containing the part
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.* FROM assemblies a
            JOIN assembly_parts ap ON a.assembly_code = ap.assembly_code
            WHERE ap.part_number = ?
            ORDER BY a.assembly_code
        """, (part_number,))
        return [dict(row) for row in cursor.fetchall()]

    def get_esps_using_assembly(self, assembly_code: str) -> list[dict]:
        """Find all ESPs that use a specific assembly.

        Args:
            assembly_code: Assembly to search for

        Returns:
            List of ESPs using the assembly
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.* FROM esp_units e
            JOIN esp_assemblies ea ON e.esp_id = ea.esp_id
            WHERE ea.assembly_code = ?
            ORDER BY e.esp_id
        """, (assembly_code,))
        return [dict(row) for row in cursor.fetchall()]

    # ============ ESP CRUD Operations ============

    def create_esp(self, esp_id: str, model_name: str, series: str, power_rating_kw: float,
                   voltage_v: int, frequency_hz: float, flow_rate_m3d: float,
                   stages: int, cable_length_m: float,
                   assembly_codes: list[str] = None) -> dict:
        """Create a new top-level ESP.

        Args:
            esp_id: Unique identifier
            model_name: Model name (e.g., "RedZone Pro 500")
            series: Series name (e.g., "RedZone Pro")
            power_rating_kw: Power rating in kW
            voltage_v: Voltage in volts
            frequency_hz: Frequency in Hz
            flow_rate_m3d: Flow rate in m3/day
            stages: Number of stages
            cable_length_m: Cable length in meters
            assembly_codes: List of assemblies to include (optional)

        Returns:
            The created ESP as a dict

        Raises:
            ValueError: If ESP already exists or if any assembly doesn't exist
        """
        cursor = self.conn.cursor()

        # Check if ESP already exists
        cursor.execute("SELECT 1 FROM esp_units WHERE esp_id = ?", (esp_id,))
        if cursor.fetchone():
            raise ValueError(f"ESP {esp_id} already exists")

        # Create the ESP
        cursor.execute("""
            INSERT INTO esp_units
            (esp_id, model_name, series, power_rating_kw, voltage_v, frequency_hz, flow_rate_m3d, stages, cable_length_m)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (esp_id, model_name, series, power_rating_kw, voltage_v, frequency_hz, flow_rate_m3d, stages, cable_length_m))

        # Add assemblies if provided
        if assembly_codes:
            for ac in assembly_codes:
                cursor.execute("SELECT 1 FROM assemblies WHERE assembly_code = ?", (ac,))
                if not cursor.fetchone():
                    self.conn.rollback()
                    raise ValueError(f"Assembly {ac} does not exist")
                cursor.execute("""
                    INSERT INTO esp_assemblies (esp_id, assembly_code)
                    VALUES (?, ?)
                """, (esp_id, ac))

        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()
        return self.get_esp(esp_id)

    def update_esp(self, esp_id: str, model_name: str = None, series: str = None,
                   power_rating_kw: float = None, voltage_v: int = None,
                   frequency_hz: float = None, flow_rate_m3d: float = None,
                   stages: int = None, cable_length_m: float = None) -> Optional[dict]:
        """Update an ESP's specifications.

        Args:
            esp_id: ESP to update
            model_name: New model name (optional)
            series: New series (optional)
            power_rating_kw: New power rating (optional)
            voltage_v: New voltage (optional)
            frequency_hz: New frequency (optional)
            flow_rate_m3d: New flow rate (optional)
            stages: New stages count (optional)
            cable_length_m: New cable length (optional)

        Returns:
            Updated ESP as dict, or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM esp_units WHERE esp_id = ?", (esp_id,))
        if not cursor.fetchone():
            return None

        # Build dynamic update
        updates = []
        params = []
        if model_name is not None:
            updates.append("model_name = ?")
            params.append(model_name)
        if series is not None:
            updates.append("series = ?")
            params.append(series)
        if power_rating_kw is not None:
            updates.append("power_rating_kw = ?")
            params.append(power_rating_kw)
        if voltage_v is not None:
            updates.append("voltage_v = ?")
            params.append(voltage_v)
        if frequency_hz is not None:
            updates.append("frequency_hz = ?")
            params.append(frequency_hz)
        if flow_rate_m3d is not None:
            updates.append("flow_rate_m3d = ?")
            params.append(flow_rate_m3d)
        if stages is not None:
            updates.append("stages = ?")
            params.append(stages)
        if cable_length_m is not None:
            updates.append("cable_length_m = ?")
            params.append(cable_length_m)

        if not updates:
            return self.get_esp(esp_id)

        params.append(esp_id)
        cursor.execute(f"""
            UPDATE esp_units SET {', '.join(updates)} WHERE esp_id = ?
        """, params)
        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()

        return self.get_esp(esp_id)

    def delete_esp(self, esp_id: str) -> bool:
        """Delete an ESP.

        Args:
            esp_id: ESP to delete

        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM esp_units WHERE esp_id = ?", (esp_id,))
        deleted = cursor.rowcount > 0
        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()
        return deleted

    def add_assembly_to_esp(self, esp_id: str, assembly_code: str) -> Optional[dict]:
        """Add an assembly to an ESP.

        Args:
            esp_id: Target ESP
            assembly_code: Assembly to add

        Returns:
            Updated ESP, or None if ESP or assembly doesn't exist

        Raises:
            ValueError: If assembly is already in the ESP
        """
        cursor = self.conn.cursor()

        # Verify ESP exists
        cursor.execute("SELECT 1 FROM esp_units WHERE esp_id = ?", (esp_id,))
        if not cursor.fetchone():
            return None

        # Verify assembly exists
        cursor.execute("SELECT 1 FROM assemblies WHERE assembly_code = ?", (assembly_code,))
        if not cursor.fetchone():
            return None

        # Check if already in ESP
        cursor.execute("""
            SELECT 1 FROM esp_assemblies
            WHERE esp_id = ? AND assembly_code = ?
        """, (esp_id, assembly_code))
        if cursor.fetchone():
            raise ValueError(f"Assembly {assembly_code} is already in ESP {esp_id}")

        # Add the assembly
        cursor.execute("""
            INSERT INTO esp_assemblies (esp_id, assembly_code)
            VALUES (?, ?)
        """, (esp_id, assembly_code))
        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()

        return self.get_esp(esp_id)

    def remove_assembly_from_esp(self, esp_id: str, assembly_code: str) -> Optional[dict]:
        """Remove an assembly from an ESP.

        Args:
            esp_id: Target ESP
            assembly_code: Assembly to remove

        Returns:
            Updated ESP, or None if ESP doesn't exist
        """
        cursor = self.conn.cursor()

        # Verify ESP exists
        cursor.execute("SELECT 1 FROM esp_units WHERE esp_id = ?", (esp_id,))
        if not cursor.fetchone():
            return None

        # Remove the assembly
        cursor.execute("""
            DELETE FROM esp_assemblies
            WHERE esp_id = ? AND assembly_code = ?
        """, (esp_id, assembly_code))
        self.conn.commit()
        # If the database is empty, populate sample data
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parts")
        if cursor.fetchone()[0] == 0:
            self.populate_sample_data()

        return self.get_esp(esp_id)

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def init_database(db_path: str = DatabasePath.DEFAULT) -> ESPDatabase:
    """Initialize database and populate with sample data."""
    db = ESPDatabase(db_path)
    db.populate_sample_data()
    return db
