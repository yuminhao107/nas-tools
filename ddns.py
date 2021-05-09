from requests import get
from time import sleep
import random
import sys
from configparser import ConfigParser

url_pattern = "https://dynamicdns.park-your-domain.com/update?host={host}&domain={domain_name}&password={ddns_password}&ip={ip}"


def get_ip():
    ip = get('https://api.ipify.org').text
    return ip

def update_ip(ip, config):
    url = url_pattern.format(
        host=config['ddns']['host'],
        domain_name=config['ddns']['domain_name'],
        ddns_password=config['ddns']['ddns_password'],
        ip=ip
    )
    print("Updating ddns")
    get(url)
    return

def main():
    if len(sys.argv) < 2:
        print("Script need path to config.ini as argument")
        return

    config = ConfigParser()
    config.read(sys.argv[1], encoding='UTF-8')
    sleep_time=config['ddns']['sleep']

    last_ip=""
    while True:
        sleep(sleep_time)
        try:
            ip = get_ip()
            if ip!=last_ip:
                print('Get new ip {}'.format(ip))
                update_ip(ip, config)
                last_ip=ip
        except:
            print("Error. Try after {} seconds".format(sleep_time))

if __name__=="__main__":
    main()