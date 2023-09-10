#!/usr/bin/env python3
import webuntis, datetime, json, requests, sys, threading

def log(message):
	with open("error.log", "a") as file:
		file.write(datetime.datetime.now().strftime("%d/%m/%Y %H:%M") + " " + message + "\n")

def getTimeRange(klasse, untisSession):
	try:
		untisSession.login()

		today = datetime.date.today()

		timetable = []
		for elem in untisSession.timetable(klasse=untisSession.klassen().filter(name=klasse)[0], start=today, end=today):
			elem = json.loads(str(elem).replace("'", "\""))
			if "code" in elem:
				if elem["code"] != "cancelled":
					timetable.append({"startTime": elem["startTime"], "endTime": elem["endTime"]})
			else:
				timetable.append({"startTime": elem["startTime"], "endTime": elem["endTime"]})

		untisSession.logout()

		timetable = sorted(timetable, key=lambda d: d["startTime"])

		if timetable != []:
			return [[timetable[0]["startTime"], timetable[-1]["endTime"]]]
		else:
			return []
	except IndexError:
		log(f"Untis: Klasse '{klasse}' not found.")
		sys.exit(1)
	except webuntis.errors.Error as e:
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
	ACCESS_KEY = user["divera247_accesskey"]
	untisSession = webuntis.Session(
		server=user["untis_server"],
		school=user["untis_school"],
		username=user["untis_username"],
		password=user["untis_password"],
		useragent="Untis-Divera247"
	)

	timeRange = getTimeRange(user["untis_timetable_class"], untisSession)
	if isInTimeRange(timeRange, datetime.datetime.now().strftime("%H%M")):
		setStatus(user["divera247_status_present"], ACCESS_KEY)
	else:
		setStatus(user["divera247_status_absent"], ACCESS_KEY)

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
