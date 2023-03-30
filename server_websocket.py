#coding=utf-8

import asyncio
import json
import os
import websockets
import random
import subprocess
import socket
import time
import psutil
import glob
import platform
import wmi

if ('Windows' == platform.system()):
    print('Windows')
elif ('Linux' == platform.system()):
    print('Linux')
else:
    print(platform.system())


refresh_interval = 30

#获取windows硬盘
def disk():
    c = wmi.WMI ()
    Disks = []
    #默认测试假数据
    Disks.append({"ID": '345', 
                "IP": '123', 
                "Serial": '123', 
                "DeviceName": '123', 
                "Model": '123', 
                "Size": '123', 
                "Used": '123', 
                "Usaged": '123', 
                "NumOfPlot": '123', 
                "Temp": '123', 
                "Path": '123', 
                "Healthy": '123', 
                "GetDateTime": time.strftime("%Y-%m-%d %H:%M:%S")})
    for physical_disk in c.Win32_DiskDrive ():           
         Disks.append({"ID": '123', 
                "IP": '123', 
                "Serial": physical_disk.SerialNumber, 
                "DeviceName": physical_disk.Caption, 
                "Model": '123', 
                "Size": physical_disk.Size, 
                "Used": '123', 
                "Usaged": '123', 
                "NumOfPlot": '123', 
                "Temp": '123', 
                "Path": physical_disk.DeviceID, 
                "Healthy": physical_disk.Status, 
                "GetDateTime": time.strftime("%Y-%m-%d %H:%M:%S")})
         
        
    return Disks

def get_mounted_devices():
    # 获取已挂载的设备节点
    # 这个不适合windows，属于linux命令模式，需要做适配
    lines= ""
    if ('Windows' == platform.system()):
        print(platform.system())
    else:    
        try  :
            output = subprocess.check_output(['lsblk', '-o', 'NAME,MOUNTPOINT,TYPE', '-r']).decode('utf-8')
            lines = output.strip().split('\n')
        except Exception as e :
            print(e)
            print("Error Command: lsblk -o NAME,MOUNTPOINT,TYPE")
    

    devices = {}
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 3 and parts[1].startswith("/") and (not parts[1].startswith("/boot")) and (parts[2] == "disk" or parts[2] == "part"):
            devices[parts[0]] = parts[1]
    return devices

def get_disk_info(device):

    print('====================get_disk_info++=====================')

    # 获取硬盘信息
    lines = ""
    try  :
        
        output = subprocess.check_output(['smartctl', '-i', '/dev/' + device]).decode('utf-8')
        lines = output.strip().split('\n')
    except Exception as e :
        print(e)
        print("Error Command: smartctl -i /dev/" + device)
    
    info = {}
    info['model'] = "N/A"
    info['serial'] = "N/A"
    info['temperature'] = "N/A"
    info['capacity'] = "N/A"
    info['health'] = "Warning"


    for line in lines:
        parts = line.strip().split(':')
        if len(parts) == 2:

            key = parts[0].strip()
            value = parts[1].strip()
            # == 'Device Model'
            if 'Model' in key:
                info['model'] = value
            elif key == 'Serial Number':
                info['serial'] = value
    
    try  :
        output = subprocess.check_output(['hddtemp', '-n', '/dev/' + device]).decode('utf-8')
        lines = output.strip().split('\n')
        
    except Exception as e :
        print("Error Command: hddtemp -n /dev/"+device)

    for line in lines:
        parts = line.strip().split(':')
        if len(parts) == 1 and len(parts[0].strip()) < 3 and parts[0].strip().isdigit():
            info['temperature'] = parts[0].strip()

    # Health
    output = subprocess.check_output(['smartctl', '-H', '/dev/' + device]).decode('utf-8')
    lines = output.strip().split('\n')
    devices = {}
    for line in lines:
        if 'PASSED' in line:
            info['health'] = 'Health'

    print('====================get_disk_info--=====================')
    return info

def get_root_plot_files(path):
    # 获取硬盘根目录下的.plot文件数量
    plot_files = glob.glob(os.path.join(path, "*.plot"))
    return len(plot_files)

def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))  # 114.114.114.114也是dns地址
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# 获取CPU使用率
def get_cpu_usage():
    return psutil.cpu_percent(interval=3)

