
from datetime import datetime, timezone
import matplotlib.pyplot as plt
import re
import requests
from bs4 import BeautifulSoup


def plot_rating_progress(contests, filename="images/rating_progress.png"):
    # Extract contest years & ratings
    contest_years2 = [datetime.fromtimestamp(contest['ratingUpdateTimeSeconds'], tz=timezone.utc).year for contest in contests]
    ratings = [contest['newRating'] for contest in contests]

    # Generate unique x positions (using contest index)
    x_positions = list(range(len(contest_years2)))

    contest_years = []
    for i in range(1, len(contest_years2)):
        if contest_years2[i] != contest_years2[i-1]:
            contest_years.append(contest_years2[i])

    #print(contest_years)

    plt.figure(figsize=(10, 5))

    # Scatter plot for better clarity
    plt.scatter(x_positions, ratings, color='blue', label="Contests", alpha=0.8)

    # Smooth trend line
    plt.plot(x_positions, ratings, color='red', linestyle='-', linewidth=1.5, alpha=0.7, label="Rating Progression")

    # Improve x-axis labels
    plt.xticks(ticks=x_positions, labels=contest_years2, rotation=45, ha='right')

    plt.xlabel("Contests Over Time")
    plt.ylabel("Rating")
    plt.title("User Rating Progression")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)

    # Save before showing (to prevent empty image issues)
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    #plt.show()
    plt.close()  # Close to free memory


def get_codechef_profile(username):
    url = f"https://www.codechef.com/users/{username}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch data.")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract rating
    rating_section = soup.find("div", class_="rating-number")
    rating = rating_section.text.strip() if rating_section else "N/A"

    # Extract problems solved (UPDATED METHOD)

    problems_div = soup.find("section", class_="problems-solved")  # Check for correct class

    # Extract only numbers from specific h3 elements
    contests = 0
    total_problems_solved = 0

    for h3 in problems_div.find_all("h3"):
        text = h3.text.strip()

        if "Contests" in text:
            contests = int(re.search(r"\d+", text).group())  # Extract number from "Contests (60)"
        elif "Total Problems Solved" in text:
            total_problems_solved = int(
                re.search(r"\d+", text).group())  # Extract number from "Total Problems Solved: 317"

    #print(contests, total_problems_solved)  # Output: 60 317

    #print()

    # Output data
    return {
        "rating": rating,
        "problems_solved": total_problems_solved,
        "contests_participated": contests
    }


def get_user_info_codeforces(username):
    url = f"https://codeforces.com/api/user.info?handles={username}"
    response = requests.get(url)
    data = response.json()

    ret = {}

    if data['status'] == 'OK':
        ret = data['result'][0]
    else:
        return None

 # API URLs
    rating_url = f"https://codeforces.com/api/user.rating?handle={username}"
    status_url = f"https://codeforces.com/api/user.status?handle={username}&from=1&count=10000"

    # Fetch contest rating data
    rating_response = requests.get(rating_url).json()
    if rating_response['status'] == 'OK':
        contests = rating_response['result']
        ret['contests'] = len(contests)  # Number of contests
        ret['max_rating'] = max([contest['newRating'] for contest in contests]) if contests else 0  # Max rating
    else:
        print("Error fetching contest data.")
        return None

    # Fetch problem-solving data
    status_response = requests.get(status_url).json()
    if status_response['status'] == 'OK':
        submissions = status_response['result']
        solved_problems = {f"{sub['problem']['contestId']}-{sub['problem']['index']}" for sub in submissions if sub['verdict'] == "OK"}
        ret['problems'] = len(solved_problems)  # Number of unique solved problems

    else:
        print("Error fetching problem-solving data.")
        return None

    return ret

def get_user_contests(username):
    url = f"https://codeforces.com/api/user.rating?handle={username}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK':
        contests = data['result']
        return contests
    else:
        print("Error fetching contest data.")
        return []


def update_readme(cf, cc):
    with open('Readme.md', 'r', encoding='utf-8', errors='replace') as file:
        lines = file.readlines()


    #print(lines[20])
    lines[20] = '- **Current Rating:** [' + str(cf['rating']) + ']\n'
    #print(lines[20])

    lines[21] = '- **Max Rating:** [' + str(cf['max_rating']) + ']\n'
    lines[22] = '- **Rank:** [' + str(cf['rank']) + ']\n'
    lines[23] = '- **Contests Participated:** [' + str(cf['contests']) + ']\n'
    lines[24] = '- **Problems Solved:** [' + str(cf['problems']) + ']\n\n\n'

    #print(lines[36])
    #print(str(cc['rating']))
    lines[34] = '- **Current Rating:** [' + str(cc['rating']) + ']\n'
    lines[35] = '- **Contests Participated:** [' + str(cc['contests_participated']) + ']\n'
    lines[36] = '- **Problems Solved:** [' + str(cc['problems_solved']) + ']\n'

    # Write the updated content back to the file
    with open('Readme.md', 'w', encoding='utf-8') as file:
        file.writelines(lines)


'''
23- **Current Rating:** [1686]
24- **Max Rating:** [1712]
25- **Rank:** [expert]
26- **Contests Participated:** [300]
27- **Problems Solved:** [500]

73- **Current Rating:** [1793]
75- **Contests Participated:** [60]
77- **Problems Solved:** [317]
'''

if __name__ == "__main__":
    username = "veks_the_boss"

    user_info = get_user_info_codeforces(username)
    profile_data = get_codechef_profile(username)

    update_readme(user_info, profile_data)

    contests = get_user_contests(username)
    plot_rating_progress(contests)


