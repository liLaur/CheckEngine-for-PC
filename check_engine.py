import ctypes
from infi.systray import SysTrayIcon
import schedule
import time
import datetime
import win32com.client as com
import win32api
import psutil
import speedtest

import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

running = True

def getUptime():
    lib = ctypes.windll.kernel32
    t = lib.GetTickCount64()
    t = int(str(t)[:-3])
    secs = t % 60
    mins = (t // 60) % 60
    hour = (t // 3600) % 24
    days = t // (24 * 3600)
    return days, hour, mins, secs

def TotalSize(drive):
    try:
        fso = com.Dispatch("Scripting.FileSystemObject")
        drv = fso.GetDrive(drive)
        return drv.TotalSize/2**30
    except:
        return 0

def FreeSpace(drive):
    try:
        fso = com.Dispatch("Scripting.FileSystemObject")
        drv = fso.GetDrive(drive)
        return drv.FreeSpace/2**30
    except:
        return 0
    
lights_h = []
lights_10m = []
lights_1m = []
lights_30s = []
internet_down = None

def onquit(systray):
    global running
    for light in lights_h:
        SysTrayIcon.shutdown(light)
    for light in lights_10m:
        SysTrayIcon.shutdown(light)
    for light in lights_1m:
        SysTrayIcon.shutdown(light)
    for light in lights_30s:
        SysTrayIcon.shutdown(light)
    if internet_down is not None:
        SysTrayIcon.shutdown(internet_down)
    running = False

system_checker = SysTrayIcon(resource_path("assets/system_checker.ico"), "Checking your system", None, onquit)
system_checker.start()

def createLight_h(icon, problem, menu_options):
    check_engine = SysTrayIcon(icon, problem, menu_options)
    check_engine.start()
    lights_h.append(check_engine)

def createLight_10m(icon, problem, menu_options):
    check_engine = SysTrayIcon(icon, problem, menu_options)
    check_engine.start()
    lights_10m.append(check_engine)

def createLight_1m(icon, problem, menu_options):
    check_engine = SysTrayIcon(icon, problem, menu_options)
    check_engine.start()
    lights_1m.append(check_engine)
    
def createLight_30s(icon, problem, menu_options):
    check_engine = SysTrayIcon(icon, problem, menu_options)
    check_engine.start()
    lights_30s.append(check_engine)

def restart(systray):
    win32api.InitiateSystemShutdown()

def check_hourly():
    now = datetime.datetime.now()

    print(f"[{now.time()}]Checking (60m)...")

    global lights_h

    for light in lights_h:
        SysTrayIcon.shutdown(light)

    lights_h.clear()

    days, hour, mins, secs = getUptime()
    usagePercent = int(FreeSpace("C:") / TotalSize("C:") * 100)

    # check for problems
    if (days >= 2):
        menu_options = (("Restart", None, restart),)

        problem = f"Too much uptime ({days} days)"
        createLight_h(resource_path("assets/check_engine_light.ico"), problem, menu_options)
    if (usagePercent < 10):
        problem = f"Low disk space ({usagePercent}%)"
        createLight_h(resource_path("assets/fuel_light.ico"), problem, None)

def check_10m():
    now = datetime.datetime.now()

    print(f"[{now.time()}]Checking (10m)...")

    global lights_10m, internet_down

    for light in lights_10m:
        SysTrayIcon.shutdown(light)

    if internet_down is not None:
        SysTrayIcon.shutdown(internet_down)

    lights_10m.clear()

    try:
        st = speedtest.Speedtest()
        download_speed = st.download() / 1000000
        upload_speed = st.upload() / 1000000

        print(f"download speed: {download_speed:.2f} Mbps")
        print(f"upload speed: {upload_speed:.2f} Mbps")

        # check for problems
        if (download_speed < 30):
            problem = f"Download speed is low ({download_speed:.2f} Mbps)"
            createLight_10m(resource_path("assets/spark_plug_light.ico"), problem, None)
        if upload_speed < 30:
            problem = f"Upload speed is low ({upload_speed:.2f} Mbps)"
            createLight_10m(resource_path("assets/spark_plug_light.ico"), problem, None)
    except:
        problem = f"Internet is down"
        if internet_down is None:
            internet_down = SysTrayIcon(resource_path("assets/spark_plug_light_red.ico"), problem)
            internet_down.start()
        return

def check_1m():
    now = datetime.datetime.now()

    print(f"[{now.time()}]Checking (1m)...")

    global lights_1m

    for light in lights_1m:
        SysTrayIcon.shutdown(light)

    lights_1m.clear()

    cpuPercernt = psutil.cpu_percent()
    ramPercent = psutil.virtual_memory()[2]

    if (cpuPercernt > 90):
        menu_options = (("Restart", None, restart),)

        problem = f"CPU usage is too high ({cpuPercernt}%)"
        createLight_1m(resource_path("assets/check_engine_light.ico"), problem, menu_options)
    if (ramPercent > 95):
        menu_options = (("Restart", None, restart),)

        problem = f"RAM usage is too high ({ramPercent}%)"
        createLight_1m(resource_path("assets/check_engine_light.ico"), problem, menu_options)

def check_30s():
    now = datetime.datetime.now()

    print(f"[{now.time()}]Checking (30s)...")

    global lights_30s, internet_down

    for light in lights_30s:
        SysTrayIcon.shutdown(light)

    if internet_down is not None:
        SysTrayIcon.shutdown(internet_down)

    lights_30s.clear()

    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        print(f"ping: {st.results.ping} ms")
        if (st.results.ping > 100):
            problem = f"Ping is too high ({st.results.ping} ms)"
            createLight_30s(resource_path("assets/spark_plug_light.ico"), problem, None)
    except:
        problem = f"Internet is down"
        if internet_down is None:
            internet_down = SysTrayIcon(resource_path("assets/spark_plug_light_red.ico"), problem)
            internet_down.start()
        return

schedule.every().hour.do(check_hourly)
schedule.every().minute.do(check_1m)
schedule.every(30).seconds.do(check_30s)
schedule.every(10).minutes.do(check_10m)

# main loop
check_hourly()
check_1m()
check_30s()
check_10m()

while running:
    schedule.run_pending()
    time.sleep(1)