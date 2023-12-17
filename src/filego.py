# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 15:29:22 2023

@author: 10467
"""

import os
def creat_folder(path):
    if os.path.exists(path):
        return
    else:
        os.mkdir(path)


class  Filego(object):
        def  filein(file_content, file_name, sender, receiver):
             creat_folder("Resource")
             file_path = os.path.join("Resource", file_name)
             with open(file_path, "ab") as f:
              f.write(file_content)
             return