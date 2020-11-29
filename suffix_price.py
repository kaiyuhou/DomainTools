import requests
from domain_tool_comment import *

# get top level domain price from tld-list.com
# https://tld-list.com/tld/af


def update_price():
    #
    # get_price(suffic)
    pass


if __name__ == '__main__':
    # update_price()

    print(get_reginfomation('csy', ['su', 'whois.tcinet.ru', 'No entries found']))
    print(get_reginfomation('csy', 'sx=whois.sx=o match for='.split('=')))