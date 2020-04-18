from algorithms.ss.ss import SpaceSaving


class SpaceSavingSlide(SpaceSaving):
    def __init__(self, args):
        super().__init__(args)

    def flush_table(self):
        pass

    def get_minimum_key(self):
        # find oldest flow, then find minimum val
        minimum_key = ''
        minimum_val = 2 << 31
        minimum_win = 2 << 31

        for k, v in self.table.items():
            win = v[1]
            if win < minimum_win:
                minimum_win = v[1]

        for k, v in self.table.items():
            val, win = v

            if win == minimum_win and val < minimum_val:
                minimum_key = k
                minimum_val = v[0]
                minimum_win = v[1]

        return minimum_key

    def insert(self, key, current_window):
        if key in self.table:
            val, win = self.table[key]
            window_diff = abs(current_window - win)

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