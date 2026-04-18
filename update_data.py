"""
Generate updated KFUPM parking data files based on official parking statistics document.
Translates all Arabic content and creates comprehensive English-first data.
"""
import pandas as pd

# ===========================================
# PARKING LOTS — Based on official KFUPM document
# ===========================================
# The document shows:
# - المواقف المغطاة (Covered Parking): Lots 1-11
# - المواقف المكشوفة (Open Parking): Lots 15-77
# - Named special lots

parking_lots = [
    # --- Covered Parking (المواقف المغطاة) ---
    {"lot_id": "C01", "lot_name": "Covered Lot 1",              "lot_name_ar": "موقف مغطى ١",                  "zone": "Academic Core",     "type": "covered", "category": "student",  "capacity": 384, "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "07:00-17:00", "near_buildings": "22,24,40",       "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "C02", "lot_name": "Covered Lot 2",              "lot_name_ar": "موقف مغطى ٢",                  "zone": "Academic Core",     "type": "covered", "category": "student",  "capacity": 34,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "07:00-17:00", "near_buildings": "22,24",          "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "C03", "lot_name": "Covered Lot 3",              "lot_name_ar": "موقف مغطى ٣",                  "zone": "Academic Core",     "type": "covered", "category": "student",  "capacity": 271, "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "07:00-17:00", "near_buildings": "24,40",          "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "C04", "lot_name": "Covered Lot 4",              "lot_name_ar": "موقف مغطى ٤",                  "zone": "Administrative",    "type": "covered", "category": "staff",    "capacity": 55,  "allowed_permits": "staff,faculty",  "gender_access": "all",    "allowed_residency": "all",          "time_rules": "06:00-18:00", "near_buildings": "9,10,11",        "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "C05", "lot_name": "Covered Lot 5",              "lot_name_ar": "موقف مغطى ٥",                  "zone": "Academic Core",     "type": "covered", "category": "faculty",  "capacity": 271, "allowed_permits": "faculty,staff",  "gender_access": "all",    "allowed_residency": "all",          "time_rules": "06:00-18:00", "near_buildings": "24,40,54",       "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "C06", "lot_name": "Covered Lot 6",              "lot_name_ar": "موقف مغطى ٦",                  "zone": "Administrative",    "type": "covered", "category": "staff",    "capacity": 68,  "allowed_permits": "staff,faculty",  "gender_access": "all",    "allowed_residency": "all",          "time_rules": "06:00-18:00", "near_buildings": "9,10,11",        "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "C07", "lot_name": "Covered Lot 7",              "lot_name_ar": "موقف مغطى ٧",                  "zone": "Student Services",  "type": "covered", "category": "student",  "capacity": 10,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "65,66",          "nearest_gate": 5, "restricted": "false"},
    {"lot_id": "C08", "lot_name": "Covered Lot 8",              "lot_name_ar": "موقف مغطى ٨",                  "zone": "Academic Core",     "type": "covered", "category": "student",  "capacity": 575, "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "22,24,40,54",    "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "C09", "lot_name": "Covered Lot 9",              "lot_name_ar": "موقف مغطى ٩",                  "zone": "Medical",           "type": "covered", "category": "visitor",  "capacity": 71,  "allowed_permits": "visitor,staff",  "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "22",             "nearest_gate": 2, "restricted": "false"},
    {"lot_id": "C10", "lot_name": "Covered Lot 10",             "lot_name_ar": "موقف مغطى ١٠",                 "zone": "Academic Core",     "type": "covered", "category": "student",  "capacity": 1008,"allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "non_resident", "time_rules": "07:00-17:00", "near_buildings": "24,40,54",       "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "C11", "lot_name": "Covered Lot 11",             "lot_name_ar": "موقف مغطى ١١",                 "zone": "Residential",       "type": "covered", "category": "resident", "capacity": 74,  "allowed_permits": "resident",       "gender_access": "all",    "allowed_residency": "resident",     "time_rules": "all",         "near_buildings": "65,66,68",       "nearest_gate": 3, "restricted": "false"},

    # --- Open/Uncovered Parking (المواقف المكشوفة) ---
    {"lot_id": "O15", "lot_name": "Open Lot 15",                "lot_name_ar": "موقف مكشوف ١٥",                "zone": "Academic Core",     "type": "open",    "category": "student",  "capacity": 221, "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "non_resident", "time_rules": "07:00-17:00", "near_buildings": "22,24",          "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "O16", "lot_name": "Open Lot 16",                "lot_name_ar": "موقف مكشوف ١٦",                "zone": "Academic Core",     "type": "open",    "category": "student",  "capacity": 26,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "non_resident", "time_rules": "07:00-17:00", "near_buildings": "22,24",          "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "O17", "lot_name": "Open Lot 17",                "lot_name_ar": "موقف مكشوف ١٧",                "zone": "Outer Zone",        "type": "open",    "category": "student",  "capacity": 150, "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "54,65",          "nearest_gate": 2, "restricted": "false"},
    {"lot_id": "O18", "lot_name": "Open Lot 18",                "lot_name_ar": "موقف مكشوف ١٨",                "zone": "Outer Zone",        "type": "open",    "category": "student",  "capacity": 51,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "54,66",          "nearest_gate": 2, "restricted": "false"},
    {"lot_id": "O19", "lot_name": "Open Lot 19",                "lot_name_ar": "موقف مكشوف ١٩",                "zone": "Academic Core",     "type": "open",    "category": "student",  "capacity": 33,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "07:00-17:00", "near_buildings": "40",             "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "O20", "lot_name": "Open Lot 20",                "lot_name_ar": "موقف مكشوف ٢٠",                "zone": "Residential",       "type": "open",    "category": "resident", "capacity": 268, "allowed_permits": "resident",       "gender_access": "all",    "allowed_residency": "resident",     "time_rules": "all",         "near_buildings": "65,66,68",       "nearest_gate": 3, "restricted": "false"},
    {"lot_id": "O21", "lot_name": "Open Lot 21",                "lot_name_ar": "موقف مكشوف ٢١",                "zone": "Residential",       "type": "open",    "category": "resident", "capacity": 118, "allowed_permits": "resident",       "gender_access": "all",    "allowed_residency": "resident",     "time_rules": "all",         "near_buildings": "65,66",          "nearest_gate": 3, "restricted": "false"},
    {"lot_id": "O22", "lot_name": "Open Lot 22",                "lot_name_ar": "موقف مكشوف ٢٢",                "zone": "Outer Zone",        "type": "open",    "category": "student",  "capacity": 14,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "38",             "nearest_gate": 8, "restricted": "false"},
    {"lot_id": "O23", "lot_name": "Open Lot 23",                "lot_name_ar": "موقف مكشوف ٢٣",                "zone": "Administrative",    "type": "open",    "category": "staff",    "capacity": 26,  "allowed_permits": "staff,faculty",  "gender_access": "all",    "allowed_residency": "all",          "time_rules": "06:00-18:00", "near_buildings": "9,10,11",        "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "O24", "lot_name": "Open Lot 24",                "lot_name_ar": "موقف مكشوف ٢٤",                "zone": "Administrative",    "type": "open",    "category": "staff",    "capacity": 75,  "allowed_permits": "staff,faculty",  "gender_access": "all",    "allowed_residency": "all",          "time_rules": "06:00-18:00", "near_buildings": "9,10,11",        "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "O25", "lot_name": "Open Lot 25",                "lot_name_ar": "موقف مكشوف ٢٥",                "zone": "Academic Core",     "type": "open",    "category": "student",  "capacity": 39,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "07:00-17:00", "near_buildings": "24,40",          "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "O26", "lot_name": "Open Lot 26",                "lot_name_ar": "موقف مكشوف ٢٦",                "zone": "Sports",            "type": "open",    "category": "student",  "capacity": 97,  "allowed_permits": "student,visitor","gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "20,27",          "nearest_gate": 4, "restricted": "false"},
    {"lot_id": "O27", "lot_name": "Open Lot 27",                "lot_name_ar": "موقف مكشوف ٢٧",                "zone": "Student Services",  "type": "open",    "category": "student",  "capacity": 17,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "65,66",          "nearest_gate": 5, "restricted": "false"},
    {"lot_id": "O28", "lot_name": "Open Lot 28",                "lot_name_ar": "موقف مكشوف ٢٨",                "zone": "Academic Core",     "type": "open",    "category": "student",  "capacity": 51,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "07:00-17:00", "near_buildings": "24,40",          "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "O29", "lot_name": "Open Lot 29",                "lot_name_ar": "موقف مكشوف ٢٩",                "zone": "Medical",           "type": "open",    "category": "visitor",  "capacity": 172, "allowed_permits": "visitor,staff",  "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "22",             "nearest_gate": 2, "restricted": "false"},
    {"lot_id": "O30", "lot_name": "Open Lot 30",                "lot_name_ar": "موقف مكشوف ٣٠",                "zone": "Outer Zone",        "type": "open",    "category": "student",  "capacity": 54,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "38,54",          "nearest_gate": 2, "restricted": "false"},
    {"lot_id": "O31", "lot_name": "Open Lot 31",                "lot_name_ar": "موقف مكشوف ٣١",                "zone": "Academic Core",     "type": "open",    "category": "student",  "capacity": 220, "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "07:00-17:00", "near_buildings": "22,24,40",       "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "O32", "lot_name": "Open Lot 32",                "lot_name_ar": "موقف مكشوف ٣٢",                "zone": "Academic Core",     "type": "open",    "category": "student",  "capacity": 177, "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "07:00-17:00", "near_buildings": "22,24,40",       "nearest_gate": 1, "restricted": "false"},
    {"lot_id": "O33", "lot_name": "Open Lot 33",                "lot_name_ar": "موقف مكشوف ٣٣",                "zone": "Outer Zone",        "type": "open",    "category": "student",  "capacity": 53,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "54",             "nearest_gate": 2, "restricted": "false"},

    # --- Named Special Lots ---
    {"lot_id": "S01", "lot_name": "Student Complex Parking",     "lot_name_ar": "مواقف مجمع الطلاب",            "zone": "Student Services",  "type": "open",    "category": "student",  "capacity": 53,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "65,66",          "nearest_gate": 5, "restricted": "false"},
    {"lot_id": "S02", "lot_name": "Medical Center Parking",      "lot_name_ar": "مواقف المركز الطبي",           "zone": "Medical",           "type": "open",    "category": "visitor",  "capacity": 78,  "allowed_permits": "visitor,staff",  "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "22",             "nearest_gate": 2, "restricted": "false"},
    {"lot_id": "S03", "lot_name": "Behind Sports Stadium",       "lot_name_ar": "المواقف خلف الاستاد الرياضي",  "zone": "Sports",            "type": "open",    "category": "student",  "capacity": 120, "allowed_permits": "student,visitor","gender_access": "all",    "allowed_residency": "all",          "time_rules": "08:00-22:00", "near_buildings": "27",             "nearest_gate": 4, "restricted": "false"},
    {"lot_id": "S04", "lot_name": "Family Complex (Square)",     "lot_name_ar": "مجمع العوائل (سكوير)",         "zone": "Residential",       "type": "open",    "category": "resident", "capacity": 9,   "allowed_permits": "resident",       "gender_access": "all",    "allowed_residency": "resident",     "time_rules": "all",         "near_buildings": "68",             "nearest_gate": 3, "restricted": "false"},
    {"lot_id": "S05", "lot_name": "Emergency / Clinic Parking",  "lot_name_ar": "مواقف الطوارئ / العيادة",      "zone": "Medical",           "type": "open",    "category": "visitor",  "capacity": 45,  "allowed_permits": "visitor,staff",  "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "22",             "nearest_gate": 2, "restricted": "false"},
    {"lot_id": "S06", "lot_name": "Dhahran Mosque Parking",      "lot_name_ar": "مواقف جامع الظهران",           "zone": "Outer Zone",        "type": "open",    "category": "student",  "capacity": 180, "allowed_permits": "student,staff",  "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "",               "nearest_gate": 8, "restricted": "false"},
    {"lot_id": "S07", "lot_name": "Grand Mosque Parking",        "lot_name_ar": "مواقف مسجد الكبير",            "zone": "Outer Zone",        "type": "open",    "category": "student",  "capacity": 95,  "allowed_permits": "student,staff",  "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "",               "nearest_gate": 8, "restricted": "false"},
    {"lot_id": "S08", "lot_name": "Community Center Parking",    "lot_name_ar": "مواقف مركز المجتمع",           "zone": "Student Services",  "type": "open",    "category": "student",  "capacity": 43,  "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "66",             "nearest_gate": 5, "restricted": "false"},
    {"lot_id": "S09", "lot_name": "Faculty Singles Housing",     "lot_name_ar": "مواقف سكن الأساتذة (العزاب)", "zone": "Residential",       "type": "open",    "category": "faculty",  "capacity": 110, "allowed_permits": "faculty,staff",  "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "",               "nearest_gate": 3, "restricted": "false"},
    {"lot_id": "S10", "lot_name": "Wadi Dhahran Parking",        "lot_name_ar": "مواقف وادي الظهران",           "zone": "Outer Zone",        "type": "open",    "category": "student",  "capacity": 200, "allowed_permits": "student",        "gender_access": "all",    "allowed_residency": "all",          "time_rules": "all",         "near_buildings": "",               "nearest_gate": 8, "restricted": "false"},
]

parking_df = pd.DataFrame(parking_lots)
parking_df.to_excel("data/parking_lots.xlsx", index=False)
print(f"Created parking_lots.xlsx with {len(parking_df)} lots")
print(f"Total capacity: {parking_df['capacity'].sum()}")

# ===========================================
# MOCK LIVE OCCUPANCY — Generate realistic data
# ===========================================
import random
random.seed(42)

occupancy_rows = []
for _, lot in parking_df.iterrows():
    cap = lot["capacity"]
    cat = lot["category"]

    # Different fill rates for different categories
    if cat == "student":
        fill_rate = random.uniform(0.35, 0.95)  # students vary a lot
    elif cat == "staff" or cat == "faculty":
        fill_rate = random.uniform(0.55, 0.85)  # more consistent
    elif cat == "visitor":
        fill_rate = random.uniform(0.20, 0.70)  # visitors lighter
    elif cat == "resident":
        fill_rate = random.uniform(0.70, 0.95)  # residents high
    else:
        fill_rate = random.uniform(0.40, 0.80)

    occupied = min(int(cap * fill_rate), cap)
    occupancy_rows.append({"lot_id": lot["lot_id"], "occupied": occupied})

occ_df = pd.DataFrame(occupancy_rows)
occ_df.to_excel("data/mock_live_occupancy.xlsx", index=False)
print(f"Created mock_live_occupancy.xlsx with {len(occ_df)} entries")

# ===========================================
# BUILDINGS — Already in English, keep as-is
# ===========================================
print("Buildings data already has English translations — no changes needed.")

# ===========================================
# GATES — Already in English, keep as-is
# ===========================================
print("Gates data already has English translations — no changes needed.")

print("\nDone! All parking lot names are now in English with Arabic translations preserved.")
