# 🧰 MQTT Setup Guide for Raspberry Pi (Mosquitto as a Service)

This guide describes how to install and configure the Mosquitto MQTT client and broker on a Raspberry Pi, and run it as a service. It also includes steps for setting it up to allow access from external devices.

---

## ✅ 1. (Optional) Update your Raspberry Pi

Updating ensures you have the latest security patches and software.

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 🐍 2. Activate Python Environment (if used)

If your project uses a virtual Python environment:

```bash
source env/bin/activate
```

---

## 🔄 3. Update the FPF Repository

Pull the latest changes and install required Python packages.

```bash
cd ~/FarmInsight-FPF-Backend
git pull --no-rebase
pip install -r requirements.txt
```

---

## 📦 4. Install Mosquitto Broker and Client Tools

Install Mosquitto and ensure it starts automatically on boot:

```bash
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

---

## 🌐 5. Allow External Access via Custom Configuration

Create a custom configuration file to allow connections from other devices on your network:

```bash
sudo nano /etc/mosquitto/conf.d/external-listener.conf
```

Paste the following content:

```
bind_address 0.0.0.0
allow_anonymous true
```

Save and exit (`CTRL + O`, `Enter`, `CTRL + X`).

---

## 🔁 6. Restart Mosquitto to Apply Config

```bash
sudo systemctl restart mosquitto
```

---

## 🧪 7. Verify and Debug

### Check if Mosquitto is listening on port 1883

```bash
sudo netstat -tulnp | grep 1883
```

You should see a line showing `tcp` on port `1883` with `mosquitto` as the service.

### Subscribe to all topics for testing

```bash
mosquitto_sub -t "#" -v
```

If you send a message from another device (e.g., using `mosquitto_pub`), it should show up in the terminal.

---

## ✅ Done!

You now have Mosquitto running as a broker on your Raspberry Pi, accessible across your network, and ready to be used with your IoT applications.
