import json
import os

CONFIG_FILE = "data/memory_test_config.json"

def load_config():
    default = {
        "com_port": "",
        "com_baudrate": 115200,
        "com_data_bits": 8,
        "com_stop_bits": 1,
        "com_parity": "N",
        "com_flow_ctrl": 0,
        "ram_start": 0x00000000,
        "ram_end": 0x0001FFFF,
        "rom_start": 0x00000000,
        "rom_end": 0x000FFFFF,
        "details": True,
        "language": 0,
        "cycle_tests": False,
        "expected_crc": None,
        "show_com_toolbar": True,
        "selected_tests": ["ram", "rom", "cpu_exc", "fpu_exc"]
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                saved = json.load(f)
                default.update(saved)
        except:
            pass
    return default


def save_config(cfg):
    os.makedirs("data", exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=4)


config = load_config()