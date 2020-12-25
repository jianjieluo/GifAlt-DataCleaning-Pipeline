import csv
import json
import argparse
import os

CAP_MAX_NUM = 2

def dump_json(data, path):
    print('Dump json to %s...' % path)
    with open(path, 'w') as f:
        json.dump(data, f)

def load_url2cap(stage, check_url):
    if check_url:
        with open('txt/exist_url.txt', 'r', encoding='utf-8') as f:
            exist_urls = set([l.strip() for l in f])

    csv_path = 'result/gif_alt_info_clean_{}.csv'.format(stage)
    reader = csv.DictReader(open(csv_path, 'r'), delimiter='\t')
    url2cap = {}
    for row in reader:
        gid = row['gid']
        uid = row['uid']
        gifUrl = row['gifUrl']
        title = row['title'].strip()
        alt = row['alt'].strip()

        if check_url:
            if gifUrl not in exist_urls:
                continue

        if gifUrl not in url2cap:
            url2cap[gifUrl] = set()
        
        if title != 'none' and len(title) > 0:
            url2cap[gifUrl].add(title)
        if alt != 'none' and len(alt) > 0:
            url2cap[gifUrl].add(alt)
    
    res = {k:list(v) for k,v in url2cap.items()}

    return res


def pre_release_statistics(stage, check_url):
    url2caps = load_url2cap(stage, check_url)
    print('Valid gifs num: ', len(url2caps))

    result = {}
    for url, caps in url2caps.items():
        for cap in caps:
            if cap not in result:
                result[cap] = set()
            result[cap].add(url)
    cap2urls = {k:list(v) for k,v in result.items()}

    new_url2caps = {}
    for cap, urls in cap2urls.items():
        urls_count = [(url, len(url2caps[url])) for url in urls]
        selected = sorted(urls_count, key=lambda x: x[1])[:CAP_MAX_NUM]
        selected_urls = [x[0] for x in selected]
        for u in selected_urls:
            if u not in new_url2caps:
                new_url2caps[u] = set()
            new_url2caps[u].add(cap)
    new_url2caps = {k:list(v) for k,v in new_url2caps.items()}

    print('CAP_MAX_NUM = %d' % CAP_MAX_NUM)
    print('Result gifs num: ', len(new_url2caps))

    # Calculate the pairs num
    count = 0
    valid_captions = []
    for _, caps in new_url2caps.items():
        count += len(caps)
        valid_captions += caps
        
    print('Result pairs num: ', count)

    return valid_captions, new_url2caps

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', type=str, default=None)
    parser.add_argument('--check_url', action="store_true")
    parser.add_argument('--dump', type=str, default=None)

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    res_dir = 'result/result_analysis/stage_{}'.format(args.stage)
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    valid_captions, new_url2caps = pre_release_statistics(args.stage, args.check_url)

    valid_captions_set = sorted(set(valid_captions))
    with open(os.path.join(res_dir, 'valid_corpus.txt'), 'w') as f:
        for sent in valid_captions_set:
            f.write(sent + '\n')

    new_cap2urls = {}
    for url, caps in new_url2caps.items():
        for cap in caps:
            if cap not in new_cap2urls:
                new_cap2urls[cap] = set()
            new_cap2urls[cap].add(url)
    new_cap2urls = {k:list(v) for k,v in new_cap2urls.items()}
    dump_json(new_cap2urls, os.path.join(res_dir, 'valid_caps2urls.json'))
