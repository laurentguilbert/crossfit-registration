# Crossfit Registration

Tired of forgetting to subscribe to your favorite WOD ? No more !

### Install the script

`python setup.py develop`

### Create the JSON configuration file

```
{
    "username": "username",
    "password": "password",
    "email": "email",
    "id_compte": 12345,
    "id_membre": 12345,
    "slots": [
        [0, "1830", 50],
        [1, "1830", 50],
        [2, "1830", 50],
        [3, "1830", 50],
        [3, "1830", 45],
    ]
}
```

Each entry in slots is composed of the day of the week (starting from 0), the desired time and the activity type.

### Setup the cron job

```
crontab -e
5 0 * * * /usr/local/bin/crossfit-registration -c /path/to/conf.json
```

### Logging

Logging informations are stored inside `/var/tmp/crossfit-registration.log`.
