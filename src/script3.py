import requests
import sqlite3
import re
from bs4 import BeautifulSoup


'''
This script is about getting all the player's salary information and finding their corresponding agent.
Moreover, finding the agent id (main key) and stored as foreign key in Players database.
'''


# Http request and handling the error.
def request(url):
    try:
        return requests.get(url)
    except requests.exceptions.ConnectionError:
        pass


# Return the player's salary and agent information
def get_player_salary(response):
    parsed_html = BeautifulSoup(response.content, features="html.parser")

    stephen = parsed_html.findAll(class_="name")
    curry = parsed_html.findAll(class_="hh-salaries-sorted")

    n = 1
    temp_list = []
    while n < len(stephen):
        temp = str(stephen[n].contents[1].contents[0]).strip()
        temp2 = int(str(curry[n].contents[0]).strip().replace("$", "").replace(",", ""))
        temp_href = stephen[n].contents[1]['href']

        temp_response = request(temp_href)
        temp_parsed_html = BeautifulSoup(temp_response.content, features="html.parser")
        agent_of_player = temp_parsed_html.findAll(class_="player-fact")

        match = re.findall(r'His agent is <a.*>(.*)</a>', str(agent_of_player))
        if not match:
            match = re.findall(r'His agents are <a.*>(.*)</a>', str(agent_of_player))

        try:
            temp_match = str(match[0])
        except IndexError:
            temp_match = 'Null'

        print("\r", temp_match, end="")

        temp_list.append([temp, temp2, temp_match])
        n += 1
    return temp_list


# Finding the agent ID in the Agents database and then insert player's salary and agent foreign id information into the Players database.
def insert_salary_players(player_salary_list):
    conn = sqlite3.connect('nba.db')
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS Players')
    cur.execute('CREATE TABLE Players (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, salary INTEGER, agents_id INTEGER)')
    for a in player_salary_list:
        cur.execute('SELECT id FROM Agents WHERE (name=?)', (a[2],))
        try:
            temp_agent_id = int(str(cur.fetchone())[1:-2])
        except ValueError:
            temp_agent_id = None

        cur.execute('SELECT * FROM Players WHERE (name=? AND salary=? AND agents_id=?)', (a[0], a[1], temp_agent_id))
        entry = cur.fetchone()
        if entry == None:
            cur.execute('''INSERT INTO Players (name, salary, agents_id) VALUES (?, ?, ?)''', (a[0], a[1], temp_agent_id))

    conn.commit()


print("Running script3.py [Extracting from https://hoopshype.com/salaries/players/)] ......")
target_url = 'https://hoopshype.com/salaries/players/'
response = request(target_url)
player_salary_list = get_player_salary(response)
insert_salary_players(player_salary_list)


