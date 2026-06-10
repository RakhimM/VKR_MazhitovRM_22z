import zlib

class MemoryTester:
    def __init__(self,
                 comm,
                 progress_callback,
                 log_callback):

        self.comm = comm

        self.progress_callback = progress_callback
        self.log_callback = log_callback

        self.running = True

    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        self.running = False

    # ========================================================
    # READ MEMORY
    # ========================================================

    def read_memory(self,
                    addr):

        return self.comm.read_memory(addr)

    # ========================================================
    # WRITE MEMORY
    # ========================================================

    def write_memory(self,
                     addr,
                     value):

        self.comm.write_memory(
            addr,
            value
        )

    # ========================================================
    # RAM TEST
    # ========================================================

    def test_external_ram(self,
                          start,
                          end):

        patterns = [
            0x00000000,
            0xFFFFFFFF,
            0x55555555,
            0xAAAAAAAA,
            0x12345678,
            0x87654321
        ]

        errors = 0

        total = (
            (end - start) // 4
        )

        current = 0

        for pattern in patterns:

            if not self.running:
                break

            self.log_callback(
                f"Паттерн {pattern:08X}",
                "info"
            )

            addr = start

            while addr < end:

                if not self.running:
                    break

                self.write_memory(
                    addr,
                    pattern
                )

                addr += 4

            addr = start

            while addr < end:

                if not self.running:
                    break

                val = self.read_memory(addr)

                if val != pattern:

                    errors += 1

                    self.log_callback(
                        f"RAM ERROR "
                        f"ADDR={addr:08X} "
                        f"READ={val:08X} "
                        f"EXP={pattern:08X}",
                        "error"
                    )

                addr += 4

                current += 1

                if self.progress_callback:

                    self.progress_callback(
                        int(
                            current * 100 /
                            (
                                total *
                                len(patterns)
                            )
                        )
                    )

        return errors

    # ========================================================
    # ROM CRC TEST
    # ========================================================

    def test_rom_crc(self,
                     start,
                     end,
                     expected_crc=None):

        data = bytearray()

        total = (
            (end - start) // 4
        )

        current = 0

        addr = start

        while addr < end:

            if not self.running:
                break

            val = self.read_memory(addr)

            if val is None:
                raise RuntimeError(
                    f"Ошибка чтения "
                    f"0x{addr:08X}"
                )

            data += val.to_bytes(
                4,
                "little"
            )

            addr += 4

            current += 1

            if self.progress_callback:

                self.progress_callback(
                    int(current * 100 / total)
                )

        crc = (
            zlib.crc32(data)
            &
            0xFFFFFFFF
        )

        err = 0

        if expected_crc is not None:

            if crc != expected_crc:
                err = 1

        return err, crc
