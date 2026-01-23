import time
import subprocess
import psutil
from ppadb.client import Client as AdbClient

from services.volume_worker import get_resource_path

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

    # 1. Clear Chrome data (optional, but keeps it fresh)
    device.shell("pm clear com.android.chrome")
    time.sleep(1)

    # 2. FORCE FULLSCREEN SYSTEM-WIDE (Hides status bar)
    # This works on most Android 4.3+ devices
    device.shell("settings put global policy_control immersive.full=com.android.chrome")

    # 3. Launch chrome
    launch_cmd = f"am start -n com.android.chrome/com.google.android.apps.chrome.Main -d {target_url}"
    device.shell(launch_cmd)


def homepage_restart():
    devices = client.devices()
    if len(devices) > 0:
        device = devices[0]
        home = "input keyevent 3"
        device.shell(home)
        device.shell("am force-stop com.android.chrome")


def auto_tether():
    run_adb_server()
    print("Searching for Galaxy S3...")

    while True:
        devices = client.devices()
        if len(devices) > 0:
            device = devices[0]
            # Disable UI
            #device.shell("su -c 'pm disable com.android.systemui'")
            #launch_cmd = f"am start -n com.android.chrome/com.google.android.apps.chrome.Main -d {flags}"

            interface_active = device.shell("ip addr show rndis0")
            time.sleep(1)
            # If already up, don't force it again
            if "UP" in interface_active:
                print("Interface already up, tethering active!")
                time.sleep(2)
                return True

            print(f"Found {device.serial}. Forcing USB tethering")
            time.sleep(2)

            device.shell("su -c 'setprop sys.usb.config rndis,adb'")
            time.sleep(2)
            device.shell("su -c 'service call connectivity 33 i32 1'")
            device.shell("su -c 'ifconfig rndis0 192.168.42.129 netmask 255.255.255.0 up'")

            result = device.shell("ip addr show rndis0")
            if "inet 192.168.42.129" in result:
                print("!!! TETHERING ACTIVE !!!")
                time.sleep(2)
                return True

        time.sleep(2)
