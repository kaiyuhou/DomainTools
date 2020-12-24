#!/usr/local/bin/python
# coding: utf-8

# 引入相关模块
import socket
import select
import time
import os
import threading
import sys
import platform

max_thread = 2  # 并发最大线程数
timeout = 2  # 等待时间
socket.setdefaulttimeout(timeout)
# 设置套接字操作的超时期，timeout是一个浮点数，单位是秒。值为None表示没有超时期。
# 代表经过timeout秒后，如果还未下载成功，自动跳入下一次操作，此次下载失败。
sleep_time = 0.01  # 推迟调用线程的运行，单位是秒
disallow_sleep_time = 600 #


# 读取域名后缀列表
def get_top_level_domain_name_suffix():
    top_level_domain_name_suffix_list = list()
    # 创建一个叫top_level_domain_name_suffix_list的列表，列表类似于数组，用于储存一串信息，从0开始计数
    with open('top_level_domain_name_suffix', 'r') as f:
        for line in f:
            if not line.startswith('//'):
                # startswith() 方法用于检查字符串是否是以指定子字符串开头，如果是则返回 True，否则返回 False。
                # 如果不是以'//'开头则追加到列表
                top_level_domain_name_suffix_list.append(line)
    return top_level_domain_name_suffix_list


# 判断检测: 域名信息，域名后缀，whois服务器
def whois_query(domain_name, domain_name_server, domain_name_whois_server):
    retry = 2
    # 重复相应连接次数
    domain = domain_name + '.' + domain_name_server
    # 重组 域名.域名后缀
    infomation = ''
    while not infomation and retry > 0:
        # 如果info为空且retry剩余尝试连接次数大于0
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((domain_name_whois_server, 43))
            # 主动初始化TCP服务器连接，。一般address的格式为元组（hostname,port），如果连接出错，返回socket.error错误。

            s.send(f'{domain} \r\n'.encode())
            # 发送TCP数据，将string中的数据发送到连接的套接字。返回值是要发送的字节数量，该数量可能小于string的字节大小。
            # encode() 方法以 encoding 指定的编码格式编码字符串。errors参数可以指定不同的错误处理方案。

            while True:
                res = s.recv(1024)
                # 接收TCP数据，数据以字符串形式返回，1024指定要接收的最大数据量。
                if not len(res):
                    break
                infomation += str(res)
            s.close()
            time.sleep(sleep_time)
        except Exception as e:
            pass
        finally:
            retry -= 1

    return infomation


# 输出结果写入文件
def get_reginfomation(domain_name, domain_name_suffix_infomation):
    infomation = whois_query(domain_name, domain_name_suffix_infomation[0], domain_name_suffix_infomation[1])
    # 调用“whois_query” 获得返回

    reg = domain_name_suffix_infomation[2]
    # 判断有没有返回信息
    if not infomation:
        with open(f'failure.txt', 'a') as f:
            f.write(f'{domain_name}.{domain_name_suffix_infomation[0]}\n')
        # print(f'域名{domain_name}.{domain_name_suffix_infomation[0]}查询失败！')
        return -1

    disallow_str = 'exceeded allowed connection rate'
    if infomation.find(disallow_str) >= 0:
        with open(f'failure.txt', 'a') as f:
            f.write(f'{domain_name}.{domain_name_suffix_infomation[0]}\n')
        time.sleep(disallow_sleep_time)
        return -1

    with open('information.txt', 'a') as f:
        f.write(f'{domain_name}.{domain_name_suffix_infomation[0]} {infomation}\n')

    # 判断返回信息包不包含没注册的标志
    if infomation.find(reg) >= 0:
        # Python find() 方法检测字符串中是否包含子字符串 str ，
        # 如果指定 beg（开始） 和 end（结束） 范围，则检查是否包含在指定范围内，如果包含子字符串返回开始的索引值，否则返回-1
        with open(f'success.txt', 'a') as f:
            f.write(f'{domain_name}.{domain_name_suffix_infomation[0]}\n')
        # print(f'域名{domain_name}.{domain_name_suffix_infomation[0]} 未注册')
        return 1
    else:
        return 0
    #     print(f'域名{domain_name}.{domain_name_suffix_infomation[0]} 已注册')


"""
修改这个函数，生成所有希望查询的 Domain List
"""


