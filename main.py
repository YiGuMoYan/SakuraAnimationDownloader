import os

import requests
from bs4 import BeautifulSoup
import Animation

chapter = -1
srcUrl = 'https://tup.yinghuacd.com/?vid='

animation = Animation.Animation()


def getUrlList():
    print('开始解析...')
    url = 'http://www.yinghuacd.com/show/' + str(chapter) + '.html'
    htmlListRequest = requests.get(url).text.encode('raw_unicode_escape').decode()
    bs = BeautifulSoup(htmlListRequest, 'html.parser')
    titleBs = BeautifulSoup(str(bs.find(class_='rate r')), 'html.parser')
    animation.name = str(titleBs.h1.string).replace(' ', '')
    listBs = BeautifulSoup(str(bs.find(class_='movurl')), 'html.parser')
    for i in listBs.select('li'):
        liBs = BeautifulSoup(str(i), 'html.parser')
        animation.chapterList[liBs.li.string] = liBs.li.a['href']
    print('[信息]')
    print('\t序号：' + str(chapter))
    print('\t昵称：' + animation.name)
    print('\t集数：' + str(len(animation.chapterList)))
    print('\t链接：' + url)


def getM3U8(chapterName, chapterUrl):
    print('获取 ' + chapterName + ' m3u8文件')
    url = 'http://www.yinghuacd.com/' + chapterUrl
    html = requests.get(url).text.encode('raw_unicode_escape').decode()
    bs = BeautifulSoup(html, 'html.parser')
    url = srcUrl + bs.find(id='playbox')['data-vid']
    html = requests.get(url).text.encode('raw_unicode_escape').decode()
    start = html.index('url: \"')
    end = html.index('m3u8')
    url = html[start + 6: end + 4]
    m3u8 = requests.get(url).text.encode('raw_unicode_escape').decode()
    return m3u8


def analyseM3U8(chapterName, m3u8):
    print('解析 ' + chapterName + ' m3u8文件')
    jpgList = []
    for i in m3u8.split('\n'):
        if 'https' in i:
            jpgList.append(i)
    return jpgList


def analyseJPG(jpgList, chapterNum):
    nameList = []
    txtUrl = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + '/Animation/txt.txt'
    txtUrl = txtUrl.replace('/', '\\\\')
    txtFile = open(txtUrl, 'w+')
    for i in range(len(jpgList)):
        jpgBytes = requests.get(jpgList[i]).content
        jpgBytes = jpgBytes[120: len(jpgBytes)]
        url = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + '/Animation/' + str(
            i) + '.ts'
        file = open(url, 'wb')
        file.write(jpgBytes)
        file.close()
        nameList.append(url)
        txtFile.write('file \'' + url + '\'\n')
    txtFile.close()
    aimUrl = os.path.dirname(os.path.abspath(__file__)).replace('\\',
                                                                '/') + '/Animation/' + animation.name + '-' + chapterNum + '.mp4'
    sysCall = 'ffmpeg -f concat -safe 0 -i ' + txtUrl + ' -c copy ' + aimUrl
    print('合并 ' + animation.name + '-' + chapterNum + '.ts 文件')
    os.system(sysCall)
    print('清除临时文件...')
    for i in nameList:
        os.remove(i)
    os.remove(txtUrl)


if __name__ == '__main__':
    chapter = int(input('请输入 樱花动漫 序号：'))
    getUrlList()
    if not os.path.exists('./Animation'):
        os.makedirs('./Animation')
    for key, value in animation.chapterList.items():
        m3u8 = getM3U8(key, value)
        jpgList = analyseM3U8(key, m3u8)
        analyseJPG(jpgList, key)
    odlUrl = os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/Animation'
    newUrl = os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + '/' + str(animation.name)
    os.rename(odlUrl, newUrl)
