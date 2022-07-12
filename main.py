import requests as r
import random
import time


guild_id = input("Guild ID : ")
token = input("User token : ")
user_id = input("Your user ID : ")

headers = {"authorization": token}
url = "https://discord.com/api/v9/guilds/" + guild_id + "/messages/search?author_id=" + user_id

data = r.get(url, headers=headers)
if data.status_code != 200:
    print("Incorrect values.")
    raise SystemExit

data = data.json()

totalmsgcount = data["total_results"]

print("Beginning deletion of", totalmsgcount, "messages.")

msgcount = 0
offset = 0
deleted_count = 0
failed = []


while msgcount < totalmsgcount:
    for msg in data["messages"]:
        response = r.delete(f"https://discord.com/api/v9/channels/{msg[0]['channel_id']}/messages/{msg[0]['id']}", headers=headers)

        if response.status_code == 204:
            deleted_count += 1
            print(f"\rDeleted {deleted_count}/{totalmsgcount}", end=" ")
        else:
            delay = response.json()["retry_after"]
            time.sleep(delay + 10)
            response = r.delete(f"https://discord.com/api/v9/channels/{msg[0]['channel_id']}/messages/{msg[0]['id']}", headers=headers)
            if response.status_code == 204:
                deleted_count += 1
                print(f"\nDelayed deletion : deleted {deleted_count}/{totalmsgcount} (waited ({delay} + 10) = {delay + 10}s)")
            else:
                failed.append({"id": msg['id'], "channel_id": msg['channel_id']})
                print(f"\n!! Deletion failed (total={len(failed)}) !!")

        time.sleep(1 + random.uniform(0, 0.3))

        msgcount += 1

    offset += 25

    data = r.get(url + f"&offsef={offset}", headers=headers)

    while data.status_code != 200:
        print("Temporizing...")
        time.sleep(1)

    data = data.json()


print("Done")

with open("failed.txt", "w") as logfile:
    logfile.write(str(failed))
