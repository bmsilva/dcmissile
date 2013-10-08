import logging
log = logging.getLogger(__name__)

import time
import usb.core

from django.core.urlresolvers import reverse 
from django.shortcuts import redirect

from dcmissile.util.decorators import do
from dcmissile.www.forms import MissileForm

DOWN    = 0x01
UP      = 0x02
LEFT    = 0x04
RIGHT   = 0x08
FIRE    = 0x10
STOP    = 0x20

USB_DEVICE = None

@do('home.html')
def home(request):
    global USB_DEVICE
    if USB_DEVICE is None:
        USB_DEVICE = setup_usb()
    form = MissileForm(request.POST or None)
    log.debug("got a %s" % request.method)
    if form.is_valid():
        log.debug("form is valid")
        action = form.cleaned_data['action']
        parameter = form.cleaned_data['parameter']
        run_command(action, parameter)
        return redirect(reverse('home'))
    else:
        log.debug(request.POST)
    return {
        'form': form,
    }

def setup_usb():
    # Tested only with the Cheeky Dream Thunder
    device = usb.core.find(idVendor=0x2123, idProduct=0x1010)

    if device is None:
        raise ValueError('Missile device not found')

    device.set_configuration()

    return device

def run_command(command, value):
    if command == "right":
        send_move(RIGHT, value)
    elif command == "left":
        send_move(LEFT, value)
    elif command == "up":
        send_move(UP, value)
    elif command == "down":
        send_move(DOWN, value)
    elif command == "zero" or command == "park" or command == "reset":
        # Move to bottom-left
        send_move(DOWN, 2000)
        send_move(LEFT, 8000)
    elif command == "pause" or command == "sleep":
        time.sleep(value / 1000.0)
    elif command == "fire" or command == "shoot":
        if value < 1 or value > 4:
            value = 1
        # Stabilize prior to the shot, then allow for reload time after.
        time.sleep(0.5)
        for i in range(value):
            send_cmd(FIRE)
            time.sleep(4.5)

def send_move(cmd, duration_ms):
    send_cmd(cmd)
    time.sleep(duration_ms / 1000.0)
    send_cmd(STOP)

def send_cmd(cmd):
    USB_DEVICE.ctrl_transfer(0x21, 0x09, 0, 0,
        [0x02, cmd, 0x00,0x00,0x00,0x00,0x00,0x00])
