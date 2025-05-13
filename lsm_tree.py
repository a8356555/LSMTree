class LSMTree:
    def __init__(self, flush_threshold):
        self.flush_threshold = flush_threshold
        self.mem_table = {}
        self.sstables = []
        
    def write(self, key, value):
        self.mem_table[key] = value
        if len(self.mem_table) > self.flush_threshold:
            self.flush()

    def read(self, key):
        if key in self.mem_table:
            return self.mem_table[key]

        # TODO: read from sstables
        return None

    def flush(self):
        # TODO
        return
