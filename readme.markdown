# pinguin

Penguins are gritty guards for your HTTP endpoints. Moreover, they won't spam
your website with their checks.

Assumes Python 3 on both the main script and the test sever.

# Usage

Start an SMTP server. You can use Python's as follows

    sudo python -m smtpd -n -c DebuggingServer localhost:25

Create a JSON config file which will specify the endpoints you want to hit and
the expected status code. You also need to specify the email address you want
to be notified when something seems amiss.

    {
        "notify": "email@company.co",
        "checks": [
            {
                "url": "http://127.0.0.1:7070",
                "method": "GET",
                "resp": 200
            }
            ...
        ],
        ...
    }

There are other config values; check `sample_config.json` for the available
options.

Pinguin will check this endpoint four times per minute and notify you if
anything is amiss.

A Flask app is provided as a test server.

## Reporting behavior

The window for error reporting frequency is not sliding; that is, the counter
for errors resets everytime a report is made.

## Try it out

Create separate virtualenvs for the main pinguin script as well as for the
test server. `cd` into the `test_server/` directory and, while in your
virtualenv, run the server:

    $ python server.py 
     * Running on http://127.0.0.1:3141/ (Press CTRL+C to quit)

Change the email in the `notify` field of the config to where you want to
receive notifications then invoke the main script:

    $ python pinguin.py sample_config.json

# Caveats

This relies on your web server responding with the proper status codes. Some
websites, for some reason, always respond with status 200, despite rendering a
page that basically tells the user they got anything but status 200.

Just right now, checking a lot of URLs will surely cause scheduling problems.

# License

MIT
