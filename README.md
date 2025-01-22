<img src="https://github.com/user-attachments/assets/bb514772-084e-439f-997a-badfe089be76" width="300">

# FarmInsight-FPF-Backend

A Django-based sensor service that allows configuring sensors, collecting sensor data, and sending it to a remote system based on configurable intervals.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Development Setup](#development-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Deploy](#deploy-the-application-on-raspberrypi)
- [Contributing](#contributing)
- [License](#license)

## Overview
The Sensor Service application collects data from all configured sensors and sends measurements to a remote system based on user-configured intervals.

## Features
- Manage sensor configurations.
- Schedule sensor data collection based on configurable intervals.
- Send sensor measurements to a remote API.
- API support for managing sensor configurations.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Django 3.x or higher
- SQLite
- `pip` (Python package manager)
- `virtualenv` (recommended for isolated environments)

### Step-by-Step Guide

Install the required dependencies for the project using `pip`:

```
pip install -r requirements.txt
```

Setup .env files at: 
* django-server/.env.dev
* django-server/.env.prod

Example of .env file:
```
MEASUREMENTS_BASE_URL=http://localhost:3001
GENERATE_MEASUREMENTS=True

RESOURCE_SERVER_INTROSPECTION_URL=https://development-isse-identityserver.azurewebsites.net/connect/introspect
DASHBOARD_BACKEND_USER_ID=<ID HERE>
```

Run the server via the IDE or via:
```
python manage.py runserver
```

## Running the Application
You can start the app with the following command.
In development mode, there are predefined settings (e.g. a default port) in order for the app to work seamlessly with other FarmInsight projects.
Start the app with:
```
python manage.py runserver
```
Otherwise, you can also specify the port yourself:
```
python manage.py runserver 8002
```
On server startup, the scheduler starts automatically.

## API Endpoints
Here are some of the key API endpoints for the sensor service:

* POST /api/sensorInterval/{sensorId} - Update the interval for a sensor.

## Deploy the Application on Raspberrypi

Install Python:
```bash
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install python3-pip python3-venv
```
Run these inside the /home directory to setup the virtual environment:
```bash
python3 -m venv env --system-site-packages
```
Activate the virtual environment when installing any python libraries:
```bash 
source env/bin/activate
```
Git clone the FPF-Backend into the home folder.
And install requirements for the django project:
```bash 
pip install -r FarmInsight-FPF-Backend/django_server/requirements.txt 
```
Edit the "farminsight-fpf.service" file depending on the user and exact path to the django project, then copy it into /etc/systemd/system/ so it is available as /etc/systemd/system/farminsight-fpf.service:
```bash 
cp ~/FarmInsight-FPF-Backend/farminsight-fpf.service /etc/systemd/system/farminsight-fpf.service
```
Now enable the service to start at reboot:
```bash 
systemctl enable farminsight-fpf
```
You can also manually start it to test 
```bash 
systemctl start farminsight-fpf
```
Edit the startup.sh file to change the port of the fpf server (from our default 8001) or what outside connections it allows.

Now make sure that you have all the sensor types you need in your 
FarmInsight-FPF-Backend/django_server/fpf_sensor_service/sensors folder and are loading them into the module in the __init__.py file it is also best to disable any sensors you don't support.

### How to Install DHT Libraries if required for direct sensor access:
First step is to setup adafruit-blinka ([adafruit docs](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi)):
```bash
sudo apt install --upgrade python3-setuptools
pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo -E env PATH=$PATH python3 raspi-blinka.py
```
Next is to install adafruit CircuitPythons DHT library ([adafruit docs](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup)):
```bash 
pip3 install adafruit-circuitpython-dht
sudo apt-get install libgpiod2
```

## Contributing

## License
