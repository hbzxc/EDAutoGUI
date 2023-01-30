# %%
#%pip install 
#%pip install olefile
#%pip install pyprctl

# %%
# Import the required libraries
import tkinter as tk
import tkinter.scrolledtext as st
import keyboard
import threading
import kthread
import pickle
import math
import logging

from dev_autopilot import autopilot, resource_path, get_bindings, set_scan_btn, clear_input, load_keys, load_logging_1, load_logging_2, load_logging_3, load_logging_4

#load_logging_2()
#load_logging_3()
#load_logging_4()

#load the keybind values
keys = load_keys()
color_tags = {}

#create class to store settings
class AutoToggle(object):
    def __init__(self, text, color, fuel, scan_fire):
        self.text = text
        self.color = color
        self.fuel = fuel
        self.scan_fire = scan_fire

#read the settings file and if none exits set a default
try:
    settings_file = open("settings", "rb")
    nToggle = pickle.load(settings_file)
    settings_file.close()
except:
    nToggle = AutoToggle("INACTIVE", "green", 33, 0)
    settings_file = open("settings", "wb")
    pickle.dump(nToggle, settings_file)
    settings_file.close()

#set the scan settings
set_scan_btn(nToggle.scan_fire)

# %%
class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record).replace('-','').strip()
        info_tag = record.levelname
        def append():
            to_console(msg, info_tag)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

# %%
def start_action():
    stop_action()
    toggle_on()
    to_console("Toggle on")
    kthread(target = autopilot(nToggle, active_text, auto_status), name = "EDAutopilot").start()
            
def stop_action():
    toggle_off()
    for thread in threading.enumerate():
        if thread.getName() == 'EDAutopilot':
            thread.kill()     
    to_console("Toggle off")
    clear_input(get_bindings())

def to_console(string, *rName):
    message = string+"\n"
    console_text.tag_config('green', foreground="green")
    console_text.tag_config('cyan', foreground='cyan')
    console_text.tag_config('yellow', background='yellow', foreground='blue')
    console_text.tag_config('error', background='red', foreground='white')
    console_text.tag_config('red', background='red', foreground='yellow')
    console_text.tag_config('default', foreground=text_color)

    err_flg = 0

    try:
        if rName[0]=="INFO":
            txt_color = 'cyan'
        elif rName[0]=="DEBUG":
            txt_color = 'green'
        elif rName[0]=="WARNING":
            txt_color = 'yellow'
        elif rName[0]=="ERROR":
            txt_color = 'error'
        elif rName[0]=="CRITICAL":
            txt_color = 'red'
        else:
            txt_color = 'default'
    except:
        txt_color = 'default'

    console_text.configure(state ='normal')
    console_text.insert(tk.END, message, txt_color)
    console_text.see("end")
    console_text.configure(state ='disabled')

    if err_flg == 1:
        stop_action()

keyboard.add_hotkey('home', start_action)
keyboard.add_hotkey('end', stop_action)

# %%
text_color = '#e08533'
bg_color = 'black'
bg_hover = '#e08533'

# Create an instance of tkinter frame or window
win=tk.Tk()
#set the back ground color
win.config(background=bg_color)

var = tk.IntVar()
active_text=tk.StringVar()
active_text.set("INACTIVE")

fuel_var=tk.IntVar()
#fuel_var.set(nToggle.fuel)

# Set the size of the window
win.title('Elite Auto Pilot')
#win.geometry("238x320")
win.geometry("580x360")

def toggle_off():
   active_text.set("INACTIVE")
   auto_status["fg"] = 'red'
   to_console('Auto Pilot off')

def toggle_on():
   active_text.set("ACTIVE")
   auto_status["fg"] = 'green'
   to_console('Auto Pilot on')

#set auto pilot on
def auto_on():
   if active_text.get() == "ACTIVE":
      toggle_off()
      stop_action()
   else:
      toggle_on()
      #start_action()

#set the fuel scoop percentange
def set_scoop(none):
   fuel_lvl = scoop_slide.get()
   #fuel_var.set(fuel_lvl)
   nToggle.fuel = fuel_lvl

#set the discover scan button primary or secondary
def set_scan():
   AutoToggle.scan_fire = var.get()
   if AutoToggle.scan_fire == 1:
      fire_btn = "PrimaryFire"
   else:
      fire_btn = "SecondaryFire"
   nToggle.scan_fire=fire_btn
   selection = nToggle.scan_fire + " selected"
   set_scan_btn(fire_btn)
   to_console(selection)

#event handler on button hover
def on_enter_auto(event):
   auto_status["background"] = bg_hover

def on_leave_auto(event):
   auto_status["background"] = bg_color

#functions to keep the scale object active to give it a different color
def active_delay():
   scoop_slide["state"] = 'active'

def keep_active(event):
   win.after(2, active_delay)

def btn_release(event):
   to_console("Fuel Scoop Threshold set to "+str(nToggle.fuel)+'%')

#create the autopilot statyic text
AutoText=tk.Label(
   win, 
   text="Auto Pilot", 
   fg=text_color, 
   font=("Helvetica", 16), 
   background=bg_color
   )

AutoText.grid(
   row = 0, 
   column = 0, 
   padx = (20,0), 
   pady = (20, 5),
   sticky = 'w'
   )

