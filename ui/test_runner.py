import threading
import time
from memory_tests import MemoryTester
from config import config


class TestRunner:
    def __init__(self, parent, comm, output,
                 progress_callback,
                 log_callback):

        self.parent = parent
        self.comm = comm
        self.output = output

        self.progress_callback = progress_callback
        self.log_callback = log_callback

        self.testing_active = False
        self.tester = None

        self.cycle_count = 0
        self.total_errors = 0

        self.finish_callback = None

        
        self.ram_errors = 0
        self.rom_errors = 0
        self.exc_errors = 0

        self.rom_crc = 0

        
        self.client_ready = False
        self.in_function = False
        self.broken = False

    def start(self, tests_to_run, cycle_var, on_finished):

        if self.testing_active:
            return

        self.testing_active = True

        self.cycle_count = 0
        self.total_errors = 0

        self.ram_errors = 0
        self.rom_errors = 0
        self.exc_errors = 0

        self.rom_crc = 0

        self.broken = False

        self.finish_callback = on_finished

        threading.Thread(
            target=self._test_loop,
            args=(tests_to_run, cycle_var),
            daemon=True
        ).start()

    def stop(self):

        self.testing_active = False
        self.broken = True

        if self.tester:
            self.tester.stop()

        if self.comm:
            try:
                
                self.comm.interrupt()
            except Exception:
                pass

    def _test_loop(self, tests_to_run, cycle_var):

        while self.testing_active and not self.broken:

            self.cycle_count += 1

            self.parent.after(
                0,
                lambda: self._update_cycle_label()
            )

            cycle_errors = 0

            self.log_callback("")
            self.log_callback(
                f"================ ЦИКЛ {self.cycle_count} ================",
                "info"
            )

            if "ram" in tests_to_run or "rom" in tests_to_run:

                self.tester = MemoryTester(
                    self.comm,
                    self.progress_callback,
                    self.log_callback
                )

                if "ram" in tests_to_run and self.testing_active:

                    ram_start = config["ram_start"]
                    ram_end = config["ram_end"]

                    self.log_callback(
                        "=== Запуск теста внешнего ОЗУ ===",
                        "info"
                    )

                    try:

                        err = self.tester.test_external_ram(
                            ram_start,
                            ram_end
                        )

                        cycle_errors += err
                        self.ram_errors += err

                        self.log_callback(
                            f"Тест ОЗУ завершён. Ошибок: {err}",
                            "error" if err else "success"
                        )

                    except Exception as e:

                        err = 1

                        cycle_errors += err
                        self.ram_errors += err

                        self.log_callback(
                            f"Ошибка теста ОЗУ: {e}",
                            "error"
                        )

                if "rom" in tests_to_run and self.testing_active:

                    rom_start = config["rom_start"]
                    rom_end = config["rom_end"]

                    expected_crc = config.get("expected_crc")

                    self.log_callback(
                        "=== Запуск теста ПЗУ ===",
                        "info"
                    )

                    try:

                        err, crc = self.tester.test_rom_crc(
                            rom_start,
                            rom_end,
                            expected_crc
                        )

                        self.rom_crc = crc

                        cycle_errors += err
                        self.rom_errors += err

                        self.log_callback(
                            f"CRC32 = {crc:08X}",
                            "success" if err == 0 else "error"
                        )

                        self.log_callback(
                            f"Тест ПЗУ завершён. Ошибок: {err}",
                            "error" if err else "success"
                        )

                    except Exception as e:

                        err = 1

                        cycle_errors += err
                        self.rom_errors += err

                        self.log_callback(
                            f"Ошибка теста ПЗУ: {e}",
                            "error"
                        )

            exc_flags = 0

            if "cpu_exc" in tests_to_run:
                exc_flags |= (1 << 5)

            if "fpu_exc" in tests_to_run:
                exc_flags |= (1 << 6)

            if exc_flags and self.testing_active:

                self.log_callback(
                    "=== Запуск тестов исключений CPU/FPU ===",
                    "info"
                )

                self.log_callback(
                    f"Маска флагов: 0x{exc_flags:X}",
                    "info"
                )

                try:

                    self.comm.set_vars_and_run(exc_flags)

                    
                    timeout = 10.0
                    start = time.time()

                    while self.testing_active:

                        if time.time() - start > timeout:
                            raise TimeoutError(
                                "Таймаут теста исключений"
                            )

                        if self.comm.is_done():
                            break

                        time.sleep(0.05)

                except Exception as e:

                    cycle_errors += 1
                    self.exc_errors += 1

                    self.log_callback(
                        f"Ошибка при запуске тестов исключений: {e}",
                        "error"
                    )

            monitor_flags = 0

            if "monitor" in tests_to_run:

                monitor_flags |= 0xFFFFFFFF

            if monitor_flags and self.testing_active:

                try:

                    err = self._run_monitor_tests(
                        monitor_flags
                    )

                    cycle_errors += err

                except Exception as e:

                    cycle_errors += 1

                    self.log_callback(
                        f"Ошибка monitor tests: {e}",
                        "error"
                    )

            self.total_errors += cycle_errors

            self.log_callback("")

            self.log_callback(
                f"Всего ошибок в цикле "
                f"{self.cycle_count}: {cycle_errors}",
                "error" if cycle_errors else "success"
            )

            
            
            

            if not cycle_var.get():
                break

            if not self.testing_active:
                break

            
            for _ in range(20):

                if not self.testing_active:
                    break

                time.sleep(0.25)

        self.parent.after(0, self._finish)

    def _update_cycle_label(self):

        if hasattr(self.parent, "cycle_label"):

            self.parent.cycle_label.config(
                text=f"Цикл {self.cycle_count}"
            )

    def _finish(self):

        self.testing_active = False

        if self.tester:
            self.tester.stop()

        self.tester = None

        self.log_callback("")
        self.log_callback(
            "=== Тестирование завершено ===",
            "info"
        )

        if self.finish_callback:

            self.finish_callback(
                total_errors=self.total_errors,
                cycles=self.cycle_count,
                ram_err=self.ram_errors,
                rom_err=self.rom_errors,
                exc_err=self.exc_errors,
                crc=self.rom_crc
            )

    def _run_monitor_tests(self,
                        flags):

        self.log_callback(
            "=== Запуск monitor tests ===",
            "info"
        )

        if not self.comm.check_monitor():

            raise RuntimeError(
                "Монитор не отвечает"
            )

        self.log_callback(
            "Monitor OK",
            "success"
        )

        vars_to_send = [

            (0, config.get("language", 0)),
            (1, flags),
            (2, config.get("details", 0)),
            (3, config.get("dpk_group", 0)),
            (4, config.get("new_sw6", 0)),
            (5, config.get("eth_packet_size", 1024)),
            (6, config.get("eth_num_packs", 64)),
            (7, config.get("npack", 100))
        ]

        self.comm.state.no_report = True

        for idx, value in vars_to_send:

            cmd = (
                f"setvar {idx} 0x{value:X}\r"
            )

            self.comm.write_raw(
                cmd.encode("ascii")
            )

            time.sleep(0.02)

        self.comm.state.no_report = False
        self.comm.write_raw(
            b"run\r"
        )

        self.log_callback(
            "Команда RUN отправлена",
            "info"
        )

        start = time.time()
        timeout = 60.0

        while self.testing_active:
            if self.comm.state.done:

                self.comm.state.done = False

                self.log_callback(
                    "Monitor tests done",
                    "success"
                )

                return 0

            if self.broken:

                self.comm.write_raw(b"\x18")

                raise RuntimeError(
                    "Тест прерван"
                )

            if (
                self.comm.state.com_command >= 0
                and
                not self.in_function
            ):

                cmd = self.comm.state.com_command

                self.log_callback(
                    f"COM CALLBACK: {cmd}",
                    "info"
                )

                self.comm.state.com_command = -1

            if time.time() - start > timeout:

                raise TimeoutError(
                    "Timeout monitor test"
                )

            time.sleep(0.01)

        return 0