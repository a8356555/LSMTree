import json


class SSTable:
    def __init__(self, filename: str):
        self.filename = filename

    def read_key(self, key: str):
        with open(self.filename) as f:
            for line in f:
                record = json.loads(line.strip())
                if record["key"] == key:
                    return record["value"]
        return None

    def read_records(self):
        with open(self.filename) as f:
            for line in f:
                record = json.loads(line.strip())
                yield record

    def save(self, mem_table: dict) -> None:
        with open(self.filename, "w") as f:
            for key, value in sorted(mem_table.items()):
                dump_value = json.dumps({"key": key, "value": value})
                f.write(dump_value + "\n")
