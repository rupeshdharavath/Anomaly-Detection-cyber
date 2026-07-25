# ==========================
# Project Configuration
# ==========================

NUM_USERS = 500
NUM_DEVICES = 700
NUM_DAYS = 90
ATTACK_PERCENTAGE = 2

# ==========================
# Office Locations
# ==========================

OFFICES = [
    "Hyderabad",
    "Bangalore",
    "Chennai",
    "Pune",
    "Mumbai"
]

# ==========================
# Departments
# ==========================

DEPARTMENTS = [
    "HR",
    "Finance",
    "Engineering",
    "IT",
    "Sales",
    "Marketing",
    "Support"
]

# ==========================
# Device Types
# ==========================

DEVICE_TYPES = [
    "Laptop",
    "Desktop",
    "Workstation"
]

# ==========================
# Operating Systems
# ==========================

OPERATING_SYSTEMS = [
    "Windows 11",
    "Windows 10",
    "Ubuntu 22.04",
    "macOS Sonoma"
]

# ==========================
# Browsers
# ==========================

BROWSERS = [
    "Chrome",
    "Edge",
    "Firefox",
    "Brave"
]

# ==========================
# Authentication Methods
# ==========================

AUTH_METHODS = [
    "Password",
    "MFA",
    "Biometric"
]

# ==========================
# Resources
# ==========================

RESOURCE_LIST = [
    "Email",
    "GitHub",
    "Jira",
    "Confluence",
    "HR Portal",
    "Finance DB",
    "VPN",
    "CRM",
    "Internal Server",
    "Database"
]

# ==========================
# Entity Types
# ==========================

ENTITY_TYPES = [
    "user",
    "service_account",
    "edge_device"
]

# ==========================
# Geo Locations
# ==========================

GEO_LOCATIONS = [
    "Hyderabad",
    "Bangalore",
    "Chennai",
    "Pune",
    "Mumbai"
]

# ==========================
# Command List
# ==========================

COMMANDS = [
    "login",
    "authenticate",
    "open_vpn",
    "query_database",
    "read_file",
    "write_file",
    "download_file",
    "upload_file",
    "execute_script",
    "logout"
]

# ==========================
# Attack Types
# ==========================

ATTACK_TYPES = [
    "Normal",
    "Brute Force",
    "Impossible Travel",
    "Credential Stuffing",
    "Device Spoofing",
    "Lateral Movement"
]

# ==========================
# Sequence and cold-start settings
# ==========================

SEQUENCE_WINDOW_SIZE = 5
COLD_START_MIN_EVENTS = 3