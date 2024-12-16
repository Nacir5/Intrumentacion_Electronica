#include <Arduino.h>

const int input_Pin = 9;              // Pin for reading analog voltage
char userInput;


float voltage_Value = 0;              // Variable for reading of input pin 
float raw_Data = 0;                   // ADC raw convertion 
float water_Level = 0;                // Water level in cm


float user_value = 10;                   // user level input
float user_valueCod = 1;               // Valor para que la codificacion no se comparene valores negativos

// Visual indicators definitions
#define blinky            11
#define Pump_ON           16
#define LED_Pump_OFF      15

// Macros
#define MAX_RANGE_VALUE   3.3
#define SLOPE             0.15978
#define VOLTAGE_OFFSET    0.83384

// Factor de autocorrección 
#define OFFSET_DECODE     48.00

volatile int pwmDutyCycle = 0; 

// Timer Handler
hw_timer_t *blinkyTimer = NULL;
hw_timer_t *pumpTimer = NULL;

volatile bool blinkyState = false;
volatile bool pumpState = false;
volatile bool enablePump = false;

// Blinky function 
void IRAM_ATTR onBlinkyTimer() {
  blinkyState = !blinkyState; // Toggle the blinky state
  digitalWrite(blinky, blinkyState);
}

// Pump control function
void IRAM_ATTR onPumpTimer() {
  if (enablePump) {
    pumpState = !pumpState; // Toggle the pump state
    digitalWrite(Pump_ON, pumpState);
  } else {
    pumpState = false;
    digitalWrite(Pump_ON, LOW);
  }
}

void setup() {

  // Serial set up
  Serial.begin(9600);

  pinMode(blinky, OUTPUT);
  pinMode(Pump_ON, OUTPUT);
  pinMode(LED_Pump_OFF, OUTPUT);

  // Blinky timer initialization 
  blinkyTimer = timerBegin(0, 80, true); // Timer 0, prescaler 80 (1us per tick)
  timerAttachInterrupt(blinkyTimer, &onBlinkyTimer, true);
  timerAlarmWrite(blinkyTimer, 50000, true); // 500ms interval
  timerAlarmEnable(blinkyTimer);

  // Pump timer initialization
  pumpTimer = timerBegin(1, 80, true); // Timer 1, prescaler 80 (1us per tick)
  timerAttachInterrupt(pumpTimer, &onPumpTimer, true);
  timerAlarmWrite(pumpTimer, 1000000, true); // 1s interval (default)
  timerAlarmEnable(pumpTimer);

  delay(100);

}

void loop() {

  if(Serial.available()> 0){ 
    
      String userInput = Serial.readStringUntil('\n');               // read user input
      //Serial.println("Cadena recibida: '" + userInput + "'");
      if(userInput == "g"){                  // if we get expected value 

        // read the input pin
        raw_Data = analogRead(input_Pin);    

        // Raw Data to Voltage Value
        voltage_Value = ((raw_Data)/(4096))* MAX_RANGE_VALUE;

        // Voltage to water level
        water_Level = ((voltage_Value)-(VOLTAGE_OFFSET))/(SLOPE);

        Serial.println(water_Level); 

      } 

      else{

        userInput.trim(); // Eliminar espacios y saltos de línea
        //Serial.println("Cadena procesada: '" + userInput + "'"); // Depuración después de limpiar

        float new_value = userInput.toFloat(); // Convertir a flotante
        //Serial.println("Valor convertido: " + String(new_value)); // Mostrar el valor convertido

        if (new_value > 0 && new_value <= 10) {
          user_value = new_value; // Actualizar el nivel de agua deseado
          Serial.println("Nuevo nivel deseado: " + String(user_value));
        } else {
          Serial.println("Error: Valor fuera de rango o no válido.");
        }
      }

  }


  if(water_Level > user_value)
  {

      float Reduction = water_Level - user_value;

      // Enable pump control if water level exceeds user value
      enablePump = true;

          // Adjust pump timer frequency based on difference
    if (Reduction > 1.0) {
      timerAlarmWrite(pumpTimer, 1000000, true); // Faster switching (500ms)
    } else if (Reduction > 0.5) {
      timerAlarmWrite(pumpTimer, 500000, true); // Normal switching (1s)
    } else {
      timerAlarmWrite(pumpTimer, 250000, true); // Slower switching (2s)
    }

      // Visual indicators
      digitalWrite(LED_Pump_OFF, LOW);


  } else if (water_Level <= user_value)
 {
    // Disable pump control when water level is below user value
    enablePump = false;

    digitalWrite(Pump_ON, LOW);

    digitalWrite(LED_Pump_OFF, HIGH);
  }

}