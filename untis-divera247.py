#!/usr/bin/env python3
import datetime, pytz, json, requests, sys, threading

def log(message):
	with open("error.log", "a") as file:
		file.write(datetime.datetime.now().strftime("%d/%m/%Y %H:%M") + " " + message + "\n")

def getTimeRange(UNTIS_URL, untisSession):
	try:
		rawTimetable = requests.get(UNTIS_URL, cookies={"JSESSIONID": untisSession["sessionId"]}, json = {
			"id": "getting-timetable",
			"method": "getTimetable",
			"params": {
				"id": 1754,
				"type": 5
			},
			"jsonrpc": "2.0"
		}).json()

		timetable = []

		if not "error" in rawTimetable:
			for lesson in rawTimetable["result"]:
				if "code" in lesson:
					if lesson["code"] != "cancelled":
						timetable.append({"startTime": lesson["startTime"], "endTime": lesson["endTime"]})
				else:
					timetable.append({"startTime": lesson["startTime"], "endTime": lesson["endTime"]})
		else:
			log(f"Untis: {rawTimetable}")
			sys.exit(1)

		requests.post(UNTIS_URL, cookies={"JSESSIONID": untisSession["sessionId"]}, json = {
			"id": "logging-out",
			"method":"logout",
			"params": {},
			"jsonrpc": "2.0"
		})

		timetable = sorted(timetable, key=lambda d: d["startTime"])

		if timetable != []:
			return [[timetable[0]["startTime"], timetable[-1]["endTime"]]]
		else:
			return []
	except Error as e:
		log(f"Untis: {e}")
		sys.exit(1)

def isInTimeRange(timeRanges, time):
	inTimeRange = False
	for timeRange in timeRanges:
		startTime = datetime.datetime.strptime(str(timeRange[0]), "%H%M")
		endTime = datetime.datetime.strptime(str(timeRange[1]), "%H%M")
		time = datetime.datetime.strptime(str(time), "%H%M")

		if startTime < time and endTime > time:
			inTimeRange = True
	return inTimeRange

def setStatus(statusID, accessKey):
	statusCache = {}
	try:
		with open("status-cache.json", "r") as file:
			statusCache = json.load(file)
			if accessKey in statusCache:
				if statusCache[accessKey] == statusID:
					return None
	finally:
		request = requests.post(f"https://app.divera247.com/api/setstatus?Status[id]={statusID}&accesskey={accessKey}")
		if request.status_code == 200:
			with open("status-cache.json", "w") as file:
				statusCache[accessKey] = statusID
				json.dump(statusCache, file)
		else:
			log(f"Divera 24/7: {request.text}")
			sys.exit(1)


def main(user):
	UNTIS_URL = f"https://{user['untis_server']}/WebUntis/jsonrpc.do?school={user['untis_school']}"
	ACCESS_KEY = user["divera247_accesskey"]

	untisSession = requests.get(UNTIS_URL, json = {
		"id": "authenticating",
		"method": "authenticate",
		"params": {
			"user": user["untis_username"],
			"password": user["untis_password"],
			"client": "Untis-Divera247"
		},
		"jsonrpc": "2.0"
	}).json()

	if not "error" in untisSession:
		timeRange = getTimeRange(UNTIS_URL, untisSession["result"])
		if isInTimeRange(timeRange, datetime.datetime.now(pytz.timezone(user["timezone"])).strftime("%H%M")):
			setStatus(user["divera247_status_present"], ACCESS_KEY)
		else:
			setStatus(user["divera247_status_absent"], ACCESS_KEY)
	else:
		log(f"Untis: {untisSession}")

if __name__ == "__main__":
	users = []
	try:
		with open("users.json", "r") as file:
			users = json.load(file)

		for user in users:
			threading.Thread(target=main, args=(user,)).start()

	except FileNotFoundError:
		log("users.json not found!")
	except KeyError as e:
		log(f"untis.json is corrupt. Key {e} does not exist.")
