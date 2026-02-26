import pigpio
from evdev import InputDevice, ecodes

# ================= PIGPIO SETUP =================

pi = pigpio.pi()

if not pi.connected:
    print("Brak połączenia z pigpio!")
    exit()

pwmFreq = 20000  # 20 kHz dla silników

# ====== PINY SILNIKÓW ======
PWMA = 18
AIN2 = 24
AIN1 = 23
STBY = 25
BIN1 = 22
BIN2 = 27
PWMB = 17

# ====== SERWO ======
SERVO_PIN = 12
SERVO_CENTER = 1500
SERVO_MIN = 1000
SERVO_MAX = 2000
SERVO_DEADZONE = 0.1

motorPins = [PWMA, AIN2, AIN1, STBY, BIN1, BIN2, PWMB]

for pin in motorPins:
    pi.set_mode(pin, pigpio.OUTPUT)

# PWM konfiguracja silników
pi.set_PWM_frequency(PWMA, pwmFreq)
pi.set_PWM_frequency(PWMB, pwmFreq)

pi.set_PWM_range(PWMA, 1000)
pi.set_PWM_range(PWMB, 1000)

pi.set_PWM_dutycycle(PWMA, 0)
pi.set_PWM_dutycycle(PWMB, 0)

pi.write(STBY, 0)

# Serwo start w centrum
pi.set_servo_pulsewidth(SERVO_PIN, SERVO_CENTER)

# ================= GAMEPAD =================

gamepad = InputDevice('/dev/input/event11')
print("RT = gaz | LT = hamulec | Lewa gałka = skręt")

steer_val = 0
throttle = 0
brake = 0

# ================= MOTOR CONTROL =================

def setMotorPower(power):
    """
    power: -1 (max wstecz) → 0 → 1 (max przód)
    """
    power = max(-1, min(1, power))
    speed = int(abs(power) * 1000)

    if power > 0:
        pi.write(AIN1, 1)
        pi.write(AIN2, 0)
        pi.write(BIN1, 1)
        pi.write(BIN2, 0)
    elif power < 0:
        pi.write(AIN1, 0)
        pi.write(AIN2, 1)
        pi.write(BIN1, 0)
        pi.write(BIN2, 1)
    else:
        pi.write(AIN1, 0)
        pi.write(AIN2, 0)
        pi.write(BIN1, 0)
        pi.write(BIN2, 0)

    pi.set_PWM_dutycycle(PWMA, speed)
    pi.set_PWM_dutycycle(PWMB, speed)

    if power == 0:
        pi.write(STBY, 0)
    else:
        pi.write(STBY, 1)

# ================= STEERING =================

def setSteering(value):
    # Normalizacja -32768 → 32767
    value = value / 32767

    if abs(value) < SERVO_DEADZONE:
        value = 0

    pulse = SERVO_CENTER + value * (SERVO_MAX - SERVO_CENTER)
    pulse = max(SERVO_MIN, min(SERVO_MAX, pulse))

    pi.set_servo_pulsewidth(SERVO_PIN, pulse)

# ================= MAIN LOOP =================

def main():
    global steer_val, throttle, brake

    try:
        for event in gamepad.read_loop():

            if event.type == ecodes.EV_ABS:

                # ----- SKRĘT (LEWA GAŁKA) -----
                if event.code == ecodes.ABS_X:
                    steer_val = event.value
                    setSteering(steer_val)

                # ----- LT (HAMULEC / WSTECZNY) -----
                if event.code == ecodes.ABS_Z:
                    brake = event.value / 255  # triggery 0–255

                # ----- RT (GAZ) -----
                if event.code == ecodes.ABS_RZ:
                    throttle = event.value / 255

                # Moc = gaz - hamulec
                power = throttle - brake

                setMotorPower(power)

    except KeyboardInterrupt:
        print("STOP")
        setMotorPower(0)
        pi.set_servo_pulsewidth(SERVO_PIN, 0)
        pi.stop()

# ================= START =================

if __name__ == "__main__":
    main()