def get_domian_name_list():
    domain_dictionary = 'dic/26pl3.txt'
    domain_name_length = 3
    domain_name_list = []
    with open(domain_dictionary, 'r') as f:
        for line in f:
            if line and len(line.strip()) <= domain_name_length:
                name = line.strip()
                if ('dli.su' < name < 'qab.su' or 'tlm.su' < name) and ('gwy.su' < name < 'qab.su' or 'tlm.su' < name < 'wwd.su'):
                    domain_name_list.append(name)

    return domain_name_list


"""
修改这个函数，生成所有希望查询的后缀 List
"""


def get_domain_name_suffix_list():
    domain_name_suffix_list = []
    top_level_domain_name_suffix_list = get_top_level_domain_name_suffix()
    top_level_domain_name_suffix_array = [x.split('=')[0] for x in top_level_domain_name_suffix_list]
    top_level_domain_name_par_list = [x.split('=')[:-1] for x in top_level_domain_name_suffix_list]

    with open('suffix_list.txt', 'r') as f:
        for line in f:
            if line.strip() and line.strip() in top_level_domain_name_suffix_array:
                domain_name_suffix_list.append(line.strip())

    # 所有 suffix
    # domain_name_suffix_list = []
    #
    # for suffix in top_level_domain_name_suffix_array:
    #     index = top_level_domain_name_suffix_array.index(suffix)
    #     if len(top_level_domain_name_par_list[index]) >= 4:
    #         price = float(top_level_domain_name_par_list[index][3])
    #     else:
    #         price = 0.0
    #     # if len(suffix) <= 2 and price < 20:
    #     if True:
    #         domain_name_suffix_list.append(suffix)

    return domain_name_suffix_list


# 指定“后缀”和“字典”检测能否注册
def specify_suffix_and_dictionary():
    domain_name_list = get_domian_name_list()
    domain_name_suffix_list = get_domain_name_suffix_list()

    top_level_domain_name_suffix_list = get_top_level_domain_name_suffix()
    # eg: ['com', 'org', ...]
    top_level_domain_name_suffix_array = [x.split('=')[0] for x in top_level_domain_name_suffix_list]
    # eg: [['com', 'whois.verisign-grs.com', 'No match for'], ...]
    top_level_domain_name_par_list = [x.split('=')[:-1] for x in top_level_domain_name_suffix_list]

    for domain_name_suffix in domain_name_suffix_list:
        print(f'查询域名 {domain_name_suffix}, 待查询数量 {len(domain_name_list)}')

        suffix_index = top_level_domain_name_suffix_array.index(domain_name_suffix)

        for i, domain_name in enumerate(domain_name_list):
            sys.stdout.write(f'\r {i} / {len(domain_name_list)}')
            while threading.active_count() > max_thread:
                time.sleep(sleep_time)
            t = threading.Thread(target=get_reginfomation,
                                 args=(domain_name, top_level_domain_name_par_list[suffix_index],))
            t.start()
            time.sleep(sleep_time)

        print()


"""
直接使用文件查询： domain.txt
"""


def specify_domain():
    top_level_domain_name_suffix_list = get_top_level_domain_name_suffix()
    # eg: ['com', 'org', ...]
    top_level_domain_name_suffix_array = [x.split('=')[0] for x in top_level_domain_name_suffix_list]
    # eg: [['com', 'whois.verisign-grs.com', 'No match for'], ...]
    top_level_domain_name_par_list = [x.split('=')[:-1] for x in top_level_domain_name_suffix_list]

    domain_list = []
    with open('domain.txt', 'r') as f:
        for line in f:
            if line and line.strip():
                domain_list.append(line.strip())

    for i, domain in enumerate(domain_list):
        sys.stdout.write(f'\r {i} / {len(domain_list)}')

        name, suffix = domain.split('.')

        suffix_index = top_level_domain_name_suffix_array.index(suffix)
        while threading.active_count() > max_thread:
            time.sleep(sleep_time)
        t = threading.Thread(target=get_reginfomation,
                             args=(name, top_level_domain_name_par_list[suffix_index],))
        t.start()
        time.sleep(sleep_time)


if __name__ == '__main__':
    # -n: 情况 success.txt 和 和 failure 文件
    if '-n' in sys.argv:
        with open('success.txt', 'w') as fs, open('failure.txt', 'w') as ff:
            fs.truncate()
            ff.truncate()

    if '-f' in sys.argv:
        specify_domain()
    else:
        specify_suffix_and_dictionary()
