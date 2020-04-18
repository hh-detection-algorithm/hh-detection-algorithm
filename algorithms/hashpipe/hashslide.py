from algorithms.hashpipe.hashpipe import HashPipe


class HashSlide(HashPipe):
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
            if window_diff <= self.WINDOW_OFFSET:
                self.table[0][index] = (key, val + 1, current_window)
            else:
                self.table[0][index] = (key, 1, current_window)
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

        # get age for carried entry
        age_carried = current_window - carried_window_id
        old_carried = True if age_carried > self.WINDOW_OFFSET else False

        index = self.get_index(carried_key, current_stage)

        key = self.table[current_stage][index][0]
        val = self.table[current_stage][index][1]
        win = self.table[current_stage][index][2]

        # get age for table entry
        age_table = current_window - win
        old_table = True if age_table > self.WINDOW_OFFSET else False

        if key == carried_key:
            if not old_carried and not old_table:  # both are new
                self.table[current_stage][index] = (carried_key, val + carried_val, carried_window_id)
                return  # return if inserted
            elif old_carried and not old_table:   # carried key is old
                return  # do nothing
            elif not old_carried and old_table:   # table key is old
                self.table[current_stage][index] = (carried_key, carried_val, carried_window_id)
                return  # return if inserted
            else:  # both are old
                if carried_val > val:  # carried val is greater
                    self.table[current_stage][index] = (carried_key, carried_val, carried_window_id)
                    return
                else:  # table val is greater or equal
                    return  # do nothing
                # if age_carried > age_table:  # carried key is older
                #     return  # do nothing
                # elif age_table > age_carried:  # table key is older
                #     self.table[current_stage][index] = (carried_key, carried_val, carried_window_id)
                #     return
                # else:  # both are as old as each other
                #     if carried_val > val:  # carried val is greater
                #         self.table[current_stage][index] = (carried_key, carried_val, carried_window_id)
                #         return
                #     else:  # table val is greater
                #         return  # do nothing
                # self.table[current_stage][index] = (0, 0, 0)  # throw out both old entries
        elif key == 0:
            if not old_carried:  # carried key is new
                self.table[current_stage][index] = (carried_key, carried_val, carried_window_id)
                return  # return if inserted
            else:  # carried key is old
                return  # do nothing
        else:  # collision occurs, eviction takes place
            if not old_carried and not old_table:  # both are new
                if carried_val > val:  # carried key is greater
                    tempKey = carried_key
                    tempVal = carried_val
                    tempWin = carried_window_id
                    carried_key = key
                    carried_val = val
                    carried_window_id = win
                    self.table[current_stage][index] = (tempKey, tempVal, tempWin)
                    self.insert_remaining_stages((carried_key, carried_val, carried_window_id, current_window), current_stage + 1)
                else:
                    self.insert_remaining_stages((carried_key, carried_val, carried_window_id, current_window), current_stage + 1)
            elif old_carried and not old_table:   # carried key is old
                return  # do nothing
            elif not old_carried and old_table:   # table key is old
                self.table[current_stage][index] = (carried_key, carried_val, carried_window_id)
                return  # return if inserted
            else:  # both are old
                if carried_val > val:  # carried val is greater
                    self.table[current_stage][index] = (carried_key, carried_val, carried_window_id)
                    return
                else:  # table val is greater or equal
                    return  # do nothing
                # self.table[current_stage][index] = (0, 0, 0)  # throw out both old entries

        # if key == carried_key:
        #     window_diff = abs(carried_window_id - win)
        #     if window_diff <= self.WINDOW_OFFSET:
        #         self.table[current_stage][index] = (carried_key, val + carried_val, carried_window_id)
        #     else:
        #         self.table[current_stage][index] = (carried_key, carried_val, carried_window_id)
        #     return  # return if inserted
        # elif key == 0:
        #     self.table[current_stage][index] = (carried_key, carried_val, carried_window_id)
        #     return  # return if inserted
        # elif abs(win - carried_window_id) <= self.WINDOW_OFFSET:
        #     if carried_val > val:
        #         tempKey = carried_key
        #         tempVal = carried_val
        #         tempWin = carried_window_id
        #         carried_key = key
        #         carried_val = val
        #         carried_window_id = win
        #         self.table[current_stage][index] = (tempKey, tempVal, tempWin)
        #         self.insert_remaining_stages((carried_key, carried_val, carried_window_id, current_window), current_stage + 1)
        #     else:
        #         return
        # else:
        #     if carried_window_id > win:
        #         tempKey = carried_key
        #         tempVal = carried_val
        #         tempWin = carried_window_id
        #         carried_key = key
        #         carried_val = val
        #         carried_window_id = win # isn't this win?
        #         self.table[current_stage][index] = (tempKey, tempVal, tempWin)
        #         self.insert_remaining_stages((carried_key, carried_val, carried_window_id, current_window), current_stage + 1)
        #     elif win > carried_window_id:
        #         # do nothing
        #         self.insert_remaining_stages((carried_key, carried_val, carried_window_id, current_window), current_stage + 1)
        #     else:
        #         return
