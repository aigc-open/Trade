# -*- coding: utf-8 -*-
#
# Copyright 2024 Enflame. All Rights Reserved.

import compileall
import os
from pathlib import Path


def compile_and_delete_py(root_path="."):
    root = Path(root_path)
    compileall.compile_dir(root, force=True, legacy=True)
    print("编译完成")

    # 删除原始的 .py 文件，忽略当前执行的脚本文件
    current_script = os.path.realpath(__file__)
    for py_file in root.rglob("*.py"):
        if os.path.realpath(py_file) != current_script:
            os.remove(py_file)

if __name__ == '__main__':
    compile_and_delete_py()
