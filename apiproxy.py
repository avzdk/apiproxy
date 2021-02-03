from flask import Flask, request, Response
import requests
import logging
import configparser

conf = configparser.ConfigParser()
conf.read(['apiproxy.ini','apiproxy_local.ini'])

log = logging.getLogger(__name__)
logging.basicConfig(
    level=conf["LOG"]["level"],
    format="%(levelname)s %(module)s.%(funcName)s %(message)s",
)
log.info(f"Starting service loglevel={conf['LOG']['LEVEL']} ")
log.info(f"Url={conf['TARGET']['url']} ")

def makeRequest(*args, **kwargs):
      
    log.debug(request.get_data())
    resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, conf["TARGET"]["url"]),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        auth=(conf["TARGET"]["user"],conf["TARGET"]["password"]),
        stream=True)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    data=resp.text

    return Response(data, resp.status_code, headers)


app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def apicall(path):
    return makeRequest()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(conf["ENDPOINT"]["port"]), debug=False)