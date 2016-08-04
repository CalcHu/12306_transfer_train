import requests


def request_server(url, method='get', res_type='json', **kwargs):
    requests.packages.urllib3.disable_warnings()
    if method == 'post':
        r = requests.post(url, data=kwargs, verify=False)
    elif method == 'get':
        r = requests.get(url, params=kwargs, verify=False)
    else:
        print('param_error')
    if res_type == 'json':
        res = r.json()
    elif res_type == 'text':
        res = r.text
    else:
        print('param_error')

    return res
