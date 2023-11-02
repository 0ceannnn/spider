from flask import Flask, render_template,request
from PIL import Image
from wordcloud import WordCloud
from matplotlib import pyplot as plt
import numpy as np
import main.store_search
import main.store_search_dianping
import main.area_check
import redis
import sys
import io
import threading
from concurrent.futures import ProcessPoolExecutor


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['DEBUG'] = True
r = redis.Redis(host='localhost', port=6379, db=0 ,decode_responses=True, encoding='utf-8')

results = []
meituan_area = "sjz"
dianping_area = 24
area1 = "石家庄"
content = ""
count = 0
dicts3 = None

@app.route('/')
def index():
    word_num = r.scard('words')
    return render_template("index.html", word_num=word_num)

@app.route('/index')
def home():
    return index()

@app.route("/bar")
def get_bar():
    options = request.args.get('options', content)
    if options == "评分":
        new_dicts1 = {d['店铺名称']: d['美团评分'] for d in dicts3
                     if d['店铺名称'] and d['美团评分']
                     and d['店铺名称'] is not None and d['美团评分'] is not None}
        new_dicts = new_dicts1
    elif options == "评论数量":
        new_dicts2 = {d['店铺名称']: d['美团评论数量'] for d in dicts3
                     if d['店铺名称'] and d['美团评论数量']
                     and d['店铺名称'] is not None and d['美团评论数量'] is not None}
        new_dicts = new_dicts2
    elif options == "消费水平":
        new_dicts3 = {d['店铺名称']: d['美团消费水平（元）'] for d in dicts3
                     if d['店铺名称'] and d['美团消费水平（元）']
                     and d['店铺名称'] is not None and d['美团消费水平（元）'] is not None}
        new_dicts = new_dicts3
    top_five = sorted([(k, int(v)) for k, v in new_dicts.items()], key=lambda x: x[1], reverse=True)[:5]
    store_names = []
    meituan_scores = []
    for item in top_five:
        store_names.append(item[0])
        meituan_scores.append(item[1])
    # 构建option配置项
    option = {
        "xAxis": {
            "data": store_names
        },
        "yAxis": {},
        "series": [{
            "name": "sales",
            "type": "bar",
            'barWidth': 1,
            "data": meituan_scores
        }]
    }
    # 返回option JSON字符串
    return render_template("rank.html", option=option, content=content, area1=area1, options=options)



@app.route('/word')
def count_word():
    global count
    word_freq = r.hgetall('word_freq')#返回哈希表中所有的字段和值
    top_50 = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]#lambda对于数组的第几个元素进行比较
    #result = ' '.join(['{} {}'.format(word, count) for word, count in top_50])
    count += 1  # 计数器加1
    # 生成遮罩图片
    img = Image.open(r'.\static\assets\img\tree.jpg')  # 打开遮罩图片
    img_array = np.array(img)  # 将图片转换为数组
    wc = WordCloud(  # 封装WordCloud对象
        background_color='white',
        mask=img_array,
        font_path="msyh.ttc",
        # font_path="SourceHanSansCN-Bold.otf",  # 字体所在位置：C:\Windows\Fonts
        min_word_length=2,  # 一个单词必须包含的最小字符数
        stopwords={"就是", "一个", "不是", "这样", "一部", "我们", "没有", "不会", "不能", "每个"}  # 屏蔽词
    )
    result = ' '.join(['{} {}'.format(word, count) for word, count in top_50])
    wc.generate_from_text(result)
    #fig = plt.figure(1)  # 绘制图片
    plt.imshow(wc)  # 按照词云wc的规则显示图片
    plt.axis('off')  # 是否显示坐标轴

    # 输出词云图片到文件
    plt.savefig(r'.\static\assets\img\word.jpg', dpi=100)
    return render_template("word.html")


@app.route('/region',methods=['get'])
def region():
    global area1
    global meituan_area
    global dianping_area
    global flag
    area = request.args.get('area',area1)
    areas = main.area_check.area_check(area=area)
    if areas != "false":
        area1 = area
    else:
        pass
    if areas == "false":
        flag = False
        areas = [dianping_area, meituan_area]
    else:
        flag = True
        dianping_area = areas[0]
        meituan_area = areas[1]
    return render_template("region.html", flag=flag, areas=areas, area=area1)


@app.route('/search',methods=['get'])
def search():
    global content
    try:
        content = request.args.get('content')
        words = content.split()
        for word in words:
            r.sadd('words', word)
            r.hincrby('word_freq', word, 1)
            r.expire('words', 86400)  # 设置words生命周期为1天(86400秒)
            r.expire('word_freq', 86400)  # 设置word_freq生命周期为1天(86400秒)

        #word_freq = r.hgetall('word_freq')
        dicts1 = main.store_search.get_info(target=content)
        dicts2 = main.store_search_dianping.get_info(target=content)
        dicts1_index = {d['店铺名称']: d for d in dicts1}
        dicts2_index = {d['店铺名称']: d for d in dicts2}

        for d in dicts2:
            if d['店铺名称'] in dicts1_index:
                dicts1_index[d['店铺名称']].update(d)
                dicts2_index[d['店铺名称']] = dicts1_index[d['店铺名称']]
            else:
                dicts1_index[d['店铺名称']] = d
                dicts2_index[d['店铺名称']] = d

        for d in dicts1:
            if d['店铺名称'] not in dicts2_index:
                dicts1_index[d['店铺名称']].update(d)
            else:
                dicts1_index[d['店铺名称']].update(d)
        global dicts3
        dicts3 = dicts1.copy()
        dicts1.clear()

        return render_template("search.html", dicts1=dicts3, content=content)
    except Exception:
        return render_template("search.html")

@app.route('/team')
def team():
    return render_template("team.html")


if __name__ == '__main__':
    pool = ProcessPoolExecutor()  # 进程池对象必须在所有函数生成时建立
app.run(host='0.0.0.0', debug=True)