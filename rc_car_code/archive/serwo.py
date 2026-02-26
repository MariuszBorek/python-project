import pigpio
from evdev import InputDevice, ecodes

# ================= SETUP =================

SERVO_PIN = 12
DEADZONE = 0.1

pi = pigpio.pi()
if not pi.connected:
    print("Brak połączenia z pigpiod")
    exit()

# SPRAWDŹ swój numer event!
gamepad = InputDevice('/dev/input/event11')

print("Sterowanie serwem prawą gałką aktywne")

# ================= SERVO FUNCTION =================

def set_angle(angle):
    angle = max(0, min(180, angle))
    pulse = 1000 + (angle / 180.0) * 1000
    pi.set_servo_pulsewidth(SERVO_PIN, pulse)

# Start na środku
set_angle(90)

# ================= MAIN LOOP =================

try:
    for event in gamepad.read_loop():

        if event.type == ecodes.EV_ABS:

            # PRAWA GAŁKA POZIOMO
            if event.code == ecodes.ABS_RX:

                # Normalizacja -32768 → 32767 do -1 → 1
                value = event.value / 32767

                # Deadzone
                if abs(value) < DEADZONE:
                    value = 0

                # Mapowanie -1..1 → 0..180
                angle = (value + 1) * 90

                set_angle(angle)

except KeyboardInterrupt:
    print("STOP")
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()