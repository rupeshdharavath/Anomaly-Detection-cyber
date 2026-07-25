import random
import pandas as pd
from datetime import timedelta

from src.utils import (
    generate_ip,
    generate_logout_time,
    generate_resource,
    generate_command_sequence,
    start_date
)

from src.config import NUM_DAYS


def generate_events(profiles_df):

    events = []

    current_date = start_date()

    for day in range(NUM_DAYS):

        for _, profile in profiles_df.iterrows():

            # Login hour inside user's normal window
            login_hour = random.randint(
                profile["normal_login_start"],
                profile["normal_login_end"]
            )

            login_minute = random.randint(0, 59)

            login_time = current_date.replace(
                hour=login_hour,
                minute=login_minute,
                second=random.randint(0, 59)
            )

            # Session duration close to user's normal duration
            session_duration = max(
                15,
                int(random.gauss(profile["normal_session_duration"], 15))
            )

            logout_time = generate_logout_time(
                login_time,
                session_duration
            )

            # Failed logins are usually normal
            failed = profile["normal_failed_login_attempts"]

            if random.random() < 0.15:
                failed += 1

            # Mostly access normal resources
            normal_resources = profile["normal_resources"].split(",")

            if random.random() < 0.85:
                resource = random.choice(normal_resources)
            else:
                resource = generate_resource()

            event = {

                "entity_id": profile["entity_id"],

                "entity_type": profile["entity_type"],

                "timestamp": login_time,

                "logout_time": logout_time,

                "source_ip": generate_ip(),

                "geo_location": profile["geo_location"],

                "resource_accessed": resource,

                "auth_method": profile["auth_method"],

                "session_duration": session_duration,

                "command_sequence": generate_command_sequence(),

                "device_fingerprint": profile["device_fingerprint"],

                "failed_login_attempts": failed,

                "label": "Normal",

                "attack_type": None

            }

            events.append(event)

        current_date += timedelta(days=1)

    return pd.DataFrame(events)


if __name__ == "__main__":

    profiles = pd.read_csv("data/raw/user_profiles.csv")

    events = generate_events(profiles)

    events.to_csv(
        "data/raw/normal_events.csv",
        index=False
    )

    print(events.head())

    print(f"\nGenerated {len(events)} normal events.")