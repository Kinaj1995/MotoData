## ==================== Storage ==================== ##
## by Pascal Rusca
"""
    ChangeLog:
    - 0-02: Added new Filenamesystem
    - 0-01: Init Class

"""
## ================================================= ##


class STORAGE_lib():
    
    filename = ""
    
    def __init__(self) -> None:
        pass

    
    def getFilename(self):
        return str(self.filename)
        
    
    ## Checks SD-Card and gives back new File Name
    def getNewFileName(self, dir_list):
        
        fn = ""
        nfn = ""
        
        dir_list.sort
        

        if(len(dir_list) > 1):

            fn = int(dir_list[-1].split(".")[0]) + 1
            
            for i in range (5 - len(str(fn))):
                nfn = nfn + "0"

            self.filename = nfn + str(fn) + ".csv"
            
        else:
            self.filename = "00001.csv"
               
        
        
        return 






