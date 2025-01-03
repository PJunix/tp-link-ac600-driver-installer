# TP-Link AC600 Driver Installer

This Python script automates the process of installing drivers for the TP-Link AC600 WiFi adapter. It’s tested on **Kali Linux** and supports **kernel version 6.11.2**.

## Features
- **Kernel version detection**: Ensures the correct drivers are installed based on your system.
- **Package management**: Automatically downloads and installs required kernel packages.
- **Driver installation**: Clones the required GitHub repository and installs the drivers.

## Usage
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/tp-link-ac600-driver-installer.git

2. Navigate to the repository directory:
   ```
    cd tp-link-ac600-driver-installer

3. Run the script:
   ```
    python3 driver_installer.py

4. During the installation, the installer-driver.sh script will prompt:
   ``` 
    "Do you want to edit [something]?"
    Input n (no).
    "Do you want to reboot?"
    Input y (yes).
    
    After the reboot, your TP-Link AC600 adapter will work smoothly—like butter! 🧈🎉
