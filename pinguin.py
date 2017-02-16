from email.mime.text import MIMEText

import json
import logging
import requests
import smtplib
import sys
import time


EMAIL_MSG_TEMPLATE = """
The endpoint %s has been returning unexpected status codes. You are expecting %d
but we are getting %s.
"""

logger = logging.getLogger("pinguin")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler("_pinguin.log")
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def raise_alarm(email, endpoint, error, email_sender):
    msg = MIMEText(EMAIL_MSG_TEMPLATE % (endpoint["url"], endpoint["resp"], error))
    msg["Subject"] = "Persistent %s error on %s" % (error, endpoint["url"])
    msg["From"] = "pinguin@skytreader.net"
    msg["To"] = email
    email_sender.sendmail(msg["from"], msg["To"], msg.as_string())


def pinguin_daemon(email, watchlist, email_sender):
    endpoint_errors = {}
    try:
        while True:
            for idx, endpoint in enumerate(watchlist):
                logger.info("checking %s" % endpoint["url"])
                resp = requests.request(endpoint["method"], endpoint["url"])
                logger.info("response status code %d" % resp.status_code)

                if resp.status_code != endpoint["resp"]:
                    if endpoint_errors.get(endpoint["url"]):
                        if endpoint_errors[endpoint["url"]].get(resp.status_code):
                            endpoint_errors[endpoint["url"]][resp.status_code] += 1
                        else:
                            endpoint_errors[endpoint["url"]][resp.status_code] = 1
                        
                        # TODO Fix magic number
                        if endpoint_errors[endpoint["url"]][resp.status_code] > 4:
                            logger.warn("Raising alarm for error %d on endpoint %s" % (resp.status_code, endpoint["url"]))
                            raise_alarm(email, endpoint, resp.status_code, email_sender)
                    else:
                        endpoint_errors[endpoint["url"]] = {}
                        endpoint_errors[endpoint["url"]][resp.status_code] = 1

            time.sleep(15)
    except:
        import traceback
        traceback.print_exc()
    finally:
        email_sender.close()


if __name__ == "__main__":
    email_sender = smtplib.SMTP("localhost")
    
    if len(sys.argv) != 2:
        print("Usage: python3 %s <config_file>" %  __name__)
        exit(1)

    with open(sys.argv[1]) as config:
        cfg = json.load(config)
        email_sender = smtplib.SMTP("localhost")
        pinguin_daemon(cfg["notify"], cfg["checks"], email_sender)
