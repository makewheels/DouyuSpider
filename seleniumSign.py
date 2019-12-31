#selenium js 签名
from selenium import webdriver
import time
import requests
import json

print('init selenium')
driver = webdriver.Chrome()

deviceId = '715ec34e5d4f97353617712100071501'
acf_auth='ed25kNvkOs3WZ629%2FXjHi%2BttxIPrxik8b8MP2XA8UGos%2FZh5KBiHa7nn%2B4kloVCqATAPrATGRjb51QbUQgnPzHUNK9ToMyfsU8PgwFzFcqlVUEuZpyel'

def getM3u8Url(videoId,pointId):
    url='https://v.douyu.com/show/'+videoId
    print('selenium opening url: '+url)
    driver.get(url)
    getStreamUrl = 'https://v.douyu.com/api/stream/getStreamUrl'
    timestamp = str(int(time.time()))
    #调用js
    jsSignResult = driver.execute_script("return ub98484234('"+pointId + "','"+deviceId + "','"+timestamp + "');")
    #关闭标签页
    #driver.close()
    data = jsSignResult+"&vid="+videoId
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    cookies = {'dy_did': deviceId
    , 'acf_auth': acf_auth
    }
    streamUrlJson = json.loads(requests.post(getStreamUrl, data=data, headers=headers, cookies=cookies).text)
    # get the best quality m3u8 video url
    bestM3u8Url = ''
    thumb_video = streamUrlJson['data']['thumb_video']
    if 'normal' in thumb_video and thumb_video['normal'] != '':
        bestM3u8Url=thumb_video['normal']['url']
    if 'high' in thumb_video and thumb_video['high'] != '':
        bestM3u8Url = thumb_video['high']['url']
    if 'super' in thumb_video and thumb_video['super'] != '':
        bestM3u8Url = thumb_video['super']['url']
    return bestM3u8Url

