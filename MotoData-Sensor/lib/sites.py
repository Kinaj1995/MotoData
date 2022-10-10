def web_page(state):
    html = """<html>

    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css"
         integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
        <style>
            html {
                font-family: Arial;
                display: inline-block;
                margin: 0px auto;
                text-align: center;
            }

            .button {
                background-color: #ce1b0e;
                border: none;
                color: white;
                padding: 16px 40px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
            }

            .button1 {
                background-color: #000000;
            }
        </style>
    </head>

    <body>
        <h2>ESP MicroPython Web Server</h2>
        <p>LED state: <strong>""" + state + """</strong></p>
        <p>
            <i class="fas fa-lightbulb fa-3x" style="color:#c81919;"></i>
            <a href=\"?RECORD\"><button class="button">Record</button></a>
        </p>
        <p>
            <i class="fas fa-lightbulb fa-3x" style="color:#c81919;"></i>
            <a href=\"?RECORD_STOP\"><button class="button">Record Stop</button></a>
        </p>
        <p>
            <i class="far fa-lightbulb fa-3x" style="color:#000000;"></i>
            <a href=\"?CALIBRATE\"><button class="button button1">Calibrate</button></a>
        </p>
    </body>

    </html>"""
    return html