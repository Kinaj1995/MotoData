

def send_command(command):
    """Send a command string to the GPS.  If add_checksum is True (the
    default) a NMEA checksum will automatically be computed and added.
    Note you should NOT add the leading $ and trailing * to the command
    as they will automatically be added!
    """
    add_checksum = True
    GPSSerial.write(b"$")
    GPSSerial.write(command)
    if add_checksum:
        checksum = 0
        for char in command:
            checksum ^= char
        GPSSerial.write(b"*")
        GPSSerial.write(bytes("{:02x}".format(checksum).upper(), "ascii"))
    GPSSerial.write(b"\r\n")