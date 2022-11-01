def web_content(state):

    html = """ """

    if(state == "READY"):
        html = """
        <p>
            <a href=\"?RECORD\"><button class="button">Record</button></a>
        </p>
        <p>
            <a href=\"?CALIBRATE\"><button class="button button1">Calibrate</button></a>
        </p>        
        """
    elif(state == "RECORD"):
        html = """
        <p>
            <a href=\"?RECORD_STOP\"><button class="button">Record Stop</button></a>
        </p>
      
        """
    elif(state == "CALIBRATE"):
        html = """
            <h2> Wait for finishing calibration </h2>
            <script>
                setTimeout(function(){
                    window.location.href = 'http://192.168.4.1/';
                }, 12000);
            </script>
        """
    elif(state == "INIT_RECORD"):
        html = """
            <h2> Wait for the start of the Recording </h2>
            <script>
                setTimeout(function(){
                    window.location.href = 'http://192.168.4.1/';
                }, 8000);
            </script>
        """
    elif(state == "STOP_RECORD"):
        html = """
            <h2> Wait for the stop of the Recording </h2>
            <script>
                setTimeout(function(){
                    window.location.href = 'http://192.168.4.1/';
                }, 8000);
            </script>
        """
    elif(state == "ERROR"):
        html = """
            <h2> Something went wrong </h2>
        """

    return html





def web_page(state):
    html = """
    
    <html>

    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
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
        <h2>MotoData Sensor Site</h2>
        <p>Current Sensor State: <strong>""" + state + """</strong></p>

    """ + web_content(state) + """
        


    </body>

    </html>
    
    """
    return html
