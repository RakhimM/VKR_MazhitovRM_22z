import threading
import time
import serial.tools.list_ports
from tkinter import messagebox
from core.comm_state import CommState
from core.device_comm import DeviceComm

class PortManager:
    def __init__(self,
                 parent,
                 output,
                 status_label):

        self.parent = parent
        self.output = output
        self.status_label = status_label

        self.comm = None

        self.state = CommState()

        self.reader_thread = None
        self.reader_running = False

    def refresh_ports(self,
                      combo):

        ports = [
            p.device
            for p in serial.tools.list_ports.comports()
        ]

        combo["values"] = ports

    def open_port(self,
                  port,
                  config,
                  btn_open,
                  btn_close):

        if not port:

            messagebox.showerror(
                "Ошибка",
                "Выберите COM-порт"
            )

            return False

        self.comm = DeviceComm(
            port,
            baudrate=config.get(
                "com_baudrate",
                115200
            ),
            data_bits=config.get(
                "com_data_bits",
                8
            ),
            stop_bits=config.get(
                "com_stop_bits",
                1
            ),
            parity=config.get(
                "com_parity",
                "N"
            ),
            flow_ctrl=config.get(
                "com_flow_ctrl",
                0
            )
        )

        self.comm.state = self.state
        self.comm.log = self.output.print_message

        if not self.comm.open():

            messagebox.showerror(
                "Ошибка",
                f"Не удалось открыть {port}"
            )

            return False

        self.state.prompt_received = 0
        self.state.client_ready = False
        self.state.done = False

        self.reader_running = True

        self.reader_thread = threading.Thread(
            target=self._read_loop,
            daemon=True
        )

        self.reader_thread.start()

        self.status_label.config(
            text=f"{port} открыт",
            foreground="green"
        )

        btn_open.config(
            state="disabled"
        )

        btn_close.config(
            state="normal"
        )

        self.output.print_message(
            "Порт подключен",
            "success"
        )

        return True

    def close_port(self,
                   btn_open,
                   btn_close):

        self.reader_running = False

        if self.reader_thread:
            self.reader_thread.join(
                timeout=1
            )

        if self.comm:
            self.comm.close()

        self.status_label.config(
            text="Порт закрыт",
            foreground="red"
        )

        btn_open.config(
            state="normal"
        )

        btn_close.config(
            state="disabled"
        )

    def check_monitor(self):

        if not self.comm:
            return False

        self.state.prompt_received = 0

        try:

            self.comm.write(b"\r")

        except Exception:
            return False

        start = time.time()

        while time.time() - start < 10.0:

            if self.state.prompt_received >= 3:
                return True

            time.sleep(0.01)

        return False

    def get_monitor_reply(self,
                          timeout=2.0):

        self.state.prompt_received = 0

        start = time.time()

        while time.time() - start < timeout:

            if self.state.prompt_received >= 3:
                return True

            time.sleep(0.01)

        return False

    def send_command(self,
                     cmd,
                     wait_reply=True):

        try:

            if not cmd.endswith("\r"):
                cmd += "\r"

            self.comm.write(
                cmd.encode("ascii")
            )

            self.output.print_message(
                f">>> {cmd.strip()}",
                "info"
            )

            if wait_reply:
                return self.get_monitor_reply()

            return True

        except Exception as e:

            self.output.print_message(
                f"Ошибка отправки: {e}",
                "error"
            )

            return False

    def _read_loop(self):
    
        state = self.state

        line_buffer = ""

        while (
            self.reader_running and
            self.comm and
            self.comm.serial and
            self.comm.serial.is_open
        ):

            try:

                if self.comm.serial.in_waiting:

                    data = self.comm.serial.read(
                        self.comm.serial.in_waiting
                    )

                    for val in data:

                        if val == 0x10:
                            state.busy = False

                        elif val == 0x11:
                            state.color = "blue"

                        elif val == 0x12:
                            state.color = "red"

                        elif val == 0x14:
                            state.done = True

                        elif val == 0x15:

                            if state.load_srec:
                                state.irsp = -1

                        elif val == 0x06:

                            if state.load_srec:
                                state.irsp = 1

                        elif val == 0x07:
                            state.client_ready = True

                        elif val == 0x0C:
                            state.com_get_command = True

                        elif (
                            val == ord('\r') or
                            (
                                val == ord('>')
                                and
                                state.prompt_received == 2
                            )
                        ):

                            state.prompt_received += 1

                            if state.prompt_received > 3:
                                state.prompt_received = 0

                        elif state.com_get_hex_data:

                            ch = chr(val)

                            if ch == "#":

                                state.hex_buffer = ""

                            elif ch == ">":

                                state.com_get_hex_data = False

                            elif (
                                ch.lower()
                                in
                                "0123456789abcdef"
                            ):

                                state.hex_buffer += ch

                                if len(state.hex_buffer) == 8:

                                    state.last_hex_word = (
                                        state.hex_buffer
                                    )

                                    state.com_got_hex_word = True

                                    state.hex_buffer = ""

                            else:

                                state.hex_buffer = ""

                        elif val == ord("\n"):

                            self.output.print_message(
                                line_buffer,
                                state.color
                            )

                            line_buffer = ""

                        elif val >= 0x20:

                            line_buffer += chr(val)

                    if line_buffer:

                        self.output.print_message(
                            line_buffer,
                            state.color
                        )

                        line_buffer = ""

                else:

                    time.sleep(0.01)

            except Exception as e:

                print(e)
                break

    def is_open(self):

        return (
            self.comm and
            self.comm.serial and
            self.comm.serial.is_open
        )


