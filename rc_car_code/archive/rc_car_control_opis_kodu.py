import pigpio  # biblioteka do niskopoziomowego sterowania GPIO z PWM
from evdev import InputDevice, ecodes  # biblioteka do obsługi kontrolera / pada

# ================= PIGPIO SETUP =================

pi = pigpio.pi()  # inicjalizacja połączenia z daemonem pigpio

if not pi.connected:  # jeśli nie udało się połączyć z pigpiod
    print("Brak połączenia z pigpio!")
    exit()  # zakończ program

pwmFreq = 20000  # częstotliwość PWM dla silników (20 kHz)

# ====== PINY SILNIKÓW ======
PWMA = 18  # PWM dla silnika A
AIN2 = 24  # kierunek A2 dla silnika A
AIN1 = 23  # kierunek A1 dla silnika A
STBY = 25  # włączenie / wyłączenie mostka H (standby)
BIN1 = 22  # kierunek B1 dla silnika B
BIN2 = 27  # kierunek B2 dla silnika B
PWMB = 17  # PWM dla silnika B

# ====== SERWO ======
SERVO_PIN = 12  # pin sygnału serwa
SERVO_CENTER = 1500  # impuls środkowy (90°)
SERVO_MIN = 1000  # minimalny impuls (0°)
SERVO_MAX = 2000  # maksymalny impuls (180°)
SERVO_DEADZONE = 0.1  # martwa strefa joysticka, aby serwo nie drgało

# lista wszystkich pinów silników, żeby łatwo ustawić OUTPUT
motorPins = [PWMA, AIN2, AIN1, STBY, BIN1, BIN2, PWMB]

# ustawienie wszystkich pinów silników jako wyjścia
for pin in motorPins:
    pi.set_mode(pin, pigpio.OUTPUT)

# konfiguracja PWM dla silników
pi.set_PWM_frequency(PWMA, pwmFreq)
pi.set_PWM_frequency(PWMB, pwmFreq)

pi.set_PWM_range(PWMA, 1000)  # zakres PWM 0-1000
pi.set_PWM_range(PWMB, 1000)

# ustawienie początkowej mocy silników na 0
pi.set_PWM_dutycycle(PWMA, 0)
pi.set_PWM_dutycycle(PWMB, 0)

pi.write(STBY, 0)  # wyłączenie mostka H (silniki nie pracują)

# ustawienie serwa w pozycji środkowej (90°)
pi.set_servo_pulsewidth(SERVO_PIN, SERVO_CENTER)

# ================= GAMEPAD =================

# podłączenie do pada
gamepad = InputDevice('/dev/input/event11')
print("RT = gaz | LT = wsteczny | B = hamulec | Lewa gałka = skręt")

# zmienne do przechowywania wartości joysticków i przycisków
steer_val = 0      # skręt serwa
throttle = 0       # gaz
reverse = 0        # cofanie
brake_pressed = False  # stan przycisku B

# ================= MOTOR CONTROL =================

def setMotorPower(power):
    """
    power: -1 (max wstecz) → 0 → 1 (max przód)
    """
    power = max(-1, min(1, power))  # ograniczenie wartości do [-1,1]
    speed = int(abs(power) * 1000)  # moc silnika w zakresie PWM 0-1000

    # jeśli przycisk hamulca jest wciśnięty
    if brake_pressed:
        # ustawienie wszystkich pinów LOW → natychmiastowe zatrzymanie silników
        pi.write(AIN1, 0)
        pi.write(AIN2, 0)
        pi.write(BIN1, 0)
        pi.write(BIN2, 0)
        pi.set_PWM_dutycycle(PWMA, 0)
        pi.set_PWM_dutycycle(PWMB, 0)
        pi.write(STBY, 0)  # wyłączenie mostka H
        return  # wyjście z funkcji, nie sterujemy dalej

    # kierunek jazdy do przodu
    if power > 0:
        pi.write(AIN1, 1)
        pi.write(AIN2, 0)
        pi.write(BIN1, 1)
        pi.write(BIN2, 0)
    # kierunek jazdy do tyłu
    elif power < 0:
        pi.write(AIN1, 0)
        pi.write(AIN2, 1)
        pi.write(BIN1, 0)
        pi.write(BIN2, 1)
    # jeśli power = 0 → brak ruchu
    else:
        pi.write(AIN1, 0)
        pi.write(AIN2, 0)
        pi.write(BIN1, 0)
        pi.write(BIN2, 0)

    # ustawienie mocy PWM dla obu silników
    pi.set_PWM_dutycycle(PWMA, speed)
    pi.set_PWM_dutycycle(PWMB, speed)

    # włączenie STBY jeśli silnik ma moc != 0
    pi.write(STBY, 1 if power != 0 else 0)

# ================= STEERING =================

def setSteering(value):
    # normalizacja wartości joysticka -32768..32767 → -1..1
    value = value / 32767

    # martwa strefa, żeby serwo się nie drgało
    if abs(value) < SERVO_DEADZONE:
        value = 0

    # obliczenie impulsu dla serwa
    pulse = SERVO_CENTER + value * (SERVO_MAX - SERVO_CENTER)
    pulse = max(SERVO_MIN, min(SERVO_MAX, pulse))  # ograniczenie do zakresu 1000-2000 µs

    pi.set_servo_pulsewidth(SERVO_PIN, pulse)  # wysłanie sygnału do serwa

# ================= MAIN LOOP =================

def main():
    global steer_val, throttle, reverse, brake_pressed

    try:
        # pętla odczytu eventów z pada
        for event in gamepad.read_loop():

            # ----- GAŁKI I TRIGGERY -----
            if event.type == ecodes.EV_ABS:

                # lewa gałka X → skręt serwa
                if event.code == ecodes.ABS_X:
                    steer_val = event.value
                    setSteering(steer_val)

                # prawy trigger (RT) → gaz
                if event.code == ecodes.ABS_RZ:
                    throttle = event.value / 255  # normalizacja 0..1

                # lewy trigger (LT) → cofanie
                if event.code == ecodes.ABS_Z:
                    reverse = event.value / 255  # normalizacja 0..1

                # moc = gaz - cofanie
                power = throttle - reverse
                setMotorPower(power)  # ustawienie silników

            # ----- PRZYCISKI -----
            if event.type == ecodes.EV_KEY:

                # przycisk B → hamulec
                if event.code == ecodes.BTN_EAST:
                    brake_pressed = (event.value == 1)  # True jeśli wciśnięty
                    setMotorPower(0)  # natychmiast zatrzymaj silniki

    except KeyboardInterrupt:  # CTRL+C
        print("STOP")
        setMotorPower(0)  # zatrzymanie silników
        pi.set_servo_pulsewidth(SERVO_PIN, 0)  # wyłączenie serwa
        pi.stop()  # zamknięcie połączenia z pigpio

# ================= START =================

if __name__ == "__main__":
    main()  # uruchomienie głównej pętli