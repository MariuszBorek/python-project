from time import sleep
import RPi.GPIO as GPIO
from evdev import InputDevice, ecodes

# ================= GPIO SETUP =================

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

pwmFreq = 100

# Motor driver pins
GPIO.setup(12, GPIO.OUT)  # PWMA
GPIO.setup(18, GPIO.OUT)  # AIN2
GPIO.setup(16, GPIO.OUT)  # AIN1
GPIO.setup(22, GPIO.OUT)  # STBY
GPIO.setup(15, GPIO.OUT)  # BIN1
GPIO.setup(13, GPIO.OUT)  # BIN2
GPIO.setup(11, GPIO.OUT)  # PWMB

pwma = GPIO.PWM(12, pwmFreq)
pwmb = GPIO.PWM(11, pwmFreq)

pwma.start(0)
pwmb.start(0)

GPIO.output(22, GPIO.LOW)  # sterownik na start wyłączony

# ================= GAMEPAD SETUP =================

# SPRAWDŹ numer event!!!
gamepad = InputDevice('/dev/input/event11')

print("Sterowanie padem Xbox aktywne")

x_val = 0
y_val = 0

DEADZONE = 0.2  # większa martwa strefa


# ================= MOTOR CONTROL =================

def setMotor(motor, power):
    power = max(-1, min(1, power))
    speed = abs(power) * 100

    if motor == 0:  # Motor A
        if power > 0:
            GPIO.output(16, GPIO.HIGH)
            GPIO.output(18, GPIO.LOW)
        elif power < 0:
            GPIO.output(16, GPIO.LOW)
            GPIO.output(18, GPIO.HIGH)
        else:  # STOP
            GPIO.output(16, GPIO.LOW)
            GPIO.output(18, GPIO.LOW)
        pwma.ChangeDutyCycle(speed)

    elif motor == 1:  # Motor B
        if power > 0:
            GPIO.output(15, GPIO.HIGH)
            GPIO.output(13, GPIO.LOW)
        elif power < 0:
            GPIO.output(15, GPIO.LOW)
            GPIO.output(13, GPIO.HIGH)
        else:  # STOP
            GPIO.output(15, GPIO.LOW)
            GPIO.output(13, GPIO.LOW)
        pwmb.ChangeDutyCycle(speed)


def stopMotors():
    setMotor(0, 0)
    setMotor(1, 0)
    GPIO.output(22, GPIO.LOW)  # wyłącz sterownik


# ================= MOVEMENT LOGIC =================

def handleMovement():
    global x_val, y_val

    # Normalizacja -32768 do 32767 → -1 do 1
    x = x_val / 32767
    y = y_val / 32767

    y = -y  # odwrócenie osi Y

    # Deadzone
    if abs(x) < DEADZONE:
        x = 0
    if abs(y) < DEADZONE:
        y = 0

    # Napęd różnicowy (dwa silniki)
    left = y + x
    right = y - x

    left = max(-1, min(1, left))
    right = max(-1, min(1, right))

    # Jeśli joystick w centrum → wyłącz silniki
    if left == 0 and right == 0:
        stopMotors()
    else:
        GPIO.output(22, GPIO.HIGH)  # włącz sterownik
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
        GPIO.cleanup()


# ================= START =================

if __name__ == "__main__":
    main()