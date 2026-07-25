import random
import pandas as pd

from src.config import (
    AUTH_METHODS,
    RESOURCE_LIST,
    ENTITY_TYPES
)


def generate_profiles(users_df, devices_df):

    profiles = []

    # Assign one device to each user
    selected_devices = devices_df.sample(
        n=len(users_df),
        replace=False,
        random_state=42
    ).reset_index(drop=True)

    for i in range(len(users_df)):

        user = users_df.iloc[i]
        device = selected_devices.iloc[i]

        # Normal login window
        login_start = random.randint(8, 10)
        login_end = login_start + 2

        # Normal session duration (minutes)
        normal_session = random.randint(60, 180)

        # Usually users fail 0 or 1 login
        normal_failed = random.choice([0, 0, 0, 1])

        # Normal resources accessed
        normal_resources = random.sample(
            RESOURCE_LIST,
            random.randint(2, 4)
        )

        profile = {

            "entity_id": user["user_id"],

            "entity_type": random.choices(
                ENTITY_TYPES,
                weights=[90, 5, 5],
                k=1
            )[0],

            "department": user["department"],

            "geo_location": user["office"],

            "device_id": device["device_id"],

            "device_fingerprint": device["device_fingerprint"],

            "auth_method": random.choice(AUTH_METHODS),

            "normal_login_start": login_start,

            "normal_login_end": login_end,

            "normal_session_duration": normal_session,

            "normal_failed_login_attempts": normal_failed,

            "normal_resources": ",".join(normal_resources)

        }

        profiles.append(profile)

    return pd.DataFrame(profiles)


if __name__ == "__main__":

    users = pd.read_csv("data/raw/users.csv")
    devices = pd.read_csv("data/raw/devices.csv")

    profiles = generate_profiles(users, devices)

    profiles.to_csv(
        "data/raw/user_profiles.csv",
        index=False
    )

    print(profiles.head())

    print(f"\nGenerated {len(profiles)} user profiles.")