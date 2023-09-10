import hashlib
import random
import re
import time
import requests
import os
import json
import hashlib

# 百度api
apiurl = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
appid = '2021******1449' # 百度翻译api的appid
secretKey = 'jBal******JrtJ' # 百度翻译api的secretKey


# 查找文本中的中文字符，并将连续的中文字符以列表返回
def find_chinese(text):
    regStr = r".*?([\u4E00-\u9FA5]+).*?"
    aa = re.findall(regStr, text)
    return aa


# 翻译内容 源语言 翻译后的语言
def translateBaidu(content, fromLang='zh', toLang='pt'):
    salt = str(random.randint(32768, 65536))
    sign = appid + content + salt + secretKey  # appid+q+salt+密钥 的MD5值
    sign = hashlib.md5(sign.encode("utf-8")).hexdigest()  # 对sign做md5，得到32位小写的sign
    try:
        # 根据技术手册中的接入方式进行设定
        paramas = {
            'appid': appid,
            'q': content,
            'from': fromLang,
            'to': toLang,
            'salt': salt,
            'sign': sign
        }
        response = requests.get(apiurl, paramas)
        jsonResponse = response.json()  # 获得返回的结果，结果为json格式
        dst = str(jsonResponse["trans_result"][0]["dst"])  # 取得翻译后的文本结果
        return dst
    except Exception as e:
        print(e)


# 读取文件，翻译成葡萄牙语，返回一个翻译好的文档的每行的list
def text_deal(filename, fromLang='zh', toLang='pt'):
    '''
    读取文件，翻译成葡萄牙语，返回一个翻译好的文档的每行的list
    :param filename: 翻译的文档路径
    :return: 翻译好的每行的list
    '''
    # 读取字典
    dic_file = open("dictionary_" + fromLang + "_" + toLang + ".txt", 'r', encoding="utf-8")
    js = dic_file.read()
    dictionary = json.loads(js)
    dic_file.close()
    # 文件翻译
    try:
        file = open(filename, encoding="utf-8")

        while 1:
            lines = file.readlines(100000)
            if not lines:

                break
            newline = []
            # 遍历每一行代码
            i = 0
            for line in lines:
                i += 1
                linea = line.lstrip()  # 去除了左方空行
                # 判断是否是注释，是注释则跳过
                if linea[0:2] == "//" or linea[0:4] == "<!--" or linea[0:2] == "/*" or linea[0:2] == "* ":
                    newline.append(line)
                    continue
                # 查找中文字符
                chineses = find_chinese(linea)
                if chineses:
                    print("[" + str(i) + "]: ", linea)
                    # 查找到中文字符，并调用翻译api翻译进行字符串替换
                    for c in chineses:
                        # 首先在字典中找
                        if dictionary.get(c)!=None:
                            translate_str = dictionary.get(c)
                        else:
                            time.sleep(2)
                            try:
                                translate_str = translateBaidu(c, fromLang, toLang)
                            except Exception as e:
                                js = json.dumps(dictionary)
                                dic_file = open("dictionary_" + fromLang + "_" + toLang + ".txt", 'w', encoding='utf-8')
                                dic_file.write(js)
                                dic_file.close()
                                return newline
                                exit()
                            print('============', translate_str)
                            dictionary[c] = translate_str
                        line = line.replace(c, translate_str)
                        print(c + " ----> " + translate_str)
                newline.append(line)
        file.close()


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    except Exception as e:
        print("******" + filename + '******')
        file = open(filename, encoding="utf-8")
        while 1:
            lines = file.readlines(100000)
            if not lines:
                break
            # 遍历每一行代码
            newline = []
            i = 0
            for line in lines:
                i += 1
                linea = line.lstrip()  # 去除了左方空行
                # 判断是否是注释，是注释则跳过
                if linea[0:2] == "//" or linea[0:4] == "<!--":
                    newline.append(line)
                    continue
                # 查找中文字符
                chineses = find_chinese(linea)
                if chineses:
                    print("[" + str(i) + "]: ", linea)
                    # 查找到中文字符，并调用翻译api翻译进行字符串替换
                    for c in chineses:
                        # 首先在字典中找
                        if dictionary.get(c) != None:
                            translate_str = dictionary.get(c)
                        else:
                            time.sleep(2)
                            translate_str = translateBaidu(c, fromLang, toLang)
                            dictionary[c] = translate_str
                        line = line.replace(c, translate_str)
                        print(c + " ----> " + translate_str)
                newline.append(line)
        file.close()
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


    # 保存字典
    js = json.dumps(dictionary)
    dic_file = open("dictionary_" + fromLang + "_" + toLang + ".txt", 'w', encoding='utf-8')
    dic_file.write(js)
    dic_file.close()

    return [] if newline==None else newline


if __name__ == '__main__':

    # 调用函数处理文档
    files = os.listdir('./translate')
    files = [os.path.join('./translate', x) for x in files]
    total_file = len(files)
    for i, file in enumerate(files):
        print("=====================[{}/{}][{}%]=====================".format(i+1, total_file, (i+1)/total_file*100))
        # 读取已经处理过的文件 dic
        dic_file = open("dictionary_deal.txt", 'r', encoding="utf-8")
        js = dic_file.read()
        dictionary_deal = json.loads(js)
        dic_file.close()

        file_md5 = hashlib.md5(file.encode(encoding='UTF-8')).hexdigest()

        if dictionary_deal.get(file_md5) != None:
            continue

        print("=====================正在处理文件：" + file)

        # 各国简写 https://fanyi-api.baidu.com/doc/21
        newlines = text_deal(file, "zh", "cht")

        save_file = file.replace('translate', 'translated')
        fw = open(save_file, "w", encoding="utf-8")
        for l in newlines:
            fw.write(l)
        fw.close()

        dictionary_deal[file_md5] = 'true'

        # 保存字典
        js = json.dumps(dictionary_deal)
        dic_file = open("dictionary_deal.txt", 'w')
        dic_file.write(js)
        dic_file.close()

