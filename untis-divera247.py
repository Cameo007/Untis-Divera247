#!/usr/bin/env python3
import webuntis, datetime, json, requests

def getTimeRange(klasse, untisSession):
	untisSession.login()

	today = datetime.date.today()

	timetable = []
	for elem in untisSession.timetable(klasse=untisSession.klassen().filter(name=klasse)[0], start=today, end=today):
		elem = json.loads(str(elem).replace("'", "\""))
		timetable.append({"startTime": elem["startTime"], "endTime": elem["endTime"]})

	untisSession.logout()

	timetable = sorted(timetable, key=lambda d: d["startTime"])

	return [[timetable[0]["startTime"], timetable[-1]["endTime"]]]

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
	try:
		with open("untis-divera247-status.txt", "r") as file:
			if int(file.read()) == statusID:
				return None
	except FileNotFoundError:
		pass
	except Exception as e:
		print(e)
		with open("untis-divera247.log", "a") as file:
			file.write(str(e))

	request = requests.post(f"https://app.divera247.com/api/setstatus?Status[id]={statusID}&accesskey={accessKey}")
	if request.status_code == 200:
		with open("untis-divera247-status.txt", "w") as file:
			file.write(str(statusID))
	else:
		with open("untis-divera247.log", "a") as file:
			file.write(request.text)

if __name__ == "__main__":
	users = []
	try:
		with open("users.json", "r") as file:
			users = json.load(file)

		for user in users:
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
	except FileNotFoundError:
		print("ERROR: users.json not found!")
