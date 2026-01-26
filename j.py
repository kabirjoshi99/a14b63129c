import datetime
import time
from winreg import (HKEY_CURRENT_USER, KEY_QUERY_VALUE, KEY_SET_VALUE, OpenKey,
                    QueryValueEx, REG_BINARY, SetValueEx)
import psutil
import os
import logging
interval = 0.05

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def disable() -> None:
    with OpenKey(
        HKEY_CURRENT_USER,
        r'Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections',
        access=KEY_QUERY_VALUE | KEY_SET_VALUE
    ) as connections:
        settings = bytearray(QueryValueEx(connections, 'DefaultConnectionSettings')[0])
        
        # Increment version number
        settings[0x4:0x8] = (int.from_bytes(settings[0x4:0x8], 'little') + 1).to_bytes(4, 'little')

        # Disable proxy settings (set to 0)
        settings[0x8:0xc] = (0x1).to_bytes(4, 'little')

        SetValueEx(connections, 'DefaultConnectionSettings', 0, REG_BINARY, bytes(settings))

def get_processes_in_folder(target_folder):
    processes = []
    for process in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            process_path = process.info['exe']
            if process_path and os.path.dirname(process_path) == target_folder:
                processes.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def kill_processes(processes, exclude_list):
    for process in processes:
        if process.name() not in exclude_list:
            try:
                process.terminate()
                logging.info(f"Found 1 Process(es) in target folder. Terminated: {process.name()} (PID: {process.pid})")
            except psutil.AccessDenied:
                logging.warning(f"Access Denied: Cannot terminate {process.name()} (PID: {process.pid})")
            except psutil.NoSuchProcess:
                logging.info(f"Process already terminated: {process.name()} (PID: {process.pid})")

def main():
    target_folder = r"C:\Program Files\DyKnow\Cloud\7.12.1.55" 
    exclude_list = ['winProcess.exe'] 


    try:
        processes = get_processes_in_folder(target_folder)
        if processes:
             kill_processes(processes, exclude_list)

    
    except KeyboardInterrupt:
        logging.info("Process stopped by user.")

if __name__ == '__main__':
    print ("Disabler Active")
    while True:
        disable()
        main()
        time.sleep(interval)
