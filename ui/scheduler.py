import time
import threading

class TestScheduler:
    def __init__(self, test_callback):
        self.test_callback = test_callback
        self.running = False
        self._next_run_time = None
        self._timer_thread = None

    def start_interval(self, value, unit):
        if unit == "minutes":
            seconds = value * 60
        elif unit == "hours":
            seconds = value * 3600
        else:
            seconds = value
        self.running = True
        self._next_run_time = time.time() + seconds
        self._schedule_next(seconds)

    def start_at_time(self, time_str):
        now = time.localtime()
        target_h, target_m = map(int, time_str.split(':'))
        target = time.mktime((now.tm_year, now.tm_mon, now.tm_mday,
                              target_h, target_m, 0, 0, 0, -1))
        if target <= time.time():
            target += 86400  # следующий день
        self.running = True
        self._next_run_time = target
        self._schedule_next(target - time.time())

    def _schedule_next(self, delay):
        if not self.running:
            return
        self._timer_thread = threading.Timer(delay, self._run_test)
        self._timer_thread.start()

    def _run_test(self):
        if not self.running:
            return
        self.test_callback()
        if self.running and self._next_run_time is not None:
            now = time.time()
            if hasattr(self, '_interval_seconds'):
                self._next_run_time = now + self._interval_seconds
                self._schedule_next(self._interval_seconds)

    def stop(self):
        self.running = False
        if self._timer_thread and self._timer_thread.is_alive():
            self._timer_thread.cancel()
        self._next_run_time = None

    def get_seconds_to_next(self):
        if not self.running or self._next_run_time is None:
            return None
        delta = self._next_run_time - time.time()
        return max(0, int(delta))