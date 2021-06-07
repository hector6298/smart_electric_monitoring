
double ac_read(int sampleDuration, int rZero) {
  int rVal = 0;
  int sampleCount = 0;
  unsigned long rSquaredSum = 0;         
  uint32_t startTime = millis();  // take samples for 100ms
  while((millis()-startTime) < sampleDuration)
  {
    rVal = analogRead(A0) - rZero;
    rSquaredSum += rVal * rVal;
    sampleCount++;
  }
  double voltRMS = 5.0 * sqrt(rSquaredSum / sampleCount) / 1024.0;
  double ampsRMS = (voltRMS*66.0);
  return ampsRMS;
}

double get_power(double amps){
  return amps * 110;
}

int calibrate(){
  for( int i=0; i<50; i++){
    initial_read += analogRead(A0);
    millis();
  }
  initial_read /= 50;
  rZero = initial_read;
  return rZero;
}
