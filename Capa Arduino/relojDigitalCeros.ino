const bool CATHODE_COMMON = true;

// Pines de segmentos por display (a,b,c,d,e,f,g)
const int decenasPins[7]  = {13, 19, 18, 17, 16, 14, 21};
const int unidadesPins[7] = {22, 32, 27, 26, 25, 23, 33};

// Mapa de segmentos (a,b,c,d,e,f,g) para dígitos 0–9
const byte DIGITOS[10][7] = {
  {1,1,1,1,1,1,0}, // 0
  {0,1,1,0,0,0,0}, // 1
  {1,1,0,1,1,0,1}, // 2
  {1,1,1,1,0,0,1}, // 3
  {0,1,1,0,0,1,1}, // 4
  {1,0,1,1,0,1,1}, // 5
  {1,0,1,1,1,1,1}, // 6
  {1,1,1,0,0,0,0}, // 7
  {1,1,1,1,1,1,1}, // 8
  {1,1,1,1,0,1,1}  // 9
};

// Segmentos para "E" (error)
const byte ERROR_SEG[7] = {1,0,0,1,1,1,1};

int contador = 0;
unsigned long t0 = 0;
bool running = false;
bool ascendiendo = true;

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < 7; i++) {
    pinMode(decenasPins[i], OUTPUT);
    pinMode(unidadesPins[i], OUTPUT);
  }
  apagarDisplays();
  mostrarNumero(0);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "STARTUP") { running = true; ascendiendo = true; }
    else if (cmd == "STARTDOWN") { running = true; ascendiendo = false; }
    else if (cmd == "STOP") { running = false; }
    else if (cmd == "RESET") { contador = 0; mostrarNumero(contador); }
    else if (cmd.startsWith("DISPLAY:")) {
      String val = cmd.substring(8);
      if (val == "ERROR") {
        mostrarError();
      } else {
        int numero = val.toInt();
        if (numero < 0) numero = 0;
        if (numero > 99) numero = 99;
        contador = numero;
        mostrarNumero(contador);
      }
    }
  }

  unsigned long t = millis();
  if (running && (t - t0 >= 1000)) {
    t0 = t;
    if (ascendiendo) {
      contador++;
      if (contador > 99) contador = 0;
    } else {
      contador--;
      if (contador < 0) contador = 99;
    }
    mostrarNumero(contador);
    Serial.print("VALOR:");
    Serial.println(contador);
  }
}

void mostrarNumero(int num) {
  int dec = num / 10;
  int uni = num % 10;
  mostrarDigitoEn(dec, decenasPins);
  mostrarDigitoEn(uni, unidadesPins);
}

void mostrarDigitoEn(int dig, const int pins[7]) {
  for (int s = 0; s < 7; s++) {
    bool on_raw = DIGITOS[dig][s];
    bool level  = CATHODE_COMMON ? on_raw : !on_raw;
    digitalWrite(pins[s], level ? HIGH : LOW);
  }
}

void mostrarError() {
  mostrarCustom(ERROR_SEG, decenasPins);
  mostrarCustom(ERROR_SEG, unidadesPins);
}

void mostrarCustom(const byte segs[7], const int pins[7]) {
  for (int s = 0; s < 7; s++) {
    bool level = CATHODE_COMMON ? segs[s] : !segs[s];
    digitalWrite(pins[s], level ? HIGH : LOW);
  }
}

void apagarDisplays() {
  for (int i = 0; i < 7; i++) {
    digitalWrite(decenasPins[i], CATHODE_COMMON ? LOW : HIGH);
    digitalWrite(unidadesPins[i], CATHODE_COMMON ? LOW : HIGH);
  }
}
