# Temperature and Humidity Monitoring Service

This repository contains a Python script designed to read temperature and humidity data from a DHT22 sensor connected to
a Raspberry Pi or similar device. The script logs this information and is prepared to run as a systemd service, suitable
for long-term deployment on Linux systems. Additionally, this script is commonly used with a companion Go program that
serves the data via Prometheus metrics.

## Features

- Reads temperature and humidity data from a DHT22 sensor.
- Outputs data in JSON format for compatibility with the Go program.
- Robust error handling and retry mechanism.
- Can run continuously as a background service.
- Includes logging and signal handling for graceful shutdowns.

## Prerequisites

Before deploying this script, ensure you have the following:

- A Raspberry Pi or any compatible board.
- Python 3.6 or later.
- Access to GPIO pins for the DHT22 sensor.
- Required Python libraries: `adafruit_dht`, `board`.

## System Requirements

Before installing and running dht22, ensure the following dependencies are installed on your system:

* **libsystemd-dev:** Required for logging integration with systemd's journal. This package provides the necessary
  development libraries for systemd-python.

### Installing System Dependencies

On Debian-based systems, you can install all required system dependencies with the following command:

```bash
sudo apt-get update
sudo apt-get install libsystemd-dev
```

Ensure these packages are installed before proceeding with the installation of the Python dependencies or running the
application.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/skroczek/dht22py.git
   cd your-repository-directory
   ```

2. **Setup Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Hardware Setup:**
    - Connect the DHT22 sensor to GPIO4 (default) or adjust the port in the script as needed.

## Configuration

### Creating the User for the systemd Service

To securely run the systemd service, it is recommended to create a specific user with minimal rights. This step reduces the risk that vulnerabilities in the application could compromise the system. Execute the following command to create the user `dht22`:

```bash
sudo adduser --system --no-create-home --group dht22
```

This command creates a system user without a home directory (`--no-create-home`) and a corresponding group (`--group`). The user `dht22` will be used to run the systemd service.

### Setting Permissions

The user `dht22` needs specific permissions to access the necessary resources, including the directory where the script and the virtual environment are stored. Set the appropriate permissions with the following commands:

```bash
sudo chown -R dht22:dht22 /opt/dht22py
sudo chmod -R 750 /opt/dht22py
```

These commands change the owner of the `/opt/dht22py` directory to the user `dht22` and set the access rights so that the owner has full access rights, the group has restricted rights, and other users have no access.

### Access to GPIO Pins

If the script requires access to GPIO pins, the user `dht22` may need to be added to the `gpio` group to obtain the necessary permissions:

```bash
sudo usermod -a -G gpio dht22
```

This command adds the user `dht22` to the `gpio` group, granting the required permissions to access the GPIO pins.

### Systemd Service Configuration

Ensure that the systemd unit file is correctly configured to use the user `dht22`:

```ini
[Unit]
Description=My Python Application to monitor temperature and humidity
After=network.target

[Service]
Type=simple
User=dht22
Group=dht22
WorkingDirectory=/opt/dht22py
ExecStart=/opt/dht22py/venv/bin/python /opt/dht22py/dht22py.py --output json --file /var/lib/dht22py/data.json
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

This ensures that the service runs under the user `dht22` and uses the correct environmental settings.

### Checking Service Status

After starting the service, its status can be checked with the following command:

```bash
sudo systemctl status dht22py.service
```

## Usage

To start the service manually:

```bash
sudo systemctl start dht22py.service
```

To enable automatic startup at boot time:

```bash
sudo systemctl enable dht22py.service
```

## Companion Go Program

This Python service is typically used with the following Go program, which reads the JSON data file, updates Prometheus
metrics, and serves them via an HTTP endpoint. This setup allows for easy monitoring and integration with systems like
Grafana.

```bash
go run main.go
```

## Logs

- The Python service logs are stored in `/var/log/dht22py/dht22py.log`.
- Ensure the logging directory exists and is writable:
  ```bash
  sudo mkdir /var/log/dht22py
  sudo chown dht22pyuser:dht22pygroup /var/log/dht22py
  ```

## Contributing

Contributions to this project are welcome. Please ensure to update tests as appropriate.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Sebastian Kroczek - [me@xbug.com](mailto:me@xbug.de)
