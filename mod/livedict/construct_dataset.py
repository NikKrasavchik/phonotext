import sys
import sqlite3
import re
import numpy as np
import pandas as pd

def reader(directory):
    def read_file(filename):
        with open(directory + filename, encoding="utf8") as f:
            text = f.read().lower()
            text = re.sub(r"\d+", " ", text) # delete didgits
            text = re.sub(r"\W+ ", " ", text) # delete special chars
            text = re.sub(r"_+", " ", text)
            text = re.sub(r"\s+", " ", text) # delete extra spaces

            return text
    return read_file

def load_dataset(db_sqlite, db_json, use_binary=False, directory='./'):
    con = sqlite3.connect(directory + db_sqlite)
    cursor = con.cursor()
    titles = list(pd.read_sql_query("select * from structure", con).title.values)
    important_feat = [3,4,5,7,8,9,10,11,12,13,14,15,16,17,18]
    binary_feat = {2, 5, 7, 8, 9, 10, 11, 12, 13, 17}
    structure = ({titles[i]: cursor.execute(f"SELECT * FROM field{i}").fetchall() for i in important_feat},
                {i: titles[i] for i in important_feat})
    data = pd.read_sql_query("select * from question", con)
    data.field6 = data.field6.apply(reader(directory))
    data = data.fillna("0,")
    if use_binary:
        for i in binary_feat:
            data[f"field{i}"] = data[f"field{i}"].replace("1,", "0,")
    else:
        for i in binary_feat:
            data[f"field{i}"] = data[f"field{i}"].replace("0,", "1,")
    if use_binary:
        for i in important_feat:
            data[f"field{i}"] = data[f"field{i}"].apply(lambda x: x!="0,").astype(int)

    data.to_json(db_json)
    return structure

