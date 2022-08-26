from ECE16Lib.Communication import Communication
from ECE16Lib.HRMonitor import HRMonitor
from ECE16Lib.CircularList import CircularList
from ECE16Lib.Pedometer import Pedometer
from matplotlib import pyplot as plt
from time import time
import numpy as np
from datetime import datetime
from pyowm import OWM

if __name__ == "__main__":
  fs = 50                         # sampling rate
  num_samples = 500               # 10 seconds of data @ 50Hz
  refresh_time = 1                # plot every second
  
  #initializing pedometer and hr monitor objects
  ped=Pedometer(num_samples, fs, [])
  HRMon = HRMonitor(num_samples, fs, [],[])
  filepath="" 

  #initializes the model
  


  comms = Communication('/dev/cu.NIKECE16-6', 115200)
  comms.clear()                   # just in case any junk is in the pipes
  comms.send_message("wearable")  # begin sending data
  

  #filesaver saves a value, but checks if that value is different from the most recent value it added. This is to prevent
  #exploitation of the device, such as attaching a motor to the pedometer and gaining infinite currency
  def filesaver(filepath,value): 
    data=np.genfromtxt(filepath,delimiter=",")
    if data[-1]!=value:
      data=np.append(data,value)
    data=np.array([data[-2],data[-1]])
    np.savetxt(filepath,data,delimiter=",")

  try:
    previous_time = time()
    while(True):
      message = comms.receive_message()
      if(message != None):
        try:
          (m1,m2,m3,m4,m5) = message.split(',')
          HRMon.add(int(m1),int(m5))  
          ped.add(int(m2),int(m3),int(m4))

        except ValueError:        # if corrupted data, skip the sample
          continue

        # add the new values to the circular lists
        
      
        current_time = time()
        if (current_time - previous_time > refresh_time):
          previous_time = current_time
          
          #Try except block for the hr and steps functions.
          try:
              #note: hr thresh refers to the hr using the threshold
            hr,peaksThresh,filtered=HRMon.process()
            steps, peaks, jumps, filtered = ped.process()
          except:
            continue
         #this hr is the machine learning model heart rate.
          
          
          today=datetime.now()
          #today1=today.strftime("%m/%d/%Y")
          timeNow=today.strftime("%H:%M:%S")
          owm = OWM('3fb35009e6e89e5e3bc654ec5d6c94fc').weather_manager()
          #obtaining the string for temperature
          observation = owm.weather_at_place('San Diego,CA,US').weather.temperature('fahrenheit')
          #apparently, the temperature is returned as a dictionary type
          #this process must be done to convert it to a string
          weatherFinal="{0} Degrees".format(observation['temp'])

          plt.clf()
          plt.plot(filtered)
          plt.title("Heart Rate: %d Steps: %d " % (hr,steps))
          plt.show(block=False)
          plt.pause(0.001)           
          
          
          ##conditions to send the currency to the tamagotchi
          if steps%2==0 and steps>0: 
            filesaver(filepath,3) 
          elif hr<100 and hr>50: 
            filesaver(filepath,1) 


          #if larger than 480, it will send the dead message to the mcu
          #480 was the highest ever recorded heart rate. 
          # You are most likely dead if your heart rate is above this
          if (hr>480):
            comms.send_message("dead")
          else:
         #sends all the data of heart rate, steps and time to the oled
            comms.send_message(str(int(hr))+","+str(int(steps))+"@"+str(timeNow)+"&"+str(weatherFinal))
            

       


  except(Exception, KeyboardInterrupt) as e:
    print(e) # exiting the program due to exception
  finally:
    print("Closing connection.")
    comms.send_message("sleep")  # stop sending data
    comms.close()