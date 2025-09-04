from time import monotonic
from gpiozero import Motor
from asyncio import sleep

# H-bridge control using gpiozero Motor (PWM-enabled)
MOTOR_FWD = 20  # IN1
MOTOR_REV = 21  # IN2


class MotorDriver:
    def __init__(self, pin_fwd = MOTOR_FWD, pin_rev = MOTOR_REV):
        self.motor = Motor(forward=pin_fwd, backward=pin_rev, pwm=True)

    def __clamp(self, x, lo, hi):
        return max(lo, min(hi, x))

    def run(self, speed):
        # -speed because we want positive to correspond to pumping out water
        self.motor.value = self.__clamp(-speed, -1, 1);

    async def run_for(self, speed, duration):
            self.run(speed)
            await sleep(duration)
            self.stop()

    def stop(self):
        self.motor.value = 0