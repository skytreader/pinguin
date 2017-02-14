# pinguin

Penguins are gritty guards for your HTTP endpoints. Moreover, they won't spam
your website with their checks.

# Usage

Create a JSON config file which will specify the endpoints you want hit and the
expected status code. You also need to specify the email address you want to be
notified when something seems amiss.

    {
        "notify": "email@company.co",
        "checks": [
            {
                "url": "http://127.0.0.1:7070"
                "method": "GET"
                "resp": 200
            }
            ...
        ]
    }

Pinguin will check this endpoint four times per minute and notify you if
anything is amiss.

# Caveats

This relies on your web server responding with the proper status codes. Some
websites, for some reason, always respond with status 200, despite rendering a
page that basically tells the user they got anything but status 200.

# License

MIT
