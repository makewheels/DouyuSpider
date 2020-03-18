# 执行下载
import os

import db
import m3u8Downloader
import seleniumSign

# 指定upId
upId = '0rEdlk3MgwNM'
# 指定basePath
basePath = 'D:/douyu_download'
# 连接数据库
connect = db.getMysqlConnect()
cursor = connect.cursor()


# 从数据库读所有showId
def getShowIdList():
    showIdList = []
    cursor.execute("select show_id from douyu_show where upId='" + upId + "'")
    results = cursor.fetchall()
    for row in results:
        showId = int(row[0])
        showIdList.append(showId)
    # 排序，从最小的开始下
    list.sort(showIdList)
    return showIdList


# 合并文件
def mergeFiles(videoFilePathList, finalPath):
    if len(videoFilePathList) == 0:
        return
    cmd = 'ffmpeg -y -i \"concat:'
    for each in videoFilePathList:
        cmd = cmd + each + '|'
    cmd = cmd + '\" -c copy ' + finalPath.replace('.ts', '.mp4')
    print(cmd)
    os.system(cmd)
    # 删除之前的videos
    for each in videoFilePathList:
        os.remove(each)


# 程序从这里开始
# 每次下载的最小单位，以show_id作为区分
# 直接从数据库中把所有的show_id都读出来
# 一个show_id是一个文件
showIdList = getShowIdList()
# 遍历所有show
for showId in showIdList:
    # 把这个show查出来，因为后面文件名需要时间
    cursor.execute("select * from douyu_show where show_id='" + str(showId) + "'")
    show = cursor.fetchone()
    start_time = show[3]
    # 先看这个回放是是不是已经下载过了
    isReplayDownload = show[14]
    # 如果已经下载过了，则跳过
    if isReplayDownload == 1:
        print("skip show " + str(showId))
        continue
    # 截取时间
    year = start_time[0:4]
    month = start_time[5:7]
    day = start_time[8:10]
    hour = start_time[11:13]
    # 查询video表，查出所有属于show_id的video
    # 这里设置video_type=0，只要直播回放
    cursor.execute("select * from douyu_video where video_type=0 and show_id='" + str(showId) + "'")
    videoList = cursor.fetchall()
    # 视频文件路径集合
    videoFilePathList = []
    # 文件名
    folder = basePath + "/" + upId + "/" + year + "-" + month
    filename = year + "-" + month + "-" + day + "_" + hour + ".ts"
    finalPath = folder + "/" + filename
    # 每个视频
    video_part = 0
    # 遍历每个所属的video
    for video in videoList:
        hash_id = video[7]
        point_id = video[9]
        # 获得m3u8下载地址
        m3u8Url = seleniumSign.getM3u8Url(hash_id, point_id)
        print(m3u8Url)
        videoFilePathList.append(finalPath + ".video" + str(video_part))
        # 调用函数下载每个video
        # /[upId]/2018-08/2018-08-01_19.ts
        m3u8Downloader.download(m3u8Url, folder, filename + ".video" + str(video_part))
        video_part = video_part + 1
    # 合并video为一个show（可选项），文件命名按照show的日期
    mergeFiles(videoFilePathList, finalPath)
    # 这个show下载完成后，更新数据库，标记为已下载
    cursor.execute("update douyu_show set isReplyDownload=1 where show_id='" + showId + "'")
    connect.commit()
    # 下载一个show至此完成
