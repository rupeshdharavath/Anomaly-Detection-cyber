import random
import uuid
from datetime import datetime, timedelta
from src.config import RESOURCE_LIST, COMMANDS


from faker import Faker

fake = Faker("en_IN")

def generate_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

def generate_mac():
    return ":".join(
        "{:02x}".format(random.randint(0, 255))
        for _ in range(6)
    )

def generate_device_fingerprint(os_name, browser):
    return f"{os_name}_{browser}_{uuid.uuid4().hex[:8]}"

def generate_email(name):
    username = (
        name.lower()
        .replace(" ", ".")
        .replace("'", "")
    )
    return f"{username}@company.com"

def random_login_time(start_date, day):
    login_date = start_date + timedelta(days=day)

    login_time = login_date.replace(
        hour=random.randint(8, 9),
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=0
    )

    return login_time

def generate_session_duration():
    return random.randint(120, 540)

def generate_logout_time(login_time, duration):
    return login_time + timedelta(minutes=duration)

def failed_login_attempts():
    return random.randint(0, 2)

def random_id():
    return str(uuid.uuid4())

def random_name():
    return fake.name()

def start_date():
    return datetime(2026, 1, 1)


def generate_resource():
    return random.choice(RESOURCE_LIST)


def generate_command_sequence():

    n = random.randint(3, 8)

    sequence = random.sample(COMMANDS, n)

    if sequence[-1] != "logout":
        sequence.append("logout")

    return " -> ".join(sequence)