# 执行下载
import db
import json
import seleniumSign
import datetime
import m3u8Downloader

# 指定upId
upId = '0rEdlk3MgwNM'
# 指定basePath
basePath = 'D:/down'
# 连接数据库
connect = db.getMysqlConnect()
cursor = connect.cursor()


def downloadSingleDay():
    # 指定年月日查数据库的douyu_show表，获取showId
    sql = "SELECT startTimestamp,show_id FROM douyu_show WHERE startYear=%d and startMonth=%d and startDay=%d and upId='%s'" % (
        startYear, startMonth, startDay, upId)
    cursor.execute(sql)
    showResults = cursor.fetchall()
    showList = []
    for row in showResults:
        show = {'startTimestamp': row[0], 'show_id': row[1]}
        showList.append(show)
    # 遍历所有showList
    for show in showList:
        videoList = []
        # 根据showId查video
        showId = show['show_id']
        sql = "SELECT start_time,hash_id,point_id,json FROM douyu_video WHERE show_id='%s' and video_type=0 and upId='%s'" % (
            showId, upId)
        cursor.execute(sql)
        videoResults = cursor.fetchall()
        for row in videoResults:
            video = {'start_time': row[0], 'hash_id': row[1], 'point_id': row[2], 'json': json.loads(row[3])}
            videoList.append(video)
        # 遍历这些videoList
        for video in videoList:
            # 获取videoId和pointId
            videoId = video['hash_id']
            pointId = video['point_id']
            # 调用seleniumSign，获取m3u8文件的url
            m3u8Url = seleniumSign.getM3u8Url(videoId, pointId)
            print(m3u8Url)
            # 给出本地保存路径：basePath/up_[upId]/[year]-[month]-[day]/2019-10-10 19-53.ts
            start_time = datetime.datetime.utcfromtimestamp(int(video['start_time']))
            savePath = basePath + '/up_' + upId + '/' + str(start_time.year) + '-' + str(start_time.month) + '-' \
                       + str(start_time.day)
            filename = str(start_time.year) + '-' + str(start_time.month) + '-' \
                       + str(start_time.day) + ' ' + str(start_time.hour) + '-' + str(start_time.minute) + '.ts'
            # video['point_id']
            # 调用m3u8Downloader下载videos
            m3u8Downloader.download(m3u8Url, savePath, filename)


# 程序从这里开始
# 指定年月日
startYear = 2018
startMonth = 8
startDay = 1
# 每次下载的最小单位，以show_id作为区分
# 直接从数据库中把所有的show_id读出来
# 排序，从最小的开始下
# 一个show_id是一个文件
# 查询video表，查出所有属于show_id的video
# 调用函数下载每个video
#合并video为一个show（可选项），文件命名按照show的日期
