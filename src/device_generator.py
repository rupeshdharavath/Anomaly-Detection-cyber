import random
import pandas as pd

from src.config import NUM_DEVICES, DEVICE_TYPES, OPERATING_SYSTEMS, BROWSERS
from src.utils import generate_mac, generate_device_fingerprint


def generate_devices():

    devices = []

    for i in range(1, NUM_DEVICES + 1):

        os_name = random.choice(OPERATING_SYSTEMS)
        browser = random.choice(BROWSERS)

        devices.append({
            "device_id": f"D{i:04d}",
            "device_type": random.choice(DEVICE_TYPES),
            "operating_system": os_name,
            "browser": browser,
            "mac_address": generate_mac(),
            "device_fingerprint": generate_device_fingerprint(os_name, browser)
        })

    return pd.DataFrame(devices)


if __name__ == "__main__":

    devices_df = generate_devices()

    print(devices_df.head())

    devices_df.to_csv("data/raw/devices.csv", index=False)

    print(f"\nTotal Devices Generated: {len(devices_df)}")