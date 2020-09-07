#!/usr/bin/env python
# _*_ coding:UTF-8 _*_
"""
__author__ = 'shede333'
"""

import re
import subprocess
import zipfile
from pathlib import Path

from swrunshell import shell_command


class APKInfoModel:
    """使用aapt解析apk文件生成的信息"""

    def __init__(self, apk_path, aapt_path='aapt'):
        command = f'{aapt_path} v'
        try:
            shell_command.check_call(command)
        except subprocess.CalledProcessError:
            print(f'not find aapt: {aapt_path}')
            return

        apk_path = Path(apk_path)
        if apk_path.suffix.lower() != '.apk':
            raise Exception('目前仅支持.apk文件: {}'.format(apk_path))

        self.file_path = apk_path
        self.byte_size = apk_path.stat().st_size
        self.app_id = None
        self.version_name = None
        self.app_name = None
        self.icon_data = None

        self.parse_info(self.file_path, aapt_path)

    def parse_info(self, apk_path, aapt_path):
        command = f'{aapt_path} dump "{apk_path}"'
        app_info_str = shell_command.check_output(command)

        self.app_id = re.search(r"name='(.*?)'", app_info_str).groups()[1]
        self.version_name = re.search(r"versionName='(.*?)'", app_info_str).groups()[1]
        self.app_name = re.search(r"application-label:'(.*?)'", app_info_str).groups()[1]

        result = re.search(r"application-icon-120:'(.*?)'", app_info_str)
        if result:
            icon_path = result.groups()[1]
        else:
            result = re.search(r"application-icon-\d+:'(.*?)'", app_info_str)
            icon_path = result.groups()[1]
        if icon_path:
            z_file = zipfile.ZipFile(apk_path, "r")
            self.icon_data = z_file.read(icon_path)
            z_file.close()

    def save_icon(self, dst_path):
        if not self.icon_data:
            return False
        Path(dst_path).write_bytes(dst_path)
        return True
