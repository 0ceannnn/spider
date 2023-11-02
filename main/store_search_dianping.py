import requests
import redis
from lxml import etree
import re
import app


# 连接 Redis 服务器
redis_conn = redis.Redis(host='localhost', port=6379, db=0)
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48',
    'Cookie':'_lxsdk_cuid=1856d55bcd8c8-0092bd56abe5cc-7a575473-1fa400-1856d55bcd8c8; _hc.v=e4d4ed74-bfac-3eeb-4f56-4e2b31e87ad7.1672576614; WEBDFPID=2z7662z228y051y8005xu3xwx45685w08143w42y367979587w6434y1-1987936742689-1672576741960EMESSWCfd79fef3d01d5e9aadc18ccd4d0c95071183; ua=烟雨无陌; ctu=b0e5f8a7af06575799542e9aec87b4d0b403d20015160799ac98e28814a00003; s_ViewType=10; _lx_utm=utm_source=bing&utm_medium=organic; qruuid=32eacdf4-5878-4adc-9fb6-683575e58f2e; dplet=5f219605d4a352b8ac3979e88accde7d; dper=0c173312e0df18548261e811294b64cb1d6eca517eff4192b1792169b75e5c463d5bac568096bd957a2ef552886aaa2793e27cbaae709d03dbf8ecdec060bdf9; ll=7fd06e815b796be3df069dec7836c3df; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1681697265; fspop=test; uuid=D36C54F13ECDDF11239AD598B028CF481CBE66D68071325E46644EA819FD2FC8; iuuid=D36C54F13ECDDF11239AD598B028CF481CBE66D68071325E46644EA819FD2FC8; _lxsdk=D36C54F13ECDDF11239AD598B028CF481CBE66D68071325E46644EA819FD2FC8; _ga=GA1.2.495411257.1681697304; _gid=GA1.2.1152107452.1681697304; cy=24; cye=shijiazhuang; Hm_lpvt_602b80cf8079ae6591966cc70a3940e7=1681706290; _lxsdk_s=1878d79fafd-c94-deb-04b||39'.encode('GBK')
}

def get_page_content(url):
    """
    获取页面内容，并将结果存入 Redis 缓存中
    """
    # 先从 Redis 中获取页面内容
    content = redis_conn.get(url)
    if content:
        print('从 Redis 缓存中获取到数据')
        content = content.decode('utf-8')
        return content

    # 如果 Redis 中不存在，则重新下载页面内容并存入 Redis 中
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            content = response.content
            redis_conn.set(url, content,ex=86400)
            print('成功将数据存入 Redis 缓存')
            content = content.decode('utf-8')
            return content
    except:
        print('下载页面失败')
        return None

results = []

def get_info(target):
    # 测试代码
    urls = ['https://www.dianping.com/search/keyword/{}/0_{}'.format(app.dianping_area,target),
            'https://www.dianping.com/search/keyword/{}/0_{}/p2'.format(app.dianping_area,target),
            'https://www.dianping.com/search/keyword/{}/0_{}/p3'.format(app.dianping_area,target)]
    for url in urls:
        content = get_page_content(url)
        html = etree.HTML(content)
        for li in html.xpath('/html/body/div[2]/div[3]/div[1]/div[1]/div[2]/ul/li'):
            # 评分
            score_class = li.xpath('./div[2]/div[2]/div/div/span/@class')
            all_numbers = []
            output_list = []
            if score_class:
                for i in range(1, len(score_class) + 1, 5):
                    if i <= len(score_class):
                        output_list.append(score_class[i - 1])
                # 定义一个正则表达式，用来匹配数字部分
                pattern = r'[0-9]+'
                # 循环遍历需要提取数字的字符串列表
                for my_str in output_list:
                    # 使用re.findall()函数查找所有符合正则表达式的数字
                    numbers = re.findall(pattern, my_str)

                    # 将提取到的数字添加到all_numbers中
                    all_numbers.extend(numbers)
                all_numbers = ''.join(str(i) for i in all_numbers)
            else:
                score = 0

            # 评论数量
            comment_num_raw = li.xpath('./div[2]/div[2]/a[1]/b/text()')
            if comment_num_raw:
                comment_num = comment_num_raw
                comment_num = ''.join(str(i) for i in comment_num)
            else:
                comment_num = 0

            # 人均消费
            avg_cost_raw = li.xpath('./div[2]/div[2]/a[2]/b/text()')
            if avg_cost_raw:
                avg_cost = avg_cost_raw
                avg_cost = ''.join(str(i) for i in avg_cost)
                avg_cost = avg_cost.replace('￥', '')
            else:
                avg_cost = 0
            #
            # # 类型
            # category = li.xpath('./div[2]/div[3]/a[1]/span/text()')
            #
            # # 地点
            # location = li.xpath('./div[2]/div[3]/a[2]/span/text()')

            # 店铺名称
            store_name = li.xpath('./div[2]/div[1]/a/h4/text()')[0]
            store_name = ''.join(str(i) for i in store_name)

            results.append(
                {'店铺名称': store_name, '大众点评评分': all_numbers, '大众点评评论数': comment_num, '大众点评消费水平（元）': avg_cost})
    # print(results)
    return results


# if __name__=="__main__":
#     get_info('火锅')