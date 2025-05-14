from sstable import SSTable


class LSMTree:
    def __init__(self, flush_threshold=5, compact_threshold=5):
        self.flush_threshold = flush_threshold
        self.compact_threshold = compact_threshold
        self.mem_table = {}
        self.sstables = []
        self.last_sstable_id = 0

    def write(self, key, value):
        self.mem_table[key] = value
        if len(self.mem_table) >= self.flush_threshold:
            self.flush()

    def read(self, key):
        if key in self.mem_table:
            return self.mem_table[key]

        for sstable in self.sstables[::-1]:
            if not sstable.min_key <= key <= sstable.max_key:
                continue

            data = sstable.read_key(key)
            if data is not None:
                return data
        return None

    def read_range(self, start_key, end_key):
        result = {}
        for key in self.mem_table:
            if start_key <= key <= end_key:
                result[key] = self.mem_table[key]

        for sstable in self.sstables[::-1]:
            if start_key > sstable.max_key or end_key < sstable.min_key:
                continue

            for record in sstable.read_records():
                key, value = record["key"], record["value"]
                if record["key"] in result:
                    continue
                else:
                    if start_key <= key <= end_key:
                        result[key] = value
        return result

    def flush(self):
        filename = f"sstable_{self.last_sstable_id}.txt"
        new_sstable = SSTable(filename)
        new_sstable.save(self.mem_table)
        self.sstables.append(new_sstable)
        self.mem_table = {}
        self.last_sstable_id += 1

        if len(self.sstables) >= self.compact_threshold:
            self.compact()

    def compact(self):
        merged = {}
        for sstable in self.sstables:
            for record in sstable.read_records():
                key, value = record["key"], record["value"]
                merged[key] = value

        self.sstables = []

        filename = f"sstable_{self.last_sstable_id}.txt"
        new_sstable = SSTable(filename)
        new_sstable.save(merged)
        self.sstables.append(new_sstable)
        self.last_sstable_id += 1
