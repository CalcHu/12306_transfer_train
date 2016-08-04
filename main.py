import connection
import config
import time
from prettytable import PrettyTable
from configparser import ConfigParser


def query(cfg):
    start_station_name = check_station_name(input('请输入出发站名: ').lower())
    start_code = station_cn_name_dict[start_station_name]
    end_station_name = check_station_name(input('请输入目的地站名：').lower())
    end_code = station_cn_name_dict[end_station_name]
    is_transfer = input('是否需要中转：0，不需要；1，需要:    ')
    if is_transfer in ['1']:
        transfer_station_name = check_station_name(input('请输入中转站名：').lower())
        transfer_code = station_cn_name_dict[transfer_station_name]
    else:
        transfer_station_name = None
        transfer_code = None

    # 获取输出数据
    output_data = get_data(cfg, start_code,end_code,transfer_code,is_transfer != '0')

    output(output_data, cfg.getboolean('config','export_csv'), start_station=start_station_name,
           end_station=end_station_name, transfer_station=transfer_station_name)


def get_data(cfg, start_station_code, end_station_code, transfer_station_code=None, need_transfer=True):
    list_data = []
    if need_transfer :
        railway_info1 = get_railway_info(start_station_code, transfer_station_code, cfg)['data']['datas']
        railway_info2 = get_railway_info(transfer_station_code, end_station_code, cfg)['data']['datas']

        arrive_time1 = {}
        start_time2 = {}

        railway_info_dict1 = {}
        railway_info_dict2 = {}

        for i in railway_info1:
            hour_str, min_str = i['arrive_time'].split(':')
            arrive_time1[i['station_train_code']] = 60 * int(hour_str) + int(min_str)
            railway_info_dict1[i['station_train_code']] = i
        for i in railway_info2:
            hour_str, min_str = i['start_time'].split(':')
            start_time2[i['station_train_code']] = 60 * int(hour_str) + int(min_str)
            railway_info_dict2[i['station_train_code']] = i

        title = ['始发站', '出发时间', '车次1', '到达中转站时间', '中转站', '中转站出发时间',
                                  '车次2', '终到时间', '终到站']

        transfer_wait_min = cfg.getint('config','transfer_station_min_interval')
        transfer_wait_max = cfg.getint('config','transfer_station_max_wait_minute')
        for j in railway_info_dict1:
            for k in railway_info_dict2:
                delta = start_time2[k] - arrive_time1[j]
                if railway_info_dict1[j]['to_station_name'] == railway_info_dict2[k]['from_station_name'] and \
                        (
                                    ((delta > transfer_wait_min) and (delta < transfer_wait_max)) or
                                    ((arrive_time1[j] + transfer_wait_max >= 1440 and delta + 1440 > transfer_wait_min and delta + 1440 < transfer_wait_max))
                        ):
                    list_data.append([
                        railway_info_dict1[j]['from_station_name'],
                        railway_info_dict1[j]['start_time'],
                        railway_info_dict1[j]['station_train_code'],
                        railway_info_dict1[j]['arrive_time'],
                        railway_info_dict1[j]['to_station_name'],
                        railway_info_dict2[k]['start_time'],
                        railway_info_dict2[k]['station_train_code'],
                        railway_info_dict2[k]['arrive_time'],
                        railway_info_dict2[k]['to_station_name']
                    ])

    else:
        railway_info = get_railway_info(start_station_code, end_station_code, cfg)['data']['datas']
        title = ['始发站', '出发时间', '车次', '终到时间', '终点站']

        for i in railway_info:
            list_data.append([i['from_station_name'], i['start_time'], i['station_train_code'],
                                i['arrive_time'], i['to_station_name']])
    return {'title':title,'rows':list_data}


# 输出数据
def output(data, export_csv, **kwargs):
    # print to screen
    table_data = PrettyTable(data['title'])
    for i in data['rows']:
        table_data.add_row(i)
    print(table_data)
    if export_csv:
        import csv
        csv_name = 'from_{}_to_{}'.format(kwargs['start_station'],kwargs['end_station'])
        if kwargs['transfer_station'] is not None:
            csv_name += '_tranfer_{}'.format(kwargs['transfer_station'])
        csv_name += '.csv'
        with open(csv_name,'w', encoding='utf8') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(data['title'])
            f_csv.writerows(data['rows'])


def check_station_name(station):
    if station in station_cn_name_dict:
        # 中文站名
        station_cn_name = station
    elif station in station_full_pinyin:
        # 站名全拼
        length = len(station_full_pinyin[station])
        if length > 1:
            _index = 1
            input_str = "请选择站名:\n"
            while(_index <= length):
                input_str += "{}:{}\n".format(_index, station_full_pinyin[station][_index-1])
                _index = _index + 1
            ans = int(input(input_str)) - 1
            station_cn_name = station_full_pinyin[station][ans]
        else:
            station_cn_name = station_full_pinyin[station][0]

    else:
        # 站名简拼
        length = len(station_simple_pinyin[station])
        if length > 1:
            _index = 1
            input_str = "请选择站名:\n"
            while(_index <= length):
                input_str += "{}:{}\n".format(_index, station_simple_pinyin[station][_index-1])
                _index = _index + 1
            ans = int(input(input_str)) - 1
            station_cn_name = station_simple_pinyin[station][ans]
        else:
            station_cn_name = station_simple_pinyin[station][0]
    print ("已选择火车站：{}\n".format(station_cn_name))
    return station_cn_name


def get_station_info_list(cfg):
    station_url = cfg.get('config','url_base') + '/resources/js/framework/station_name.js'
    station_vars = connection.request_server(station_url, 'get', 'text')
    station_str = station_vars[21:-2]
    _list = station_str.split('@')
    return _list


def get_railway_info(start_station, end_station,cfg):
    query_uri = cfg.get('config','url_base') + '/lcxxcx/query?purpose_codes=ADULT&queryDate={}&from_station={}&to_station={}'\
        .format(time.strftime('%Y-%m-%d', time.localtime(time.time()+86400)), start_station, end_station)
    return connection.request_server(query_uri)

if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read('config.ini')
    station_list = get_station_info_list(cfg)
    station_cn_name_dict = {} # dict(i.split('|')[1:3] for i in station_list)
    station_full_pinyin = {}
    station_simple_pinyin = {}
    for i in station_list:
        j = i.split('|')
        station_cn_name_dict[j[1]] = j[2]
        if j[3] in station_full_pinyin:
            station_full_pinyin[j[3]].append(j[1])
        else:
            station_full_pinyin[j[3]] = [j[1]]

        if j[4] in station_simple_pinyin:
            station_simple_pinyin[j[4]].append(j[1])
        else:
            station_simple_pinyin[j[4]] = [j[1]]

    query(cfg)
