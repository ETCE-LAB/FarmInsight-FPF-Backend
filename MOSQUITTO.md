This guide describes how to install a mosquitto client at a raspberry pi as a service.

1. Update the raspberry pi (optionally)

2. Activate python env

3. Update the FPF repository

`git pull --no-rebase`
`pip install -r requirements.txt`

4. Install the mosquito client and add it as a service

`get the mosquitto for raspberryPI`
`sudo apt install -y mosquitto mosquitto-clients`
`sudo systemctl enable mosquitto`
`sudo systemctl start mosquitto`
`sudo systemctl enable mosquitto`

5. Make it available to the network (we create here a custom config)
`sudo nano /etc/mosquitto/conf.d/external-listener.conf`

Write the following into the file and save:
`bind_address 0.0.0.0
allow_anonymous true`

6. Debug in console: Check if it is on the correct port and accessible from outside
`sudo netstat -tulnp | grep 1883`

7. Restart after the config (Optional)
`sudo systemctl restart mosquitto`

Debug: Check for incoming messages
`mosquitto_sub -t "#" -v`
