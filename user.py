import requests
import csv
import sys

token = "TKN"
headers = {"Authorization": f"token {token}"}

page_number = 1
location = "Mumbai"
followers = "50"
base_url = f"https://api.github.com/search/users?q=location:{location} followers:>{followers}&per_page=100&page={page_number}"
all_users = []

res = requests.get(base_url, headers=headers)
if res.status_code != 200:
    print("Some error encountered", res.status_code, res.json()["message"])
    sys.exit()

total_users = res.json().get("total_count", 0)
print(
    f"Total users who are in {location} and have more than {followers} followers:",
    total_users,
)


while len(all_users) < total_users:
    base_url = f"https://api.github.com/search/users?q=location:{location} followers:>{followers}&per_page=100&page={page_number}"
    response = requests.get(base_url, headers=headers)
    data = response.json()

    if response.status_code != 200:
        print("Some error encountered", response.status_code, data["message"])
        sys.exit()

    user_items = data.get("items", [])

    all_users.extend(user_items)
    print(
        f"printing length of all users after scrapping page no.: {page_number}",
        len(all_users),
    )
    print(f" {len(user_items)} users on the page no.: {page_number}")

    if len(user_items) < 100:
        print("On the last page breaking the loop")
        break

    page_number += 1

print("page no till scraped:", page_number)
print("all users length:", len(all_users))
print("Now fetching each user details....")


def get_user_details(username):
    return requests.get(
        f"https://api.github.com/users/{username}", headers=headers
    ).json()


def save_users_to_csv(users, filename="users.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "login",
                "name",
                "company",
                "location",
                "email",
                "hireable",
                "bio",
                "public_repos",
                "followers",
                "following",
                "created_at",
            ],
        )
        writer.writeheader()
        for user in users:
            writer.writerow(user)


def clean_company_name(company):
    if company:
        company = company.strip().lstrip("@").upper()
    return company


counter = 1
user_data = []
for user in all_users:
    details = get_user_details(user["login"])
    print(f"Getting details {counter} for the user:", user["login"])

    user_data.append(
        {
            "login": details["login"],
            "name": details.get("name", ""),
            "company": clean_company_name(details.get("company", "") or ""),
            "location": details.get("location", ""),
            "email": details.get("email", ""),
            "hireable": "true" if details.get("hireable") is True else "false",
            "bio": details.get("bio", ""),
            "public_repos": details.get("public_repos", 0),
            "followers": details.get("followers", 0),
            "following": details.get("following", 0),
            "created_at": details.get("created_at", ""),
        }
    )
    counter += 1


save_users_to_csv(user_data)
print("users.csv file created!")
