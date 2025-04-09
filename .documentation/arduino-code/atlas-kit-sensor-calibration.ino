#include <iot_cmd.h>
#include <sequencer4.h>                 //4-step sequencer
#include <sequencer1.h>                 //1-step sequencer (not used anymore)
#include <Ezo_i2c_util.h>               //common print utils
#include <Ezo_i2c.h>                    //Atlas Scientific EZO I2C lib
#include <Wire.h>                       //I2C library

Ezo_board PH = Ezo_board(99, "PH");
Ezo_board EC = Ezo_board(100, "EC");
Ezo_board RTD = Ezo_board(102, "RTD");
Ezo_board PMP = Ezo_board(103, "PMP");

Ezo_board device_list[] = { PH, EC, RTD, PMP };
Ezo_board* default_board = &device_list[0];
const uint8_t device_list_len = sizeof(device_list) / sizeof(device_list[0]);

// For version 1.5
const int EN_PH = 12;
const int EN_EC = 27;
const int EN_RTD = 15;
const int EN_AUX = 33;

const unsigned long reading_delay = 1000;
unsigned int poll_delay = 2000 - reading_delay * 2 - 300;

#define PUMP_BOARD        PMP
#define PUMP_DOSE         -0.5
#define EZO_BOARD         EC
#define IS_GREATER_THAN   true
#define COMPARISON_VALUE  1000

float k_val = 0;
bool polling = true;

void step1();
void step2();
void step3();
void step4();

Sequencer4 Seq(&step1, reading_delay,
               &step2, 300,
               &step3, reading_delay,
               &step4, poll_delay);

void setup() {
  pinMode(EN_PH, OUTPUT);
  pinMode(EN_EC, OUTPUT);
  pinMode(EN_RTD, OUTPUT);
  pinMode(EN_AUX, OUTPUT);
  digitalWrite(EN_PH, LOW);
  digitalWrite(EN_EC, LOW);
  digitalWrite(EN_RTD, HIGH);
  digitalWrite(EN_AUX, LOW);

  Wire.begin();
  Serial.begin(9600);

  Seq.reset();
}

void loop() {
  String cmd;

  if (receive_command(cmd)) {
    polling = false;
    if (!process_coms(cmd)) {
      process_command(cmd, device_list, device_list_len, default_board);
    }
  }

  if (polling == true) {
    Seq.run();
  }
}

void pump_function(Ezo_board &pump, Ezo_board &sensor, float value, float dose, bool greater_than) {
  if (sensor.get_error() == Ezo_board::SUCCESS) {
    bool comparison = greater_than
      ? (sensor.get_last_received_reading() >= value)
      : (sensor.get_last_received_reading() <= value);
    if (comparison) {
      pump.send_cmd_with_num("d,", dose);
      delay(100);
      Serial.print(pump.get_name());
      Serial.print(" ");
      char response[20];
      if (pump.receive_cmd(response, 20) == Ezo_board::SUCCESS) {
        Serial.print("pump dispensed ");
      } else {
        Serial.print("pump error ");
      }
      Serial.println(response);
    } else {
      pump.send_cmd("x");
    }
  }
}

void step1() {
  RTD.send_read_cmd();
}

void step2() {
  receive_and_print_reading(RTD);
  if ((RTD.get_error() == Ezo_board::SUCCESS) && (RTD.get_last_received_reading() > -1000.0)) {
    PH.send_cmd_with_num("T,", RTD.get_last_received_reading());
    EC.send_cmd_with_num("T,", RTD.get_last_received_reading());
  } else {
    PH.send_cmd_with_num("T,", 25.0);
    EC.send_cmd_with_num("T,", 25.0);
  }
  Serial.print(" ");
}

void step3() {
  PH.send_read_cmd();
  EC.send_read_cmd();
}

void step4() {
  receive_and_print_reading(PH);
  Serial.print("  ");
  receive_and_print_reading(EC);
  Serial.println();
  pump_function(PUMP_BOARD, EZO_BOARD, COMPARISON_VALUE, PUMP_DOSE, IS_GREATER_THAN);
}

void start_datalogging() {
  polling = true;
}

bool process_coms(const String &string_buffer) {
  if (string_buffer == "HELP") {
    print_help();
    return true;
  }
  else if (string_buffer.startsWith("DATALOG")) {
    start_datalogging();
    return true;
  }
  else if (string_buffer.startsWith("POLL")) {
    polling = true;
    Seq.reset();

    int16_t index = string_buffer.indexOf(',');
    if (index != -1) {
      float new_delay = string_buffer.substring(index + 1).toFloat();
      float mintime = reading_delay * 2 + 300;
      if (new_delay >= (mintime / 1000.0)) {
        Seq.set_step4_time((new_delay * 1000.0) - mintime);
      } else {
        Serial.println("delay too short");
      }
    }
    return true;
  }
  return false;
}

void get_ec_k_value() {
  char rx_buf[10];
  EC.send_cmd("k,?");
  delay(300);
  if (EC.receive_cmd(rx_buf, 10) == Ezo_board::SUCCESS) {
    k_val = String(rx_buf).substring(3).toFloat();
  }
}

void print_help() {
  get_ec_k_value();
  Serial.println(F("Atlas Scientific I2C hydroponics kit"));
  Serial.println(F("Commands:"));
  Serial.println(F("poll             Takes readings continuously of all sensors"));
  Serial.println(F(""));
  Serial.println(F("ph:cal,mid,7     calibrate to pH 7"));
  Serial.println(F("ph:cal,low,4     calibrate to pH 4"));
  Serial.println(F("ph:cal,high,10   calibrate to pH 10"));
  Serial.println(F("ph:cal,clear     clear calibration"));
  Serial.println(F(""));
  Serial.println(F("ec:cal,dry           calibrate a dry EC probe"));
  Serial.println(F("ec:k,[n]             switch K values: 0.1, 1, or 10"));
  Serial.println(F("ec:cal,clear         clear calibration"));

  if (k_val > 9) {
    Serial.println(F("For K10 probes: ec:cal,low,12880 / ec:cal,high,150000"));
  } else if (k_val > .9) {
    Serial.println(F("For K1 probes: ec:cal,low,12880 / ec:cal,high,80000"));
  } else if (k_val > .09) {
    Serial.println(F("For K0.1 probes: ec:cal,low,84 / ec:cal,high,1413"));
  }

  Serial.println(F(""));
  Serial.println(F("rtd:cal,t            calibrate temp probe to temp 't'"));
  Serial.println(F("rtd:cal,clear        clear calibration"));
}
