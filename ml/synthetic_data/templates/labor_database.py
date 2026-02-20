"""Labor time standards and rate database for synthetic warranty claim generation.

Contains standard repair operations with flat-rate book times, regional
labor rate data for dealer and independent shops, and complexity
classifications. Pricing reflects 2024-2025 era market conditions.

Sources:
    - ALLDATA and Mitchell flat-rate labor guides
    - AAA auto repair cost survey (2024-2025)
    - autoGMS / Identifix labor rate reports (2025)
    - Bureau of Labor Statistics automotive repair data
"""

from typing import TypedDict


class LaborOperationEntry(TypedDict):
    """Schema for a labor operation entry."""

    operation_name: str
    category: str
    book_time_hours: float       # standard flat-rate book time
    complexity: str              # simple, moderate, complex
    requires_specialty_tools: bool


class RegionalLaborRate(TypedDict):
    """Labor rate structure for a specific region."""

    region: str
    dealer_rate_range: tuple[float, float]        # (low, high) $/hr
    independent_rate_range: tuple[float, float]    # (low, high) $/hr
    dealer_avg: float                              # average $/hr
    independent_avg: float                         # average $/hr


# ---------------------------------------------------------------------------
# Regional labor rates  (2024-2025 era)
# ---------------------------------------------------------------------------

LABOR_RATES_BY_REGION: list[RegionalLaborRate] = [
    {
        "region": "Northeast",
        "dealer_rate_range": (155.00, 210.00),
        "independent_rate_range": (110.00, 155.00),
        "dealer_avg": 178.00,
        "independent_avg": 132.00,
    },
    {
        "region": "Southeast",
        "dealer_rate_range": (130.00, 175.00),
        "independent_rate_range": (90.00, 130.00),
        "dealer_avg": 152.00,
        "independent_avg": 110.00,
    },
    {
        "region": "Midwest",
        "dealer_rate_range": (125.00, 170.00),
        "independent_rate_range": (85.00, 125.00),
        "dealer_avg": 148.00,
        "independent_avg": 105.00,
    },
    {
        "region": "Southwest",
        "dealer_rate_range": (135.00, 180.00),
        "independent_rate_range": (95.00, 135.00),
        "dealer_avg": 155.00,
        "independent_avg": 115.00,
    },
    {
        "region": "West Coast",
        "dealer_rate_range": (160.00, 225.00),
        "independent_rate_range": (120.00, 165.00),
        "dealer_avg": 188.00,
        "independent_avg": 142.00,
    },
    {
        "region": "Mountain",
        "dealer_rate_range": (130.00, 175.00),
        "independent_rate_range": (90.00, 130.00),
        "dealer_avg": 150.00,
        "independent_avg": 110.00,
    },
]

# Flat lookup by region name for quick access
REGION_RATE_MAP: dict[str, RegionalLaborRate] = {
    r["region"].lower(): r for r in LABOR_RATES_BY_REGION
}


# ---------------------------------------------------------------------------
# Dealer vs. Independent multiplier guidance
# ---------------------------------------------------------------------------

DEALER_VS_INDEPENDENT = {
    "description": (
        "Dealer labor rates are typically 30-55% higher than independent "
        "shops due to factory-trained technicians, OEM diagnostic tools, "
        "franchise fees, and higher facility overhead."
    ),
    "typical_dealer_premium_pct": 0.40,  # ~40% premium on average
    "luxury_dealer_premium_pct": 0.55,   # ~55% premium for luxury brands
    "diagnostic_fee_dealer": (150.00, 250.00),
    "diagnostic_fee_independent": (80.00, 150.00),
}


# ---------------------------------------------------------------------------
# Standard repair operations with flat-rate times
# ---------------------------------------------------------------------------

