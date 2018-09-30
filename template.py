'''
生成通用类模板
输入：短信文本
输出：通用类模板
'''
import pandas as pd
import jieba
import math
from collections import Counter
import re
import json


def data_pre_process(sent):
    bi = []
    tr = []
    sent = re.sub('\r*\s*\n*', '', sent)
    sent = re.sub(r'分(.)', r'分 \1', sent)
    sent = re.sub(r'(.)为', r'\1 为', sent)
    sent_seg = ' '.join(jieba.cut(sent)).split()
    for idx, i in enumerate(sent_seg):
        if idx < len(sent_seg) - 1:
            bi.append(i + '|||' + sent_seg[idx + 1])
    return sent_seg, bi


# 统计大量短信文本中1-gram，2-gram词频
def create_data_dict(sents):
    res = []
    doc_d = {}
    bi_list = []
    for sent in sents:
        sent_seg, bi = data_pre_process(sent)
        res += sent_seg + bi
        bi_list += bi
        for i in set(bi):
            doc_d.setdefault(i, 0)
            doc_d[i] += 1
    print('done')
    word_d = Counter(res)
    with open('dict/word_d.json', 'w') as f:
        json.dump(word_d, f)
    with open('dict/doc_d.json', 'w') as f:
        json.dump(doc_d, f)
    return 0


def load_dic(word_d_path, doc_d_path):
    with open(word_d_path) as f:
        word_d = json.load(f)
        N = sum(list(word_d.values()))
    with open(doc_d_path) as f:
        doc_d = json.load(f)
    return word_d, doc_d


def get_idf(w,doc_d,N):
    try:
        idf = math.log10(N / (doc_d[w] + 1))
    except KeyError:
        idf = 1
    return idf


# 就算粘结词的概率
def get_score(bi, word_d, doc_d, N):
    plist = []
    pp = []
    for idx, bi_word in enumerate(bi):
        a, b = bi_word.split('|||')
        try:
            num_AB = word_d[bi_word]
            num_A = word_d[a]
            num_B = word_d[b]
            p_AB = (num_AB / num_B) * (num_AB / num_A)
            p_A_B = (1 - num_AB / num_B) * (1 - num_AB / num_A)
        except:
            p_AB = 1e5
            p_A_B = 1e5
            num_AB = 1e5
        idf = get_idf(bi_word,doc_d,N)
        tfidf = idf * num_AB / N
        pp.append((bi_word, p_AB, p_A_B, tfidf))
        if p_AB > p_A_B:
            if tfidf < 0.000625:
                find = re.search(r'[,。，/；;：:!！“”"您的为是]+', bi_word)
                if not find:
                    plist.append((bi_word, idx))

    return plist


# 生成模板
def creat_template(sent_seg, bi, word_d, doc_d, N):
    plist = get_score(bi, word_d, doc_d, N)
    if plist == []:
        return None
    out = []
    st = plist[0][0]
    ra = []
    for num, t in enumerate(plist):
        if '|||' not in t[0]:
            out.append((t[0], '%s-%s' % (t[1], t[1])))
            ra = []
            try:
                st = plist[num + 1][0]
            except:
                pass
        else:
            ra.append(t[1])
            if num < len(plist) - 1 and t[1] + 1 == plist[num + 1][1]:
                st += plist[num + 1][0].split('|||')[1]
                ra.append(t[1] + 1)
            else:
                start, end = ra[0], ra[-1]
                out.append((st.replace('|||', ''), '%s-%s' % (start, end)))
                ra = []
                try:
                    st = plist[num + 1][0]
                except:
                    pass
    sent2 = [i for i in sent_seg]

    iid = 0

    for i, j in out:
        start, end = map(int, j.split('-'))
        length = len(sent_seg[start]) + len(sent_seg[end + 1])
        for ii in range(start + 1, end + 1):
            length += len(sent_seg[ii])
            sent2[ii] = ''
        sent2[start] = '{W%d:0-%d' % (iid, length)
        sent2[end + 1] = '}'
        iid += 1

    template = ''.join(sent2)
    template = re.sub('{W(\d+):\d+-(\d+)}({W\d+:\d+-\d+})+', r'{W\1:0-10}', template)
    return template


def parsedSliod(s):
    wanted = []
    re_pattern = '{(?P<key_type>.*?)[：:](?P<key_name>.*?)}'
    finds = re.findall(re_pattern, s)

    if finds:
        for find in finds:
            wanted.append(find[0])

        # return {'key': finds.group('key_type'), 'min_key_len': finds.group('min_key_len'), 'max_key_len': finds.group('max_key_len')}
    else:
        print('illeagal key ')
    return wanted


def parsed(text, t):
    keys = parsedSliod(t)

    t = re.sub('{(?P<key_type>.*?)[：:](?P<min_key_len>.*?)}', '', t)

    text = text.replace(' ', '')
    values = []
    flag = True
    i = 0
    j = 0
    value_s_idx = -1
    while i < len(text) and j < len(t):
        if text[i] == t[j]:
            if flag == False:
                values.append(text[value_s_idx:i])
                flag = True
            i += 1
            j += 1
        else:
            if t[j] == '&':
                while t[j] == '&':
                    j += 1
                while text[i] != t[j]:
                    i += 1
            else:
                if flag:
                    value_s_idx = i
                    flag = False
                i += 1
    if i < len(text):
        values.append(text[i:])

    wanted = dict(zip(keys, values))

    return wanted