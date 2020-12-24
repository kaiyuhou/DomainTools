import requests
from domain_tool_comment import *
import re

# get top level domain price from tld-list.com
# https://tld-list.com/tld/af

def get_price(suffic):
    domain = 'https://tld-list.com/tld/' + suffic

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "origin": "https://tld-list.com",
        "referer": domain,
    }

    resp = requests.get(domain, headers=headers).text
    ans = re.search(r'registration prices from \$([0-9\.]*?) to \$([0-9\.]*?) offered', resp)
    if ans:
        return ans.group(1), ans.group(2)
    else:
        return 0, 0


def update_price():
    top_level_domain_name_suffix_list = get_top_level_domain_name_suffix()
    suffix_array = [x.split('=')[0] for x in top_level_domain_name_suffix_list]

    for i, suffix in enumerate(suffix_array):
        low, high = get_price(suffix)
        print(f'{suffix} {low} {high}')
        top_level_domain_name_suffix_list[i] = top_level_domain_name_suffix_list[i].strip() + str(low) + '='

    with open('top_level_domain_name_suffix_with_price', 'w') as f:
        for line in top_level_domain_name_suffix_list:
            f.write(line.strip() + '\n')


def set_price_to_file(filename):
    domain_list = []
    with open(filename, 'r') as f:
        for line in f:
            if line and line.strip():
                domain_list.append(line.strip())

    top_level_domain_name_suffix_list = get_top_level_domain_name_suffix()
    # eg: ['com', 'org', ...]
    suffix_array = [x.split('=')[0] for x in top_level_domain_name_suffix_list]
    # eg: [['com', 'whois.verisign-grs.com', 'No match for', '121'], ...]
    par_list = [x.split('=')[:-1] for x in top_level_domain_name_suffix_list]

    with open(filename, 'w') as f:
        for domain in domain_list:
            name, suffix = domain.split('.')
            index = suffix_array.index(suffix)
            price = par_list[index][3]
            f.write(f'{domain}\t{price}\n')


def sort_success():
    domain_set = set()
    with open('success.txt', 'r') as f:
        for line in f:
            if line and line.strip():
                domain_set.add(line.strip())
    domain_list = list(domain_set)
    domain_list.sort()
    with open('success.txt', 'w') as f:
        for domain in domain_list:
            f.write(f'{domain}\n')


if __name__ == '__main__':
    # update_price()
    # set_price_to_file('data数据库/所有单字域名-2020-11-29.txt')
    # print(get_reginfomation('csy', 'sx=whois.sx=o match for='.split('=')))
    sort_success()
