# selenium js 签名
from selenium import webdriver
import time
import requests
import json

print('init selenium')
driver = webdriver.Chrome()

deviceId = '1cebd38f0e9643024ff4406700071501'
acf_auth = 'eed6RR%2F3qN2sm2ZcZxSi6IICZGV%2BQamBFcGL64hOybGnvK%2Bf9iGcmbmlJQ211m2ZDz%2B9GZ9sVkKgDXYbJQGdWDSzZbRC4jqhv906pR9KLCDX7bzd%2B4n1'


def getM3u8Url(hash_id, point_id):
    url = 'https://v.douyu.com/show/' + hash_id
    print('selenium opening url: ' + url)
    driver.get(url)
    getStreamUrl = 'https://v.douyu.com/api/stream/getStreamUrl'
    timestamp = str(int(time.time()))
    # 调用js
    jsSignResult = driver.execute_script("return ub98484234('" + point_id + "','" + deviceId + "','" + timestamp + "');")
    # 关闭标签页
    # driver.close()
    data = jsSignResult + "&vid=" + hash_id
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    cookies = {'dy_did': deviceId, 'acf_auth': acf_auth}
    streamUrlJson = json.loads(requests.post(getStreamUrl, data=data, headers=headers, cookies=cookies).text)
    # get the best quality m3u8 video url
    bestM3u8Url = ''
    thumb_video = streamUrlJson['data']['thumb_video']
    if 'normal' in thumb_video and thumb_video['normal'] != '':
        bestM3u8Url = thumb_video['normal']['url']
    if 'high' in thumb_video and thumb_video['high'] != '':
        bestM3u8Url = thumb_video['high']['url']
    if 'super' in thumb_video and thumb_video['super'] != '':
        bestM3u8Url = thumb_video['super']['url']
    return bestM3u8Url
