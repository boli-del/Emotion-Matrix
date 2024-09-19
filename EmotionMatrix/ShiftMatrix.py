import RPi.GPIO as GPIO
import smbus
from time import sleep

# GPIO pin setup for 74HC595
DATA_PIN = 17
LATCH_PIN = 22
CLOCK_PIN = 27

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DATA_PIN, GPIO.OUT)
GPIO.setup(LATCH_PIN, GPIO.OUT)
GPIO.setup(CLOCK_PIN, GPIO.OUT)

# MPU-6050 registers and addresses
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT = 0x3B
ACCEL_YOUT = 0x3D
ACCEL_ZOUT = 0x3F
GYRO_XOUT = 0x43
GYRO_YOUT = 0x45
GYRO_ZOUT = 0x47

# MPU-6050 address
Device_Address = 0x68

# Initialize the MPU-6050
bus = smbus.SMBus(1)

def MPU_Init():
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
    bus.write_byte_data(Device_Address, CONFIG, 0)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

MPU_Init()

# Define emoji patterns
emojis = {
    "happy": [
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "sad": [
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
}

def shift_out(data):
    for bit in range(8):
        GPIO.output(DATA_PIN, data & (1 << (7 - bit)))
        GPIO.output(CLOCK_PIN, GPIO.HIGH)
        GPIO.output(CLOCK_PIN, GPIO.LOW)

def display_emoji(emoji_name):
    emoji = emojis.get(emoji_name)
    if emoji:
        GPIO.output(LATCH_PIN, GPIO.LOW)
        for row in emoji:
            shift_out(int(''.join(map(str, row)), 2))
            shift_out(0xFF)
        GPIO.output(LATCH_PIN, GPIO.HIGH)

try:
    while True:
        acc_x = read_raw_data(ACCEL_XOUT)
        acc_y = read_raw_data(ACCEL_YOUT)
        acc_z = read_raw_data(ACCEL_ZOUT)

        Ax = acc_x / 16384.0
        Ay = acc_y / 16384.0
        Az = acc_z / 16384.0

        # Determine which emoji to display based on the tilt
        if Ay > 0.5:
            display_emoji("happy")
        else:
            display_emoji("sad")

        sleep(0.5)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()