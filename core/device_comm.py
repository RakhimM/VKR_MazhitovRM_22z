import serial
import time
import os
import threading


class DeviceComm:
    def __init__(self, port, baudrate=115200, data_bits=8, stop_bits=1, parity='N', flow_ctrl=0):
        self.port = port
        self.baudrate = baudrate
        self.data_bits = data_bits
        self.stop_bits = stop_bits
        self.parity = parity
        self.flow_ctrl = flow_ctrl

        self.serial = None
        self.irsp = 0
        self.state = None
        
        self.rx_thread = None
        self.running = False

    def open(self):
        try:
            parity_map = {
                'N': serial.PARITY_NONE,
                'E': serial.PARITY_EVEN,
                'O': serial.PARITY_ODD
            }

            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.data_bits,
                stopbits=self.stop_bits,
                parity=parity_map.get(self.parity, serial.PARITY_NONE),
                timeout=0,
                write_timeout=0,
                rtscts=(self.flow_ctrl == 0)
            )

            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            self.running = True

            self.rx_thread = threading.Thread(
                target=self._rx_worker,
                daemon=True
            )

            self.rx_thread.start()
            return True

        except Exception as e:
            print(f"Ошибка открытия порта: {e}")
            return False

    def close(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
            
        self.running = False

        if self.rx_thread:
            self.rx_thread.join(timeout=1)

    def write_raw(self, data):
        if self.serial and self.serial.is_open:
            return self.serial.write(data)
        return 0

    def wait_monitor_reply(self, timeout=0.2):
        start = time.time()
        self.state.prompt_received = 0

        while time.time() - start < timeout:
            if self.state.prompt_received == 3:
                return True
            time.sleep(0.01)

        return False

    def load_srec(self, file_path, progress_callback, check_broken):
        if not os.path.exists(file_path):
            return False

        self.state.load_srec = True

        with open(file_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            if check_broken():
                self.write_raw(b'\x18')
                break

            clean = line.strip() + '\r'

            for _ in range(7):
                self.irsp = 0
                self.write_raw(clean.encode())

                start = time.time()
                while self.irsp == 0 and (time.time() - start < 1):
                    time.sleep(0.01)

                if self.irsp == 1:
                    break

            if self.irsp == -1:
                break

            progress_callback()

        self.state.load_srec = False
        return True

    def write(self, data):

        return self.write_raw(data)

    def interrupt(self):

        self.write_raw(b"\x18")

    def check_monitor(self,
                    timeout=1.0):

        self.state.prompt_received = 0

        self.write_raw(b"\r")

        start = time.time()

        while time.time() - start < timeout:

            if self.state.prompt_received >= 3:
                return True

            time.sleep(0.01)

        return False
    
    def send_command(self, command):
    
        if not self.serial or not self.serial.is_open:
            raise RuntimeError("Порт не открыт")

        if not command.endswith("\r"):
            command += "\r"

        self.write_raw(
            command.encode("ascii")
        )
        
        
    def get_console_text(self):
    
        if not self.state.console_buffer:
            return ""

        text = "\n".join(
            self.state.console_buffer
        )

        self.state.console_buffer.clear()

        return text
    
    def _rx_worker(self):
        
        line_buffer = ""
        

        while self.running:

            try:

                if self.serial.in_waiting:

                    data = self.serial.read(
                        self.serial.in_waiting
                    )

                    text = data.decode(
                        "ascii",
                        errors="ignore"
                    )

                    for ch in text:

                        if ch == "\r":
                            continue

                        if ch == "\n":

                            line = line_buffer.strip()

                            if line:

                                self.state.console_buffer.append(
                                    line
                                )

                                self.state.current_line = line

                            line_buffer = ""

                        else:

                            line_buffer += ch

                            if ch == ">":
                                self.state.prompt_received += 1

                time.sleep(0.01)

            except Exception:
                break
            
    def write_memory(self, addr, value):
        
        cmd = f"#{addr:08X}W{value:08X}"

        self.write_raw(
            cmd.encode("ascii")
        )

        if not self.wait_monitor_reply(1.0):
            raise RuntimeError(
                f"Ошибка записи 0x{addr:08X}"
            )
            
    def read_memory(self, addr):
    
        self.state.current_line = ""

        cmd = f"#{addr:08X}R\r"

        self.write_raw(
            cmd.encode("ascii")
        )

        start = time.time()

        while time.time() - start < 1.0:

            line = self.state.current_line.strip()

            if line:
                try:
                    value = int(line, 16)

                    self.state.current_line = ""

                    return value

                except ValueError:
                    pass

            time.sleep(0.01)

        raise RuntimeError(
            f"Таймаут чтения адреса 0x{addr:08X}"
        )
        
    def set_vars_and_run(self, flags):
    
        if not self.check_monitor():
            raise RuntimeError("Монитор не отвечает")

        cmd = f"setvar 1 0x{flags:X}\r"

        self.write_raw(cmd.encode("ascii"))

        time.sleep(0.05)

        self.write_raw(b"run\r")