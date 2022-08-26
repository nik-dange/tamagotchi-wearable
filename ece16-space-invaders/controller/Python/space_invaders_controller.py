"""
@author: Ramsin Khoshabeh
"""

from ECE16Lib.Communication import Communication
from time import sleep
import socket, pygame

# Setup the Socket connection to the Space Invaders game
host = "127.0.0.1"
port = 65432
mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(mySocket.connect((host, port)))
mySocket.setblocking(False)
mySocket.send("Begin".encode("utf-8"))

class PygameController:
  comms = None

  def __init__(self, serial_name, baud_rate):
    self.comms = Communication(serial_name, baud_rate)

  def run(self):
    # 1. make sure data sending is stopped by ending streaming
    self.comms.send_message("stop")
    self.comms.clear()

    # 2. start streaming orientation data
    input("Ready to start? Hit enter to begin.\n")
    self.comms.send_message("start")

    # 3. Forever collect orientation and send to PyGame until user exits
    print("Use <CTRL+C> to exit the program.\n")
    while True:
      message = self.comms.receive_message()
      try:
        oled_score, _ = mySocket.recvfrom(1024)
        #print(f"before: {oled_score}")
        oled_score = oled_score.decode("utf-8")
        #print(f"after: {oled_score}") 
        self.comms.send_message(oled_score)
      except Exception as e:
        #print(e)
        pass
 
      if(message != None):
        command = None
        message = int(message)
        # if message == 0:
        #   command = "FLAT"
        # if message == 1:
        #   command = "UP"
        if message == 5:
          command = "FIRE"
        ##supershoot is for tilt+ button  
        elif message == 8:
          command ="SUPERSHOOT"
        elif message == 3:
          command = "LEFT"
        elif message == 4:
          command = "RIGHT"
        elif message == 6:
        ##superleft is for extremely left tilts
          command="SUPERLEFT"
        elif message == 7: 
        ##superright is for extremely right tilts
          command="SUPERRIGHT"

        if command is not None:
          mySocket.send(command.encode("UTF-8"))


if __name__== "__main__":
  serial_name = '/dev/cu.NIKECE16-6'
  baud_rate = 115200
  controller = PygameController(serial_name, baud_rate)

  try:
    controller.run()
  except(Exception, KeyboardInterrupt) as e:
    print(e)
  finally:
    print("Exiting the program.")
    controller.comms.send_message("stop")
    controller.comms.close()
    mySocket.send("QUIT".encode("UTF-8"))
    mySocket.close()

  input("[Press ENTER to finish.]")