LABOR_OPERATIONS: list[LaborOperationEntry] = [

    # ======================================================================
    # ENGINE  --  Maintenance & Minor Repairs
    # ======================================================================
    {
        "operation_name": "Oil and Filter Change",
        "category": "Engine",
        "book_time_hours": 0.3,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Synthetic Oil and Filter Change",
        "category": "Engine",
        "book_time_hours": 0.3,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Engine Air Filter Replacement",
        "category": "Engine",
        "book_time_hours": 0.1,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Spark Plug Replacement (4-cylinder)",
        "category": "Engine",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Spark Plug Replacement (V6)",
        "category": "Engine",
        "book_time_hours": 2.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Spark Plug Replacement (V8)",
        "category": "Engine",
        "book_time_hours": 2.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "PCV Valve Replacement",
        "category": "Engine",
        "book_time_hours": 0.3,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Serpentine Belt Replacement",
        "category": "Engine",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Belt Tensioner Replacement",
        "category": "Engine",
        "book_time_hours": 0.8,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },

    # ======================================================================
    # ENGINE  --  Moderate Repairs
    # ======================================================================
    {
        "operation_name": "Ignition Coil Replacement (single)",
        "category": "Engine",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Ignition Coil Pack Replacement (all)",
        "category": "Engine",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Valve Cover Gasket Replacement (I4)",
        "category": "Engine",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Valve Cover Gasket Replacement (V6/V8)",
        "category": "Engine",
        "book_time_hours": 3.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Intake Manifold Gasket Replacement",
        "category": "Engine",
        "book_time_hours": 3.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Oil Pan Gasket Replacement",
        "category": "Engine",
        "book_time_hours": 3.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Engine Mount Replacement",
        "category": "Engine",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Transmission Mount Replacement",
        "category": "Engine",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Throttle Body Cleaning/Replacement",
        "category": "Engine",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Variable Valve Timing Solenoid Replacement",
        "category": "Engine",
        "book_time_hours": 0.8,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },

    # ======================================================================
    # ENGINE  --  Major Repairs
    # ======================================================================
    {
        "operation_name": "Timing Chain Replacement",
        "category": "Engine",
        "book_time_hours": 6.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Timing Belt and Water Pump Replacement",
        "category": "Engine",
        "book_time_hours": 5.5,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Head Gasket Replacement (I4)",
        "category": "Engine",
        "book_time_hours": 7.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Head Gasket Replacement (V6/V8)",
        "category": "Engine",
        "book_time_hours": 10.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Water Pump Replacement (timing belt driven)",
        "category": "Engine",
        "book_time_hours": 4.5,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Water Pump Replacement (external)",
        "category": "Engine",
        "book_time_hours": 2.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Oil Pump Replacement",
        "category": "Engine",
        "book_time_hours": 6.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Turbocharger Replacement",
        "category": "Engine",
        "book_time_hours": 5.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Rear Main Seal Replacement",
        "category": "Engine",
        "book_time_hours": 6.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Camshaft Phaser / VVT Gear Replacement",
        "category": "Engine",
        "book_time_hours": 4.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Engine Replacement (long block)",
        "category": "Engine",
        "book_time_hours": 14.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Engine Rebuild (in-frame)",
        "category": "Engine",
        "book_time_hours": 20.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },

    # ======================================================================
    # ENGINE  --  Sensor Replacements
    # ======================================================================
    {
        "operation_name": "Oxygen Sensor Replacement (upstream)",
        "category": "Engine",
        "book_time_hours": 0.8,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Oxygen Sensor Replacement (downstream)",
        "category": "Engine",
        "book_time_hours": 0.8,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Mass Air Flow Sensor Replacement",
        "category": "Engine",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Camshaft Position Sensor Replacement",
        "category": "Engine",
        "book_time_hours": 0.8,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Crankshaft Position Sensor Replacement",
        "category": "Engine",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Throttle Position Sensor Replacement",
        "category": "Engine",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Coolant Temperature Sensor Replacement",
        "category": "Engine",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Knock Sensor Replacement",
        "category": "Engine",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Oil Pressure Sensor Replacement",
        "category": "Engine",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },

    # ======================================================================
    # BRAKES
    # ======================================================================
    {
        "operation_name": "Front Brake Pad Replacement",
        "category": "Brakes",
        "book_time_hours": 0.8,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Rear Brake Pad Replacement",
        "category": "Brakes",
        "book_time_hours": 0.8,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Front Brake Pads and Rotors Replacement",
        "category": "Brakes",
        "book_time_hours": 1.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Rear Brake Pads and Rotors Replacement",
        "category": "Brakes",
        "book_time_hours": 1.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Four-Wheel Brake Pads and Rotors",
        "category": "Brakes",
        "book_time_hours": 3.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Brake Caliper Replacement (single)",
        "category": "Brakes",
        "book_time_hours": 1.2,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Brake Master Cylinder Replacement",
        "category": "Brakes",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Brake Booster Replacement",
        "category": "Brakes",
        "book_time_hours": 2.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Brake Line Replacement",
        "category": "Brakes",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Brake Fluid Flush",
        "category": "Brakes",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "ABS Wheel Speed Sensor Replacement",
        "category": "Brakes",
        "book_time_hours": 0.8,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "ABS Module Replacement",
        "category": "Brakes",
        "book_time_hours": 2.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Parking Brake Adjustment",
        "category": "Brakes",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Brake Rotor Resurfacing (per axle)",
        "category": "Brakes",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },

    # ======================================================================
    # SUSPENSION
    # ======================================================================
    {
        "operation_name": "Front Strut Replacement (pair)",
        "category": "Suspension",
        "book_time_hours": 2.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Rear Shock Replacement (pair)",
        "category": "Suspension",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Front Lower Control Arm Replacement",
        "category": "Suspension",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Front Upper Control Arm Replacement",
        "category": "Suspension",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Ball Joint Replacement (each)",
        "category": "Suspension",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Sway Bar Link Replacement (each)",
        "category": "Suspension",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Wheel Bearing/Hub Assembly Replacement",
        "category": "Suspension",
        "book_time_hours": 1.8,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Front Coil Spring Replacement",
        "category": "Suspension",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Leaf Spring Replacement",
        "category": "Suspension",
        "book_time_hours": 2.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Wheel Alignment (4-wheel)",
        "category": "Suspension",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Control Arm Bushing Replacement",
        "category": "Suspension",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },

    # ======================================================================
    # ELECTRICAL
    # ======================================================================
    {
        "operation_name": "Alternator Replacement",
        "category": "Electrical",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Starter Motor Replacement",
        "category": "Electrical",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Battery Replacement",
        "category": "Electrical",
        "book_time_hours": 0.3,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "ECU/ECM Replacement and Programming",
        "category": "Electrical",
        "book_time_hours": 1.5,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "TCM Replacement and Programming",
        "category": "Electrical",
        "book_time_hours": 1.5,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "BCM Replacement and Programming",
        "category": "Electrical",
        "book_time_hours": 1.5,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Power Window Motor Replacement",
        "category": "Electrical",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Power Window Regulator Replacement",
        "category": "Electrical",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Door Lock Actuator Replacement",
        "category": "Electrical",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Headlight Assembly Replacement",
        "category": "Electrical",
        "book_time_hours": 0.8,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Headlight Bulb Replacement",
        "category": "Electrical",
        "book_time_hours": 0.3,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Tail Light Assembly Replacement",
        "category": "Electrical",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Wiper Motor Replacement",
        "category": "Electrical",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Ignition Switch Replacement",
        "category": "Electrical",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Backup Camera Replacement",
        "category": "Electrical",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Instrument Cluster Replacement",
        "category": "Electrical",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "TPMS Sensor Replacement (each)",
        "category": "Electrical",
        "book_time_hours": 0.3,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },

    # ======================================================================
    # HVAC
    # ======================================================================
    {
        "operation_name": "AC Compressor Replacement",
        "category": "HVAC",
        "book_time_hours": 3.5,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "AC Condenser Replacement",
        "category": "HVAC",
        "book_time_hours": 2.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "AC Evaporator Replacement",
        "category": "HVAC",
        "book_time_hours": 6.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "AC Recharge (evacuate and recharge)",
        "category": "HVAC",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "AC Expansion Valve Replacement",
        "category": "HVAC",
        "book_time_hours": 2.0,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Blower Motor Replacement",
        "category": "HVAC",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Blower Motor Resistor Replacement",
        "category": "HVAC",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Heater Core Replacement",
        "category": "HVAC",
        "book_time_hours": 6.0,
        "complexity": "complex",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Cabin Air Filter Replacement",
        "category": "HVAC",
        "book_time_hours": 0.2,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Blend Door Actuator Replacement",
        "category": "HVAC",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "AC System Leak Detection and Repair",
        "category": "HVAC",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },

    # ======================================================================
    # TRANSMISSION & DRIVETRAIN
    # ======================================================================
    {
        "operation_name": "Transmission Fluid Service",
        "category": "Transmission",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Transmission Fluid and Filter Change",
        "category": "Transmission",
        "book_time_hours": 1.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Automatic Transmission Replacement",
        "category": "Transmission",
        "book_time_hours": 8.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "CVT Transmission Replacement",
        "category": "Transmission",
        "book_time_hours": 8.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Transmission Rebuild",
        "category": "Transmission",
        "book_time_hours": 12.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Torque Converter Replacement",
        "category": "Transmission",
        "book_time_hours": 6.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Clutch Kit Replacement (manual trans)",
        "category": "Transmission",
        "book_time_hours": 5.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Flywheel/Dual-Mass Flywheel Replacement",
        "category": "Transmission",
        "book_time_hours": 5.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Transmission Solenoid Replacement",
        "category": "Transmission",
        "book_time_hours": 3.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Transmission Speed Sensor Replacement",
        "category": "Transmission",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "CV Axle/Half Shaft Replacement",
        "category": "Transmission",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "U-Joint Replacement",
        "category": "Transmission",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Driveshaft Replacement",
        "category": "Transmission",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Transfer Case Replacement",
        "category": "Transmission",
        "book_time_hours": 5.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Differential Fluid Service",
        "category": "Transmission",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Rear Differential Replacement",
        "category": "Transmission",
        "book_time_hours": 4.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },

    # ======================================================================
    # EXHAUST & EMISSIONS
    # ======================================================================
    {
        "operation_name": "Catalytic Converter Replacement",
        "category": "Exhaust",
        "book_time_hours": 2.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Muffler Replacement",
        "category": "Exhaust",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Exhaust Manifold Replacement",
        "category": "Exhaust",
        "book_time_hours": 2.5,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Exhaust Pipe Section Replacement",
        "category": "Exhaust",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "EGR Valve Replacement",
        "category": "Exhaust",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "EVAP Purge Valve Replacement",
        "category": "Exhaust",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "DPF Cleaning/Replacement (diesel)",
        "category": "Exhaust",
        "book_time_hours": 2.5,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "EVAP System Smoke Test and Repair",
        "category": "Exhaust",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },

    # ======================================================================
    # STEERING
    # ======================================================================
    {
        "operation_name": "Power Steering Pump Replacement",
        "category": "Steering",
        "book_time_hours": 2.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Steering Rack and Pinion Replacement",
        "category": "Steering",
        "book_time_hours": 3.5,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Electric Power Steering Motor Replacement",
        "category": "Steering",
        "book_time_hours": 2.5,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Outer Tie Rod End Replacement",
        "category": "Steering",
        "book_time_hours": 0.8,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Inner Tie Rod End Replacement",
        "category": "Steering",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Power Steering Fluid Flush",
        "category": "Steering",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Power Steering Hose Replacement",
        "category": "Steering",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Intermediate Steering Shaft Replacement",
        "category": "Steering",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Steering Column Replacement",
        "category": "Steering",
        "book_time_hours": 3.0,
        "complexity": "complex",
        "requires_specialty_tools": True,
    },

    # ======================================================================
    # COOLING SYSTEM
    # ======================================================================
    {
        "operation_name": "Radiator Replacement",
        "category": "Cooling",
        "book_time_hours": 2.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Thermostat Replacement",
        "category": "Cooling",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Radiator Hose Replacement",
        "category": "Cooling",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Radiator Fan Motor Replacement",
        "category": "Cooling",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Radiator Fan Assembly Replacement",
        "category": "Cooling",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Coolant Flush and Fill",
        "category": "Cooling",
        "book_time_hours": 0.8,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Coolant Reservoir Replacement",
        "category": "Cooling",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Fan Clutch Replacement",
        "category": "Cooling",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Cooling System Pressure Test",
        "category": "Cooling",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },

    # ======================================================================
    # FUEL SYSTEM
    # ======================================================================
    {
        "operation_name": "Fuel Pump Assembly Replacement",
        "category": "Fuel System",
        "book_time_hours": 2.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "High-Pressure Fuel Pump Replacement (GDI)",
        "category": "Fuel System",
        "book_time_hours": 2.0,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Fuel Injector Replacement (single)",
        "category": "Fuel System",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Fuel Injector Replacement (all, 4-cyl)",
        "category": "Fuel System",
        "book_time_hours": 2.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Fuel Filter Replacement",
        "category": "Fuel System",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Throttle Body Replacement",
        "category": "Fuel System",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Intake Manifold Replacement",
        "category": "Fuel System",
        "book_time_hours": 3.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Fuel Pressure Regulator Replacement",
        "category": "Fuel System",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },

    # ======================================================================
    # DIAGNOSTICS & INSPECTION
    # ======================================================================
    {
        "operation_name": "Check Engine Light Diagnostic",
        "category": "Diagnostics",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Electrical System Diagnostic",
        "category": "Diagnostics",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Drivability Diagnostic",
        "category": "Diagnostics",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "AC System Performance Test",
        "category": "Diagnostics",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Noise/Vibration Diagnostic",
        "category": "Diagnostics",
        "book_time_hours": 1.0,
        "complexity": "moderate",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Pre-Purchase Inspection",
        "category": "Diagnostics",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Multi-Point Vehicle Inspection",
        "category": "Diagnostics",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Transmission Diagnostic",
        "category": "Diagnostics",
        "book_time_hours": 1.5,
        "complexity": "moderate",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Brake System Inspection",
        "category": "Diagnostics",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },

    # ======================================================================
    # BODY & MISCELLANEOUS
    # ======================================================================
    {
        "operation_name": "Side Mirror Replacement",
        "category": "Body",
        "book_time_hours": 0.8,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Door Handle Replacement (exterior)",
        "category": "Body",
        "book_time_hours": 0.8,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Liftgate Strut Replacement (pair)",
        "category": "Body",
        "book_time_hours": 0.3,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Windshield Washer Pump Replacement",
        "category": "Body",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Tire Rotation",
        "category": "Body",
        "book_time_hours": 0.3,
        "complexity": "simple",
        "requires_specialty_tools": False,
    },
    {
        "operation_name": "Tire Balance (4 wheels)",
        "category": "Body",
        "book_time_hours": 0.5,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },
    {
        "operation_name": "Tire Mount and Balance (4 tires)",
        "category": "Body",
        "book_time_hours": 1.0,
        "complexity": "simple",
        "requires_specialty_tools": True,
    },
]


