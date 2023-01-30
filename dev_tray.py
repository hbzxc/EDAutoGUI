from pystray import Icon, MenuItem, Menu
from PIL import Image # big
from dev_autopilot import autopilot, resource_path, get_bindings, clear_input, set_scanner, RELEASE
from src.directinput import *
import threading
import kthread
import keyboard

STATE = 0

def setup(icon):
    icon.visible = True

def exit_action():
    stop_action()
    icon.visible = False
    icon.stop()

def start_action():
    stop_action()
    kthread.KThread(target = autopilot, name = "EDAutopilot").start()

def stop_action():
    for thread in threading.enumerate():
        if thread.getName() == 'EDAutopilot':
            thread.kill()
    clear_input(get_bindings())

def set_state(v):
    def inner(icon, item):
        global STATE
        STATE = v
        set_scanner(STATE)
    return inner

def get_state(v):
    def inner(item):
        return STATE == v
    return inner

def tray():
    global icon, thread
    icon = None
    thread = None

    name = 'ED - Autopilot'
    icon = Icon(name=name, title=name)
    logo = Image.open(resource_path('src/logo.png'))
    icon.icon = logo

    keyboard.add_hotkey('home', start_action)
    keyboard.add_hotkey('end', stop_action)

    icon.run(setup)

if __name__ == '__main__':
    tray()
