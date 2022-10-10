



import time



#  the gyro's x,y,z values drift by a steady amount. if we measure this when arduino is still
#  we can correct the drift when doing real measurements later

class IMU:
    
    accelX, accelY, accelZ = 0.0                                	# units m/s/s i.e. accelZ if often 9.8 (gravity)
    gyroX, gyroY, gyroZ = 0.0                                   	# units dps (degrees per second)
    gyroDriftX, gyroDriftY, gyroDriftZ = 0.0                    	# units dps
    accRoll, accPitch, accYaw = 0.0			                    	# units degrees (roll and pitch noisy, yaw not possible)
    complementaryRoll, complementaryPitch, complementaryYaw = 0.0    # units degrees (excellent roll, pitch, yaw minor drift)
    
    lastTime = 0
    lastInterval = 0
    
    def readIMU(x_acc, y_acc, z_acc, x_gy, y_gy, z_gy):
        accelX = x_acc
        accelY = y_acc
        accelZ = z_acc
        gyroX = x_gy
        gyroY = y_gy
        gyroZ = z_gy
        

    def calibrateIMU(delayMillis, calibrationMillis):
        
        calibrationCount = 0
        
        sumX = 0.0
        sumY = 0.0
        sumZ = 0.0
        
        starttime = time.ticks_ms()
        
        while(time.ticks_ms() < starttime + calibrationMillis):
        
        
    
    