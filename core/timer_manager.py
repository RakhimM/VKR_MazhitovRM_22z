from config import config

class TimerManager:
    def __init__(self, parent, scheduler, log_callback):
        self.parent = parent
        self.scheduler = scheduler
        self.log_callback = log_callback
        self.last_countdown_announce = 0
        self.monitoring = False

    def start_interval(self, value, unit):
        self.scheduler.start_interval(value, unit)
        self.log_callback(f"Таймер: каждые {value} {unit}", "info")
        self._start_monitoring()

    def start_at_time(self, time_str):
        self.scheduler.start_at_time(time_str)
        self.log_callback(f"Таймер: запуск в {time_str}", "info")
        self._start_monitoring()

    def stop(self):
        self.scheduler.stop()
        self.last_countdown_announce = 0
        self.log_callback("Таймер остановлен", "info")
        self.monitoring = False

    def _start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self._countdown_loop()

    def _countdown_loop(self):
        if not self.monitoring or not self.scheduler or not getattr(self.scheduler, 'running', False):
            return

        if config.get("show_countdown", False):
            rem = self.scheduler.get_seconds_to_next()
            step = config.get("countdown_step", 10)

            if rem is not None and rem > 0:
                if rem % step == 0 and rem != self.last_countdown_announce:
                    self.log_callback(f"До следующего теста осталось: {rem} сек.", "info")
                    self.last_countdown_announce = rem

        self.parent.after(1000, self._countdown_loop)