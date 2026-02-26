# Sterowanie samochodem RC za pomocą gamepada i Raspberry Pi
# version: 1.0.0
# 1. Uruchom demona pigpio
#
# Wpisz:
# sudo systemctl start pigpiod
#
# Potem sprawdź:
# sudo systemctl status pigpiod
#
# Powinno być:
# Active: active (running)
#
# 2. Jeśli chcesz, żeby uruchamiał się automatycznie po restarcie
# sudo systemctl enable pigpiod
#
# 3. Alternatywa (jednorazowo)
#
# Możesz też po prostu uruchomić:
# sudo pigpiod
#
# To działa do restartu systemu.

import pigpio
from evdev import InputDevice, ecodes

# ================= PIGPIO SETUP =================

pi = pigpio.pi()

if not pi.connected:
    print("Brak połączenia z pigpio!")
    exit()

pwmFreq = 20000

PWMA = 18
AIN2 = 24
AIN1 = 23
STBY = 25
BIN1 = 22
BIN2 = 27
PWMB = 17

SERVO_PIN = 12
SERVO_CENTER = 1500
SERVO_MIN = 1000
SERVO_MAX = 2000
SERVO_DEADZONE = 0.1

motorPins = [PWMA, AIN2, AIN1, STBY, BIN1, BIN2, PWMB]

for pin in motorPins:
    pi.set_mode(pin, pigpio.OUTPUT)

pi.set_PWM_frequency(PWMA, pwmFreq)
pi.set_PWM_frequency(PWMB, pwmFreq)

pi.set_PWM_range(PWMA, 1000)
pi.set_PWM_range(PWMB, 1000)

pi.set_PWM_dutycycle(PWMA, 0)
pi.set_PWM_dutycycle(PWMB, 0)

pi.write(STBY, 0)

pi.set_servo_pulsewidth(SERVO_PIN, SERVO_CENTER)

# ================= GAMEPAD =================

gamepad = InputDevice('/dev/input/event11')
print("RT = gaz | LT = wsteczny | B = hamulec | Lewa gałka = skręt")

steer_val = 0
throttle = 0
reverse = 0
brake_pressed = False

# ================= MOTOR CONTROL =================

def setMotorPower(power):
    power = max(-1, min(1, power))
    speed = int(abs(power) * 1000)

    if brake_pressed:
        # HAMULEC - twarde zatrzymanie
        pi.write(AIN1, 0)
        pi.write(AIN2, 0)
        pi.write(BIN1, 0)
        pi.write(BIN2, 0)
        pi.set_PWM_dutycycle(PWMA, 0)
        pi.set_PWM_dutycycle(PWMB, 0)
        pi.write(STBY, 0)
        return

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

    pi.write(STBY, 1 if power != 0 else 0)

# ================= STEERING =================

def setSteering(value):
    value = value / 32767

    if abs(value) < SERVO_DEADZONE:
        value = 0

    pulse = SERVO_CENTER + value * (SERVO_MAX - SERVO_CENTER)
    pulse = max(SERVO_MIN, min(SERVO_MAX, pulse))

    pi.set_servo_pulsewidth(SERVO_PIN, pulse)

# ================= MAIN LOOP =================

def main():
    global steer_val, throttle, reverse, brake_pressed

    try:
        for event in gamepad.read_loop():

            # ----- GAŁKI I TRIGGERY -----
            if event.type == ecodes.EV_ABS:

                if event.code == ecodes.ABS_X:
                    steer_val = event.value
                    setSteering(steer_val)

                if event.code == ecodes.ABS_RZ:  # RT
                    throttle = event.value / 255

                if event.code == ecodes.ABS_Z:  # LT
                    reverse = event.value / 255

                power = throttle - reverse
                setMotorPower(power)

            # ----- PRZYCISKI -----
            if event.type == ecodes.EV_KEY:

                if event.code == ecodes.BTN_EAST:  # B button
                    brake_pressed = (event.value == 1)
                    setMotorPower(0)

    except KeyboardInterrupt:
        print("STOP")
        setMotorPower(0)
        pi.set_servo_pulsewidth(SERVO_PIN, 0)
        pi.stop()

# ================= START =================

if __name__ == "__main__":
    main()