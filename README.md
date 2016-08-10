# 12306_transfer_train
> 本项目可以查询两城市之间火车的中转方案，中转方案只包含同站换乘，不包含同城不同站换乘

## requirements
* python3
* requests
* prettytable

## usage
config.ini 是本项目的配置文件

config.ini的字段含义：

* export_csv : 是否将结果导出到csv文件   true 或 false
* transfer_station_max_wait_minute : 中转车辆间隔最大时间(分钟)，即你能忍受在中转火车站最长等待时间
* transfer_station_min_interval : 中转车辆间隔最短时间（分钟）,即你在中转火车站等待的最短时间，建议不要小于10
* travel_data_time : 乘车日期,按照"yyyy-mm-dd"的格式,形如:2016-08-06;此参数为可选参数,可以不使用这个参数
 

