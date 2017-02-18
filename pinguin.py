from email.mime.text import MIMEText

import json
import logging
import requests
import smtplib
import sys
import time


EMAIL_MSG_TEMPLATE = """
The endpoint %s has been returning unexpected status codes. You are expecting %d
but penguins are getting %s.
"""
FREQUENCY_THRESHOLD_SECS = 121
logger = logging.getLogger("pinguin")


def raise_alarm(email, endpoint, error, email_sender):
    msg = MIMEText(EMAIL_MSG_TEMPLATE % (endpoint["url"], endpoint["resp"], error))
    msg["Subject"] = "Persistent %s error on %s" % (error, endpoint["url"])
    msg["From"] = "pinguin@skytreader.net"
    msg["To"] = email
    email_sender.sendmail(msg["from"], msg["To"], msg.as_string())


def pinguin_daemon(email, watchlist, email_sender):
    endpoint_errors = {}
    error_timestamps = {}
    try:
        while True:
            for idx, endpoint in enumerate(watchlist):
                logger.info("checking %s" % endpoint["url"])
                resp = requests.request(endpoint["method"], endpoint["url"])
                resp_time = time.time()
                logger.info("response status code %d" % resp.status_code)

                if resp.status_code != endpoint["resp"]:
                    if endpoint_errors.get(endpoint["url"]):
                        if endpoint_errors[endpoint["url"]].get(resp.status_code):
                            timediff = resp_time - error_timestamps[endpoint["url"]][resp.status_code]
                            endpoint_errors[endpoint["url"]][resp.status_code] += 1
                            if timediff > FREQUENCY_THRESHOLD_SECS:
                                error_timestamps[endpoint["url"]][resp.status_code] = time.time()
                        else:
                            endpoint_errors[endpoint["url"]][resp.status_code] = 1
                            error_timestamps[endpoint["url"]][resp.status_code] = time.time()

                        has_error_reached_threshold = (
                            endpoint_errors[endpoint["url"]][resp.status_code] > 4
                        )
                        timediff = resp_time - error_timestamps[endpoint["url"]][resp.status_code]
                        has_timefreq_reached_threshold = timediff <= FREQUENCY_THRESHOLD_SECS
                        logger.debug("error count threshold? %s" % has_error_reached_threshold)
                        logger.debug(
                            "timefreq threshold (%s)? %s diff: %s" %
                            (resp.status_code, has_timefreq_reached_threshold, timediff)
                        )
                        
                        # TODO Fix magic number
                        if has_error_reached_threshold and has_timefreq_reached_threshold:
                            logger.warn("Raising alarm for error %d on endpoint %s" % (resp.status_code, endpoint["url"]))
                            raise_alarm(email, endpoint, resp.status_code, email_sender)
                    else:
                        endpoint_errors[endpoint["url"]] = {}
                        endpoint_errors[endpoint["url"]][resp.status_code] = 1
                        error_timestamps[endpoint["url"]] = {}
                        error_timestamps[endpoint["url"]][resp.status_code] = time.time()

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

        logger.setLevel(logging.getLevelName(cfg["loglevel"]))
        
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler = logging.FileHandler("_pinguin.log")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        email_sender = smtplib.SMTP("localhost")
        pinguin_daemon(cfg["notify"], cfg["checks"], email_sender)
