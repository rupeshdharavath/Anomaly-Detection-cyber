import os
import pandas as pd

from src.user_generator import generate_users
from src.device_generator import generate_devices
from src.profile_generator import generate_profiles
from src.event_generator import generate_events
from src.attack_generator import inject_attacks

def generate_dataset():

    print("=" * 50)

    print("Generating Users...")
    users = generate_users()

    print("Generating Devices...")
    devices = generate_devices()

    print("Generating User Profiles...")
    profiles = generate_profiles(users, devices)

    print("Generating Normal Events...")
    normal_events = generate_events(profiles)

    print("Injecting Cyber Attacks...")
    cyber_logs = inject_attacks(
    normal_events,
    profiles,
    devices
)

    # -----------------------------
    # Save intermediate datasets
    # -----------------------------
    os.makedirs("data/raw", exist_ok=True)

    users.to_csv("data/raw/users.csv", index=False)
    devices.to_csv("data/raw/devices.csv", index=False)
    profiles.to_csv("data/raw/user_profiles.csv", index=False)
    normal_events.to_csv("data/raw/normal_events.csv", index=False)
    cyber_logs.to_csv("data/raw/cyber_logs.csv", index=False)

        # ==========================================================
    # Merge Everything
    # ==========================================================

    # Rename profile columns to preserve baseline behaviour
    profiles_merge = profiles.rename(columns={
        "entity_type": "normal_entity_type",
        "department": "normal_department",
        "geo_location": "normal_geo_location",
        "auth_method": "normal_auth_method",
        "device_fingerprint": "normal_device_fingerprint"
    })

    # Merge Users
    final_df = cyber_logs.merge(
        users,
        left_on="entity_id",
        right_on="user_id",
        how="left"
    )

    # Merge Devices
    final_df = final_df.merge(
        devices,
        on="device_fingerprint",
        how="left"
    )

    # Merge User Profiles
    final_df = final_df.merge(
        profiles_merge,
        on="entity_id",
        how="left"
    )

    # Remove duplicate columns
    final_df.drop(
        columns=["user_id"],
        inplace=True,
        errors="ignore"
    )

    # ==========================================================
    # Derived Security Features
    # ==========================================================

    # Convert timestamp to datetime
    final_df["timestamp"] = pd.to_datetime(final_df["timestamp"])

    # Extract login hour
    final_df["login_hour"] = final_df["timestamp"].dt.hour

    # Location changed
    final_df["location_changed"] = (
        final_df["geo_location"] != final_df["normal_geo_location"]
    )

    # Device changed
    final_df["device_changed"] = (
        final_df["device_fingerprint"] != final_df["normal_device_fingerprint"]
    )

    # Authentication method changed
    final_df["auth_changed"] = (
        final_df["auth_method"] != final_df["normal_auth_method"]
    )

    # Login outside normal working hours
    final_df["login_time_changed"] = (
        (final_df["login_hour"] < final_df["normal_login_start"]) |
        (final_df["login_hour"] > final_df["normal_login_end"])
    )

    # Session duration longer than expected
    final_df["long_session"] = (
        final_df["session_duration"] >
        (final_df["normal_session_duration"] * 1.5)
    )

    # Failed login attempts higher than normal
    final_df["high_failed_login"] = (
        final_df["failed_login_attempts"] >
        final_df["normal_failed_login_attempts"]
    )

    # Resource accessed is different from user's normal resources
    final_df["resource_changed"] = final_df.apply(
        lambda row: row["resource_accessed"] not in [
            r.strip() for r in str(row["normal_resources"]).split(",")
        ],
        axis=1
    )

    final_df["risk_score"] = (
    final_df["location_changed"].astype(int)
    + final_df["device_changed"].astype(int)
    + final_df["auth_changed"].astype(int)
    + final_df["login_time_changed"].astype(int)
    + final_df["long_session"].astype(int)
    + final_df["high_failed_login"].astype(int)
    + final_df["resource_changed"].astype(int)
)

    # Save final dataset
    final_df.to_csv(
    "data/raw/cybersecurity_dataset.csv",
    index=False
    )

    print("\nAll files generated successfully!")

    print("\nDataset Summary")
    print("-" * 35)
    print(f"Users            : {len(users)}")
    print(f"Devices          : {len(devices)}")
    print(f"Profiles         : {len(profiles)}")
    print(f"Normal Events    : {len(normal_events)}")
    print(f"Cyber Logs       : {len(cyber_logs)}")
    print(f"Merged Dataset   : {len(final_df)}")

    print("\nAttack Distribution")
    print(cyber_logs["attack_type"].value_counts())

    print("\nFinal Dataset Shape")
    print(final_df.shape)

    print("\nSaved:")
    print("data/raw/users.csv")
    print("data/raw/devices.csv")
    print("data/raw/user_profiles.csv")
    print("data/raw/normal_events.csv")
    print("data/raw/cyber_logs.csv")
    print("data/raw/cybersecurity_dataset.csv")

    return final_df


if __name__ == "__main__":

    generate_dataset()