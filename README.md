# 🔋 K380 Battery Monitor for macOS

Extract the battery level from a **Logitech K380 keyboard** and display it in **AllMyBatteries** — automatically, every 5 minutes.

> macOS does not expose battery information for Logitech devices natively. This project reverse-engineers the **HID++ 2.0 protocol** to read the battery level directly from the keyboard and pipe it into AllMyBatteries via a Siri Shortcut.

![AllMyBatteries showing K380 battery level](assets/screenshot.png)

---

## How it works

The K380 connects to macOS as a classic Bluetooth HID device. While macOS doesn't expose its battery, the keyboard implements **Logitech's proprietary HID++ 2.0 protocol** on a hidden interface (Usage Page `0xFF00`).

The process:

1. **Discover** the HID++ interface on the K380 (Usage Page `0xFF00`)
2. **Query** the battery feature index (`0x1000` → resolves to `0x06`)
3. **Read** the battery level by calling that feature (`getBatteryLevelStatus`)
4. **Write** the result to a temp file (`/tmp/k380_battery.txt`)
5. **Update** AllMyBatteries via a Siri Shortcut (`shortcuts run "UpdateK380"`)
6. **Automate** with `launchd` to run every 5 minutes

### HID++ Protocol Details

```
Request:  [0x10, 0xFF, 0x06, 0x00, 0x00, 0x00, 0x00]
Response: [0x11, 0xFF, 0x06, 0x00, BATTERY%, ...]
```

The battery percentage is at byte index 4 of the response.

---

## Requirements

- macOS (tested on macOS 15)
- Python 3.x
- [hidapi](https://github.com/libusb/hidapi) (`brew install hidapi`)
- Python `hid` library (`pip3 install hid`)
- [AllMyBatteries](https://apps.apple.com/app/all-my-batteries/id1621263412) (App Store)
- macOS Shortcuts app

---

## Installation

### 1. Install dependencies

```bash
brew install hidapi
pip3 install hid
```

Patch the `hid` library to find hidapi without `DYLD_LIBRARY_PATH`:

```bash
sudo sed -i '' "s|'libhidapi.dylib'|'/usr/local/lib/libhidapi.dylib'|" \
  $(python3 -c "import site; print(site.getsitepackages()[0])")/hid/__init__.py
```

### 2. Allow sudo without password for Python

```bash
sudo visudo
```

Add these lines:

```
Defaults env_keep += "DYLD_LIBRARY_PATH"
miguel ALL=(ALL) NOPASSWD: /usr/local/bin/python3
```

### 3. Set up AllMyBatteries

1. Open AllMyBatteries → Add Device → **Custom Device**
2. Name it `Keyboard` and set an initial battery level
3. Open the **Shortcuts** app on macOS
4. Create a new shortcut named `UpdateK380`:
   - Add action: **"Modify battery level manually"** (from AllMyBatteries)
   - Select device: `Keyboard`
   - Set battery level to: **Shortcut Input**

### 4. Clone and configure

```bash
git clone https://github.com/yourusername/k380-battery-macos
cd k380-battery-macos
```

Edit `run_k380.sh` and `k380.py` to match your Python path if needed.

### 5. Set up launchd automation

```bash
cp launchd/com.miguel.k380battery.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.miguel.k380battery.plist
```

Verify it's running:

```bash
launchctl list | grep k380
# Should show: [PID]  0  com.miguel.k380battery
```

---

## Usage

**Run manually:**

```bash
bash run_k380.sh
```

**Force a specific value (for testing):**

```bash
python3 k380.py --force 50
```

**Check launchd status:**

```bash
launchctl list | grep k380
```

---

## Project Structure

```
k380-battery-macos/
├── README.md
├── k380.py                              # Main script
├── run_k380.sh                          # Shell wrapper (sudo + user)
└── launchd/
    └── com.miguel.k380battery.plist     # launchd automation config
```

---

## Why this exists

Logitech does not expose battery information to macOS via standard HID Battery Service (`0x180F`). Their official app (Logi Options+) uses a proprietary HID++ protocol to fetch this data. This project replicates that behavior without requiring Logi Options+ to be installed.

---

## References

- [HID++ Protocol Documentation](https://lekensteyn.nl/files/logitech/logitech_hidpp_2.0_specification_draft_2012-06-04.pdf)
- [Logitech HID++ Feature 0x1000 - Battery Status](https://github.com/pwr-Solaar/Solaar)
- [AllMyBatteries](https://apps.apple.com/app/all-my-batteries/id1621263412)

---

## License

MIT
