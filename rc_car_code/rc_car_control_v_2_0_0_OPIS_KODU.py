# Import biblioteki do sterowania GPIO przez demona pigpio
import pigpio

# Biblioteka do obsługi kontrolera Xbox
import pygame

# Biblioteka do opóźnień (sleep)
import time


# ==================================================
# ================ RACING CONTROLLER ===============
# ==================================================

class RacingController:

    def __init__(self):
        # Tworzymy połączenie z demonem pigpio
        self.pi = pigpio.pi()

        # Jeśli nie udało się połączyć → błąd
        if not self.pi.connected:
            raise RuntimeError("Brak połączenia z pigpio")

        # ===== DEFINICJA PINÓW =====

        # PWM dla silnika A
        self.PWMA = 18

        # Kierunek silnika A
        self.AIN1 = 23
        self.AIN2 = 24

        # PWM dla silnika B (jeśli masz dwa silniki)
        self.PWMB = 17

        # Kierunek silnika B
        self.BIN1 = 22
        self.BIN2 = 27

        # Standby mostka H
        self.STBY = 25

        # Pin serwa
        self.SERVO_PIN = 12

        # Ustawienia serwa
        self.SERVO_CENTER = 1500   # środek
        self.SERVO_MIN = 1000      # maks w lewo
        self.SERVO_MAX = 2000      # maks w prawo
        self.SERVO_DEADZONE = 0.08 # martwa strefa joysticka

        # Ustawienia PWM
        self.PWM_FREQ = 20000      # 20kHz (cichy silnik)
        self.PWM_RANGE = 1000      # zakres PWM 0-1000

        # Aktualna moc (do soft ramp)
        self.current_power = 0

        # Konfiguracja pinów
        self._setup_pins()

        # Konfiguracja PWM
        self._setup_pwm()


    # ===== USTAWIENIE TRYBU PINÓW =====
    def _setup_pins(self):

        # Lista wszystkich pinów wyjściowych
        pins = [
            self.PWMA, self.AIN1, self.AIN2,
            self.PWMB, self.BIN1, self.BIN2,
            self.STBY, self.SERVO_PIN
        ]

        # Ustawiamy wszystkie jako OUTPUT
        for p in pins:
            self.pi.set_mode(p, pigpio.OUTPUT)


    # ===== KONFIGURACJA PWM =====
    def _setup_pwm(self):

        # Ustawiamy częstotliwość PWM dla obu kanałów
        self.pi.set_PWM_frequency(self.PWMA, self.PWM_FREQ)
        self.pi.set_PWM_frequency(self.PWMB, self.PWM_FREQ)

        # Ustawiamy zakres PWM (0–1000)
        self.pi.set_PWM_range(self.PWMA, self.PWM_RANGE)
        self.pi.set_PWM_range(self.PWMB, self.PWM_RANGE)

        # Na start brak mocy
        self.pi.set_PWM_dutycycle(self.PWMA, 0)
        self.pi.set_PWM_dutycycle(self.PWMB, 0)

        # Mostek w standby (wyłączony)
        self.pi.write(self.STBY, 0)

        # Serwo ustawione na środek
        self.pi.set_servo_pulsewidth(self.SERVO_PIN, self.SERVO_CENTER)


    # ==================================================
    # ==================== NAPĘD =======================
    # ==================================================

    def set_throttle(self, value):
        """
        value: zakres -1.0 do 1.0
        -1.0 = pełne cofanie
         0   = stop
         1.0 = pełny gaz
        """

        # Ograniczenie zakresu bezpieczeństwa
        value = max(-1.0, min(1.0, value))

        # Soft ramp — wygładzanie zmiany mocy
        self.current_power += (value - self.current_power) * 0.2
        power = self.current_power

        # Obliczamy prędkość PWM
        speed = int(abs(power) * self.PWM_RANGE)

        # ===== KIERUNEK =====
        if power > 0:
            # Jazda do przodu
            self.pi.write(self.AIN1, 1)
            self.pi.write(self.AIN2, 0)
            self.pi.write(self.BIN1, 1)
            self.pi.write(self.BIN2, 0)

        elif power < 0:
            # Cofanie
            self.pi.write(self.AIN1, 0)
            self.pi.write(self.AIN2, 1)
            self.pi.write(self.BIN1, 0)
            self.pi.write(self.BIN2, 1)

        else:
            # Jeśli 0 → zatrzymaj
            self.stop()
            return

        # Ustawiamy PWM na silnikach
        self.pi.set_PWM_dutycycle(self.PWMA, speed)
        self.pi.set_PWM_dutycycle(self.PWMB, speed)

        # Wyłączamy standby → mostek aktywny
        self.pi.write(self.STBY, 1)


    # ==================================================
    # ==================== SKRĘT =======================
    # ==================================================

    def set_steering(self, value):

        # Martwa strefa (żeby auto nie skręcało samo)
        if abs(value) < self.SERVO_DEADZONE:
            value = 0

        # Obliczamy impuls serwa
        pulse = self.SERVO_CENTER + value * (self.SERVO_MAX - self.SERVO_CENTER)

        # Ograniczamy do bezpiecznego zakresu
        pulse = max(self.SERVO_MIN, min(self.SERVO_MAX, pulse))

        # Wysyłamy sygnał do serwa
        self.pi.set_servo_pulsewidth(self.SERVO_PIN, pulse)


    # ==================================================
    # ===================== STOP =======================
    # ==================================================

    def stop(self):

        # Zerujemy PWM
        self.pi.set_PWM_dutycycle(self.PWMA, 0)
        self.pi.set_PWM_dutycycle(self.PWMB, 0)

        # Zerujemy kierunek
        self.pi.write(self.AIN1, 0)
        self.pi.write(self.AIN2, 0)
        self.pi.write(self.BIN1, 0)
        self.pi.write(self.BIN2, 0)

        # Mostek w standby
        self.pi.write(self.STBY, 0)


    def shutdown(self):

        # Pełne zatrzymanie
        self.stop()

        # Wyłączenie sygnału serwa
        self.pi.set_servo_pulsewidth(self.SERVO_PIN, 0)

        # Zamknięcie połączenia pigpio
        self.pi.stop()


# ==================================================
# ================= XBOX CONTROL ===================
# ==================================================

def main():

    # Tworzymy obiekt sterownika auta
    rc = RacingController()

    # Inicjalizacja pygame
    pygame.init()
    pygame.joystick.init()

    # Sprawdzenie czy kontroler jest podłączony
    if pygame.joystick.get_count() == 0:
        print("Brak kontrolera Xbox")
        return

    # Bierzemy pierwszy kontroler
    joy = pygame.joystick.Joystick(0)
    joy.init()

    print("🎮 Xbox controller connected")

    try:
        while True:

            # Aktualizacja stanu pada
            pygame.event.pump()

            # TRIGGERY
            lt = (joy.get_axis(2) + 1) / 2
            rt = (joy.get_axis(5) + 1) / 2

            # RT przód, LT tył
            throttle = rt - lt
            rc.set_throttle(throttle)

            # Prawa gałka poziomo
            steering = joy.get_axis(3)
            rc.set_steering(steering)

            # Przycisk B = hamulec
            if joy.get_button(1):
                rc.set_throttle(0)

            # START = wyjście
            if joy.get_button(7):
                break

            # 20 ms opóźnienia
            time.sleep(0.02)

    finally:
        rc.shutdown()
        pygame.quit()


# Uruchamiamy tylko jeśli plik startuje bezpośrednio
if __name__ == "__main__":
    main()