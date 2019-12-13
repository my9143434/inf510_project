import requests
import sqlite3
from bs4 import BeautifulSoup

'''
This script is about getting all the available agent on the website:
https://hoopshype.com/reps/
And store them into a Agents database
This script won't take a lot of time.
Only scraping a website.
'''


# Http request and handling the error.
def request(url):
    try:
        return requests.get(url)
    except requests.exceptions.ConnectionError:
        pass


# Getting all the agent (138) and store them into a list.
def get_agent_list(response):
    parsed_html = BeautifulSoup(response.content, features="html.parser")

    agent = parsed_html.findAll(class_="name")
    # print(str(agent[1].contents[1].contents[0]).strip())        # agent name; start from 1 to 137
    # print(agent[1].contents[1]['href'])     # agent href

    temp_list = []
    n = 1
    while n < 137:
        # print(agent[n])
        temp_name = str(agent[n].contents[1].contents[0]).strip()
        temp_href = agent[1].contents[1]['href']

        temp_list.append([temp_name, temp_href])
        n += 1
    return temp_list


# Inserting each agent into the database.
def insert_agent(agent_list):
    conn = sqlite3.connect('nba.db')
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS Agents')
    cur.execute('CREATE TABLE Agents (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, href TEXT)')
    for a in agent_list:
        cur.execute('SELECT * FROM Agents WHERE (name=? AND href=?)', (a[0], a[1]))
        entry = cur.fetchone()
        if entry == None:
            cur.execute('''INSERT INTO Agents (name, href) VALUES (?, ?)''', (a[0], a[1]))

    conn.commit()


print("Running script.py [Extracting from https://hoopshype.com/reps/)].......")
target_url = 'https://hoopshype.com/reps/'
response = request(target_url)
agent_list = get_agent_list(response)
insert_agent(agent_list)

