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
print("RC aktywne: lewa gałka = napęd, prawa = skręt")

x_val = 0
y_val = 0
steer_val = 0
DEADZONE = 0.2

# ================= MOTOR CONTROL =================

def setMotor(motor, power):
    power = max(-1, min(1, power))
    speed = int(abs(power) * 1000)

    if motor == 0:
        pi.write(AIN1, power > 0)
        pi.write(AIN2, power < 0)
        pi.set_PWM_dutycycle(PWMA, speed)

    elif motor == 1:
        pi.write(BIN1, power > 0)
        pi.write(BIN2, power < 0)
        pi.set_PWM_dutycycle(PWMB, speed)


def stopMotors():
    setMotor(0, 0)
    setMotor(1, 0)
    pi.write(STBY, 0)

# ================= STEERING =================

def setSteering(value):
    value = value / 32767

    if abs(value) < SERVO_DEADZONE:
        value = 0

    pulse = SERVO_CENTER + value * (SERVO_MAX - SERVO_CENTER)
    pulse = max(SERVO_MIN, min(SERVO_MAX, pulse))

    pi.set_servo_pulsewidth(SERVO_PIN, pulse)

# ================= MOVEMENT =================

def handleMovement():
    global x_val, y_val

    x = x_val / 32767
    y = y_val / 32767
    y = -y

    if abs(x) < DEADZONE:
        x = 0
    if abs(y) < DEADZONE:
        y = 0

    left = y + x
    right = y - x

    left = max(-1, min(1, left))
    right = max(-1, min(1, right))

    if left == 0 and right == 0:
        stopMotors()
    else:
        pi.write(STBY, 1)
        setMotor(0, left)
        setMotor(1, right)

# ================= MAIN LOOP =================

def main():
    global x_val, y_val, steer_val

    try:
        for event in gamepad.read_loop():

            if event.type == ecodes.EV_ABS:

                # LEWA GAŁKA
                if event.code == ecodes.ABS_X:
                    x_val = event.value

                if event.code == ecodes.ABS_Y:
                    y_val = event.value

                # PRAWA GAŁKA (skręt)
                if event.code == ecodes.ABS_RX:
                    steer_val = event.value
                    setSteering(steer_val)

                handleMovement()

    except KeyboardInterrupt:
        print("STOP")
        stopMotors()
        pi.set_servo_pulsewidth(SERVO_PIN, 0)
        pi.stop()

# ================= START =================

if __name__ == "__main__":
    main()