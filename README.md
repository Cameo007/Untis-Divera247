# Untis-Divera247

# Moved to [Codeberg](https://codeberg.org/Cameo007/Untis-Divera247.git)

## What is Untis-Divera247 for?
With Untis-Divera247 your [Divera 24/7](https://www.divera247.com/) status can be set, according to your timetable, which should be available via [Untis](https://www.untis.at/).

## Configuration (`users.json`)
This is a sample `users.json` config file, which you have to provide.
```
[
	{
		"untis_server":"", # Untis server domain name
		"untis_school":"", # Untis school name
		"untis_username":"",
		"untis_password":"",
		"divera247_accesskey":"", # Divera 24/7 access key; available at Settings -> Debug
		"divera247_status_present":"", # Divera 24/7 status ID for presence
		"divera247_status_absent":"", # Divera 24// status ID for absence
		"timezone":"" # Time zone which is used for checking against the timetable, not for logs
	}
]
```

## Logs (`error.log`)
Logs are stored in `error.log`.