AutoText=tk.Label(
   win, 
   text="Key Binds", 
   fg=text_color, 
   font=("Helvetica", 16), 
   background=bg_color
   )

AutoText.grid(
   row = 0, 
   column = 3, 
   padx = (20,0), 
   pady = (20, 5),
   columnspan=3, 
   sticky = 'news'
   )

#create auto pilot toggle button default inactive
auto_status=tk.Button(
   win, 
   text="INACTIVE", 
   textvariable=active_text, 
   fg = 'red', 
   font=("Helvetica", 16), 
   height=1, 
   width=8, 
   activebackground=bg_hover, 
   background=bg_color, 
   borderwidth=0,
   command=auto_on
   )

auto_status.grid(
   row = 0, 
   column = 1,
   padx=(0,20),
   pady = (20,5)
   )

#check for button hover
auto_status.bind("<Enter>", on_enter_auto)
auto_status.bind("<Leave>", on_leave_auto)

fuel_text = tk.Label(
   win,
   text="Fuel Scoop Threshold", 
   fg=text_color, font=("Helvetica", 10), 
   background=bg_color
)

fuel_text.grid(
   row=2, 
   column=0, 
   padx=(20,5), 
   #sticky="sw",
   columnspan=2
   )

#create the fuel scoop percentage
scoop_slide = tk.Scale(win, 
   from_=0, to=100, 
   orient="horizontal",
   length=150,
   fg=text_color, 
   background=bg_color, 
   borderwidth=0, 
   activebackground='white', 
   troughcolor=text_color, 
   highlightthickness=5, 
   highlightcolor=bg_color, 
   highlightbackground=bg_color,
   state='active',
   foreground=text_color,
   showvalue=0,
   variable=fuel_var,
   command=set_scoop
   )

scoop_slide.bind("<Leave>", keep_active)
scoop_slide.bind("<Enter>", keep_active)
scoop_slide.bind("<ButtonRelease>", btn_release)
   

scoop_slide.set(nToggle.fuel)
scoop_slide.grid(
   row=3, 
   column=0,
   columnspan=2,
   padx=(20,20),  
   sticky="news"
   )

#display the current fuel scoop percentage
scoop_percent = tk.Label(
   win,
   text=str(nToggle.fuel)+"%",
   textvariable=fuel_var,
   fg=text_color, font=("Helvetica", 10),
   background=bg_color
)

scoop_percent.grid(
   row=4, 
   column=0, 
   padx=(0,0),
   sticky="e" 
   )

#add the fuel scoop percent sign
scoop_tick = tk.Label(
   win,
   text="%",
   fg=text_color, font=("Helvetica", 10),
   background=bg_color
)

scoop_tick.grid(
   row=4, 
   column=1,
   padx=0,
   sticky="w" 
   )

#create the scan label text
scan_label = tk.Label(
   win, 
   text="Discovery Scanner Layout", 
   fg=text_color, font=("Helvetica", 12), 
   background=bg_color
   )

scan_label.grid(
   row=5, 
   column=0, 
   padx=0, 
   pady=(5,5), 
   sticky="news", 
   columnspan=2
   )

#create radio button to select primary or secondary fire
R1 = tk.Radiobutton(
   win, 
   text="Primary", 
   variable=var, 
   fg=text_color, 
   value=1, 
   bg=bg_color, 
   command=set_scan,
   indicatoron=0,
   )

R1.grid(
   row=6, 
   column=0, 
   padx=(5,5),
   pady=(5,5), 
   sticky="e"
   )

R2 = tk.Radiobutton(
   win, 
   text="Secondary", 
   variable=var, 
   fg=text_color, 
   value=2, 
   bg=bg_color, 
   command=set_scan,
   indicatoron=0
   )

R2.grid(
   row=6, 
   column=1,
   padx=(5,5),
   pady=(5,5), 
   sticky="w" 
   )

if nToggle.scan_fire == "PrimaryFire":
   R1.select()
if nToggle.scan_fire == "SecondaryFire":
   R2.select()

console_text = st.ScrolledText(win,
   width = 55,
   height = 5, 
   font = ("Courier New", 10),
   fg='white',
   bg='black'
   )

#make the text box to display console output
console_text.grid(row= 8,column = 0,padx=(20,20), pady=(10,10), sticky='news', columnspan=31)
   
console_text.configure(state ='disabled')

text_handler = TextHandler(console_text) 
text_handler.setLevel(logging.INFO)
# Add the handler to logger
logger = logging.getLogger()
logger.addHandler(text_handler)

to_console('A GUI for EDAutopilot by hbzxc')
to_console('EDAutopilot created by skai2')
to_console('https://github.com/skai2/EDAutopilot')

load_logging_1()

buttondict={}
for count,  i in enumerate(keys):
   if i== 'HyperSuperCombination':
      i = 'HyperSuper'
   buttondict[count]=tk.Checkbutton(win, text=i, bg='black', fg='#e08533', disabledforeground='green')
   if keys.get(i)==0:
      buttondict[count].configure(disabledforeground='red')
   else:
      buttondict[count].select()

   buttondict[count].grid(row=(count%7)+1, column=(math.floor(count/7))+3, sticky='w')
   buttondict[count].configure(state='disabled')

win.mainloop()

#save any settings changes
settings_file = open("settings", "wb")
pickle.dump(nToggle, settings_file)
settings_file.close()


