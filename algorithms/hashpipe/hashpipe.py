from algorithms.algorithm import Algorithm


class HashPipe(Algorithm):
    def __init__(self, args):
        super().__init__(args)

    def init_table(self):
        self.table = [[(0, 0, 0) for _ in range(self.STAGE_SIZE)] for _ in range(self.NUM_STAGES)]

    def flush_table(self):
        self.init_table()

    def insert_first_stage(self, data):
        timestamp = data[0]  # 1458219600.000000
        ip = data[1]  # 184.21.144.173,211.106.242.60,6,80,43053
        current_window = self.get_current_window_id(timestamp)

        index = self.get_index(ip, 0)
        key = self.table[0][index][0]
        val = self.table[0][index][1]
        win = self.table[0][index][2]

        if key == ip:
            self.table[0][index] = (key, val + 1, current_window)
            return  # return if inserted
        elif key == 0:
            self.table[0][index] = (ip, 1, current_window)
            return  # return if inserted
        else:
            self.table[0][index] = (ip, 1, current_window)
            carried_key = key
            carried_val = val
            carried_window_id = win
            return carried_key, carried_val, carried_window_id  # proceed to next stage

    def insert_remaining_stages(self, carried_data, current_stage):
        if current_stage >= self.NUM_STAGES or not carried_data:
            return  # reached maximum stage

        carried_key = carried_data[0]
        carried_val = carried_data[1]
        carried_window_id = carried_data[2]

        index = self.get_index(carried_key, current_stage)
        key = self.table[current_stage][index][0]
        val = self.table[current_stage][index][1]
        win = self.table[current_stage][index][2]

        if key == carried_key:
            self.table[current_stage][index] = (carried_key, val + carried_val, carried_window_id)
            return  # return if inserted
        elif key == 0:
            self.table[current_stage][index] = (carried_key, carried_val, carried_window_id)
            return  # return if inserted
        elif carried_val > val:
            temp_key = carried_key
            temp_val = carried_val
            temp_win = carried_window_id
            carried_key = key
            carried_val = val
            carried_window_id = win
            self.table[current_stage][index] = (temp_key, temp_val, temp_win)
            # proceed to next stage
            self.insert_remaining_stages((carried_key, carried_val, carried_window_id), current_stage + 1)
        else:
            self.insert_remaining_stages((carried_key, carried_val, carried_window_id), current_stage + 1)

    def simulate_algorithm(self, data):
        carried_data = self.insert_first_stage(data)
        if carried_data:
            carried_data = self.insert_remaining_stages(carried_data, 1)

    def generate_output(self):
        all_tables = []
        for stage in self.table:
            for x in stage:
                if x[0] != 0:
                    all_tables.append(x)
        return sorted(all_tables, key=lambda tup: tup[1], reverse=True)