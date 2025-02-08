# Deploy the Application on Raspberrypi
This guide details the required shell commands u need to use.
This guide and used templates assume you're running everything from inside the home directory, you can make sure you're there by running this:
```bash
cd ~ 
```
First step should be a general update:
```bash
sudo apt-get update
sudo apt-get -y upgrade
```
Install Python:
```bash
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
Git clone the FPF-Backend this only retrieves the deployment branch without any commit history:
```bash
git clone --depth 1 -b deployment --single-branch https://github.com/ETCE-LAB/FarmInsight-FPF-Backend.git
```
And install requirements for the django project:
```bash 
pip install -r FarmInsight-FPF-Backend/django_server/requirements.txt 
```
Edit the "FarmInsight-FPF-Backend/django_server/.env.dev" file and set the required variables, using a text editor for example nano:
```bash 
nano FarmInsight-FPF-Backend/django_server/.env.dev
```
Edit the "FarmInsight-FPF-Backend/farminsight-fpf.service" file, replace the <USERNAME> with your username:
```bash 
nano FarmInsight-FPF-Backend/farminsight-fpf.service
```
Do the same thing with the "FarmInsight-FPF-Backend/startup.sh" file and make the startup.sh script executable:
```bash 
nano FarmInsight-FPF-Backend/startup.sh
chmod +x FarmInsight-FPF-Backend/startup.sh
```
Then copy it into /etc/systemd/system/ so it is available to start as a system service:
```bash 
sudo cp FarmInsight-FPF-Backend/farminsight-fpf.service /etc/systemd/system/farminsight-fpf.service
```
Enable the service to start at reboot, if you're relying on the other external requirements like the DHT libaries, install these first before doing this step:
```bash 
sudo systemctl enable farminsight-fpf
```
You can also manually start it to test 
```bash 
sudo systemctl start farminsight-fpf
```
Edit the startup.sh file to change the port of the fpf server (from our default 8001) or what outside connections it allows.

Now make sure that you have all the sensor types you need in your 
FarmInsight-FPF-Backend/django_server/fpf_sensor_service/sensors folder and are loading them into the module in the __init__.py file it is also best to disable any sensors you don't support.

### How to Install DHT Libraries if required for direct sensor access:
First step is to setup adafruit-blinka ([adafruit docs](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi))
Restart the system if prompted to and afterwards remember to reactivate the python virtual environment:
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
