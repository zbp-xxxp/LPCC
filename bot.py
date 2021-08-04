import os
os.environ['WECHATY_PUPPET']="wechaty-puppet-service"
os.environ['WECHATY_PUPPET_SERVICE_TOKEN']="" # Wechaty token

import asyncio
import requests
import json
import cv2
import base64
import serial
import numpy as np
import time

Arduino = serial.Serial('COM8', 9600, timeout=0.2)
print(Arduino)

def cv2_to_base64(image):
    data = cv2.imencode('.jpg', image)[1]
    return base64.b64encode(data.tobytes()).decode('utf8')

def base64_to_cv2(b64str):
    data = base64.b64decode(b64str.encode('utf8'))
    data = np.fromstring(data, np.uint8)
    data = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return data

from wechaty import (
    Contact,
    FileBox,
    Message,
    Wechaty,
    ScanStatus,
)


async def on_message(msg: Message):
    """
    Message Handler for the Bot
    """
    if msg.text() == 'ding':
        await msg.say('dong')

        file_box = FileBox.from_url(
            'https://ss3.bdstatic.com/70cFv8Sh_Q1YnxGkpoWK1HF6hhy/it/'
            'u=1116676390,2305043183&fm=26&gp=0.jpg',
            name='ding-dong.jpg'
        )
        await msg.say(file_box)
    # 如果收到的message是一张图片
    if msg.type() == Message.Type.MESSAGE_TYPE_IMAGE:
        # Arduino = serial.Serial('COM8', 9600, timeout=0.2)
        # print(Arduino)
        # 将Message转换为FileBox
        file_box = await msg.to_file_box()
        # 获取图片名
        img_name = file_box.name
        # 图片保存的路径
        img_path = './image/' + img_name
        print(img_path)
        # 将图片保存为本地文件
        await file_box.to_file(file_path=img_path)
        # 发送HTTP请求
        org_im = cv2.imread(img_path)
        Bmean = np.mean(org_im[:,:,0])
        Gmean = np.mean(org_im[:,:,1])
        Rmean = np.mean(org_im[:,:,2])
        print(Bmean, Gmean, Rmean)
        org_im = cv2.resize(org_im,(224, 224))
        data = {'images':[cv2_to_base64(org_im)]}
        headers = {"Content-type": "application/json"}
        url = "http://10.12.216.65:8866/predict/fcn_hrnetw18_cityscapes"
        r = requests.post(url=url, headers=headers, data=json.dumps(data))
        mask = base64_to_cv2(r.json()["results"][0])

        mask = np.asarray(mask)
        Bmean = np.mean(mask[:,:,0])
        Gmean = np.mean(mask[:,:,1])
        Rmean = np.mean(mask[:,:,2])
        print(Bmean, Gmean, Rmean)
        send_data = '{}{}{}'.format(int(Rmean), int(Gmean), int(Bmean))
        await msg.say('这张图会使流水灯的RGB值变：{} {} {} 噢~'.format(int(Rmean), int(Gmean), int(Bmean)))
        print(send_data.encode())
        if(Arduino.isOpen()):
            for _ in range(200):
                Arduino.write(send_data.encode())
                time.sleep(0.1)
            print("send successful!")
            time.sleep(10)
            Arduino.close()



async def on_scan(
        qrcode: str,
        status: ScanStatus,
        _data,
):
    """
    Scan Handler for the Bot
    """
    print('Status: ' + str(status))
    print('View QR Code Online: https://wechaty.js.org/qrcode/' + qrcode)


async def on_login(user: Contact):
    """
    Login Handler for the Bot
    """
    print(user)
    # TODO: To be written


async def main():
    """
    Async Main Entry
    """
    #
    # Make sure we have set WECHATY_PUPPET_SERVICE_TOKEN in the environment variables.
    # Learn more about services (and TOKEN) from https://wechaty.js.org/docs/puppet-services/
    #
    if 'WECHATY_PUPPET_SERVICE_TOKEN' not in os.environ:
        print('''
            Error: WECHATY_PUPPET_SERVICE_TOKEN is not found in the environment variables
            You need a TOKEN to run the Python Wechaty. Please goto our README for details
            https://github.com/wechaty/python-wechaty-getting-started/#wechaty_puppet_service_token
        ''')

    bot = Wechaty()
    # bot.on('on_logout', on_logout)
    bot.on('scan',      on_scan)
    bot.on('login',     on_login)
    bot.on('message',   on_message)

    await bot.start()

    print('[Python Wechaty] Ding Dong Bot started.')


asyncio.run(main())