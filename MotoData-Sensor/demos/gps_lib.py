import re

def convertTime(ts):

    hours = ts[0:2]
    min = ts[2:4]
    sec = ts[4:6]
    ms = ts[7:9]
    
    return hours + ":" + min + ":" + sec + "." + ms

def convertDate(ds):
    
    day = ds[0:2]
    month = ds[2:4]
    year = ds[4:6]

    return day + "/" + month + "/" + year


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
                    self.time = convertTime(GPS_MESG[1])
                    self.date = convertDate(GPS_MESG[9])

                    if(GPS_MESG[2] == "V"):
                        self.fix = False

                    if(GPS_MESG[2] == "A"):         
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