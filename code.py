import requests
import csv


GITHUB_TOKEN = "TOKEN"  
BASE_URL = "https://api.github.com"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


def fetch_users(location="London", min_followers=500):
    users = []
    url = f"{BASE_URL}/search/users?q=location:{location}+followers:>{min_followers}"
    page = 1
    while url:
        response = requests.get(url, headers=HEADERS, params={"page": page, "per_page": 100})
        response_data = response.json()
        if response.status_code != 200:
            print(f"Error fetching users: {response_data.get('message', 'Unknown error')}")
            break
        users.extend(response_data.get("items", []))
        if "next" in response.links:
            page += 1
        else:
            break
    return users


def clean_company_name(name):
    if not name:
        return ""
    name = name.strip().lstrip("@").upper()
    return name


def fetch_user_details(user):
    user_details = requests.get(f"{BASE_URL}/users/{user['login']}", headers=HEADERS).json()
    user_info = {
        "login": user_details.get("login"),
        "name": user_details.get("name", ""),
        "company": clean_company_name(user_details.get("company", "")),
        "location": user_details.get("location", ""),
        "email": user_details.get("email", ""),
        "hireable": user_details.get("hireable", ""),
        "bio": user_details.get("bio", ""),
        "public_repos": user_details.get("public_repos", 0),
        "followers": user_details.get("followers", 0),
        "following": user_details.get("following", 0),
        "created_at": user_details.get("created_at", "")
    }
    return user_info


def fetch_repositories(login):
    repos = []
    url = f"{BASE_URL}/users/{login}/repos"
    page = 1
    while url and len(repos) < 500:
        response = requests.get(url, headers=HEADERS, params={"page": page, "per_page": 100})
        response_data = response.json()
        if response.status_code != 200:
            print(f"Error fetching repositories for {login}: {response_data.get('message', 'Unknown error')}")
            break
        repos.extend(response_data)
        if "next" in response.links and len(repos) < 500:
            page += 1
        else:
            break
    return repos[:500]


def save_users_to_csv(users, filename="users.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["login", "name", "company", "location", "email", "hireable", "bio", "public_repos", "followers", "following", "created_at"])
        for user in users:
            writer.writerow([user["login"], user["name"], user["company"], user["location"], user["email"],
                             str(user["hireable"]).lower(), user["bio"], user["public_repos"], user["followers"], user["following"], user["created_at"]])


def save_repositories_to_csv(repos, filename="repositories.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["login", "full_name", "created_at", "stargazers_count", "watchers_count", "language", "has_projects", "has_wiki", "license_name"])
        for repo in repos:
            writer.writerow([repo["owner"]["login"], repo["full_name"], repo["created_at"], repo["stargazers_count"],
                             repo["watchers_count"], repo["language"], str(repo["has_projects"]).lower(),
                             str(repo["has_wiki"]).lower(), repo["license"]["key"] if repo["license"] else ""])


def main():
    print("Fetching users...")
    users_data = fetch_users()
    print(f"Fetched {len(users_data)} users.")

    print("Fetching user details and repositories...")
    users_details = []
    all_repos = []
    for user in users_data:
        user_info = fetch_user_details(user)
        users_details.append(user_info)
        
        repos = fetch_repositories(user_info["login"])
        all_repos.extend(repos)

    
    print("Saving to CSV...")
    save_users_to_csv(users_details)
    save_repositories_to_csv(all_repos)
    print("Data saved to users.csv and repositories.csv.")

if __name__ == "__main__":
    main()
