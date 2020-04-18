from algorithms.hashpipe.hashpipe import HashPipe


class HashPage(HashPipe):
    def __init__(self, args):
        super().__init__(args)

    def flush_table(self):
        pass

    def insert_first_stage(self, data):
        timestamp = data[0]
        ip = data[1]
        current_window = self.get_current_window_id(timestamp)

        index = self.get_index(ip, 0)

        key = self.table[0][index][0]
        val = self.table[0][index][1]
        win = self.table[0][index][2]

        if key == ip:
            window_diff = abs(current_window - win)
            val = val >> window_diff  # normalize
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
            return carried_key, carried_val, carried_window_id, current_window

    def insert_remaining_stages(self, carried_data, current_stage):
        if current_stage >= self.NUM_STAGES or not carried_data:
            return  # reached maximum stage

        current_window = carried_data[3]  # current window ID

        carried_key = carried_data[0]
        carried_val = carried_data[1]
        carried_window_id = carried_data[2]
        # normalize carried values
        window_diff_carried = abs(current_window - carried_window_id)
        carried_val = carried_val >> window_diff_carried
        carried_window_id = current_window

        index = self.get_index(carried_key, current_stage)

        key = self.table[current_stage][index][0]
        val = self.table[current_stage][index][1]
        win = self.table[current_stage][index][2]
        # normalize table values
        window_diff_table = abs(current_window - win)
        val = val >> window_diff_table
        win = current_window

        if key == carried_key:
            self.table[current_stage][index] = (carried_key, val + carried_val, carried_window_id)
            return  # return if inserted
        elif key == 0:
            self.table[current_stage][index] = (carried_key, carried_val, carried_window_id)
            return  # return if inserted
        else:  # collision occurs, eviction takes place
            if carried_val > val:
                tempKey = carried_key
                tempVal = carried_val
                tempWin = carried_window_id

                carried_key = key
                carried_val = val
                carried_window_id = win

                self.table[current_stage][index] = (tempKey, tempVal, tempWin)  # update table with new entry
                self.insert_remaining_stages((carried_key, carried_val, carried_window_id, carried_window_id), current_stage + 1)
            else:
                self.table[current_stage][index] = (key, val, win)  # update table entry with normalized values
                self.insert_remaining_stages((carried_key, carried_val, carried_window_id, current_window), current_stage + 1)

        # elif win == carried_window_id:  # if both entries have the same window ID
        #     # normalize carried values
        #     window_diff_carried = current_window - carried_window_id
        #     carried_val = carried_val >> window_diff_carried
        #     carried_window_id = current_window
        #
        #     # normalize table values
        #     window_diff_table = current_window - win
        #     val = val >> window_diff_table
        #     win = current_window
        #
        #     if carried_val > val:
        #         tempKey = carried_key
        #         tempVal = carried_val
        #         tempWin = carried_window_id
        #
        #         carried_key = key
        #         carried_val = val
        #         carried_window_id = win
        #
        #         self.table[current_stage][index] = (tempKey, tempVal, tempWin)
        #         self.insert_remaining_stages((carried_key, carried_val, carried_window_id, carried_window_id), current_stage + 1)
        #     else:
        #         self.table[current_stage][index] = (key, val, win)  # update table with normalized values
        #         self.insert_remaining_stages((carried_key, carried_val, carried_window_id, current_window), current_stage + 1)
        #
        # else:  # both windows have different window IDs
        #     # normalize carried values
        #     window_diff_carried = current_window - carried_window_id
        #     carried_val = carried_val >> window_diff_carried
        #     carried_window_id = current_window
        #
        #     # normalize table values
        #     window_diff_table = current_window - win
        #     val = val >> window_diff_table
        #     win = current_window
        #
        #     if carried_val > val:
        #         tempKey = carried_key
        #         tempVal = carried_val
        #         tempWin = carried_window_id
        #
        #         carried_key = key
        #         carried_val = val
        #         carried_window_id = win
        #         self.table[current_stage][index] = (tempKey, tempVal, tempWin)  # update table with new entry
        #         self.insert_remaining_stages((carried_key, carried_val, carried_window_id, current_window), current_stage + 1)
        #     else:
        #         self.table[current_stage][index] = (key, val, win)  # update table with normalized values
        #         self.insert_remaining_stages((carried_key, carried_val, carried_window_id, current_window), current_stage + 1)

            # if carried_oid > win:
            #     window_diff = carried_oid - win
            #     val = val >> window_diff  # make them at same window
            #     if carried_val > val:
            #         tempKey = carried_key
            #         tempVal = carried_val
            #         tempWin = carried_oid
            #         carried_key = key
            #         carried_val = val
            #         carried_oid = carried_oid  # becuz already shifted
            #         self.table[current_stage][index] = (tempKey, tempVal, tempWin)
            #         self.insert_remaining_stages((carried_key, carried_val, carried_oid, current_window), current_stage + 1)
            #     else:
            #         return
            # else:
            #     window_diff = win - carried_oid
            #     carried_val = carried_val >> window_diff  # make them at same window
            #     if carried_val > val:
            #         tempKey = carried_key
            #         tempVal = carried_val
            #         tempWin = win
            #         carried_key = key
            #         carried_val = val
            #         carried_oid = win
            #         self.table[current_stage][index] = (tempKey, tempVal, tempWin)
            #         self.insert_remaining_stages((carried_key, carried_val, carried_oid, current_window), current_stage + 1)
            #     else:
            #         return