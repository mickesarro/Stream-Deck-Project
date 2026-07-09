import time
import subprocess
import psutil
from ppadb.client import Client as AdbClient

from services.audio_manager import get_resource_path

client = AdbClient(host="127.0.0.1", port=5037)


def run_adb_server():
    adb = get_resource_path("adb.exe")
    # Start adb server if not running
    adb_running = any(proc.info['name'] == "adb.exe"
        for proc in psutil.process_iter(['name']))

    if not adb_running:
        print("ADB server not found. Starting adb.exe...")
        subprocess.run(f"{adb} start-server", shell=True, capture_output=True)
        time.sleep(2)


def reset_chrome(target_url):
    run_adb_server()
    devices = client.devices()
    if not devices:
        print("No device found, can't reset Chrome")
        return False

    device = devices[0]

    # Clear Chrome data
    device.shell("pm clear com.android.chrome")
    time.sleep(1)
    device.shell("settings put global policy_control immersive.full=com.android.chrome")

    launch_cmd = f"am start -n com.android.chrome/com.google.android.apps.chrome.Main -d {target_url}"
    device.shell(launch_cmd)


def homepage_restart():
    devices = client.devices()
    if len(devices) > 0:
        device = devices[0]
        home = "input keyevent 3"
        device.shell(home)
        device.shell("am force-stop com.android.chrome")


def clear_chrome_cache():
    devices = client.devices()
    if len(devices) > 0:
        device = devices[0]
        device.shell("am force-stop com.android.chrome")
        time.sleep(1)
        device.shell("pm clear com.android.chrome")
        time.sleep(1)
        device.shell("settings put global policy_control immersive.full=com.android.chrome")


def back_button():
    devices = client.devices()
    if len(devices) > 0:
        device = devices[0]
        back = "input keyevent 4"
        device.shell(back)


def auto_tether():
    run_adb_server()
    print("Searching for Galaxy S3...")

    while True:
        devices = client.devices()
        if len(devices) > 0:
            device = devices[0]

            # Check if tethering is already active
            try:
                interface_active = device.shell("ip addr show rndis0")
                if "UP" in interface_active and "inet 192.168.42.129" in interface_active:
                    print("Interface already up, tethering active!")
                    return True
            except Exception:
                pass  # Device might be resetting, keep looping

            print(f"Found {device.serial}. Forcing USB tethering")

            # 1. Switch the mode
            try:
                device.shell("su -c 'setprop sys.usb.config rndis,adb'")
            except Exception:
                print("Connection lost while switching modes, waiting for re-connection...")

            # 2. WAIT for the USB interface to reset (this is crucial!)
            time.sleep(5)

            # 3. Re-detect the device because the connection was killed
            devices = client.devices()
            if not devices:
                print("Device disconnected during mode switch, waiting...")
                continue

            device = devices[0]

            # 4. Run the rest of the commands
            device.shell("su -c 'service call connectivity 33 i32 1'")
            device.shell("su -c 'ifconfig rndis0 192.168.42.129 netmask 255.255.255.0 up'")

            # 5. Verify
            time.sleep(2)
            result = device.shell("ip addr show rndis0")
            if "inet 192.168.42.129" in result:
                print("!!! TETHERING ACTIVE !!!")
                return True

        time.sleep(2)
