#!/usr/bin/env python
# _*_ coding:UTF-8 _*_
"""
__author__ = 'shede333'

文档: https://developer.apple.com/library/archive/qa/qa1686/_index.html
"""

import plistlib
from pathlib import Path
from typing import List
from typing import Dict


# def lazy_property(fn):
#     attr = '_lazy__' + fn.__name__
#
#     @property
#     def _lazy_property(self):
#         if not hasattr(self, attr):
#             setattr(self, attr, fn(self))
#         return getattr(self, attr)
#
#     return _lazy_property

class InfoPlistModel(object):
    """.App文件里的 Info.plist信息model"""

    def __init__(self, file_path, app_path=None, is_auto_save=True):
        self.file_path = Path(file_path)
        self.app_path = app_path if app_path else self.file_path.parent
        self.is_auto_save = is_auto_save
        self._ip_obj = None

    @property
    def ip_obj(self) -> Dict:
        if not self._ip_obj:
            self._ip_obj = plistlib.loads(self.file_path.read_bytes())
        return self._ip_obj

    # def _run_command(self, sub_command):
    #     command = '/usr/libexec/PlistBuddy -c "{}" "{}"'.format(sub_command, self.file_path)
    #     output = subprocess.check_output(command, shell=True, text=True)
    #     return output and output.strip()

    def save_to_local(self):
        with self.file_path.open('wb') as fp:
            plistlib.dump(self._ip_obj, fp)

    def recursion_get_value(self, *keys, default_value=None):
        tmp_value = self.ip_obj
        for sub_key in keys:
            if tmp_value is None:
                break
            tmp_value = tmp_value.get(sub_key, None)

        return default_value if (tmp_value is None) else tmp_value

    def get_value(self, key, default_value=None):
        return self.ip_obj.get(key, default_value)

    def set_value(self, key, value):
        self.ip_obj[key] = value
        if self.is_auto_save:
            self.save_to_local()

    @property
    def bundle_id(self) -> str:
        return self.get_value("CFBundleIdentifier")

    @bundle_id.setter
    def bundle_id(self, value):
        self.set_value("CFBundleIdentifier", value)

    @property
    def exec_name(self) -> str:
        return self.get_value("CFBundleExecutable")

    @property
    def exec_path(self) -> Path:
        return Path(self.file_path).with_name(self.exec_name)

    @property
    def app_display_name(self) -> str:
        return self.get_value("CFBundleDisplayName")

    @app_display_name.setter
    def app_display_name(self, value):
        self.set_value("CFBundleDisplayName", value)

    @property
    def app_version(self) -> str:
        return str(self.get_value("CFBundleShortVersionString"))

    @app_version.setter
    def app_version(self, value):
        self.set_value("CFBundleShortVersionString", value)

    @property
    def build_version(self) -> str:
        return str(self.get_value("CFBundleVersion"))

    @build_version.setter
    def build_version(self, value):
        self.set_value("CFBundleVersion", value)

    @property
    def bundle_icons(self) -> List[Path]:
        names = self.recursion_get_value('CFBundleIcons', 'CFBundlePrimaryIcon',
                                         'CFBundleIconFiles', default_value=[])
        return icon_paths(self.app_path, names)

    @property
    def bundle_icons_ipad(self) -> List[Path]:
        names = self.recursion_get_value('CFBundleIcons~ipad', 'CFBundlePrimaryIcon',
                                         'CFBundleIconFiles', default_value=[])
        return icon_paths(self.app_path, names)

    @property
    def app_icon(self) -> Path:
        return optimal_app_icon([*self.bundle_icons, *self.bundle_icons_ipad])


def icon_paths(app_path, names: List[str]) -> List[Path]:
    app_path = Path(app_path)
    path_list = []
    name_suffix_list = ['', '~ipad', '@2x', '@2x~ipad', '@3x', '@3x~ipad']
    for sub_name in names:
        for tmp_suffix in name_suffix_list:
            tmp_path = app_path.joinpath('{}{}.png'.format(sub_name, tmp_suffix))
            if tmp_path.is_file():
                path_list.append(tmp_path)

    return path_list


def optimal_app_icon(path_list: List[Path]) -> Path:
    from PIL import Image

    icon_dict = {}
    max_width = 0
    for tmp_path in path_list:
        img = Image.open(tmp_path)
        width = int(img.size[0])
        icon_dict[width] = tmp_path
        max_width = max(max_width, width)

    # 图片尺寸，按照优先级，从高到低
    for tmp_size in [120, 180, 114, 57, 76, 72]:
        if tmp_size in icon_dict:
            return icon_dict[tmp_size]

    return icon_dict.get(max_width)
