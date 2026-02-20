"""Comprehensive OBD-II Diagnostic Trouble Code (DTC) database.

Contains 300+ real DTCs organized by category with detailed repair
information for use in synthetic warranty claim data generation.

Categories:
    P0xxx: Generic Powertrain
    P1xxx: Manufacturer-specific Powertrain
    P2xxx: Generic Powertrain (newer)
    B0xxx-B3xxx: Body
    C0xxx-C3xxx: Chassis
    U0xxx-U3xxx: Network/Communication

Sources: SAE J2012, ISO 15031-6, OBD-II standard definitions.
"""

from __future__ import annotations

from typing import TypedDict


class DTCEntry(TypedDict):
    """A single OBD-II Diagnostic Trouble Code with repair metadata."""

    code: str
    description: str
    category: str           # powertrain, body, chassis, network
    subcategory: str        # fuel_and_air, ignition, emission, etc.
    severity: str           # low, medium, high
    common_symptoms: list[str]
    common_repairs: list[str]
    common_parts: list[str]
    typical_labor_hours: float


DTC_DATABASE: list[DTCEntry] = [
    # ==========================================================================
    # P0xxx GENERIC POWERTRAIN -- Fuel and Air Metering (P00xx - P01xx)
    # ==========================================================================
    {"code": "P0010", "description": "A Camshaft Position Actuator Circuit (Bank 1)", "category": "powertrain", "subcategory": "fuel_and_air",
     "severity": "medium", "common_symptoms": ["Check engine light", "Rough idle", "Reduced fuel economy"],
     "common_repairs": ["Replace VVT solenoid", "Check wiring and connector"], "common_parts": ["VVT Solenoid", "Engine Oil"], "typical_labor_hours": 1.2},
    {"code": "P0011", "description": "A Camshaft Position - Timing Over-Advanced (Bank 1)", "category": "powertrain", "subcategory": "fuel_and_air",
     "severity": "medium", "common_symptoms": ["Check engine light", "Rough idle", "Poor acceleration", "Engine stalling"],
     "common_repairs": ["Replace VVT solenoid", "Change engine oil and filter", "Inspect timing chain"], "common_parts": ["VVT Solenoid", "Engine Oil", "Oil Filter", "Timing Chain"], "typical_labor_hours": 1.5},
    {"code": "P0012", "description": "A Camshaft Position - Timing Over-Retarded (Bank 1)", "category": "powertrain", "subcategory": "fuel_and_air",
     "severity": "medium", "common_symptoms": ["Check engine light", "Hard starting", "Rough idle", "Poor fuel economy"],
     "common_repairs": ["Replace VVT solenoid", "Change engine oil"], "common_parts": ["VVT Solenoid", "Engine Oil", "Oil Filter"], "typical_labor_hours": 1.5},
    {"code": "P0013", "description": "B Camshaft Position Actuator Circuit (Bank 1)", "category": "powertrain", "subcategory": "fuel_and_air",
     "severity": "medium", "common_symptoms": ["Check engine light", "Engine rattling noise", "Poor fuel economy"],
     "common_repairs": ["Replace exhaust camshaft actuator solenoid", "Repair wiring"], "common_parts": ["VVT Solenoid (exhaust)", "Wiring Harness Connector"], "typical_labor_hours": 1.2},
    {"code": "P0014", "description": "B Camshaft Position - Timing Over-Advanced (Bank 1)", "category": "powertrain", "subcategory": "fuel_and_air",
     "severity": "high", "common_symptoms": ["Rough idle", "Poor fuel economy", "Rattling noise from engine"],
     "common_repairs": ["Replace exhaust VVT solenoid", "Replace timing chain"], "common_parts": ["VVT Solenoid", "Timing Chain Kit"], "typical_labor_hours": 2.0},
    {"code": "P0016", "description": "Crankshaft Position - Camshaft Position Correlation (Bank 1 Sensor A)", "category": "powertrain", "subcategory": "fuel_and_air",
     "severity": "high", "common_symptoms": ["Check engine light", "Engine runs rough", "Rattling from engine", "No start condition"],
     "common_repairs": ["Replace timing chain and guides", "Replace VVT solenoid"], "common_parts": ["Timing Chain Kit", "VVT Solenoid", "Camshaft Position Sensor"], "typical_labor_hours": 6.0},
    {"code": "P0017", "description": "Crankshaft Position - Camshaft Position Correlation (Bank 1 Sensor B)", "category": "powertrain", "subcategory": "fuel_and_air",
     "severity": "high", "common_symptoms": ["Rough idle", "Rattling noise", "Check engine light"],
     "common_repairs": ["Replace timing chain", "Replace camshaft actuator"], "common_parts": ["Timing Chain Kit", "Camshaft Actuator"], "typical_labor_hours": 6.0},
    {"code": "P0020", "description": "A Camshaft Position Actuator Circuit (Bank 2)", "category": "powertrain", "subcategory": "fuel_and_air",
     "severity": "medium", "common_symptoms": ["Check engine light", "Rough idle", "Reduced fuel economy"],
     "common_repairs": ["Replace VVT solenoid bank 2", "Check oil level and condition"], "common_parts": ["VVT Solenoid", "Engine Oil"], "typical_labor_hours": 1.2},
    {"code": "P0021", "description": "A Camshaft Position - Timing Over-Advanced (Bank 2)", "category": "powertrain", "subcategory": "fuel_and_air",
     "severity": "medium", "common_symptoms": ["Check engine light", "Rough idle", "Stalling"],
     "common_repairs": ["Replace VVT solenoid bank 2", "Change engine oil"], "common_parts": ["VVT Solenoid", "Engine Oil"], "typical_labor_hours": 1.5},
