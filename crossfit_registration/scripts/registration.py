"""
Registration
"""
import argparse
import datetime
import sys
import json
import logging
import requests

from bs4 import BeautifulSoup


global conf

########################
# Logger configuration #
########################

logger = logging.getLogger('crossfit-registration')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('/var/tmp/crossfit-registration.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

logger.addHandler(ch)


# Initialize global conf variable.
conf = {}

##################
# Authentication #
##################

AUTH_COOKIE_ID = '4a45b8f51948b97b4e0ee4605174b1ca'
AUTH_COOKIE_VALUE = None


def authenticate():
    """
    Fetch authentication code.
    """
    global conf
    login_url = 'http://www.multiresa.fr/~reebok2/index.php/creation-de-compte/login.html'  # noqa
    response = requests.get(login_url)
    soup = BeautifulSoup(response.content)
    cbsecuritym3 = soup.find('input', {'name': 'cbsecuritym3'}).get('value')

    login_form = {
        'username': conf.get('username'),
        'passwd': conf.get('password'),
        'op2': 'login',
        'lang': 'french',
        'force_session': '1',
        'return': 'B:aHR0cDovL3d3dy5tdWx0aXJlc2EuZnIvfnJlZWJvazIvaW5kZXgucGhwL2plLXJlc2VydmUuaHRtbC5odG1s',  # noqa
        'message': '0',
        'loginform': 'loginform',
        'cbsecuritym3': cbsecuritym3,
        'remember': 'yes',
    }
    response = requests.post(login_url, data=login_form)
    # requests has an issue with cookies and redirections so we have to fetch
    # them from the response's history
    try:
        conf['auth_cookie'] = response.history[0].cookies[AUTH_COOKIE_ID]
    except:
        logger.error("Impossible to retrieve the authentication cookie.")
        sys.exit(-1)


################
# Registration #
################

def register_wod(day, time):
    """
    Register for a given WOD.

    Args:
        day: String formatted as "YYYY-MM-DD" (eg: "2014-03-17").
        time: String formatted as "HHMM" (eg: "1830").
    """
    registration_url = 'http://www.multiresa.fr/~reebok2/app/req/requestResa.php'  # noqa
    registration_params = {
        'action': 'sendresa',
        'idcompte': conf.get('id_compte'),
        'idMembre': conf.get('id_membre'),
        'mailMembre': conf.get('email'),
        'activite': 50,
        'lejour': day,
        'lecreno': time,
        'effectif': 12,
        'leprixu': '0.00',
        'leprixc': '0.00',
        'resadirect': 0,
        'lenomU': '',
        'leprenomU': '',
        'letelU': '',
        'lemailU': '',
        'lemultiU': 'undefined',
    }
    response = requests.get(
        registration_url,
        params=registration_params,
        cookies={AUTH_COOKIE_ID: conf['auth_cookie']}
    )
    logger.info(u"{day} {time}: {content}.".format(
        day=day, time=time, content=response.content))


def register():
    today = datetime.date.today()
    # Registrations are opened 4 days in advance.
    weekday = (today.weekday() + 4) % 7
    try_register = False
    for slot in conf.get('slots'):
        if slot[0] == weekday:
            authenticate()
            register_wod(str(today), slot[1])
            try_register = True
            break
    if not try_register:
        logger.info("Nothing to register for.")


def cmdline():
    parser = argparse.ArgumentParser(
        description=
        "Register to available crossfit WODs based on desired slots listed in "
        "the configuration file."
    )
    parser.add_argument(
        '-c',
        '--configuration-file',
        dest='configuration_file',
        required=True
    )
    args = parser.parse_args()
    configuration_file = args.configuration_file

    try:
        fil = open(configuration_file)
    except IOError:
        logger.error("Impossible to open configuration file: {}.".format(
            configuration_file))
        sys.exit(-1)

    global conf
    try:
        conf = json.load(fil)
    except ValueError as e:
        logger.error("Configuration deserialization failed: {}".format(e))
        sys.exit(-1)

    required_infos = (
        'username', 'password', 'email', 'slots', 'id_compte', 'id_membre')
    for required_info in required_infos:
        if not required_info in conf:
            logger.error("Missing information: {}.".format(required_info))
            sys.exit(-1)

    register()
