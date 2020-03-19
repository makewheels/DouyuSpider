# m3u8下载器
import os
import threading

import requests
import time


# 获取基地址
def getBaseUrl(m3u8Url):
    # 从最后一个 / 开始算
    # 问号索引
    questionMarkIndex = m3u8Url.index('?')
    # 斜杠索引
    slashIndex = questionMarkIndex - 1
    while m3u8Url[slashIndex] != '/' and slashIndex >= 0:
        slashIndex = slashIndex - 1
    return m3u8Url[0:slashIndex + 1]


# 发请求获取m3u8碎片列表
def getPieceUrlList(baseUrl, m3u8Url):
    m3u8File = requests.get(m3u8Url).text
    lines = m3u8File.splitlines()
    pieceUrlList = []
    for line in lines:
        # 不以#开头，并且不是空行
        if line.startswith('#') == False and line != '':
            pieceUrlList.append(baseUrl + line)
    return pieceUrlList


# 碎片数量
pieceAmount = 0
# 碎片缓存文件夹路径
pieceCachePath = ''
# 最终文件路径
finalFilePath = ''


# 创建缓存文件夹，保存所有碎片
def getPieceCachePath(savePath, folderName):
    pieceCachePath = ''
    if savePath.endswith('/'):
        pieceCachePath = savePath + folderName
    else:
        pieceCachePath = savePath + '/' + folderName
    if os.path.exists(pieceCachePath) == False:
        os.makedirs(pieceCachePath)
    return pieceCachePath


# 下载一个文件
def downloadSingleFile(url, path):
    try:
        r = requests.get(url)
        with open(path, 'wb') as code:
            code.write(r.content)
            code.flush()
    except:
        r = requests.get(url)
        with open(path, 'wb') as code:
            code.write(r.content)
            code.flush()


# 合并碎片
def mergePieces(fPath, pCachePath):
    pAmount = len(missionList)
    # 先拿到碎片文件列表
    pieceFilePathList = []
    for i in range(0, pAmount):
        pieceFilePathList.append(pCachePath + '/' + str(i))
    # 执行合并
    finalFile = open(fPath, 'wb')
    # 遍历每个碎片
    # for pieceFilePath in pieceFilePathList:
    #     with open(pieceFilePath, 'rb') as pieceFile:
    #         current = int(os.path.basename(pieceFilePath)) + 1
    #         total = pAmount
    #         percent = round(current / total * 100, 1)
    #         print('merge piece: ' + str(current) + ' / ' + str(total) + '  ' + str(percent) + '%')
    #         content = pieceFile.read()
    #         finalFile.write(content)
    # finalFile.close()

    cmd = 'ffmpeg -y -i \"concat:'
    for pieceFilePath in pieceFilePathList:
        cmd = cmd + pieceFilePath + '|'
    cmd = cmd + '\" -acodec copy -vcodec copy -absf aac_adtstoasc ' + fPath.replace('\\', '/')
    print(cmd)
    os.system(cmd)

    # 删除碎片缓存文件夹
    # for eachPieceFile in pieceFilePathList:
    #     os.remove(eachPieceFile)
    # 删除缓存文件夹
    # os.rmdir(pCachePath)
    print('merge ts pieces finish')


# 锁
threadLock = threading.Lock()
# 任务列表
# state: 0表示未下载，1表示正在下载，2表示已完成
missionList = []

# 下载进度
progress = {'downloadBytes': 0, 'startTime': 0}


def getProgress():
    return progress


# 初始化任务
def initDownloadMission(pieceUrlList, pieceCachePath):
    progress['downloadBytes'] = 0
    progress['startTime'] = time.time()
    for index, pieceUrl in enumerate(pieceUrlList):
        missionList.append({
            'index': index,
            'url': pieceUrl,
            'path': pieceCachePath + '/' + str(index),
            'size': 0,
            'state': 0
        })


# 获取任务
def getPieceMission():
    # 先上锁
    threadLock.acquire()
    # 遍历任务列表
    for mission in missionList:
        # 找到未下载的任务
        if mission['state'] == 0:
            # 标记为正在下载
            mission['state'] = 1
            # 释放锁
            threadLock.release()
            # 返回任务
            return mission
    # 如果走到这了，就说明所有任务都已经完成了
    # 释放锁
    threadLock.release()
    # 返回空
    return None


# 碎片下载完成，提交任务
def submitMission(mission):
    # 先上锁
    threadLock.acquire()
    # 把对应任务标记为已完成
    missionList[mission['index']]['state'] = 2
    finishCount = 0
    # 遍历mission列表
    for mission in missionList:
        # 统计已经完成的任务数
        if mission['state'] == 2:
            finishCount = finishCount + 1
    # 下载完成度
    percent = round(finishCount / len(missionList) * 100, 1)
    print(str(percent) + '%', end='')
    # 释放锁
    threadLock.release()


# 所有任务已完成
def onAllMissionsFinished():
    print('onAllMissionsFinished')
    # mergePieces()
    # 开启新线程合并碎片
    # _thread.start_new_thread(mergePieces,())


# 多线程下载类
class DownloadThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        # 获取任务
        mission = getPieceMission()
        # 循环接新任务，如果有任务
        while mission != None:
            # 执行下载
            print(threading.currentThread().getName() + ' downloading ' + str(mission['index']) + " " + mission['path'])
            downloadSingleFile(mission['url'], mission['path'])
            # 设置文件大小，用于统计速度
            mission['size'] = os.path.getsize(mission['path'])
            # 提交任务
            submitMission(mission)
            # 计算下载速度
            progress = getProgress()
            downloadBytes = progress['downloadBytes']
            downloadBytes = downloadBytes + mission['size']
            progress['downloadBytes'] = downloadBytes
            timeCost = time.time() - progress['startTime']
            speed = downloadBytes / 1024 / timeCost
            print(" " + "\033[1;34;42m " + str(int(speed)) + " K/S \033[0m")
            # 继续获取新任务
            mission = getPieceMission()


# 下载，m3u8Url，保存路径，最终文件名
def download(m3u8Url, savePath, filename):
    baseUrl = getBaseUrl(m3u8Url)
    # 拿到下载文件URL列表
    pieceUrlList = getPieceUrlList(baseUrl, m3u8Url)
    # 碎片数量
    pieceAmount = len(pieceUrlList)
    # 文件夹分隔符替换
    savePath = savePath.replace('\\', '/')
    # 获得碎片缓存文件夹路径
    pieceCachePath = getPieceCachePath(savePath, filename + '_cache')
    # 最终文件路径
    finalFilePath = savePath + '/' + filename
    # 开启多线程下载每个碎片
    # 初始化下载任务
    initDownloadMission(pieceUrlList, pieceCachePath)
    # 线程数量
    threadAmount = 5
    # 线程池
    threadPool = []
    # 创建线程
    for i in range(threadAmount):
        eachThread = DownloadThread(i, "Thread-" + str(i))
        eachThread.start()
        threadPool.append(eachThread)
        # 等待所有线程完成
    for t in threadPool:
        t.join()

    print('------thread finish------')
    mergePieces(finalFilePath, pieceCachePath)
    pieceAmount = 0
    pieceCachePath = ''
    finalFilePath = ''
    missionList.clear()
