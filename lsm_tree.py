from sstable import SSTable

class LSMTree:
    def __init__(self, flush_threshold):
        self.flush_threshold = flush_threshold
        self.mem_table = {}
        self.sstables = []
        self.last_sstable_id = 0

    def write(self, key, value):
        self.mem_table[key] = value
        if len(self.mem_table) > self.flush_threshold:
            self.flush()

    def read(self, key):
        if key in self.mem_table:
            return self.mem_table[key]

        for sstable in self.sstables[::-1]:
            data = sstable.read_key(key)
            if data is not None:
                return data
        return None

    def flush(self):
        filename = f'sstable_{self.last_sstable_id}.txt'
        new_sstable = SSTable(filename)
        new_sstable.save(self.mem_table)
        self.sstables.append(new_sstable)
        self.mem_table = {}
        self.last_sstable_id += 1

