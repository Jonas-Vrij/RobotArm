#include <Wire.h>
#include <Servo.h>


Servo elbow;
Servo shoulder;
Servo base;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(13, OUTPUT);

  elbow.attach(10);
  shoulder.attach(9);
  base.attach(8);

  elbow.write(0);
  shoulder.write(0);
  base.write(0);
  
}

void loop() { 
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0){
    String msg = Serial.readString();
    updateServos(msg);
    if(msg == "exit "){
      Serial.println("Exit");
      exit(0);
    } 
}
}


void updateServos(String msg) {
  int _index = msg.indexOf('_');
  int last_index = msg.lastIndexOf('_');
  int alphaAngle = msg.substring(0,_index).toInt();
  int betaAngle = msg.substring(_index + 1, last_index).toInt();
  //int radiantAngle = msg.substring(last_index + 1, -1).toInt();
  shoulder.write(180-alphaAngle);
  elbow.write(180-betaAngle);

}