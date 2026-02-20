"""Claim templates and domain knowledge for synthetic data generation.

These templates encode realistic warranty claim patterns, including
legitimate claims and known fraud archetypes. They serve as the
building blocks for the synthetic data generator.
"""

from dataclasses import dataclass, field


@dataclass
class RepairScenario:
    """A realistic repair scenario with expected parameters."""

    name: str
    symptoms: list[str]
    diagnoses: list[str]
    parts: list[dict[str, str | float]]
    book_time_hours: float
    labor_range: tuple[float, float]  # (min, max) reasonable hours
    applicable_makes: list[str] | None = None  # None = all makes
    min_mileage: int = 0
    max_mileage: int = 200_000


@dataclass
class FraudPattern:
    """A known fraud archetype with parameters for synthetic generation."""

    name: str
    description: str
    manipulation: str  # what gets manipulated
    severity: str  # mild, moderate, severe


# --- Vehicle database ---

VEHICLES = [
    {"make": "Ford", "model": "F-150", "years": range(2015, 2025)},
    {"make": "Ford", "model": "Explorer", "years": range(2016, 2025)},
    {"make": "Ford", "model": "Escape", "years": range(2017, 2025)},
    {"make": "Toyota", "model": "Camry", "years": range(2015, 2025)},
    {"make": "Toyota", "model": "RAV4", "years": range(2016, 2025)},
    {"make": "Toyota", "model": "Tacoma", "years": range(2016, 2025)},
    {"make": "Chevrolet", "model": "Silverado", "years": range(2015, 2025)},
    {"make": "Chevrolet", "model": "Equinox", "years": range(2017, 2025)},
    {"make": "Honda", "model": "Civic", "years": range(2016, 2025)},
    {"make": "Honda", "model": "CR-V", "years": range(2016, 2025)},
    {"make": "Hyundai", "model": "Tucson", "years": range(2017, 2025)},
    {"make": "Hyundai", "model": "Elantra", "years": range(2018, 2025)},
    {"make": "Nissan", "model": "Altima", "years": range(2016, 2025)},
    {"make": "Nissan", "model": "Rogue", "years": range(2017, 2025)},
    {"make": "BMW", "model": "X5", "years": range(2017, 2025)},
    {"make": "BMW", "model": "3 Series", "years": range(2017, 2025)},
]

# --- Repair scenarios (legitimate baselines) ---

