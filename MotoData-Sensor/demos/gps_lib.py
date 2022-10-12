import re


class GPS_lib():

    fix = False
    lat = float
    long = float
    speed = float
    time = int
    date = int

    def __init__(self) -> None:
        pass

    def read(self, GPSMESSAGE):
        
        GPSMESSAGE = re.search('(\$)(GNRMC).*$', GPSMESSAGE)

        if(GPSMESSAGE):

            GPS_MESG = str(GPSMESSAGE.group(0)).split(",")
            
            try:
                if(GPS_MESG[0] == "$GNRMC"):
                    print("GNRMC Message found")
                
                    if(GPS_MESG[2] == "V"):
                        print("no GPS Fix")
                        self.time = GPS_MESG[1]
                        self.fix = False
                        self.date = GPS_MESG[9]



                    if(GPS_MESG[2] == "A"):
                        print("GPS Fix")
                        self.time = GPS_MESG[1]
                        self.date = GPS_MESG[9]
                        self.fix = True
                        self.lat = GPS_MESG[3]
                        self.long = GPS_MESG[5]
                        self.speed = float(GPS_MESG[7]) * 1.852

                else:
                    print("No compatible datatype found")
            except:
                print("GPS Error")

        else:
            print("GPS Message Error")
