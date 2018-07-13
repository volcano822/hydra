# hydra

## 部署&运行
### 创建python虚拟环境
>> virtualenv hydra
### 激活虚拟环境
>> cd hydra && . bin/activate
### 编译&安装
>> make pip_install
### 抓取京东订单中的商品信息
>> scrapy crawl jd -o jd.jl