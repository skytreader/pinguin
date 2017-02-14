import json
import requests
import smptplib
import sys
import time


EMAIL_MSG_TEMPLATE = """
The endpoint %s has been returning unexpected status codes. You are expecting %d
but we are getting %s.
"""


def raise_alarm(email, endpoint, error):
    from_


def pinguin_daemon(email, watchlist, email_sender):
    endpoint_errors = {}
    try:
        while True:
            for idx, endpoint in enumerate(watchlist):
                resp = requests.request(endpoint["method"], endpoint["url"])
            sleep(0.25)
    finally:
        email_sender.close()


if __name__ == "__main__":
    email_sender = smtplib.SMTP("localhost")
    
    if len(sys.argv) != 2:
        print("Usage: python3 %s <config_file>" %  __name__)
        exit(1)

    with open(sys.argv[1]) as config:
        cfg = json.load(config)
        pinguin_daemon(cfg["notify"], cfg["checks"], "pinguin@skytreader.net")