# ---------------------------------------------------------------------------
# Convenience lookups
# ---------------------------------------------------------------------------

OPERATION_CATEGORIES: list[str] = sorted(
    {op["category"] for op in LABOR_OPERATIONS}
)
"""All unique operation categories."""

COMPLEXITY_LEVELS: list[str] = ["simple", "moderate", "complex"]
"""Valid complexity level values."""

REGIONS: list[str] = [r["region"] for r in LABOR_RATES_BY_REGION]
"""Available region names."""


def get_operations_by_category(category: str) -> list[LaborOperationEntry]:
    """Return all labor operations in a given category (case-insensitive)."""
    return [
        op
        for op in LABOR_OPERATIONS
        if op["category"].lower() == category.lower()
    ]


def get_operations_by_complexity(
    complexity: str,
) -> list[LaborOperationEntry]:
    """Return all operations of a given complexity level."""
    return [
        op
        for op in LABOR_OPERATIONS
        if op["complexity"].lower() == complexity.lower()
    ]


def get_labor_rate(
    region: str, shop_type: str = "dealer"
) -> float:
    """Return the average labor rate for a region and shop type.

    Args:
        region: Region name (case-insensitive). Falls back to Midwest
            if not found.
        shop_type: Either "dealer" or "independent".

    Returns:
        Average hourly labor rate in USD.
    """
    rate_data = REGION_RATE_MAP.get(
        region.lower(), REGION_RATE_MAP["midwest"]
    )
    if shop_type.lower() == "dealer":
        return rate_data["dealer_avg"]
    return rate_data["independent_avg"]


def estimate_labor_cost(
    operation_name: str,
    region: str = "Midwest",
    shop_type: str = "dealer",
) -> float | None:
    """Estimate labor cost for a named operation in a given region.

    Returns None if the operation is not found in the database.
    """
    matching = [
        op
        for op in LABOR_OPERATIONS
        if op["operation_name"].lower() == operation_name.lower()
    ]
    if not matching:
        return None
    rate = get_labor_rate(region, shop_type)
    return round(matching[0]["book_time_hours"] * rate, 2)
