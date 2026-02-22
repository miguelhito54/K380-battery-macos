import hid, time, subprocess, os, sys

VID = 0x046D
PID = 0xB342
BATTERY_FILE = '/tmp/k380_battery.txt'

if '--force' in sys.argv:
    battery = sys.argv[sys.argv.index('--force') + 1]
    print(f"🔧 Forzando batería a {battery}%")
    subprocess.run(f'echo "{battery}" | shortcuts run "UpdateK380"', shell=True)
    print("✅ Listo")
    sys.exit()

if os.geteuid() == 0:
    devices = hid.enumerate(VID, PID)
    dev_info = [d for d in devices if d['usage_page'] == 65280][0]
    device = hid.Device(path=dev_info['path'])
    device.nonblocking = 1
    request = bytes([0x10, 0xFF, 0x06, 0x00, 0x00, 0x00, 0x00])
    device.write(b'\x00' + request)
    time.sleep(0.5)
    for _ in range(10):
        data = device.read(64)
        if data and len(data) > 4 and data[2] == 0x06:
            with open(BATTERY_FILE, 'w') as f:
                f.write(str(data[4]))
            print(f"🔋 Batería: {data[4]}%")
            break
        time.sleep(0.1)
    device.close()
else:
    with open(BATTERY_FILE) as f:
        battery = f.read().strip()
    print(f"Actualizando AllMyBatteries con {battery}%")
    subprocess.run(f'echo "{battery}" | shortcuts run "UpdateK380"', shell=True)
    print("✅ Listo")