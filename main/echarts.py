@app.route("/bar")
def get_bar():
    # 构建数据
    bar_data = [5, 20, 36, 10, 75]
    # 构建option配置项
    option = {
        "xAxis": {
            "data": ["A", "B", "C", "D", "E"]
        },
        "yAxis": {},
        "series": [{
            "name": "sales",
            "type": "bar",
            "data": bar_data
        }]
    }
    # 返回option JSON字符串
    return render_template("test.html", option=option)