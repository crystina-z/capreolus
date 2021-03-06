import os
import shutil

from capreolus.index import AnseriniIndex
from capreolus.collection import ANTIQUE


def test_antique_downloadifmissing():
    cfg = {"_name": "antique"}
    col = ANTIQUE(cfg)

    path_to_col = "~/tmp_antique22/collection"
    path_to_idx = "~/tmp_antique22/index"


    if os.path.exists(path_to_col):
        _remove_folder(path_to_col)
    assert not os.path.exists(path_to_col)
    col.path = path_to_col
    # col.download_if_missing()
    path, col_path, gen_type = col.get_path_and_types()
    assert path == path_to_col

    # make sure index can be built on this collection
    cfg = {"_name": "anserini", "indexstops": False, "stemmer": "porter"}
    index = AnseriniIndex(cfg)
    index.modules["collection"] = col

    index.create_index()
    assert index.exists()
