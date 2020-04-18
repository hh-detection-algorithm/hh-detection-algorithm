from algorithms.ss.ss import SpaceSaving


class SpaceSavingPAge(SpaceSaving):
    def __init__(self, args):
        super().__init__(args)

    def flush_table(self):
        pass

    def insert(self, key, current_window):
        if key in self.table:
            val, win = self.table[key]
            window_diff = abs(current_window - win)
            val = val >> window_diff

            if window_diff <= self.WINDOW_OFFSET:
                self.table[key] = (val + 1, current_window)
            else:
                self.table[key] = (1, current_window)

            return True
        else:
            if len(self.table) < self.NUM_COUNTERS:
                self.table[key] = (1, current_window)
                return True
            else:
                return False

    def evict_and_insert(self, key, current_window):
        minimum_key = self.get_minimum_key()
        minimum_val, minimum_win = self.table[minimum_key]

        window_diff = abs(current_window - minimum_win)
        minimum_val = minimum_val >> window_diff

        self.table.pop(minimum_key)
        self.table[key] = (minimum_val + 1, current_window)