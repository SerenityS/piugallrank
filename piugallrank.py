import os
import urllib.request
import re
import sys

from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime, timedelta

url = 'http://gall.dcinside.com/board/lists/?id=pumpitup&list_num=100&page='

path = (os.path.dirname(os.path.realpath(__file__)))

def save_data(data, start_date, end_date):
    result = Counter(data).most_common()

    amount = 0
    share = 0

    f = open(path + "/펌갤창순위.txt", 'w', encoding="utf-8")
    f.write("%d-%02d-%02d부터 %d-%02d-%02d까지 집계된 %s개의 게시글 기준\n\n" %
            (end_date.year, end_date.month, end_date.day, start_date.year, start_date.month, start_date.day, str(len(data))))
    for data in result:
        if share != data[1]:
            f.write(str(result.index(data) + 1) + "위. " + data[0] + " - " + str(data[1]) + "개\n")
            amount = result.index(data) + 1
            share = data[1]
        else:
            f.write(str(amount) + "위. " + data[0] + " - " + str(data[1]) + "개\n")
    f.close()

def crawl_data(start_data, end_date, type):
    exceptions = ["공지", "설문", "이슈"]
    data = []; page = start_data[1]; total = 0
    while 1:
        source = urllib.request.urlopen(url + str(page))
        soup = BeautifulSoup(source, "lxml", from_encoding='utf-8')
        board = soup.find_all(class_="ub-content")
        try:
            for i in board:
                gall_date = i.find(class_="gall_date")
                gall_num = i.find(class_="gall_num")
                gall_writer = i.find(class_="gall_writer ub-writer").text.strip()
                if type == "Y":
                    gall_writer = re.sub("\(\d+\.\d+\)", "", gall_writer)

                if gall_date.text == end_date:
                    return data

                if gall_num.text not in exceptions and int(gall_num.text) <= int(start_data[0]):
                    data.append(gall_writer)
                    total += 1
                    print_status(total, page, 0)
        except:
            pass
        page += 1

def find_num(start_date):
    page = 1
    while 1:
        source = urllib.request.urlopen(url + str(page))
        soup = BeautifulSoup(source, "lxml", from_encoding='utf-8')
        board = soup.find_all(class_="ub-content")
        try:
            for i in board:
                gall_date = i.find(class_="gall_date")
                gall_num = i.find(class_="gall_num")
                if gall_date.text == start_date:
                    return [gall_num.text, page]
        except:
            pass
        page += 1
        sys.stdout.write('\r시작 번호를 찾고 있습니다. %s번 페이지' % page)

def print_status(total, date, flag):
    if flag == 1:
        sys.stdout.write('\r총 %d개의 게시글에서 성공적으로 순위를 집계하였습니다.\n' % total)
        sys.stdout.flush()
        return
    sys.stdout.write('\r현재 수집된 게시글 : %d개, %s번 페이지' % (total, date)),

if __name__=='__main__':
    print("펌갤 전용 갤창인생 순위 제조기\nMade by qwertycvb\n")
    end_date = input("집계 시작 일자 [Ex.(19/01/01)] : ")
    start_date = input("집계 종료 일자 [Ex.(19/01/31)] : ")
    type = input("\n유동닉 IP 제거 [Ex. ㅇㅇ(xxx.xx) -> ㅇㅇ] (Y / N) : ")
    type = type.upper()
    print()

    current_date = datetime.now()

    end_date_d = datetime(2000 + int(end_date[:2]), int(end_date[3:5]), int(end_date[6:8]), 0, 0, 0)
    end_date = end_date_d - timedelta(days=1)
    if end_date.year == current_date.year:
        end_date = str("%02d/%02d" % (end_date.month, end_date.day))
    else:
        end_date = str("%2s/%02d/%02d" % (str(end_date.year)[2:], end_date.month, end_date.day))

    start_date_d = datetime(2000 + int(start_date[:2]), int(start_date[3:5]), int(start_date[6:8]), 0, 0, 0)
    if start_date_d.year == current_date.year:
        start_date = str("%02d/%02d" % (start_date_d.month, start_date_d.day))
    else:
        start_date = str("%2s/%02d/%02d" % (str(start_date_d.year)[2:], start_date_d.month, start_date_d.day))

    start_data = find_num(start_date)
    data = crawl_data(start_data, end_date, type)
    save_data(data, start_date_d, end_date_d)
    print_status(len(data), " ", 1)
    os.system("pause")