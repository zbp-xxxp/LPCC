# LPCC：Look at the picture and change the color

# LPCC: 结合Wechaty和Paddle控制能根据图片改变颜色的LED灯

借助飞桨PaddlePaddle技术，构建未来世界的超级ChatBot，根据图像控制现实世界的LED流水灯！

<iframe style="width:98%;height: 450px;" src="//player.bilibili.com/player.html?aid=547006736&bvid=BV1pq4y1p7XH&cid=382711639&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

b站视频链接：[https://www.bilibili.com/video/BV1pq4y1p7XH/](https://www.bilibili.com/video/BV1pq4y1p7XH/)

# 一、实现思路

![](https://ai-studio-static-online.cdn.bcebos.com/3beedf273cda409ea0a24c564eff67378605b47f34a54455868ce34c272f6dca)

完成这个项目，需要把以下关键技术解决：
1. 用户与ChatBot沟通的接口，发送图片&返回结果
2. 基于PaddleHub实现的图像分割模型部署及接口调用
3. 底层硬件Arduino的控制方式，LED灯条的硬件连接

本文将从以上三大技术展开详细介绍。

# 二、ChatBot接口实现

参考资料：
- [教你用AI Studio+wechaty+阿里云白嫖一个智能微信机器人](https://aistudio.baidu.com/aistudio/projectdetail/1836012?channelType=0&channel=0)

## 1.TOKEN的获取与转换

TOKEN是一个用来连接底层服务的密钥，也是开发聊天机器人的第一步。如果要开发微信聊天机器人时，Wechaty会使用TOKEN来连接第三方的服务：

<img style="display: block; margin: 0 auto;" src="https://ai-studio-static-online.cdn.bcebos.com/10649b4c005c4969bbb3e02098eed022792cd15224d04fc5b53b1a276dd29583" width = "30%" height = "30%" />

从官方拿到的TOKEN是不能直接用的，需要搭建PadLocal Token Gateway后，才能使用，具体方法如下：[Python Wechaty如何使用PadLocal Puppet Service](https://wechaty.js.org/2021/02/03/python-wechaty-for-padlocal-puppet-service/)

## 2.基于叮咚机器人改写接口

Wechaty官方提供了一个非常简单的ChatBot案例——[叮咚机器人](https://github.com/wechaty/python-wechaty-getting-started/blob/master/examples/ding-dong-bot.py)，使用该案例可以快速改写保存图片的接口（这里只展示最关键的代码）：

```
async def on_message(msg: Message):
    """
    Message Handler for the Bot
    """
    # 如果收到的message是一张图片
    if msg.type() == Message.Type.MESSAGE_TYPE_IMAGE:
        # 将Message转换为FileBox
        file_box = await msg.to_file_box()
        # 获取图片名
        img_name = file_box.name
        # 图片保存的路径，需要提前在本地创建image文件夹
        img_path = './image/' + img_name
        print(img_path)
        # 将图片保存为本地文件
        await file_box.to_file(file_path=img_path)
```

至此，我们已经能通过ChatBot接收用户发来的图片了，拿到图片，我们才能把图片传给Paddle做进一步的处理。

# 三、PaddleHub模型部署与调用

这里我使用的是基于cityscape数据集训练得到的语义分割模型[fcn_hrnetw18_cityscapes](https://www.paddlepaddle.org.cn/hubdetail?name=fcn_hrnetw18_cityscapes&en_category=ImageSegmentation)

## 1.一行代码完成服务部署

PaddleHub Serving可以部署一个在线图像分割服务，下载完模型后，只需一行代码即可完成模型部署：
```
$ hub serving start -m fcn_hrnetw18_cityscapes
```
服务部署成功后：

<img style="display: block; margin: 0 auto;" src="https://ai-studio-static-online.cdn.bcebos.com/d34c67b543494e1ea2e54447b496c88ca423ad8ab7604d7db5c922933004255f" width = "80%" height = "80%" />


## 2.发送请求获取预测结果

配置好服务端，以下几行代码即可实现发送预测请求，并获取预测结果:

```
import requests
import json
import cv2
import base64

import numpy as np


def cv2_to_base64(image):
    data = cv2.imencode('.jpg', image)[1]
    return base64.b64encode(data.tostring()).decode('utf8')

def base64_to_cv2(b64str):
    data = base64.b64decode(b64str.encode('utf8'))
    data = np.fromstring(data, np.uint8)
    data = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return data

# 发送HTTP请求
org_im = cv2.imread('/PATH/TO/IMAGE')
data = {'images':[cv2_to_base64(org_im)]}
headers = {"Content-type": "application/json"}
url = "http://127.0.0.1:8866/predict/fcn_hrnetw18_cityscapes"
r = requests.post(url=url, headers=headers, data=json.dumps(data))
mask = base64_to_cv2(r.json()["results"][0])
```

# 四、基于Arduino的底层硬件控制

[秒上手！使用Arduino控制基于WS2812B的LED灯条](https://blog.csdn.net/zbp_12138/article/details/119299637?spm=1001.2014.3001.5501)

## 硬件准备

### 1. Arduino UNO R3 开发板

<img style="display: block; margin: 0 auto;" src="https://ai-studio-static-online.cdn.bcebos.com/d5b4c5044a9e495fa04ff545df8f609d9704092769a148f78081b4ffadd23695" width = "80%" height = "80%" />


### 2. 基于WS2812B的LED灯条

<img style="display: block; margin: 0 auto;" src="https://ai-studio-static-online.cdn.bcebos.com/cdd0c842a2d4452193fc60378cd39e75c1b33f5758774ab1b660c6680fc87f6e" width = "80%" height = "80%" />

### 3. 杜邦线若干

<img style="display: block; margin: 0 auto;" src="https://ai-studio-static-online.cdn.bcebos.com/eca20c7837444c58a4b3e8561ccfb23b19fc8129a1ad402c827ec4c47f178698" width = "80%" height = "80%" />


## 软件准备

### 1. Arduino IDE

Arduino的开发工具，可以在官网下载：[https://www.arduino.cc/en/software](https://www.arduino.cc/en/software)

<img style="display: block; margin: 0 auto;" src="https://ai-studio-static-online.cdn.bcebos.com/d374333cc83d485f97925d1c01e8dbd31ebdaa3e7cd548eeb6ba8709d54b4b33" width = "80%" height = "80%" />

### 2. LED灯条驱动库

驱动库源码已在GitHub上开源：[https://github.com/FastLED/FastLED](https://github.com/FastLED/FastLED)

下载好驱动库后，将驱动库复制到Arduino工作目录下的**libraries文件夹**里：

<img style="display: block; margin: 0 auto;" src="https://ai-studio-static-online.cdn.bcebos.com/3864d8d0986b4cffa407a6d5d108a073ebe4fbc0f0464d93b2b5e9ec23be09b9" width = "80%" height = "80%" />


## 硬件连接

硬件连接方法如下图所示：

<img style="display: block; margin: 0 auto;" src="https://ai-studio-static-online.cdn.bcebos.com/4c0bd3c5984044b688acd189fb5a9263b4bb8ca3f2dc4e2fbf57f3c561f1d295" width = "80%" height = "80%" />

接线时一定要注意接口的引脚，正负极千万不要接错了：

<img style="display: block; margin: 0 auto;" src="https://ai-studio-static-online.cdn.bcebos.com/5b4783fd628b4b9aaf87af182bf784e58e10c6d31d17493bb04d270f2f53fdce" width = "80%" height = "80%" />


## 点亮灯条

我购买的灯条有30颗小灯珠，下面我将通过Arduino驱动灯条循环点亮红、绿、蓝三种颜色。

点亮小灯珠的代码其实非常简单，首先需要导入驱动库：

```c
#include <FastLED.h>
#define LED_PIN     7
#define NUM_LEDS    30
CRGB leds[NUM_LEDS];
```

灯的颜色是由三原色决定的，因此控制灯的颜色只需要配置3种颜色的强弱即可，要想亮白光，只需要做如下配置：

```c
CRGB ( 255, 255, 255)
```

最后将代码串起来：

```c
#include <FastLED.h>
#define LED_PIN     7
#define NUM_LEDS    30
CRGB leds[NUM_LEDS];
void setup() {
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
}
void loop() {
  // Red
  for (int i = 0; i <= 29; i++) {
    leds[i] = CRGB ( 255, 0, 0);
    FastLED.show();
    delay(40);
  }

  // Green
  for (int i = 0; i <= 29; i++) {
    leds[i] = CRGB ( 0, 255, 0);
    FastLED.show();
    delay(40);
  }

  //  Blue
  for (int i = 0; i <= 29; i++) {
    leds[i] = CRGB ( 0, 0, 255);
    FastLED.show();
    delay(40);
  }

}
```

# 五、效果展示

<iframe style="width:98%;height: 450px;" src="//player.bilibili.com/player.html?aid=547113168&bvid=BV1Pq4y1n7UH&cid=382714426&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

b站视频链接：[https://www.bilibili.com/video/BV1Pq4y1n7UH/](https://www.bilibili.com/video/BV1Pq4y1n7UH/)


# 写在最后

首先非常感谢各位前辈们在我遇到问题时给予我帮助，没有你们的悉心指导，LPCC这个项目可能还只处于想法阶段。对于一些自己踩过的坑，我都记录在下面了：
- con not ping的原因及解决方案：最新版本中的ping规则出现了问题，正在修复，先使用0.8.14版本，即wechaty-puppet-service应回滚为0.8.14版本
- token无效的原因及解决方案：padlocal token 比较特殊，需要使用 token gateway 转换之后， Python Wechaty 才可以试用。See:
[https://wechaty.js.org/2021/02/03/python-wechaty-for-padlocal-puppet-service/](https://wechaty.js.org/2021/02/03/python-wechaty-for-padlocal-puppet-service/)

最后，我将本项目的所有代码开源，代码仓库如下：[https://github.com/zbp-xxxp/LPCC](https://github.com/zbp-xxxp/LPCC)

# 作者简介

> 北京联合大学 机器人学院 自动化专业 2018级 本科生 郑博培

> 中国科学院自动化研究所复杂系统管理与控制国家重点实验室实习生

> 百度飞桨开发者技术专家 PPDE

> 百度飞桨官方帮帮团、答疑团成员

> 深圳柴火创客空间 认证会员

> 百度大脑 智能对话训练师

> 阿里云人工智能、DevOps助理工程师

我在AI Studio上获得至尊等级，点亮10个徽章，来互关呀！！！<br>
https://aistudio.baidu.com/aistudio/personalcenter/thirdview/147378

![](https://ai-studio-static-online.cdn.bcebos.com/187d359bec3349c5a5e581bea14a4d2fb121952a86c342aea0eca063ed17b9a1)

