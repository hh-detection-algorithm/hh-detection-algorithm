from algorithms.cms.cms import CMS


class CMSPAge(CMS):

    def __init__(self, args):
        super().__init__(args)

    def flush_table(self):
        pass

    def increment(self, ip, current_window):
        self.table_flows.add(ip)
        indexes = self.get_hash_indexes(ip)

        for i in range(self.NUM_STAGES):
            current_index = indexes[i]
            val, win = self.table_cms[i][current_index]

            window_diff = abs(current_window - win)
            val = val >> window_diff

            self.table_cms[i][indexes[i]] = (val + 1, current_window)
