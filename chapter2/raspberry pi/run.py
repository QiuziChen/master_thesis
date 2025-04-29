"""
Execute brake pad pressure and GPS recording procedure.
step1: detecting GPS signal
step2: calibration
    - Zeroing: an empty state with no pressure applied (5 sec)
    - Loading: place your foot on the pedal without applying additional pressure (5 sec)
    - Pressing: press the brake padel to the end for 3 times
    - Unloading: the final unoccupied state, where all pressure is released (5 sec)
step3: recording
step4: saving records
"""


import time
import serial
import re
from toolkits import readADC, calR 

utctime = ''
lat = ''
ulat = ''
lon = ''
ulon = ''
numSv = ''
msl = ''
cogt = ''
cogm = ''
sog = ''
kph = ''
gps_t = 0

ser = serial.Serial("/dev/ttyUSB0", 9600)

if ser.isOpen():
    print("GPS Serial Opened! Baudrate=9600")
else:
    print("GPS Serial Open Failed!")


def Convert_to_degrees(in_data1, in_data2):
    len_data1 = len(in_data1)
    str_data2 = "%05d" % int(in_data2)
    temp_data = int(in_data1)
    symbol = 1
    if temp_data < 0:
        symbol = -1
    degree = int(temp_data / 100.0)
    str_decimal = str(in_data1[len_data1-2]) + str(in_data1[len_data1-1]) + str(str_data2)
    f_degree = int(str_decimal)/60.0/100000.0
    # print("f_degree:", f_degree)
    if symbol > 0:
        result = degree + f_degree
    else:
        result = degree - f_degree
    return result


def GPS_read():
        global utctime
        global lat
        global ulat
        global lon
        global ulon
        global numSv
        global msl
        global cogt
        global cogm
        global sog
        global kph
        global gps_t
        if ser.inWaiting():
            if ser.read(1) == b'G':
                if ser.inWaiting():
                    if ser.read(1) == b'N':
                        if ser.inWaiting():
                            choice = ser.read(1)
                            if choice == b'G':
                                if ser.inWaiting():
                                    if ser.read(1) == b'G':
                                        if ser.inWaiting():
                                            if ser.read(1) == b'A':
                                                #utctime = ser.read(7)
                                                GGA = ser.read(70)
                                                GGA_g = re.findall(r"\w+(?=,)|(?<=,)\w+", str(GGA))
                                                # print(GGA_g)
                                                if len(GGA_g) < 13:
                                                    print("GPS no found")
                                                    gps_t = 0
                                                    return 0
                                                else:
                                                    utctime = GGA_g[0]
                                                    # lat = GGA_g[2][0]+GGA_g[2][1]+'°'+GGA_g[2][2]+GGA_g[2][3]+'.'+GGA_g[3]+'\''
                                                    lat = "%.8f" % Convert_to_degrees(str(GGA_g[2]), str(GGA_g[3]))
                                                    ulat = GGA_g[4]
                                                    # lon = GGA_g[5][0]+GGA_g[5][1]+GGA_g[5][2]+'°'+GGA_g[5][3]+GGA_g[5][4]+'.'+GGA_g[6]+'\''
                                                    lon = "%.8f" % Convert_to_degrees(str(GGA_g[5]), str(GGA_g[6]))
                                                    ulon = GGA_g[7]
                                                    numSv = GGA_g[9]
                                                    msl = GGA_g[12]+'.'+GGA_g[13]+GGA_g[14]
                                                    #print(GGA_g)
                                                    gps_t = 1
                                                    return 1
                            elif choice == b'V':
                                if ser.inWaiting():
                                    if ser.read(1) == b'T':
                                        if ser.inWaiting():
                                            if ser.read(1) == b'G':
                                                if gps_t == 1:
                                                    VTG = ser.read(40)
                                                    VTG_g = re.findall(r"\w+(?=,)|(?<=,)\w+", str(VTG))
                                                    cogt = VTG_g[0]+'.'+VTG_g[1]+'T'
                                                    if VTG_g[3] == 'M':
                                                        cogm = '0.00'
                                                        sog = VTG_g[4]+'.'+VTG_g[5]
                                                        kph = VTG_g[7]+'.'+VTG_g[8]
                                                    elif VTG_g[3] != 'M':
                                                        cogm = VTG_g[3]+'.'+VTG_g[4]
                                                        sog = VTG_g[6]+'.'+VTG_g[7]
                                                        kph = VTG_g[9]+'.'+VTG_g[10]
                                                #print(kph)

# record params
channel = 0  # channel of sensor
freq = 1  # recording frequency 
records = []  # initial records
header = "UTC Lat Lon Num_of_Sate Alt TNH MNH Speed Digi_output Resist\n"  # header
records.append(header)
data = ""

type = input("Type 0 for Calibration and 1 for Recording\n")
veh_cls = input("Input vehicle level:\n")
fuel_type = input("Input fuel_type:\n")
date = input("Input date (e.g.: 2024-01-01):\n")
driver_id = input("Input driver_id:\n")

# Open the file in append mode
if '0' in type:
    file_path = f"./records/calibration_{veh_cls}_{fuel_type}_{date}_{driver_id}.txt"
else:
    file_path = f"./records/recording_{veh_cls}_{fuel_type}_{date}_{driver_id}.txt"

with open(file_path, 'a') as f:
    # Write the header
    f.write(header)

    print("Recording Started!")
    print("=============================")

    try:
        while True:
            if GPS_read():
                # pressure
                pad_digi = readADC(channel)  # digital output
                pad_resistance = calR(pad_digi)  # resistance of the pressure sensor
                # print
                print("%d:%s:%s lat:%s lon:%s v:%skm/h alt:%s pad:%d" % (int(utctime[:2])+8, utctime[2:4], utctime[4:], lat, lon, kph, msl[:-1], pad_digi))
                # store
                data = "%s %s %s %s %s %s %s %s %d %.2f\n" % (int(utctime)+80000, lat, lon, numSv, msl[:-1], cogt[:-1], cogm, kph, pad_digi, pad_resistance)
                records.append(data)
                # Write the data to the file
                f.write(data)
                f.flush()  # Ensure data is written to the file immediately

    except KeyboardInterrupt:
        # check length of records
        l_record = len(records)
        print("Length of records: %d." % l_record)
        with open(file_path, 'rb') as file:
            l_file = sum(1 for line in file)
            print("Length of saved file: %d" % l_file)
        # re-saved
        if l_file < l_record:
            if '0' in type:
                file_path_re = f"./records/calibration_{veh_cls}_{fuel_type}_{date}_{driver_id}_resave.txt"
            else:
                file_path_re = f"./records/recording_{veh_cls}_{fuel_type}_{date}_{driver_id}_resave.txt"
            
            with open(file_path_re, 'wb')as f:
                f.writelines(records)
            print('Re-saved!')
        
        ser.close()
        print("Execution done!")