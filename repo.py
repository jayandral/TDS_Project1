import requests
import csv

token1 = "TKN"
repo_url = "https://api.github.com/users/{}/repos?per_page=100&page={}&sort=pushed"


def save_repos_to_csv(repos, filename="repositories.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "login",
                "full_name",
                "created_at",
                "stargazers_count",
                "watchers_count",
                "language",
                "has_projects",
                "has_wiki",
                "license_name",
            ],
        )
        writer.writeheader()
        for repo in repos:
            writer.writerow(repo)


repo_data = []
limit = 1
flag = False

with open("users.csv", mode="r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for user in reader:
        temp = []
        max_repos = 500
        pageno = 1

        if flag:
            break

        while len(temp) < max_repos:
            response = requests.get(
                repo_url.format(user["login"], pageno),
                headers={"Authorization": f"token {token1}"},
            )
            limit += 1

            if response.status_code == 403:
                flag = True
                break

            if response.status_code != 200:
                print("Error:", response.status_code)
                break

            repos = response.json()
            temp.extend(repos)

            if len(repos) < 100 or len(temp) >= max_repos:
                break

            print(f"Currently on page {pageno} for the user: {user['login']}")
            pageno += 1

        if not flag:
            for repo in temp:
                repo_data.append(
                    {
                        "login": user["login"],
                        "full_name": repo["full_name"],
                        "created_at": repo["created_at"],
                        "stargazers_count": repo["stargazers_count"],
                        "watchers_count": repo["watchers_count"],
                        "language": repo.get("language", ""),
                        "has_projects": ("true" if repo["has_projects"] else "false"),
                        "has_wiki": ("true" if repo["has_wiki"] else "false"),
                        "license_name": (
                            repo.get("license", {}).get("key", "")
                            if repo.get("license")
                            else ""
                        ),
                    }
                )

            print(
                "Total repo for the user:",
                user["login"],
                "is:",
                user["public_repos"],
                "out of which got scraped is:",
                len(temp),
            )


if not flag:
    save_repos_to_csv(repo_data)
    print("repositories.csv file created!")
