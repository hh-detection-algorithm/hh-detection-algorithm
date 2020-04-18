from algorithms.algorithm import Algorithm


class CMS(Algorithm):

    def __init__(self, args):
        super().__init__(args)
        self.init_table()

    def init_table(self):
        # Table for CMS, Window ID (0, 0)
        # Set for FlowID
        self.table_cms = [[ (0, 0) for _ in range(self.STAGE_SIZE)] for _ in range(self.NUM_STAGES)]
        self.table_flows = set()

    def flush_table(self):
        self.init_table()

    def get_hash_indexes(self, ip):
        indexes = [self.get_index(ip, str(i)) for i in range(self.NUM_STAGES)]
        return indexes

    def increment(self, ip, current_window):
        self.table_flows.add(ip)
        indexes = self.get_hash_indexes(ip)

        for i in range(self.NUM_STAGES):
            current_index = indexes[i]
            val, win = self.table_cms[i][current_index]
            self.table_cms[i][indexes[i]] = (val+1, current_window)

    def simulate_algorithm(self, data):
        timestamp = data[0]
        ip = data[1]
        current_window = self.get_current_window_id(timestamp)
        self.increment(ip, current_window)

    def get_value(self, ip):
        minimum_val = 2 << 31
        minimum_win = 2 << 31
        indexes = self.get_hash_indexes(ip)

        for i in range(self.NUM_STAGES):
            val, win = self.table_cms[i][indexes[i]]
            # TODO: Tweak the policy, take minimum_win instead of minimum_val
            if val < minimum_val:
                minimum_val = val
                minimum_win = win
        return minimum_val, minimum_win

    def generate_output(self):
        final_table = []
        for key in self.table_flows:
            val, win = self.get_value(key)
            final_table.append((key, val, win))
        final_table = sorted(final_table, key=lambda tup: tup[1], reverse=True)
        return final_table
