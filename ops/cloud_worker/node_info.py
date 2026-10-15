#!/usr/bin/env python3
"""Moodify 宁夏节点 — 机器状态快照。

输出 JSON，供本机 AI 快速判断「这台机器现在能不能干活」。

用法：
    python3 node_info.py            # 人类可读
    python3 node_info.py --json     # 纯 JSON，便于程序解析

刻意不缓存、不推测：每一项都当场实测。测不到的写 "unknown"，不编造。
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from typing import Any, Dict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))


def sh(cmd: str, timeout: int = 20) -> str:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or r.stderr).strip()
    except Exception as e:  # noqa: BLE001
        return f'<error {type(e).__name__}>'


def imds(path: str) -> str:
    """IMDSv2 查询；失败返回 unknown。"""
    tok = sh('curl -fsS --max-time 3 -X PUT '
             '-H "X-aws-ec2-metadata-token-ttl-seconds: 60" '
             'http://169.254.169.254/latest/api/token')
    if not tok or '<error' in tok:
        return 'unknown'
    return sh(f'curl -fsS --max-time 3 -H "X-aws-ec2-metadata-token: {tok}" '
              f'http://169.254.169.254/latest/meta-data/{path}')


def collect() -> Dict[str, Any]:
    info: Dict[str, Any] = {}

    info['host'] = platform.node()
    info['os'] = sh('. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME"')
    info['kernel'] = platform.release()
    info['cpu_count'] = os.cpu_count()
    info['cpu_model'] = sh('lscpu 2>/dev/null | grep -m1 "Model name" | cut -d: -f2').strip()
    info['mem_total_gb'] = sh("free -g | awk '/^Mem:/{print $2}'")
    info['disk_root'] = sh("df -h / | awk 'NR==2{print $2\" total, \"$3\" used, \"$4\" avail, \"$5\" used%\"}'")
    info['uptime'] = sh('uptime')

    # AWS 身份
    info['instance_id'] = imds('instance-id')
    info['availability_zone'] = imds('placement/availability-zone')
    info['iam_role'] = imds('iam/security-credentials/')
    try:
        import boto3
        arn = boto3.client('sts', region_name='cn-northwest-1').get_caller_identity()['Arn']
        info['sts_arn'] = arn
    except Exception as e:  # noqa: BLE001
        info['sts_arn'] = f'unknown ({type(e).__name__})'

    # 工具链
    # awscli 装在 venv 里（不在 PATH），所以要先查 venv 再回落 PATH
    aws_path = shutil.which('aws')
    venv_aws = '/home/ubuntu/moodify-lab/.venv/bin/aws'
    if os.path.exists(venv_aws):
        aws_path = venv_aws
    info['tools'] = {
        'python3': sh('python3 -V'),
        'ffmpeg': sh('ffmpeg -version 2>/dev/null | head -1') or 'MISSING',
        'ffprobe': sh('ffprobe -version 2>/dev/null | head -1') or 'MISSING',
        'aws_cli': sh(f'{aws_path} --version 2>/dev/null | head -1') if aws_path else 'MISSING',
        'docker': shutil.which('docker') or 'MISSING',
        'nvidia_smi': shutil.which('nvidia-smi') or 'MISSING (本节点无 GPU，符合预期)',
    }

    # venv
    venv_py = '/home/ubuntu/moodify-lab/.venv/bin/python'
    if os.path.exists(venv_py):
        info['venv'] = {
            'path': venv_py,
            'version': sh(f'{venv_py} -V'),
            'has_boto3': sh(f'{venv_py} -c "import boto3;print(boto3.__version__)" 2>&1 | head -1'),
            'has_soundfile': sh(f'{venv_py} -c "import soundfile;print(soundfile.__version__)" 2>&1 | head -1'),
            'has_librosa': sh(f'{venv_py} -c "import librosa;print(librosa.__version__)" 2>&1 | head -1'),
            'has_numpy': sh(f'{venv_py} -c "import numpy;print(numpy.__version__)" 2>&1 | head -1'),
        }
    else:
        info['venv'] = 'MISSING'

    # S3 权限（这是能不能干活的关键）
    s3: Dict[str, Any] = {}
    try:
        import s3queue
        try:
            s3queue.list_pending(limit=1)
            s3['list_jobs'] = 'ALLOW'
        except s3queue.S3Error as e:
            s3['list_jobs'] = f'DENY ({e.code})'
        except Exception as e:  # noqa: BLE001
            s3['list_jobs'] = f'DENY ({type(e).__name__})'
    except Exception as e:  # noqa: BLE001
        s3['list_jobs'] = f'unknown (import failed: {type(e).__name__})'
    info['s3_permissions'] = s3
    info['s3_ready'] = s3.get('list_jobs') == 'ALLOW'

    # 外网
    info['egress'] = {
        'pypi': 'OK' if sh('curl -s -o /dev/null -w "%{http_code}" --max-time 8 https://pypi.org/simple/') == '200' else 'BLOCKED',
    }

    # systemd（unit 只 install 不 enable 是刻意的，这里如实反映状态）
    unit = '/etc/systemd/system/moodify-worker.service'
    info['systemd'] = {
        'unit_installed': os.path.exists(unit),
        'enabled': sh('systemctl is-enabled moodify-worker 2>/dev/null') or 'unknown',
        'active': sh('systemctl is-active moodify-worker 2>/dev/null') or 'unknown',
    }

    # 部署资产是否就位（deploy.sh 的六步产物）
    bashrc = os.path.expanduser('~/.bashrc')
    try:
        with open(bashrc, 'r', encoding='utf-8', errors='replace') as f:
            bashrc_wired = '.moodify_aliases' in f.read()
    except OSError:
        bashrc_wired = False
    info['deploy_assets'] = {
        'logrotate': os.path.exists('/etc/logrotate.d/moodify-worker'),
        'aliases': os.path.exists('/home/ubuntu/.moodify_aliases'),
        'bashrc_wired': bashrc_wired,
        'aws_cli_in_venv': os.path.exists('/home/ubuntu/moodify-lab/.venv/bin/aws'),
    }

    info['worker_dir'] = '/home/ubuntu/moodify-worker'
    info['worker_installed'] = os.path.isdir('/home/ubuntu/moodify-worker')
    return info


def main() -> int:
    info = collect()
    if '--json' in sys.argv:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        print('=== Moodify 宁夏节点状态 ===\n')
        for k, v in info.items():
            if isinstance(v, dict):
                print(f'{k}:')
                for kk, vv in v.items():
                    print(f'    {kk}: {vv}')
            else:
                print(f'{k}: {v}')
        print('\n--- 一句话结论 ---')
        sd = info.get('systemd', {})
        assets = info.get('deploy_assets', {})
        assets_ok = all(assets.get(k) for k in ('logrotate', 'aliases', 'bashrc_wired'))
        if info.get('s3_ready'):
            if sd.get('active') == 'active':
                print('READY：S3 权限正常，worker 正在运行。')
            else:
                print('READY：S3 权限正常，可以处理任务（worker 未常驻，可 '
                      '`sudo systemctl enable --now moodify-worker` 或先跑 `monce` 试一轮）。')
        else:
            print('NOT READY：S3 被拒（' + str(info.get('s3_permissions')) + '）。')
            print('  原因：instance role 未挂 IAM 策略，需管理员在 AWS 控制台 attach。')
            print(f"  节点配置本身：{'已全部就位' if assets_ok else '不完整 ' + str(assets)}"
                  f"；systemd unit {'已装' if sd.get('unit_installed') else '未装'}、"
                  f"enable={sd.get('enabled')}、active={sd.get('active')}（未 enable 是刻意设计）。")
    return 0


if __name__ == '__main__':
    sys.exit(main())
