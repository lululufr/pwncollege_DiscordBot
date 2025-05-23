import requests
from bs4 import BeautifulSoup
import re
import json
import datetime


import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)


from lib.maxime import maxime_quote
from lib.debug import *

class pwncollegeUser:
    def __init__(self, user):
        self.user = user
        debug(f"Getting info for : {self.user}")
        self.base_url = f"https://pwn.college/hacker/{user}"
        self.session = requests.Session()
        self._refresh_data()
        self.modules = self._get_modules()
        

    def init(self):
        
        with open(f"users/{self.user}", "w") as f:
            json.dump(self.get_all_info(), f, indent=4)

    def _refresh_data(self):
        response = self.session.get(self.base_url)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.text, "html.parser")

    def _get_modules(self):
        modules = []
        header_pattern = re.compile(r"^modules-(?P<id>.+?)-header-(?P<suffix>\d+)$")

        for header in self.soup.find_all("div", class_="accordion-item-header"):
            header_id = header.get("id", "")
            match = header_pattern.match(header_id)
            if not match:
                continue

            button = header.find("button", {"data-target": True})
            if not button:
                continue

            body_id = button["data-target"].lstrip("#")

            title_tag = header.find("h4", class_="accordion-item-name")
            if not title_tag:
                continue

            modules.append(
                {
                    "id": match.group("id"),
                    "body_id": body_id,
                    "title": title_tag.get_text(strip=True),
                }
            )

        return modules

    def get_challenges(self, body_id):
        container = self.soup.find("div", id=body_id, class_="collapse")
        if not container:
            return []

        challenges = []
        for challenge in container.find_all("div", class_="challenge-row"):
            try:
                title_tag = challenge.find("h4")
                time_tag = challenge.find("h6")

                full_title = title_tag.get_text(strip=True)
                clean_name = re.sub(
                    r"($ easy $|$ hard $|\uf024\s*|\d+ pts?)", "", full_title
                ).strip()
                level = "".join(re.findall(r"\d+", full_title)) or "0"

                parts = time_tag.get_text(strip=True).split(":", 1)
                timestamp = parts[1].strip()


                challenges.append(
                    {"name": clean_name, "level": level, "timestamp": timestamp}
                )
            except Exception as e:
                continue

        return challenges

    def get_all_info(self):
        return [
            {
                "id": mod["id"],
                "title": mod["title"],
                "challenges": self.get_challenges(mod["body_id"]),
                "count": len(self.get_challenges(mod["body_id"])),
            }
            for mod in self.modules
        ]


def compare_progress(user, delay):

    time_d = datetime.datetime.now() - datetime.timedelta(minutes=delay) # a modifier lors du changement d'heure... 
    with open(f"users/{user}", "r") as f:
        j = json.load(f)

    app = ""
    for category in j:
        if category.get("challenges"):
            for chall in category["challenges"]:
                chall_time = datetime.datetime.strptime(chall["timestamp"], "%Y-%m-%d %H:%M:%S")
                if chall_time >= time_d:
                    app += f"```✅ {category['title']} : {chall['name']}```\n"

    if app == "" :
        return None
    else :
        res = f"### **{user}** 🥋 Solve :\n" + app + "_"+maxime_quote()+"_"
    return res


def read_info(user):
    debug(f"reading info for {user}")
    with open(f"users/{user}", "r") as f:
        j = json.loads(f.read())
        res = ""
        for category in j:
            if category["challenges"]:
                res += category["title"] + ":\n"
                debug(f'category {category["title"]}')
                for chall in category["challenges"]:
                    res += "    ✅ - " + chall["name"] + "\n"
                    debug(f'chall {chall["name"]}')
    return res


def get_grade_cate_user(category_check, user):

    with open(f"users/{user}", "r") as f:
        j = json.load(f)

    grades_cate = 0
    for category in j:
        if category.get("challenges") and category.get("title") == category_check:
            for chall in category["challenges"]:
                    grades_cate += 1 

    return grades_cate