#!/usr/bin/python
import os
import gi
import subprocess  
import time
from threading import Thread

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator


def get_connected_devices():
    devices =  subprocess.check_output("bluetoothctl devices Connected", shell=True).strip().decode()
    devices = devices.split("\n")
    connected_devices = []
    for d in devices:
      d = d.split(' ')
      devId = d[1].replace(':','_')
      connected_devices.append((devId, 0, ''.join(d[2:])))
    return connected_devices


def get_battery_level(devId):
    level =  subprocess.check_output(f'dbus-send --print-reply=literal --system --dest=org.bluez /org/bluez/hci0/dev_{devId} org.freedesktop.DBus.Properties.Get string:"org.bluez.Battery1" string:"Percentage" | awk \'{{print $3}}\'', shell=True).strip().decode()
    return level

def create_indicator():
  indicator = appindicator.Indicator.new("bluetooth-active", "bluetooth", appindicator.IndicatorCategory.APPLICATION_STATUS)
  indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
  return indicator

def refresh_connected_devices():
  indicator = create_indicator()
  while True:
    connected_devices = get_connected_devices()
    for i, (devId, battery, devName) in enumerate(connected_devices):
      battery_level = get_battery_level(devId)
      connected_devices[i] = (devId, battery_level, devName)

    indicator.set_menu(create_bluetooth_menu(connected_devices))
    time.sleep(10)

def main():
  thread = Thread(target=refresh_connected_devices)
  thread.start()
  gtk.main()

def create_bluetooth_menu(devices):
  menu = gtk.Menu()
  
  for devId, battery, devName in devices:

    command_one = gtk.MenuItem()
    command_one.set_label(f'{devName} ({battery}%)')
    menu.append(command_one)
  
  menu.show_all()
  return menu
  

if __name__ == "__main__":
  main()