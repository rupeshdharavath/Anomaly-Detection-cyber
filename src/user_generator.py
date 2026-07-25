import random
import pandas as pd

from faker import Faker

from src.config import DEPARTMENTS, OFFICES, NUM_USERS
from src.utils import generate_email

fake = Faker("en_IN")


def generate_users():

    users = []

    for i in range(1, NUM_USERS + 1):

        name = fake.name()

        user = {
            "user_id": f"U{i:04d}",
            "name": name,
            "email": generate_email(name),
            "department": random.choice(DEPARTMENTS),
            "office": random.choice(OFFICES)
        }

        users.append(user)

    users_df = pd.DataFrame(users)

    return users_df


if __name__ == "__main__":

    users = generate_users()

    print(users.head())

    users.to_csv("data/raw/users.csv", index=False)

    print(f"\nGenerated {len(users)} users.")