# -*- coding:utf-8 -*-
from template import *

sent = '尊敬的三星级客户，您好！截止2018年07月05日10时22分，您的话费余额为149.36元，当月话费60.00元。本月共有数据流量9GB1023.98MB，已使用0.01MB，剩余9GB1023.97MB;以上消费信息仅供参考，详情以月结账单为准。更多流量优惠套餐戳我http://dx.10086.cn/IVR8611办理。更多信息回复对应序号查询（回复免费）：1.话费账单及积分查询；2.流量套餐使用情况查询；3.其他套餐使用情况查询；4.包月业务查询与退订；5.家庭网、集团网信息查询；6.主资费信息查询。（High享世界杯，点球赢大奖！排名赢vivoNEX手机，即日起微信搜索并专注“10086”官方微信公众号参与，还有2G流量大礼等你来。戳我http://dx.10086.cn/znydh5体验10086智能客服，优质服务无需等待！）【中国移动】'
sent_seg,bi = data_pre_process(sent)
word_d,doc_d = load_dic('dict/word_d.json','dict/doc_d.json')
N = sum(list(word_d.values()))
template = creat_template(sent_seg,bi,word_d=word_d,doc_d=doc_d,N=N)
print(template)
#尊敬的{W0:0-5}，您好！截止2018年07月05日10时22分，您的话费余额为{W1:0-7}，当月话费60.00元。本月共有数据{W2:0-14}，已使用0.01MB，{W3:0-14};以上消费信息仅供参考，详情以月结账单为准。
print(parsed(sent,template))
#{'W0': '三星级客户', 'W1': '149.36元', 'W2': '流量9GB1023.98MB', 'W3': '剩余9GB1023.97MB'}