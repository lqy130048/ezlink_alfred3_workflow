# ezlink__alfred3_workflow
ezlink vpn连接workflow

## 安装：

workflow是用python写的，需要python2.7的运行环境，请自行安装。

下载release里面打包好的VPN.alfredworkflow,双击导入 Alfred3

## root权限说明：

获取服务器延迟使用了fping工具，需要root权限，本程序调用了Authenticate.app来请求root权限，第一次使用的时候会弹窗，请输入Mac的用用户名和密码。

## 使用说明

1. 第一次使用的时候需要设置你的ezlink账号密码:
    - 在Alfred3里面使用vpnset命令设置账号密码
    - 格式：用户名|密码
    - 例: vpnset user12345|12345678
2. 获取服务器命令：
    - vpn s：使用本地缓存，获取速度很快
    - vpn r：刷新本地缓存，会重新获取延迟 获取速度会慢一点。