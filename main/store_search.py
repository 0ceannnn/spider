import requests
from lxml import etree
import redis
import app

# 连接 Redis 服务器
redis_conn = redis.Redis(host='localhost', port=6379, db=0)

cookie = '__mta=142480013.1673686407077.1675780128287.1675780321286.4; _lxsdk_cuid=185682bd7cbc8-0f09e3462ae1fa-26021151-1fa400-185682bd7cbc8; WEBDFPID=yvywu886w9y15v7yzxw3953399w05553814317yww5897958zwy22817-1987849982076-1672489981703UCGWQCCfd79fef3d01d5e9aadc18ccd4d0c95074014; _hc.v=25f3109f-2a60-b957-8eb0-c051d9e383f4.1672577231; mtcdn=K; qruuid=1ae17c8b-598d-4056-95a3-6b8b3ffd570b; oops=AgFwJgfPJ1NCpiMGwMRQeY2dGVWzoz0Xc4NjSyV6fnU_ZT-kPK3O0tuC-tnn4Ji2cj5S6cGuNsEIfAAAAACMFgAABE93r3tMGeDcI7SwflrNbQTT5ryq5TB0hLn6pBgXSDDZrzqLfc9WbG5f_at01KV6; uuid=4e5ae7a7f6d142248bbf.1675780094.1.0.0; _lx_utm=utm_source=bing&utm_medium=organic; ci=151; rvct=151,76,1,228,197,873,239; __mta=142480013.1673686407077.1675780102079.1675780128287.3; client-id=9067f27f-4739-41a6-92a5-bce806f4a14b; userTicket=vEnoCBOVnZTofgKrHoLEyHHgLetFqQlXTnLAYThL; _yoda_verify_resp=ln2vRitJMZQsS2OdmFzh8pIKYSVZCPS/k17dKdSqC+78ghIHcqvZTSezIJs8kvGH269IBb5xbEf3pQFbUDEPHJKxmen6T+Ed2q6jpisNqopV5LF930Tp8KEO9s7W+WgOh/+ICh+lGQel9z9BSbA3zfGhTSF38SCV5gBbeeEyp8mOMGQMdZxbuRIKmPTYNeJb6cxWWZHbUaE0rYUjY6ub7DyBioySHqvbyvaOzXvJWwre/OcJV0mr4nk0oU567/iApjeFK5oFSodRWQX7tsQTMhHrIDdPOhcCLEhpTCi198OQBONbrY6Yhb56Py3zW01Vi2vJgjKZVGN5GXQvgdgnfzrkZggo+yT6CWl4j1enOpFZEFvNOYtEmzwhuLgSCxJ1; _yoda_verify_rid=1685ef10d302204b; u=2944961893; n=千寻六十里; lt=AgG_I5XjWECEUdDmiLW-RZsCPo93YtRa-kAJe8xhRWAEeTwPRXNyuBLWInF5O37JWLlOvVeayhyVyAAAAAB1FgAAWvkX_BNhXOB1ho9BgyE2mUETMRf3Wp7l0ttBbXUl9LJLXCh67cCs8Lb73Cqh8Wyd; mt_c_token=AgG_I5XjWECEUdDmiLW-RZsCPo93YtRa-kAJe8xhRWAEeTwPRXNyuBLWInF5O37JWLlOvVeayhyVyAAAAAB1FgAAWvkX_BNhXOB1ho9BgyE2mUETMRf3Wp7l0ttBbXUl9LJLXCh67cCs8Lb73Cqh8Wyd; token=AgG_I5XjWECEUdDmiLW-RZsCPo93YtRa-kAJe8xhRWAEeTwPRXNyuBLWInF5O37JWLlOvVeayhyVyAAAAAB1FgAAWvkX_BNhXOB1ho9BgyE2mUETMRf3Wp7l0ttBbXUl9LJLXCh67cCs8Lb73Cqh8Wyd; token2=AgG_I5XjWECEUdDmiLW-RZsCPo93YtRa-kAJe8xhRWAEeTwPRXNyuBLWInF5O37JWLlOvVeayhyVyAAAAAB1FgAAWvkX_BNhXOB1ho9BgyE2mUETMRf3Wp7l0ttBbXUl9LJLXCh67cCs8Lb73Cqh8Wyd; _lxsdk=185682bd7cbc8-0f09e3462ae1fa-26021151-1fa400-185682bd7cbc8; firstTime=1675780320384; unc=千寻六十里; _lxsdk_s=1862c46f945-94e-edf-9ab||79'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Cookie': cookie.encode('utf-8'),
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
            print(content)
            redis_conn.set(url, content,ex=86400)
            print('成功将数据存入 Redis 缓存')
            content = content.decode('utf-8')
            return content
    except:
        print('下载页面失败')
        return None

results = []

#获取目标页面第一页信息
def get_info(target):
    url = "https://{}.meituan.com/s/{}/".format(app.meituan_area,target)
    url = url.encode('utf-8')
    response = get_page_content(url)
    html = etree.HTML(response)
    for li in html.xpath('/html/body/div/div/div/div[2]/div[1]/div[2]/div[2]/div'):
        # 店铺名称
        store_name_list = li.xpath('./div/div/div/div[1]/a/text()')
        if store_name_list:
            store_name = store_name_list
            store_name = ''.join(str(i) for i in store_name)
            store_name = store_name.replace('（', '(').replace('）', ')')
        else:
            store_name = None

        # 美团评分
        meituan_score_list = li.xpath('./div/div/div/div[1]/div[1]/span[2]/text()[1]')
        if meituan_score_list:
            meituan_score = meituan_score_list
            meituan_score = ''.join(str(i) for i in meituan_score)
            meituan_score = int(float(meituan_score)*10)
        else:
            meituan_score = None

        # 美团评论数量
        meituan_comments_list = li.xpath('./div/div/div/div[1]/div[1]/span[3]/text()[1]')
        if meituan_comments_list:
            meituan_comments = meituan_comments_list
            meituan_comments = ''.join(str(i) for i in meituan_comments)
            meituan_comments = int(meituan_comments)
        else:
            meituan_comments = None

        # 店铺类型
        store_type_list = li.xpath('./div/div/div/div[1]/div[2]/div[1]/span/span[1]/text()')
        if store_type_list:
            store_type = store_type_list
            store_type = ''.join(str(i) for i in store_type)
        else:
            store_type = 0

        # 店铺地址
        store_address_list = li.xpath('./div/div/div/div[1]/div[2]/div[1]/span/span[2]/text()[2]')
        if store_address_list:
            store_address = store_address_list
            store_address = ''.join(str(i) for i in store_address)
        else:
            store_address = 0

        # 美团消费水平（元）
        meituan_consume_list = li.xpath('./div/div/div/div[1]/div[3]/div/span/text()[2]')
        if meituan_consume_list:
            meituan_consume = meituan_consume_list
            meituan_consume = ''.join(f'{i}' for i in meituan_consume)
        else:
            meituan_consume = 0

        results.append(
            {'店铺名称': store_name,'美团评分' : meituan_score , '美团评论数量' : meituan_comments,'店铺类型' : store_type,'店铺地址' : store_address,'美团消费水平（元）' : meituan_consume})
    # print(results)
    return results

# if __name__=="__main__":
#     get_info('火锅')