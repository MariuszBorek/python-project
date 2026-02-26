import pigpio
from evdev import InputDevice, ecodes

# ================= PIGPIO SETUP =================

pi = pigpio.pi()

if not pi.connected:
    print("Brak połączenia z pigpio!")
    exit()

pwmFreq = 20000  # 20 kHz - dobre dla silników DC

# ====== BCM NUMERY PINÓW (poprawione!) ======
PWMA = 18   # BOARD 12
AIN2 = 24   # BOARD 18
AIN1 = 23   # BOARD 16
STBY = 25   # BOARD 22
BIN1 = 22   # BOARD 15
BIN2 = 27   # BOARD 13
PWMB = 17   # BOARD 11

pins = [PWMA, AIN2, AIN1, STBY, BIN1, BIN2, PWMB]

for pin in pins:
    pi.set_mode(pin, pigpio.OUTPUT)

# Konfiguracja PWM
pi.set_PWM_frequency(PWMA, pwmFreq)
pi.set_PWM_frequency(PWMB, pwmFreq)

pi.set_PWM_range(PWMA, 1000)
pi.set_PWM_range(PWMB, 1000)

pi.set_PWM_dutycycle(PWMA, 0)
pi.set_PWM_dutycycle(PWMB, 0)

pi.write(STBY, 0)  # sterownik wyłączony na start

# ================= GAMEPAD SETUP =================

gamepad = InputDevice('/dev/input/event11')

print("Sterowanie padem Xbox aktywne (pigpio)")

x_val = 0
y_val = 0
DEADZONE = 0.2

# ================= MOTOR CONTROL =================

def setMotor(motor, power):
    power = max(-1, min(1, power))
    speed = int(abs(power) * 1000)

    if motor == 0:  # Motor A
        if power > 0:
            pi.write(AIN1, 1)
            pi.write(AIN2, 0)
        elif power < 0:
            pi.write(AIN1, 0)
            pi.write(AIN2, 1)
        else:
            pi.write(AIN1, 0)
            pi.write(AIN2, 0)

        pi.set_PWM_dutycycle(PWMA, speed)

    elif motor == 1:  # Motor B
        if power > 0:
            pi.write(BIN1, 1)
            pi.write(BIN2, 0)
        elif power < 0:
            pi.write(BIN1, 0)
            pi.write(BIN2, 1)
        else:
            pi.write(BIN1, 0)
            pi.write(BIN2, 0)

        pi.set_PWM_dutycycle(PWMB, speed)


def stopMotors():
    setMotor(0, 0)
    setMotor(1, 0)
    pi.write(STBY, 0)


# ================= MOVEMENT LOGIC =================

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
    global x_val, y_val

    try:
        for event in gamepad.read_loop():

            if event.type == ecodes.EV_ABS:

                if event.code == ecodes.ABS_X:
                    x_val = event.value

                if event.code == ecodes.ABS_Y:
                    y_val = event.value

                handleMovement()

    except KeyboardInterrupt:
        print("STOP")
        stopMotors()
        pi.stop()


# ================= START =================

if __name__ == "__main__":
    main()