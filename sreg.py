#!/usr/bin/env python
# encoding: utf-8
# author: www.n0tr00t.com

import sys
import glob
import json
import chardet
import requests
import urllib.parse
import argparse
import multiprocessing

from common.color import *
from common.output import *
from collections import OrderedDict


def check(plugin, passport, passport_type):
    """
    plugin: *.json
    passport: username, email, phone
    passport_type: passport type
    """
    if plugin["request"]["{0}_url".format(passport_type)]:
        url = plugin["request"]["{0}_url".format(passport_type)]
    else:
        return
    app_name = plugin['information']['name']
    category = plugin["information"]["category"]
    website = plugin["information"]["website"]
    judge_yes_keyword = plugin['status']['judge_yes_keyword'].encode("utf-8")
    judge_no_keyword = plugin['status']['judge_no_keyword'].encode("utf-8")
    headers = OrderedDict({
        'Host': urllib.parse.urlparse(url).netloc,
        'Connection': 'closed',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Referer': url,
    })
    if "headers" in plugin:
        for header_key in list(plugin['headers'].keys()):
            headers[header_key] = plugin['headers'][header_key]

    #import ipdb; ipdb.set_trace()

    if plugin['request']['method'] == "GET":
        try:
            url = url.replace('{}', passport)
            s = requests.Session()
            s.headers = headers
            content = s.get(url, headers={}, timeout=8).content
            encoding = chardet.detect(content)["encoding"]
            if encoding == None:
                content = content.encode("utf-8")
            else:
                content = content.decode(encoding).encode("utf-8")
        except Exception as e:
            print(inRed('\n[-] %s Error: %s\n' % (app_name, str(e))))
            return
        if judge_yes_keyword in content and judge_no_keyword not in content:
            print("[{0}] {1}".format(category, ('%s (%s)' % (app_name, website))))
            icon = plugin['information']['icon']
            desc = plugin['information']['desc']
            output_add(category, app_name, website,
                       passport, passport_type, icon, desc)
        else:
            pass
    elif plugin['request']['method'] == "POST":
        post_data = plugin['request']['post_fields']
        if list(post_data.values()).count("") != 1:
            print("[*] The POST field can only leave a null value.")
            return
        for k, v in post_data.items():
            if v == "":
                post_data[k] = passport
        try:
            s = requests.Session()
            s.headers = headers
            #import ipdb; ipdb.set_trace()
            content = s.post(url, data=post_data, headers={}, timeout=8).content
            encoding = chardet.detect(content)["encoding"]
            if encoding == None:
                content = content.encode("utf-8")
            else:
                content = content.decode(encoding).encode("utf-8")

        except Exception as e:
            print(inRed('\n[-] %s Error: %s\n' % (app_name, str(e))))
            return
        if judge_yes_keyword in content and judge_no_keyword not in content:
            print("[{0}] {1}".format(category, ('%s (%s)' % (app_name, website))))
            icon = plugin['information']['icon']
            desc = plugin['information']['desc']

            output_add(category, app_name, website,
                       passport, passport_type, icon, desc)
        else:
            pass
    else:
        print(inRed('\n[*] {0} Error!\n'.format(plugin['request']['name'])))
        # print u"[-]{}:::Error!".format(plugin['request']['name'])


def main():
    parser = argparse.ArgumentParser(description="Check how many Platforms the User registered.")
    parser.add_argument("-u", action="store", dest="user")
    parser.add_argument("-e", action="store", dest="email")
    parser.add_argument("-c", action="store", dest="cellphone")
    parser_argument = parser.parse_args()
    banner = '''
     .d8888b.
    d88P  Y88b
    Y88b.
     "Y888b.  888d888 .d88b.  .d88b.
        "Y88b.888P"  d8P  Y8bd88P"88b
          "888888    88888888888  888
    Y88b  d88P888    Y8b.    Y88b 888
     "Y8888P" 888     "Y8888  "Y88888
                                  888
                             Y8b d88P
                              "Y88P"
    '''
    all_argument = [parser_argument.cellphone, parser_argument.user, parser_argument.email]
    plugins = glob.glob("./plugins/*.json")
    print(inGreen(banner))
    print('[*] App: Search Registration')
    print('[*] Version: V1.1(20180419)')
    print('[*] Website: www.n0tr00t.com')
    file_name = ""
    if all_argument.count(None) != 2:
        print('\nInput "-h" view the help information.')
        sys.exit(0)
    if parser_argument.cellphone:
        print(inYellow('\n[+] Phone Checking: %s\n') % parser_argument.cellphone)
        file_name = "cellphone_" + str(parser_argument.cellphone)
        output_init(file_name, "Phone: ", str(parser_argument.cellphone))
    if parser_argument.user:
        print(inYellow('\n[+] Username Checking: %s\n') % parser_argument.user)
        file_name = "user_" + str(parser_argument.user)
        output_init(file_name, "UserName: ", str(parser_argument.user))
    if parser_argument.email:
        print(inYellow('\n[+] Email Checking: %s\n') % parser_argument.email)
        file_name = "email_" + str(parser_argument.email)
        output_init(file_name, "E-mail: ", str(parser_argument.email))
    
    
    jobs = []
    for plugin in plugins:
        with open(plugin) as f:
            try:
                content = json.load(f)
            except Exception as e:
                print(e, plugin)
                continue
        if parser_argument.cellphone:
            p = multiprocessing.Process(target=check,
                                        args=(content, str(parser_argument.cellphone, "utf-8"), "cellphone"))
        elif parser_argument.user:
            p = multiprocessing.Process(target=check,
                                        args=(content, str(parser_argument.user, "utf-8"), "user"))
        elif parser_argument.email:
            p = multiprocessing.Process(target=check,
                                        args=(content, parser_argument.email, "email"))
        p.start()
        jobs.append(p)
    while sum([i.is_alive() for i in jobs]) != 0:
        pass
    for i in jobs:
        i.join()
    output_finished(file_name)


if __name__ == '__main__':
    main()
