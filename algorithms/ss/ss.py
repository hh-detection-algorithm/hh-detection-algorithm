from algorithms.algorithm import Algorithm


class SpaceSaving(Algorithm):
    def __init__(self, args):
        super().__init__(args)
        self.init_table()

    def init_table(self):
        # flowId : (count, windowId)
        self.table = dict()

    def flush_table(self):
        self.init_table()

    def get_minimum_key(self):
        minimum_key = ''
        minimum_val = 2 << 31

        for k, v in self.table.items():
            val = v[0]

            if val < minimum_val:
                minimum_key = k
                minimum_val = v[0]
        return minimum_key

    def insert(self, key, current_window):
        if key in self.table:
            val, win = self.table[key]
            self.table[key] = (val + 1, current_window)
            return True
        else:
            if len(self.table) < self.NUM_COUNTERS:
                self.table[key] = (1, current_window)
                return True
            else:
                return False

    def evict_and_insert(self, key, current_window):
        minimum_key = self.get_minimum_key()
        minimum_val = self.table[minimum_key]
        self.table.pop(minimum_key)
        self.table[key] = (minimum_val[0] + 1, current_window)

    def simulate_algorithm(self, data):
        timestamp = data[0]
        ip = data[1]
        current_window = self.get_current_window_id(timestamp)

        if not self.insert(ip, current_window):
            self.evict_and_insert(ip, current_window)

    def generate_output(self):
        sorted_table = sorted(self.table, key=self.table.__getitem__, reverse=True)
        final_table = []
        for k in sorted_table:
            final_table.append((k,self.table[k][0], self.table[k][1]))
        return final_table
