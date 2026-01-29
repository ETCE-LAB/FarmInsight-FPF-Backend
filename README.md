<img src="https://github.com/user-attachments/assets/bb514772-084e-439f-997a-badfe089be76" width="300">

# FarmInsight-FPF-Backend

A Django-based sensor service that allows configuring sensors, collecting sensor data, and sending it to a remote system based on configurable intervals.

## Table of Contents

- [The FarmInsight Project](#the-farminsight-project)
  - [Core vision](#core-vision)
- [Overview](#overview)
  - [Built with](#built-with)
- [Features](#features)
- [Development Setup](#development-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Add new sensor support](#add-new-sensor-support)
- [Contributing](#contributing)
- [License](#license)

## The FarmInsight Project

Welcome to the FarmInsight Project by ETCE!

The FarmInsight platform brings together advanced monitoring of "Food Production Facilities" (FPF), enabling users to
document, track, and optimize every stage of food production seamlessly.

All FarmInsight Repositories:
- <a href="https://github.com/ETCE-LAB/FarmInsight-Dashboard-Frontend">Dashboard-Frontend</a>
- <a href="https://github.com/ETCE-LAB/FarmInsight-Dashboard-Backend">Dashboard-Backend</a>
- <a href="https://github.com/ETCE-LAB/FarmInsight-FPF-Backend">FPF-Backend</a>
- <a href="https://github.com/ETCE-LAB/FarmInsight-AI-Backend">AI-Backend</a>

Link to our productive System:<a href="https://farminsight.etce.isse.tu-clausthal.de"> FarmInsight.etce.isse.tu-clausthal.de</a>

### Core vision

<img src="/.documentation/FarmInsightOverview.jpg">

FarmInsight empowers users to manage food production facilities with precision and ease.

Key features include:

- User Management: Set up organizations with role-based access control for secure and personalized use.
- FPF Management: Configure and manage Food Production Facilities (FPFs), each equipped with sensors and cameras.
- Sensor & Camera Integration: Collect sensor data and capture images or livestreams at configurable intervals, all
accessible through the web application.
- Harvest Documentation: Log and track harvests for each plant directly from the frontend interface.
- Data Visualization: Visualize sensor data with intuitive graphs and charts.
- Controllable Action: To control the FPF you can add controllable actions which can perform actions on hardware which is reachable via network.
- Weather forecast: You can configure a location for your FPF for which a weather forecast will be gathered.
- Media Display: View and manage captured images and livestreams for real-time monitoring.

## Overview

The FPF (Food Production Facility) Backend application collects data from all configured sensors and sends
measurements to the FarmInsights Dashboard-Backend based on user-configured intervals.

### Built with

[![Python][Python-img]][Python-url] <br>
[![Django][Django-img]][Django-url] <br>
[![SQLite][SQLite-img]][SQLite-url]

## Features

- Manage sensor configurations remotely via API.
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
  You need to activate the virtual environment with

```
source .venv/bin/activate
```

### Step-by-Step Guide

1. After cloning the repository, move into the following folder

```
cd .\django_server\
```

1. Install the required dependencies for the project using `pip`:

```
pip install -r requirements.txt
```

Setup .env files at:
- django-server/.env.dev
- django-server/.env.prod

Example of .env file:

```
MEASUREMENTS_BASE_URL=http://localhost:3001
GENERATE_MEASUREMENTS=True

RESOURCE_SERVER_INTROSPECTION_URL=<URL HERE>
DASHBOARD_BACKEND_USER_ID=<ID HERE>

MQTT_HOST=<IP of MQTT broker HERE>
MQTT_PORT=<Port of MQTT broker HERE (default is:1883)>

```

1. Pull the git submodule:

```
git submodule init
git submodule update
```

1. Run the server via the IDE or via:

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

### Additional Hints

If you already set the FPF-Backend up before and want to start from scratch, please remove the existing config in the local db.sqlite
as it contains an API Key for authorized communication with the Dashboard-Backend.

Option 1: Remove the entries from the database manually (e.g. with SQL queries)

Option 2: Delete the db.sqlite file and re-initialize it with

```
python manage.py makemigrations
python manage.py migrate
```

## API Endpoints

Here are some of the key API endpoints :

- GET /api/sensors/types - It will return all available sensor configs
- POST /api/sensors - Create a new sensor
- GET /api/sensors/{sensorId} - Get the config for given sensor
- PUT /api/sensors/{sensorId} - Edit a sensor

## Sensor scripts

In this repository, you can find PiPico or Arduino Nano IOT 33 code in the .documentation folder.
There, you can also find a template script for HTTP and HTTP + MQTT communication.

Available sensor scripts in this repository:

| Platform         | Sensor Type            | Script / Folder Name                                                                           | Notes                    |
|------------------|------------------------|------------------------------------------------------------------------------------------------|--------------------------|
| arduino-code     | Ultrasonic             | [A02YYUW-ultrasonic-sensor](./.documentation/arduino-code/A02YYUW-ultrasonic-sensor.ino)       | A02YYUW sensor           |
| arduino-code     | Atlas Kit              | [atlas-kit-sensor](./.documentation/arduino-code/atlas-kit-sensor.ino)                         | General Atlas sensor kit |
| arduino-code     | Atlas Kit              | [atlas-kit-sensor-calibration](./.documentation/arduino-code/atlas-kit-sensor-calibration.ino) | Calibration routine      |
| arduino-code     | pH Sensor              | [Haoshi101-ph-sensor](./.documentation/arduino-code/Haoshi101-ph-sensor.ino)                   | Haoshi 101 pH            |
| arduino-code     | Soil Sensor            | [npk-soil-sensor](./.documentation/arduino-code/npk-soil-sensor.ino)                           | NPK (nutrient) sensor    |
| arduino-code     | Soil Moisture          | [v2-soil-moisture-sensor](./.documentation/arduino-code/v2-soil-moisture-sensor.ino)           | Moisture sensor v2       |
| arduino-code     | Temperature & Humidity | [sht-31-sensor](./.documentation/arduino-code/sht-31-sensor.ino)                               | SHT-31 sensor            |
| arduino-code     | Light Sensor           | [tsl2591-sensor](./.documentation/arduino-code/tsl2591-sensor.ino)                             | TSL2591 sensor           |
| arduino-code     | Template               | [template-sensor](./.documentation/arduino-code/template-sensor.ino)                           | Basic sensor template    |
| arduino-code     | Template               | [template-sensor-mqtt](./.documentation/arduino-code/template-sensor-mqtt.ino)                 | With MQTT integration    |
| pi-pico-code     | CO Sensor              | [co-sensor](./.documentation/pi-pico-code/co2-sensor/)                                         |                          |
| pi-pico-code     | DHT Sensor             | [dht-sensor](./.documentation/pi-pico-code/dht-sensor/)                                        | DHT22                    |

## Sensor types supported by the FPF

For most cases you can use a standard `http_sensor`, `mqtt_sensor` or `http_mqtt_sensor` type but if you require special processing of the values you get from the microcontroller for example
you can implement your own type as described below.

Follow the template or the existing classes in this [sensors package](./django_server/fpf_sensor_service/sensors/).

### 🔗 Http Endpoint Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "value": 42.5
}
```

---

### 📦 2. MQTT Topic & Payload

```
measurements/sensor-id-123
```

```json
{
  "value": 42.5,
  "timestamp": "2025-06-28T14:35:00Z"
}
```

or

```json
{
  "value": 42.5
}
```

When no timestamp is provided, the FPF will insert the current time automatically.

## Add new sensor support

To add a new sensor:

1. First create a new file in fpf_sensor_service/sensors/ <sensor_model>_sensors.py.
2. Use the boilerplate code from the typed_sensor.template file to setup the basic class structure, name the class accordingly.
3. Fill out the SensorDescription in get_description() so the frontend can correctly display it as a hardware configuration, for more details on all the types and how to fill it there is further documentation in the sensor_description.py.
4. Implement the get_measurement() method and init_additional_information() if needed.
5. Import the sensor class to the \_\_init\_\_.py file so it gets loaded with the rest of the sensor module and the TypedSensorFactory can pick up on it.

If you want to add MQTT functionalities, make sure to pass 'payload' to the get_measurement function, just like in all other MQTT classes.
This will be the payload of the sensor.

## MQTT support

To enable MQTT, a MQTT broker must be running in the network, so the FPF can connect to it.
A common setup is to have a mosquitto broker running on the same raspberry PI.
A guide to set it up can be found in the MOSQUITTO.md.

👉 [MOSQUITTO.md — Full Setup Guide](./MOSQUITTO.md)

Once it is set up, you need to configure the MQTT setting in the env.dev file
e.g.
`MQTT_HOST=192.168.178.54
MQTT_PORT=1883`
Optionally add username and password in case you configured the broker with it.
The FPF will connect to the broker on startup and listens for incoming messages of the sensors which are communicating via MQTT.

## 🔄 Contribute to FarmInsight

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes and commit them: `git commit -m 'Add new feature'`
4. Push the branch: `git push origin feature/your-feature`
5. Create a pull request.

## Past/Present Contributors

This project was developed as part of the Digitalisierungsprojekt at DigitalTechnologies WS24/25 by:
- Tom Luca Heering
- Theo Lesser
- Mattes Knigge
- Julian Schöpe
- Marius Peter

Project supervision:
- Johannes Mayer
- Benjamin Leiding

## License

This project is licensed under the [AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html) license.

<!-- MARKDOWN LINKS & IMAGES -->
[Python-img]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[Django-img]: https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white
[Django-url]: https://www.djangoproject.com/
[SQLite-img]: https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white
[SQLite-url]: https://www.sqlite.org/

---
For more information or questions, please contact the ETCE-Lab team.
