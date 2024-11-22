# FarmInsight-FPF-Backend

A Django-based sensor service that allows configuring sensors, collecting sensor data, and sending it to a remote system based on configurable intervals.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Development Setup](#development-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
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
## Contributing

## License
