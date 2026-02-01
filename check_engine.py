import ctypes
from infi.systray import SysTrayIcon
import schedule
import time
import datetime
import win32com.client as com
import win32api
import psutil
import speedtest

st = speedtest.Speedtest()

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
lights_10 = []
lights_1 = []

def onquit(systray):
    global running
    for light in lights_h:
        SysTrayIcon.shutdown(light)
    for light in lights_10:
        SysTrayIcon.shutdown(light)
    running = False

system_checker = SysTrayIcon("assets/system_checker.ico", "Checking your system", None, onquit)
system_checker.start()

def createLight_h(icon, problem, menu_options):
    check_engine = SysTrayIcon(icon, problem, menu_options)
    check_engine.start()
    lights_h.append(check_engine)

def createLight_10(icon, problem, menu_options):
    check_engine = SysTrayIcon(icon, problem, menu_options)
    check_engine.start()
    lights_10.append(check_engine)

def createLight_1(icon, problem, menu_options):
    check_engine = SysTrayIcon(icon, problem, menu_options)
    check_engine.start()
    lights_1.append(check_engine)

def restart(systray):
    win32api.InitiateSystemShutdown()

def check_hourly():
    now = datetime.datetime.now()

    print(f"[{now.time()}]Checking (60)...")

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
        createLight_h("assets/check_engine_light.ico", problem, menu_options)
    if (usagePercent < 10):
        problem = f"Low disk space ({usagePercent}%)"
        createLight_h("assets/fuel_light.ico", problem, None)

def check_10():
    now = datetime.datetime.now()

    print(f"[{now.time()}]Checking (10)...")

    global lights_10

    for light in lights_10:
        SysTrayIcon.shutdown(light)

    lights_10.clear()

    # download_speed = st.download() / 1000000

    # check for problems
    # if (download_speed < 50):
    #     problem = f"Wifi speed is low ({download_speed:.2f} Mbps)"
    #     createLight_10("assets/spark_plug_light.ico", problem, None)

def check_1():
    now = datetime.datetime.now()

    print(f"[{now.time()}]Checking (1)...")

    global lights_1

    for light in lights_1:
        SysTrayIcon.shutdown(light)

    lights_1.clear()

    cpuPercernt = psutil.cpu_percent()
    ramPercent = psutil.virtual_memory()[2]

    if (cpuPercernt > 90):
        menu_options = (("Restart", None, restart),)

        problem = f"CPU usage is too high ({cpuPercernt}%)"
        createLight_1("assets/check_engine_light.ico", problem, menu_options)
    if (ramPercent > 95):
        menu_options = (("Restart", None, restart),)

        problem = f"RAM usage is too high ({ramPercent}%)"
        createLight_1("assets/low_coolant_light.ico", problem, menu_options)

schedule.every().hour.do(check_hourly)
schedule.every().minute.do(check_1)

# main loop
check_hourly()
check_1()

while running:
    schedule.run_pending()
    time.sleep(1)