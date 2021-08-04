#include <FastLED.h>
#define LED_PIN     7
#define NUM_LEDS    30
CRGB leds[NUM_LEDS];
String contral="";
int R = 127;
int G = 127;
int B = 127;

void setup() {
  Serial.begin(9600); //设置串口波特率9600
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
}

void loop() {
  while(Serial.available()>0){
    Serial.println(Serial.read());

    R = Serial.read();
    G = Serial.read();
    B = Serial.read();
    for (int i = 0; i <= 29; i++) {
      leds[i] = CRGB (R, G, B);
      FastLED.show();
      delay(300);
    }
  }
  // Red
  for (int i = 0; i <= 29; i++) {
    leds[i] = CRGB (255, 0, 0);
    FastLED.show();
    delay(40);
  }

  // Green
  for (int i = 0; i <= 29; i++) {
    leds[i] = CRGB (0, 255, 0);
    FastLED.show();
    delay(40);
  }

  //  Blue
  for (int i = 0; i <= 29; i++) {
    leds[i] = CRGB (0, 0, 255);
    FastLED.show();
    delay(40);
  }

}
