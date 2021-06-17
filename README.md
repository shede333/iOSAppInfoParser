# iOSAppInfoParser

> 解析 iOS APP 的信息，目前主要解析 Info.plist文件 信息；    
> 注意：仅支持 Python3；

## 安装 Install

```shell script

pip3 install iOSAppInfoParser

```

## 使用方法

```python

from iosappinfoparser import InfoPlistModel
from iosappinfoparser import change_app_display_name

app_path = '/xxx/xx.app'
info_model = InfoPlistModel(app_path.joinpath("Info.plist"))
info_model.set_value('CFBundleName', 'xxx')

print(info_model.app_version)  # 获取App的版本信息
info_model.app_version = "1.23"  # 修改App的版本信息

# 注意：修改App的DisplayName，除了修改Info.plist文件，还要修改对应的国际化语言文件
change_app_display_name(app_path, 'new name')  # 修改所有语言文件
change_app_display_name(app_path, 'new name', lang_key='en')  # 仅修改英文语言文件

```