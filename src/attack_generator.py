import random
import pandas as pd

from src.utils import generate_ip
from src.config import GEO_LOCATIONS, ATTACK_PERCENTAGE, RESOURCE_LIST


def inject_attacks(events_df, profiles_df, devices_df):

    events = events_df.copy()

    num_attacks = int(len(events) * ATTACK_PERCENTAGE / 100)

    attack_indices = random.sample(range(len(events)), num_attacks)

    # Original "loud" attack types + new stealthy variants
    attack_types = [
        "Brute Force",
        "Impossible Travel",
        "Credential Stuffing",
        "Device Spoofing",
        "Lateral Movement",
        "Low and Slow Brute Force",
        "Insider Threat",
        "Slow Credential Stuffing",
    ]
    weights = [
        0.06, 0.06, 0.06, 0.06, 0.06,   # 5 loud types → 30% combined
        0.233, 0.233, 0.234              # 3 stealthy types → 70% combined
    ]

    for idx in attack_indices:

        row = events.loc[idx]

        profile = profiles_df[
            profiles_df["entity_id"] == row["entity_id"]
        ].iloc[0]

        attack = random.choices(attack_types, weights=weights, k=1)[0]

        events.at[idx, "label"] = "Attack"
        events.at[idx, "attack_type"] = attack

        # ----------------------------
        # Brute Force (loud)
        # ----------------------------
        if attack == "Brute Force":

            ts = pd.to_datetime(events.at[idx, "timestamp"])

            ts = ts.replace(
                hour=random.randint(1, 4),
                minute=random.randint(0, 59)
            )

            events.at[idx, "timestamp"] = ts
            events.at[idx, "failed_login_attempts"] = random.randint(20, 50)
            events.at[idx, "auth_method"] = "Password"
            events.at[idx, "command_sequence"] = (
                "login -> login -> login -> login -> login"
            )

        # ----------------------------
        # Impossible Travel (loud)
        # ----------------------------
        elif attack == "Impossible Travel":

            new_location = random.choice(
                [
                    g for g in GEO_LOCATIONS
                    if g != profile["geo_location"]
                ]
            )

            events.at[idx, "geo_location"] = new_location
            events.at[idx, "source_ip"] = generate_ip()

        # ----------------------------
        # Credential Stuffing (loud)
        # ----------------------------
        elif attack == "Credential Stuffing":

            ts = pd.to_datetime(events.at[idx, "timestamp"])

            ts = ts.replace(
                hour=random.randint(0, 5),
                minute=random.randint(0, 59)
            )

            events.at[idx, "timestamp"] = ts
            events.at[idx, "failed_login_attempts"] = random.randint(15, 40)
            events.at[idx, "source_ip"] = generate_ip()
            events.at[idx, "auth_method"] = "Password"

        # ----------------------------
        # Device Spoofing (loud)
        # ----------------------------
        elif attack == "Device Spoofing":
            available_devices = devices_df[
                devices_df["device_fingerprint"] != profile["device_fingerprint"]
            ]

            spoof_device = available_devices.sample(1).iloc[0]

            events.at[idx, "device_fingerprint"] = spoof_device["device_fingerprint"]
            events.at[idx, "source_ip"] = generate_ip()

        # ----------------------------
        # Lateral Movement (loud)
        # ----------------------------
        elif attack == "Lateral Movement":

            normal_resources = profile["normal_resources"].split(",")

            abnormal_resources = [
                r for r in RESOURCE_LIST
                if r not in normal_resources
            ]

            if abnormal_resources:
                events.at[idx, "resource_accessed"] = random.choice(
                    abnormal_resources
                )

            events.at[idx, "command_sequence"] = (
                "login -> open_vpn -> "
                "query_database -> "
                "read_file -> "
                "write_file -> logout"
            )

            events.at[idx, "session_duration"] += random.randint(60, 180)

        # ----------------------------
        # Low and Slow Brute Force (stealthy)
        # Stays under typical high_failed_login thresholds,
        # keeps timestamp within normal login hours.
        # ----------------------------
        elif attack == "Low and Slow Brute Force":

            events.at[idx, "failed_login_attempts"] = random.randint(4, 8)
            events.at[idx, "auth_method"] = "Password"
            events.at[idx, "command_sequence"] = (
                "login -> login -> login"
            )
            # timestamp intentionally left within the entity's normal hours

        # ----------------------------
        # Insider Threat (stealthy)
        # Normal device, normal location, normal failed logins.
        # Only signal: access to a single unusual resource.
        # ----------------------------
        elif attack == "Insider Threat":

            normal_resources = profile["normal_resources"].split(",")

            abnormal_resources = [
                r for r in RESOURCE_LIST
                if r not in normal_resources
            ]

            if abnormal_resources:
                events.at[idx, "resource_accessed"] = random.choice(
                    abnormal_resources
                )
            # device_fingerprint, geo_location, failed_login_attempts
            # all left untouched — this is the point

        # ----------------------------
        # Slow Credential Stuffing (stealthy)
        # Moderate failed attempts, no location/device change,
        # timestamp kept close to normal hours.
        # ----------------------------
        elif attack == "Slow Credential Stuffing":

            events.at[idx, "failed_login_attempts"] = random.randint(6, 12)
            events.at[idx, "auth_method"] = "Password"
            # source_ip, geo_location, device_fingerprint left as-is

    return events


if __name__ == "__main__":

    events = pd.read_csv("data/raw/normal_events.csv")
    profiles = pd.read_csv("data/raw/user_profiles.csv")
    devices = pd.read_csv("data/raw/devices.csv")

    cyber_logs = inject_attacks(events, profiles, devices)

    cyber_logs.to_csv(
        "data/raw/cyber_logs.csv",
        index=False
    )

    print(cyber_logs.head())
    print(cyber_logs["attack_type"].value_counts(dropna=False))