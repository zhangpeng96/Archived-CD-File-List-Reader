from os import path
from os import walk as walk
from os import stat
from collections import Counter, OrderedDict
from pprint import pprint
from time import localtime, strftime, gmtime
import pyperclip
from moviepy.editor import VideoFileClip
import configparser
import cv2

# DISK_PATH = 'D:\Live\studio'
# DISK_PATH = 'E:'
print('视频档案光盘基本信息读取 by zhangpeng96')
print('2024/9/25\n\n')

while True:

    config = configparser.ConfigParser(interpolation=None)
    config.read('config.ini', encoding='utf8')
    DISK_PATH = path.normpath(input('输入光驱路径: '))
    TOTAL_SIZE = 0
    TOTAL_COUNT = 0
    TOTAL_DURATION = 0
    MEDIA_EXT = ['AAC','MP3','WAV','MP4','TS','MTS','WMV','AVI','MPEG','MPG', 'FLV', 'MKV','MOV','MPE','NSR','NSV','VOB','WMP', 'M4A','OGG']
    trees = []


    for root, dirs, files in walk(DISK_PATH):
        # TOTAL_SIZE = sum(path.getsize( path.join(root,file) for file in files))
        # print(TOTAL_SIZE)
        print('正在读取文件中，文件列表如下：\n')
        for file in files:
            status = stat( path.join(root, file) )
            TOTAL_SIZE += status.st_size
            TOTAL_COUNT += 1
            filename, ext = path.splitext(file)
            ext = ext.lstrip('.').upper()
            print('{}'.format(filename))
            # print(status.st_size)
            if ext in MEDIA_EXT:
                print('> 读取视频时长中，请稍等...')
                try:
                    video = VideoFileClip(path.join(root, file))
                except:
                    print('> FFmpeg解析时长失败，换用OpenCV重新解析...')
                    video = cv2.VideoCapture(path.join(root, file))
                    fps = video.get(cv2.CAP_PROP_FPS)
                    totalNoFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)
                    duration = totalNoFrames // fps
                else:
                    duration = video.duration
                TOTAL_DURATION += duration
            else:
                duration = 0
            trees.append({
                'path': path.join(root, file),
                'name': filename,
                'ext': ext,
                'duration': duration,
                'size': status.st_size,
                'mtime': status.st_mtime
            })


    # pprint(trees)

    print('========== 光盘文件统计 ==========')
    type_count = Counter(map(lambda x: x['ext'], trees))
    type_count = list(sorted(type_count.items(), key=lambda x:-x[1]))
    mtime = max(map(lambda x:x['mtime'], trees))

    if TOTAL_SIZE < 1024:
        read_size = '{}B'.format(TOTAL_SIZE)
    elif 1024 <= TOTAL_SIZE < 1024*1024:
        read_size = '{:.1f}KB'.format(TOTAL_SIZE/1024)
    elif 1024*1024 <= TOTAL_SIZE < 1024*1024*1024:
        read_size = '{:.2f}MB'.format(TOTAL_SIZE/1024/1024)
    elif 1024**3 <= TOTAL_SIZE:
        read_size = '{:.2f}GB'.format(TOTAL_SIZE/1024/1024/1024)

    print('文件类型：\t', end='')
    print(', '.join(map(lambda x:'{}：{}'.format(x[0],x[1]),type_count)))
    print('最新修改时间：\t{}'.format(strftime("%Y-%m-%d %H:%M:%S", localtime(mtime))))
    print('文件总数量：\t{}'.format(TOTAL_COUNT))
    print('文件总大小：\t{:.1f}KB / {:.2f}MB / {:.2f}GB'.format(
        TOTAL_SIZE/1024, 
        TOTAL_SIZE/1024/1024, 
        TOTAL_SIZE/1024/1024/1024
    ))
    print('视频总时长：\t{}'.format(strftime("%H:%M:%S",gmtime(TOTAL_DURATION))))
    # print(mtime)

    print('========= 以下信息已复制 =========')
    # type_count_slim = type_count.items()
    if 0 < TOTAL_DURATION < 3600:
        read_duration = strftime("%M:%S", gmtime(TOTAL_DURATION))
    elif TOTAL_DURATION >= 3600:
        read_duration = strftime("%H:%M:%S", gmtime(TOTAL_DURATION))
    else:
        read_duration = ''
    
    try:
        clipDict = {            
            'year': strftime("%Y", gmtime(mtime)),
            'date': strftime("%Y%m%d", gmtime(mtime)),
            'duration': read_duration,
            'size': read_size,
            'count': TOTAL_COUNT,
            'types': '、'.join(map(lambda x:x[0], type_count[:4]))
        }
        autocopy = config['output']['autocopy']
        cliptext = autocopy.format(**clipDict)
    except:
        print('输出信息格式配置有误，已使用缺省模式')
        cliptext = '{year}\t{date}\t{size}\t{duration}\t{count}\t{types}'.format(**clipDict).encode('utf-8').decode('unicode_escape')
    else:
        cliptext = autocopy.format(**clipDict).encode('utf-8').decode('unicode_escape')
    print(cliptext)
    print('=================================')

    pyperclip.copy(cliptext)

    input('键入任意键继续')
