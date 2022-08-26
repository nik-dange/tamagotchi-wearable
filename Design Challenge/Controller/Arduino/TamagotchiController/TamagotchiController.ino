/*
 * Global variables
 */
// Acceleration values recorded from the readAccelSensor() function
int ax = 0; int ay = 0; int az = 0;
int ppg = 0;        // PPG from readPhotoSensor() (in Photodetector tab)
int sampleTime = 0; // Time of last sample (in Sampling tab)
bool sending;
int PIN=14;
int changestate=0;
int changeMotorState=0;
//initializing strings for the different displays on the OLED
String heartRate="0";
String stepCount="0";
String timeIs="0";
String weatherNow="0";


//initializing timers
unsigned long starting=millis();
unsigned long starting2=millis();
unsigned long ending=millis();
unsigned long ending2=millis();
int defaultVal=digitalRead(PIN);
int buttonState=digitalRead(PIN);
/*
 * Initialize the various components of the wearable
 */
void setup() {
  setupAccelSensor();
  setupCommunication();
  setupDisplay();
  setupPhotoSensor();
  setupMotor();
  sending = false;
  writeDisplay("Sleep", 0, true);
}

/*
 * The main processing loop
 */
void loop() {
  String command = receiveMessage();
  if(command == "sleep") {
    sending = false;
    writeDisplay("Sleep", 0, true);
  }
  else if(command == "wearable") {
    sending = true;
    writeDisplay("Wearable", 0, true);
  }
  else 
    //uses the substring command to piece apart the intake string. We used a ',' and '@' to denote
    //where the string is split 
    //must be initialized as a global variable or the program freaks out.
    
    heartRate=command.substring(0,command.indexOf(','));
    stepCount=command.substring(command.indexOf(',')+1,command.indexOf('@'));
    timeIs=command.substring(command.indexOf('@')+1,command.indexOf('&'));
    weatherNow=command.substring(command.indexOf('&')+1,command.length());
    
    
    String message1="Heart rate: "+String(heartRate)+","+"Step Count: "+String(stepCount)+","+"Time: "+String(timeIs);
    String message2="Time: "+String(timeIs)+","+String(weatherNow);

    //right before button press, it reads the button value
    //and compares it to the default
    //if it changes and its been more than 500ms then the button registers
    ending=millis();
    defaultVal=digitalRead(PIN);
    if(buttonState!=defaultVal && ending-starting > 500)
    {
      starting=millis();
      //changestate denotes what will be displayed
        if(changestate==0)
        { 
          changestate=1;
        }
        else if(changestate==1)
        {
          changestate=0;
        }
        changeMotorState=1;
    }
    if (changestate==0)
    {
      //if change state is 0, it will display the hr, time, and  steps
      writeDisplayCSV(message1.c_str(),2); 
    } 
    if (changestate==1)
    {
      //otherwise it will display the weather and time
      writeDisplayCSV(message2.c_str(),1); 
    }
    
    //if the motor state is 1, it will begin a timer.
    //This timer will count up to 1000ms and buzz the motor
    //once it hits 1000ms, it shuts the motor off.
    if(changeMotorState==1)
    {
      ending2=millis(); 
      starting2=millis();
      changeMotorState=2;
    }
    if(ending2-starting2<1000 && changeMotorState==2)
    {
      ending2=millis();
      activateMotor(255);
    }
    else if(ending2-starting2>1000 && changeMotorState==2) 
    {
      deactivateMotor();
      changeMotorState=0;
    }
    

  if(sending && sampleSensors()) {
    String response = String(sampleTime) + ",";
    response += String(ax) + "," + String(ay) + "," + String(az);
    response += "," + String(ppg);
    sendMessage(response);
  }
}
