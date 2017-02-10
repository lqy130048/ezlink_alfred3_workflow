# -*- coding: utf-8 -*-
import base64
from pydesx.pydes import *
import requests
from xml.dom import minidom
import sys
from workflow import Workflow3
import subprocess
import threading
import Queue
import re
import pickle

reload(sys)
sys.setdefaultencoding( "utf-8" )


class Ping(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.__queue = queue
        self.__result = None

    def __execute_cmd(self, cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, _ = p.communicate()
        out_list = out.splitlines()
        return out_list

    def get_result(self):
        return self.__result

    def run(self):
        while True:
            ip = self.__queue.get()
            cmd = "./sudo.sh ./bin/fping -e -t300 %s"  % ip
            self.__result = self.__execute_cmd(cmd)
            self.__queue.task_done()

class VPNServer:

    def __init__(self):
        pass
        self.__des_key = "A2U7vzy9"
        self.__update_server_url = "https://www.189host.com/123/en.list"
    
    def __execute_cmd(self, cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, _ = p.communicate()
        out_list = out.splitlines()
        return out_list

    def __decode(self, s):
        k = des(self.__des_key, ECB, None, pad=None, padmode=None)
        org_data = base64.b64decode(s)
        out_data = k.decrypt(org_data)
        return out_data.decode("utf-8")

    def __check_cache(self):
        try:
            with open("server_cache.txt", "r") as f:
                data = f.read()
                if data and data != "":
                    return data
                else :
                    return None
        except:
            return None
    
    def get_connectioned_server(self):
        cmd = "ps aux | grep obfuscated-ssh"
        out_list = self.__execute_cmd(cmd)
        if None or len(out_list) == 0 :
            return None
        res = "(\d+\.\d+\.\d+\.\d+)"
        for out in out_list:
            m = re.search(res, out)
            if None != m:
                return unicode(m.group(1), "utf-8")
        return None

    def get_time_delay(self, server_list):
        self.__execute_cmd("./sudo.sh")
        queue = Queue.Queue()
        t_list = []
        for i in range(len(server_list)):
            t = Ping(queue)
            t.setDaemon(True)
            t.start()
            t_list.append(t)

        for server_ip in server_list.keys():
            queue.put(server_ip)
        queue.join()

        res = "(\d+\.\d+\.\d+\.\d+)\sis\salive\s\((.*)\sms\)"
        new_server_list = {}
        for t in t_list:
            ret = t.get_result()
            if None != ret and 0 < len(ret):
                m = re.search(res, ret[0])
                if m:
                    ip = unicode(m.group(1), "utf-8")
                    delay = unicode(m.group(2), "utf-8")
                    new_server_list[ip] = (server_list[ip][0],
                                       server_list[ip][1],
                                       server_list[ip][2],
                                       server_list[ip][3],
                                       server_list[ip][4],
                                       server_list[ip][5],
                                       delay)
        return new_server_list

    def get_server_list(self):
        data = self.__check_cache()
        if None == data:
            s = requests.session()
            r = s.get(self.__update_server_url, verify=False)
            data = r.text
            try:
                with open("server_cache.txt", "w") as f:
                    f.write(data)
            except:
                pass

        decode_data = self.__decode(data)
        xml_text =  decode_data.replace("<?xml version=\"1.0\"?>", "<?xml version=\"1.0\" encoding=\"utf-8\"?>").rstrip('\0')

        tree = minidom.parseString(xml_text)
        root = tree.documentElement
        server_list = {}
        for row_node in root.getElementsByTagName("Row"):
            server_name = row_node.getElementsByTagName(u"服务器")[0].childNodes[0].data.strip()
            server_ip = row_node.getElementsByTagName(u"服务器地址")[0].childNodes[0].data.strip()
            server_ssh_port = row_node.getElementsByTagName(u"SSH端口")[0].childNodes[0].data.strip()
            server_tcp_port = row_node.getElementsByTagName(u"TCP端口")[0].childNodes[0].data.strip()
            server_udp_port = row_node.getElementsByTagName(u"UDP端口")[0].childNodes[0].data.strip()
            server_ssh_type = row_node.getElementsByTagName(u"SSH类型")[0].childNodes[0].data.strip()
            server_des = row_node.getElementsByTagName(u"描述")[0].childNodes[0].data.strip()
            server_list[server_ip] = (server_name, server_ssh_port, server_tcp_port, server_udp_port, server_ssh_type, server_des)
        return server_list


def dump(obj):
    try:
        dump_data = pickle.dumps(obj)
        with open("serverlist.dump", "wb") as f:
            f.write(dump_data)
    except:
        return False
    return True
def dump_load():
    obj = None
    try:
        with open("serverlist.dump", "rb") as f:
            dump_data = f.read()
            obj = pickle.loads(dump_data)
    except:
        return None
    return obj

def load_user():
    out = None
    try:
        with open("pass.txt", "r") as f:
            data = f.read()
            out = data.split('|')
    except :
        return None
    return out

SERVER_NAME = 0
SERVER_SSH_PORT = 1
SERVER_TCP_PORT = 2
SERVER_UDP_PORT = 3
SERVER_SSH_TYPE = 4
SERVER_DES = 5
DELAY = 6


def main(wf):
    
    userinfo = load_user()
    vpn_server = VPNServer()
    
    if None == userinfo or 3!=len(userinfo):
        wf.add_item(title="请设置VPN账号信息",
                        subtitle="使用vpnset命令设置，例：vpnset 用户名|密码|SSH监听端口",
                        valid=True,
                        largetext="test4",
                        icon="vpn.ico")
        wf.send_feedback()
    else:
        if 2 == len(sys.argv):
            is_re = False
            if "r" == sys.argv[1]:
                is_re = True
            server_list = dump_load()
            if is_re or None == server_list:
                server_list = vpn_server.get_server_list()
                server_list = vpn_server.get_time_delay(server_list)
                dump(server_list)
            connectioned_server = vpn_server.get_connectioned_server()
            ctitle = "当前没有连接服务器"
            csubtitle = "请选择服务器连接"
            if None != connectioned_server:
                ctitle = "当前连接服务器[%s]" % server_list[connectioned_server][SERVER_NAME]
                csubtitle = connectioned_server
            wf.add_item(title=ctitle,
                        subtitle=csubtitle,
                        valid=False,
                        uid=u"0",
                        largetext="0",
                        icon="vpn.ico")
            for server_ip, server_info in server_list.items():
                sub_title = "IP: %s\t(%s ms)" % (server_ip, server_info[DELAY])
                arg = "%s|%s|%s|%s|%s" % (server_ip, server_info[SERVER_SSH_PORT], userinfo[0], userinfo[1], userinfo[2])
                wf.add_item(title=server_info[0],
                            subtitle=sub_title,
                            arg=arg,
                            uid=server_info[DELAY],
                            valid=True,
                            largetext="test4",
                            icon="vpn.ico")
            wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))