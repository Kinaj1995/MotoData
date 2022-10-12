##




## Checks SD-Card and gives back new File Name

def getNewFileName(dir_list):
    
    filename = ""
    nfn = ""
    
    dir_list.sort
    

    if(len(dir_list) > 1):

        filename = int(dir_list[-1].split(".")[0]) + 1
        
        for i in range (5 - len(str(filename))):
            nfn = nfn + "0"

        filename = nfn + str(filename) + ".csv"
        
    else:
        filename = "00001.csv"
                
    
    return filename
