
import urllib.parse

def urldecode(params):
    params = urllib.parse.unquote(params)
    rets = dict()
    for param in params.split("&"):
        key = param.split('=')[0]
        value = param.split('=')[-1]
        rets.update({key: value})
    return rets
