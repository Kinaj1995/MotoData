## ==================== GPS_Lib ==================== ##
## by Pascal Rusca
"""
    ChangeLog:
    - 0-03: Added Exceptions
    - 0-02: Added conversion for Date and Time
    - 0-01: Init Class

"""
## ================================================= ##



## ==================== Imports ==================== ##
## Used Libaries
##
## ================================================= ##
import re




## =============== GLOBAL FUCTIONS ================= ##
## 
##
## ================================================= ##
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

    return day + "." + month + ".20" + year


 
## ================== EXCEPTIONS =================== ##
##
"""
    GPSNoCompDataType:
    When no complete GPS Message could be recognized
    
    GPSMessageError:
    When no GPS Message could be recognized

"""
##
## ================================================= ##
class GPSNoCompDataType(Exception):
    """GPS Error"""
    def __init__(self, message="no complete GPS Message"):
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return f'{self.GPSMESSAGE}'
    


class GPSMessageError(Exception):
    """GPS Message Error"""
    
    def __init__(self, message="no GPS Message"):
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return f'{self.GPSMESSAGE}'
    



## ================== Main Class =================== ##
## Converts GPS Messages into the needed data
##
## ================================================= ##
class GPS_lib():

    # -- Class Vars
    fix = False
    lat = float
    long = float
    speed = float
    time = int
    date = int


    # -- Init Constructor
    def __init__(self) -> None:
        pass



    # -- READ Function (Parsing of the GPS Data)
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
                    raise GPSNoCompDataType()

                    
            except:
                raise GPSNoCompDataType()

        else:
            raise GPSMessageError()
            print("GPS Message Error")