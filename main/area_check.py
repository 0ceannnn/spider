import pandas as pd
import app
import sys
import io

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')
def area_check(area):
    # 读取第一个xlsx文件
    df1 = pd.read_excel('C:/graduate/spider02/main/dianping_cities.xlsx', usecols=[1, 2], names=['col2', 'col3'])

    # 读取第二个xlsx文件
    df2 = pd.read_excel('C:/graduate/spider02/main/meituan_cities.xlsx', usecols=[1, 2], names=['col2', 'col3'])

    # 用户输入需要读取的数据
    user_input = area

    # 判断数据是否均存在
    if user_input in df1['col2'].values and user_input in df2['col2'].values:
        # 输出该数据对应的第三列的数据
        dianping_city = df1.loc[df1['col2'] == user_input, 'col3'].values[0]
        meituan_city = df2.loc[df2['col2'] == user_input, 'col3'].values[0]
        city = [dianping_city,meituan_city]
        return (city)
    else:
        return ("false")
#         print(dianping_city,meituan_city)
#
# if __name__=="__main__":
#     area_check("邢台")