"""让 `pytest ops/cloud_worker/tests` 能直接 import contract / s3queue / worker。

worker 的一份源码要在两个形态下工作：仓库形态（本目录）与部署形态
（`/home/ubuntu/moodify-worker/bin`）。部署形态由 deploy.sh 把模块平铺到 bin/，
所以运行时是平铺 import；这里把 `ops/cloud_worker` 与 `ops/cloud_worker/lib`
加进 sys.path，让仓库形态与部署形态的 import 路径一致。
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

for _p in (_ROOT, os.path.join(_ROOT, "lib")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
