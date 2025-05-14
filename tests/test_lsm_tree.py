import os
import shutil
import sys
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lsm_tree import LSMTree


def test_lsm_tree_basic():
    # 建立臨時資料夾來保存 sstable 檔案
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    try:
        lsm = LSMTree(flush_threshold=2, compact_threshold=3)

        # 寫入資料並確認會觸發 flush
        lsm.write("a", "apple")
        lsm.write("b", "banana")  # flush 0
        assert os.path.exists("sstable_0.txt")

        lsm.write("c", "cat")
        lsm.write("d", "dog")  # flush 1
        assert os.path.exists("sstable_1.txt")

        lsm.write("e", "egg")
        lsm.write("f", "fish")  # flush 2 → 觸發 compact
        assert os.path.exists("sstable_2.txt")
        assert len(lsm.sstables) == 1  # compact 合併後只剩一個 sstable

        # 測試 read (mem_table 仍有資料)
        lsm.write("g", "goat")
        assert lsm.read("g") == "goat"

        # 測試 read from sstable
        assert lsm.read("a") == "apple"
        assert lsm.read("d") == "dog"
        assert lsm.read("non_exist") is None

        print("✅ All tests passed.")

    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


def test_lsm_tree_read_range():
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_dir)

    try:
        lsm = LSMTree(flush_threshold=2, compact_threshold=3)

        # 寫入資料
        lsm.write("a", "apple")
        lsm.write("b", "banana")  # flush 0
        lsm.write("c", "cat")
        lsm.write("d", "dog")  # flush 1
        lsm.write("e", "egg")
        lsm.write("f", "fish")  # flush 2 → compact

        # 再寫入一些在 memtable 中的資料
        lsm.write("g", "goat")
        lsm.write("h", "hat")

        # 測試範圍查詢
        result = lsm.read_range("b", "e")
        expected = {"b": "banana", "c": "cat", "d": "dog", "e": "egg"}

        assert result == expected, f"Expected {expected}, but got {result}"

        result2 = lsm.read_range("a", "h")
        expected2 = {
            "a": "apple",
            "b": "banana",
            "c": "cat",
            "d": "dog",
            "e": "egg",
            "f": "fish",
            "g": "goat",
            "h": "hat",
        }

        assert result2 == expected2, f"Expected {expected2}, but got {result2}"

        result3 = lsm.read_range("x", "z")
        assert result3 == {}, f"Expected empty dict, got {result3}"

        print("✅ read_range test passed.")

    finally:
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)
