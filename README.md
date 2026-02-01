# CheckEngine for PC
CheckEngine light that appears when something requires your attention.

It runs in the background and check your computers:
* uptime;
* cpu usage;
* ram usage;
* storage ramaining.

Then it shows you an icon summarizing the "problem".

<img width="189" height="58" alt="image" src="https://github.com/user-attachments/assets/60e685a5-7fa1-450d-a60f-7538c501e39d" />
(program is running) 
<br>
<img width="172" height="44" alt="image" src="https://github.com/user-attachments/assets/ed406d18-d951-49a0-acdb-1df8aa7a74c6" />
(something is detected)

# 
This repository provides the source code for buiding manually the application and also the binary for Windows.
___
# Building/Geting the software
## Pre-packaged executable:
- download `check_engine.exe`
- then continue from the **auto start section**.

## To build from source you'll need to:
- run `pip install -r requirements.txt`
- then run `pyinstaller check_engine.spec` for building the executable
- the executable is located in `dist` folder, the rest of the folders can be ignored.


# Autostart
## To autostart CheckEngine at Windows startup:
- press `Win + R`
- type `shell:startup`
- copy-paste a shortcut of `check_engine.exe`

# Uninstalling
- delete the shortcut from `shell:startup` and then delete `check_engine.exe`.
