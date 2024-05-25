import time
import argparse
import json
import sys
import signal
import board
import adafruit_dht
import logging
from systemd.journal import JournalHandler

# Setup logging to use systemd's journal
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
journal_handler = JournalHandler()
journal_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(journal_handler)

# Argument parser setup
parser = argparse.ArgumentParser(description='Read temperature and humidity data')
parser.add_argument('--port', type=int, required=True, help='GPIO port number')
parser.add_argument('--output', type=str, choices=['text', 'json'], default='json',
                    help='Output format: "text" or "json" (default: json)')
parser.add_argument('--retry', type=int, default=5, help='Maximum number of retry attempts (default: 5)')
parser.add_argument('--watch', action='store_true', help='Enable continuous monitoring of values')
parser.add_argument('--file', type=str, help='File path to write output')

args = parser.parse_args()

# Initialize the sensor based on GPIO port
try:
    gpio_pin = getattr(board, f'D{args.port}')
    sensor = adafruit_dht.DHT22(gpio_pin)
except AttributeError:
    logger.critical(f"Unsupported port: {args.port}")
    sys.exit(1)


# Function to fetch sensor data
def get_sensor_data():
    retry_count = 0
    while retry_count < args.retry:
        try:
            temperature_c = sensor.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = sensor.humidity
            data = {
                "TempC": temperature_c,
                "TempF": temperature_f,
                "Humidity": humidity
            }
            return data
        except RuntimeError as error:
            logger.error(f"RuntimeError: {error.args[0]}")
            time.sleep(2.0)
            retry_count += 1
        except Exception as error:
            sensor.exit()
            logger.critical(f"Critical sensor error: {error}", exc_info=True)
            raise error

    logger.warning("Maximum retry attempts reached")
    raise Exception("Maximum retry attempts reached")


# Signal handling for graceful shutdown
def handle_sigterm(signum, frame):
    logger.info("SIGTERM received, shutting down")
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_sigterm)


# Main function
def main():
    while True:
        try:
            data = get_sensor_data()
            if args.file:
                with open(args.file, 'w') as f:
                    json.dump(data, f)
            else:
                logger.info(
                    f"Temp={data['TempC']:0.1f}ºC, Temp={data['TempF']:0.1f}ºF, Humidity={data['Humidity']:0.1f}%")
        except Exception as e:
            logger.error(f"Error while processing sensor data: {str(e)}")
            time.sleep(10)  # Wait before retrying
        else:
            if not args.watch:
                break
            time.sleep(3.0)


if __name__ == '__main__':
    main()
