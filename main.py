import pickle
import requests as r
import random
import time


def save_msgs(offset, mess):
    container = {"offset": offset, "messages": mess}
    with open("discordmessages", "wb") as f:
        pickle.dump(container, f)


def load_msgs():
    with open("discordmessages", "rb") as f:
        container = pickle.load(f)
    return container["offset"], container["messages"]


guild_id = input("Guild ID : ")
token = input("User token : ")
user_id = input("Your user ID : ")

headers = {"authorization": token}
url = "https://discord.com/api/v9/guilds/" + guild_id + "/messages/search?author_id=" + user_id

data = r.get(url, headers=headers)
if data.status_code != 200:
    print(f"Incorrect values. (error code {data.status_code})")
    raise SystemExit

data = data.json()

totalmsgcount = data["total_results"]

print("Retrieving", totalmsgcount, "messages.")

deleted_count = 0
saved = False
delay = 0

try:
    offset, messages = load_msgs()
except Exception:
    offset, messages = 0, dict()
    save_msgs(offset, messages)

for msg in data["messages"]:
    if messages.get(msg[0]["channel_id"]) is None:
        messages[msg[0]["channel_id"]] = []
    messages[msg[0]["channel_id"]].append(msg[0]["id"])

# Retrieveing all messages
while offset < totalmsgcount:
    response = r.get(url + f"&offset={offset}", headers=headers)

    while response.status_code != 200:
        delay = response.json()["retry_after"]
        print("Temporizing for", delay, "seconds")
        if not saved:
            save_msgs(offset, messages)
            saved = True

        time.sleep(delay)
        response = r.get(url + f"&offset={offset}", headers=headers)

    saved = False
    data = response.json()
    delay = delay // 2

    for msg in data["messages"]:
        if messages.get(msg[0]["channel_id"]) is None:
            messages[msg[0]["channel_id"]] = []
        messages[msg[0]["channel_id"]].append(msg[0]["id"])

    print(f"\rSuccessfuly retrieved {offset}/{totalmsgcount} messages.", end=" ")

    time.sleep(1.5 + delay + random.uniform(0, 0.4))

    offset += 25

save_msgs(offset, messages)


for channel in messages:
    for i, msg in enumerate(messages[channel]):
        if msg is None:
            deleted_count += 1
            continue

        response = r.delete(f"https://discord.com/api/v9/channels/{channel}/messages/{msg}", headers=headers)

        while response.status_code not in (204, 404):
            print(response.status_code)
            delay = response.json()["retry_after"]
            print("Temporizing", delay, "* 3 =", delay * 3, "seconds.")
            time.sleep(delay * 3)
            response = r.delete(f"https://discord.com/api/v9/channels/{channel}/messages/{msg}", headers=headers)

        if response.stauus_code == 204:
            print(f"\rDeleted {deleted_count}/{totalmsgcount}", end=" ")
        else:
            print("\rSkipping deleted messages...", end=" ")

        messages[channel][i] = None
        deleted_count += 1

        time.sleep(0.5 + random.uniform(0.1, 0.5))

print("\nDone.")


input("[PRESS ENTER TO QUIT]")