# 获取内存使用率和已用内存/总内存
def get_memory_usage():
    mem = psutil.virtual_memory()
    return mem.percent, mem.used / 1024 / 1024 / 1024, mem.total / 1024 / 1024 /1024


def getHumanSize(x):
    if x < 1024*1024:
        return str(round(x / 1024.0, 1)) + "M"
    elif x < 1024*1024*1024:
        return str(round(x / 1024.0 / 1024.0, 1)) + "G"
    else:
        return str(round(x / 1024.0 / 1024.0 / 1024.0, 1)) + "T"
    
    return "N/A"



async def send_json(websocket, path):
    while True:
        global refresh_interval
        time_interval = await websocket.recv()
        print("Server received: ", time_interval)
        if time_interval.isdigit():
            refresh_interval = int(time_interval)
            print("Server received : set refresh_interval = ", refresh_interval)

        monitor_data ={"Machines": [], 
                        'Disks': []}

        print("*******************************************")
        devices = get_mounted_devices()
        info={}
        Disks = []
        total_plot_num = 0
        inx = 0
        for device in devices:
            if os.path.exists("/dev/" + device):
                #print("-----device:------")
                #print("/dev/" + device)
                mount_point = devices[device]
                #print("-----mountpoint:------")
                #print(mount_point)
                
                info = get_disk_info(device)
                info['device']='/dev/' + device
                info['mountpoint'] = mount_point
                print('====================info=====================')
                print(info)
                print('====================info end=====================')
                
                print('Device: ' + info['device'])
                print('Mount point: ' + info['mountpoint'])
                print('Model: ' + info['model'])
                print('Serial: ' + info['serial'])
                print('Capacity: ' + info['capacity'])
                print('Temperature: ' + info['temperature'])
                print('Health: ' + info['health'])

                if mount_point != '':
                    output = subprocess.check_output(['df', mount_point]).decode('utf-8')
                    lines = output.strip().split('\n')
                    parts = lines[1].strip().split()
                    if len(parts) == 6:
                        total = 0
                        used = 0
                        usage = 0

                        if  parts[1].isdigit():
                            total = int(parts[1])

                        if parts[2].isdigit():
                            used = int(parts[2])
                        
                        info['capacity'] = getHumanSize(total)
                        info['used'] = getHumanSize(used)
                        info['usage'] = parts[4]
                        
                        plot_num = get_root_plot_files(mount_point)
                        total_plot_num += plot_num
                        info['plot'] = str(plot_num)
                        #total = parts[1]


                        print('Used capacity: ' + info['used'])
                        print('Usage percentage: ' + info['usage'])
                        print('Number of .plot : ' + info['plot'])
                        
                        inx += 1
                        Disks.append({"ID": str(inx), 
                                    "IP": local_ip, 
                                    "Serial": info['serial'], 
                                    "DeviceName": info['device'], 
                                    "Model": info['model'], 
                                    "Size": info['capacity'], 
                                    "Used": info['used'], 
                                    "Usaged": info['usage'], 
                                    "NumOfPlot": info['plot'], 
                                    "Temp": info['temperature'], 
                                    "Path": info['mountpoint'], 
                                    "Healthy": info['health'], 
                                    "GetDateTime": time.strftime("%Y-%m-%d %H:%M:%S")})
        print("*******************************************")
        
        if ('Windows' == platform.system()):
            Disks = disk()
        monitor_data['Disks'] = Disks

        mem_percent, mem_used, mem_total = get_memory_usage()

        Machines = []

        Machines.append({"IP": local_ip, 
                        "HardDiskNum": str(inx), 
                        "CpuUsaged": str(get_cpu_usage())+"%", 
                        "MemUsaged": str(mem_percent) + "%",
                        "MemUsed": str(round(mem_used,1)) + " GB/" + str(round(mem_total,1))+ "GB", 
                        "TotalPlot": str(total_plot_num), 
                        "GetDateTime": time.strftime("%Y-%m-%d %H:%M:%S")})
        monitor_data['Machines'] = Machines

        message = json.dumps(monitor_data)
        await websocket.send(message)
        print("Server sent: ", monitor_data)

        print("refresh_interval : ", refresh_interval)
        await asyncio.sleep(refresh_interval)


local_ip=get_host_ip()

start_server = websockets.serve(send_json, local_ip, 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()