REPAIR_SCENARIOS: list[RepairScenario] = [
    RepairScenario(
        name="front_brake_service",
        symptoms=[
            "Vehicle makes grinding noise when braking",
            "Squealing from front brakes when stopping",
            "Brake pedal pulsation during braking",
        ],
        diagnoses=[
            "Front brake pads worn to 2mm, rotors scored beyond spec",
            "Brake pad material depleted, rotor surface damaged",
            "Inspection found brake pads at minimum thickness, rotor runout excessive",
        ],
        parts=[
            {"name": "Front Brake Pads", "cost": 85.00},
            {"name": "Front Rotors (pair)", "cost": 175.00},
        ],
        book_time_hours=1.5,
        labor_range=(1.2, 2.0),
    ),
    RepairScenario(
        name="alternator_replacement",
        symptoms=[
            "Battery warning light on dashboard",
            "Vehicle dies while driving, battery light illuminated",
            "Dimming headlights and electrical issues",
        ],
        diagnoses=[
            "Alternator output tested at 11.2V, below 13.5V specification",
            "Alternator failed output test, not charging battery",
            "Diagnosed alternator failure via voltage drop test",
        ],
        parts=[
            {"name": "Alternator", "cost": 350.00},
            {"name": "Serpentine Belt", "cost": 45.00},
        ],
        book_time_hours=2.0,
        labor_range=(1.5, 2.5),
    ),
    RepairScenario(
        name="water_pump_replacement",
        symptoms=[
            "Engine overheating, temperature gauge in red",
            "Coolant leak under vehicle near front of engine",
            "Customer reports overheating in traffic",
        ],
        diagnoses=[
            "Water pump weep hole leaking, bearing has play",
            "Coolant leak traced to water pump seal failure",
            "Pressure test confirmed water pump as leak source",
        ],
        parts=[
            {"name": "Water Pump", "cost": 220.00},
            {"name": "Coolant", "cost": 25.00},
            {"name": "Thermostat", "cost": 35.00},
        ],
        book_time_hours=3.0,
        labor_range=(2.5, 4.0),
    ),
    RepairScenario(
        name="ignition_coil_replacement",
        symptoms=[
            "Engine misfire, check engine light on",
            "Rough idle and loss of power",
            "Vehicle shaking at idle, CEL flashing",
        ],
        diagnoses=[
            "Fault code P0301 - cylinder 1 misfire, ignition coil failed resistance test",
            "DTC P0303 stored, coil on cylinder 3 shows no spark",
            "Misfire detected, coil pack confirmed faulty via swap test",
        ],
        parts=[
            {"name": "Ignition Coil", "cost": 65.00},
            {"name": "Spark Plug", "cost": 12.00},
        ],
        book_time_hours=0.8,
        labor_range=(0.5, 1.2),
    ),
    RepairScenario(
        name="wheel_bearing_replacement",
        symptoms=[
            "Humming noise from front driver side, gets louder with speed",
            "Grinding noise that changes with steering input",
            "Roaring sound from wheel area at highway speeds",
        ],
        diagnoses=[
            "Front left wheel bearing has excessive play, confirmed on lift",
            "Wheel bearing noise isolated to front right, roughness felt when spun by hand",
            "Bearing failed shake test, audible grinding on rotation",
        ],
        parts=[
            {"name": "Wheel Bearing Hub Assembly", "cost": 195.00},
        ],
        book_time_hours=1.8,
        labor_range=(1.5, 2.5),
    ),
    RepairScenario(
        name="oxygen_sensor_replacement",
        symptoms=[
            "Check engine light on, poor fuel economy",
            "CEL illuminated, vehicle running rich",
            "Failed emissions test, check engine light",
        ],
        diagnoses=[
            "DTC P0135 - O2 sensor heater circuit bank 1 sensor 1",
            "Oxygen sensor reading stuck lean, confirmed with scan tool live data",
            "O2 sensor response time out of spec per freeze frame data",
        ],
        parts=[
            {"name": "Oxygen Sensor", "cost": 120.00},
        ],
        book_time_hours=0.8,
        labor_range=(0.5, 1.2),
    ),
    RepairScenario(
        name="ac_compressor_replacement",
        symptoms=[
            "AC blowing warm air",
            "No cold air from AC, clutch not engaging",
            "Air conditioning stopped working, hot air only",
        ],
        diagnoses=[
            "AC system low on refrigerant, compressor clutch not engaging, internal failure",
            "Compressor seized, system contaminated with metal debris",
            "AC compressor failed, no magnetic clutch engagement, low pressure side flat",
        ],
        parts=[
            {"name": "AC Compressor", "cost": 450.00},
            {"name": "Receiver Drier", "cost": 55.00},
            {"name": "Expansion Valve", "cost": 65.00},
            {"name": "Refrigerant R-134a", "cost": 40.00},
        ],
        book_time_hours=4.0,
        labor_range=(3.0, 5.5),
    ),
    RepairScenario(
        name="starter_motor_replacement",
        symptoms=[
            "Vehicle won't start, clicking noise when turning key",
            "No crank condition, battery tests good",
            "Intermittent no-start, starter engages slowly",
        ],
        diagnoses=[
            "Starter motor draws excessive current, bench test confirms failure",
            "Starter solenoid failed, no engagement on command",
            "Starter confirmed failed via voltage drop test at battery and starter terminals",
        ],
        parts=[
            {"name": "Starter Motor", "cost": 280.00},
        ],
        book_time_hours=1.5,
        labor_range=(1.0, 2.5),
    ),
]

# --- Fraud patterns ---

FRAUD_PATTERNS: list[FraudPattern] = [
    FraudPattern(
        name="labor_inflation",
        description="Labor hours claimed significantly exceed book time for the repair",
        manipulation="hours_claimed",
        severity="moderate",
    ),
    FraudPattern(
        name="unnecessary_parts",
        description="Parts replaced that are unrelated to the diagnosed problem",
        manipulation="parts_list",
        severity="moderate",
    ),
    FraudPattern(
        name="symptom_repair_mismatch",
        description="The repair performed doesn't logically address the reported symptom",
        manipulation="diagnosis_and_repair",
        severity="severe",
    ),
    FraudPattern(
        name="phantom_repair",
        description="Claim for work that was likely never performed (mileage/timing inconsistent)",
        manipulation="claim_context",
        severity="severe",
    ),
    FraudPattern(
        name="upcoding",
        description="Cheaper repair performed but more expensive repair billed",
        manipulation="parts_and_labor",
        severity="moderate",
    ),
]

# --- Standard labor rates by region ($/hr) ---

LABOR_RATES = {
    "northeast": 135.00,
    "southeast": 110.00,
    "midwest": 105.00,
    "southwest": 115.00,
    "west": 140.00,
    "default": 120.00,
}
