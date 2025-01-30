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
- [Contributing](#contributing)
- [License](#license)

## The FarmInsight Project
Welcome to the FarmInsight Project by ETCE!

The FarmInsight platform brings together advanced monitoring of "Food Production Facilities" (FPF), enabling users to 
document, track, and optimize every stage of food production seamlessly.

All FarmInsight Repositories:
* <a href="https://github.com/ETCE-LAB/FarmInsight-Dashboard-Frontend">Dashboard-Frontend</a>
* <a href="https://github.com/ETCE-LAB/FarmInsight-Dashboard-Backend">Dashboard-Backend</a>
* <a href="https://github.com/ETCE-LAB/FarmInsight-FPF-Backend">FPF-Backend</a>

### Core vision

<img src="/.documentation/FarmInsightOverview.jpg">

FarmInsight empowers users to manage food production facilities with precision and ease. 

Key features include:

* User Management: Set up organizations with role-based access control for secure and personalized use.
* FPF Management: Configure and manage Food Production Facilities (FPFs), each equipped with sensors and cameras.
* Sensor & Camera Integration: Collect sensor data and capture images or livestreams at configurable intervals, all 
accessible through the web application.
* Harvest Documentation: Log and track harvests for each plant directly from the frontend interface.
* Data Visualization: Visualize sensor data with intuitive graphs and charts.
* Media Display: View and manage captured images and livestreams for real-time monitoring.

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

RESOURCE_SERVER_INTROSPECTION_URL=<URL HERE>
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
Here are some of the key API endpoints :

* GET /api/sensors/types - It will return all available sensor configs
* POST /api/sensors - Create a new sensor
* GET /api/sensors/{sensorId} - Get the config for given sensor
* PUT /api/sensors/{sensorId} - Edit a sensor

## Contributing

This project was developed as part of the Digitalisierungsprojekt at DigitalTechnologies WS24/25 by:
* Tom Luca Heering
* Theo Lesser
* Mattes Knigge
* Julian Schöpe
* Marius Peter

Project supervision:
* Johannes Meier
* Benjamin Leiding

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
