from telethon import TelegramClient, events
import re
import time
import json

API_ID = 27101904
API_HASH = "770feb4049c8763f3946bb1aa2e54a86"
FORWARD_CHAT_ID = -1002741490869

MARKED_FILE = "marked_users.json"

# 白名单关键词（命中就直接转发）
WHITE_KEYWORDS = ["入金金额", "银行卡号后四位"]  # 你自己改

# 关键词
FILTER_KEYWORDS = ["精聊", "刷单", "大区", "泰铢", "仲裁", "卡主姓名", "入金金额", "香港", "股票", "换汇", "公检法", "通道", "源头", "进算", "拖算", "滲透", "哈萨克", "无视", "尼日"]
FILTER_REGEXES = [r".*支付.*群", r".*换汇.*", r".*博彩.*"]
COUNTRIES = [
    "阿富汗","阿尔巴尼亚","阿尔及利亚","安道尔","安哥拉","安提瓜和巴布达","阿根廷","亚美尼亚","澳大利亚","奥地利",
    "阿塞拜疆","巴哈马","巴林","孟加拉国","巴巴多斯","白俄罗斯","比利时","伯利兹","贝宁","不丹",
    "玻利维亚","波斯尼亚和黑塞哥维那","博茨瓦纳","巴西","文莱","保加利亚","布基纳法索","布隆迪","柬埔寨","喀麦隆",
    "加拿大","佛得角","中非共和国","乍得","智利","哥伦比亚","科摩罗","刚果",
    "库克群岛","哥斯达黎加","克罗地亚","古巴","塞浦路斯","捷克","丹麦","吉布提","多米尼加","多米尼加共和国",
    "厄瓜多尔","埃及","萨尔瓦多","赤道几内亚","厄立特里亚","爱沙尼亚","斯威士兰","埃塞俄比亚","斐济","芬兰",
    "法国","加蓬","冈比亚","格鲁吉亚","德国","加纳","希腊","格林纳达","危地马拉","几内亚",
    "几内亚比绍","圭亚那","海地","洪都拉斯","匈牙利","冰岛","印度","印度尼西亚","伊朗","伊拉克",
    "爱尔兰","以色列","意大利","牙买加","日本","约旦","哈萨克斯坦","肯尼亚","基里巴斯","韩国",
    "科威特","吉尔吉斯斯坦","老挝","拉脱维亚","黎巴嫩","莱索托","利比里亚","利比亚","列支敦士登","立陶宛",
    "卢森堡","马达加斯加","马拉维","马来西亚","马尔代夫","马里","马耳他","马绍尔群岛","毛里塔尼亚","毛里求斯",
    "墨西哥","密克罗尼西亚","摩尔多瓦","摩纳哥","蒙古","黑山","摩洛哥","莫桑比克","缅甸","纳米比亚",
    "瑙鲁","尼泊尔","荷兰","新西兰","尼加拉瓜","尼日尔","尼日利亚","北马其顿","挪威","阿曼",
    "巴基斯坦","帕劳","巴拿马","巴布亚新几内亚","巴拉圭","秘鲁","菲律宾","波兰","葡萄牙","卡塔尔",
    "罗马尼亚","俄罗斯","卢旺达","圣基茨和尼维斯","圣卢西亚","圣文森特和格林纳丁斯","萨摩亚","圣马力诺","圣多美和普林西比","沙特阿拉伯",
    "塞内加尔","塞尔维亚","塞舌尔","塞拉利昂","新加坡","斯洛伐克","斯洛文尼亚","所罗门群岛","索马里","南非",
    "南苏丹","西班牙","斯里兰卡","苏丹","苏里南","瑞典","瑞士","叙利亚","塔吉克斯坦","坦桑尼亚",
    "泰国","多哥","汤加","特立尼达和多巴哥","突尼斯","土耳其","土库曼斯坦","图瓦卢","乌干达","乌克兰",
    "阿拉伯联合酋长国","英国","乌拉圭","乌兹别克斯坦","瓦努阿图","梵蒂冈","委内瑞拉","越南","也门",
    "赞比亚","津巴布韦"
]
AD_KEYWORDS = ["买卖", "拉群", "招募", "代理", "广告", "推广", "加群", "扫码", "兼职", "刷信誉"]
AD_PATTERNS = [r"t\.me\/", r"telegram\.me\/", r"tg:\/\/join", r"@[\w_]+", r"https?:\/\/"]

# 新增：屏蔽词
BLOCK_KEYWORDS = ["京东", "淘宝", "天猫", "拼多多", "支付宝", "微信", "Q币", "苏宁", "粉", "能量", "数据", "反扫", "内转港", "跨境", "常规",
                  "全国", "飞机", "键盘", "搞", "资料", "SPA", "慈善", "活跃", "bc", "贷", "司法", "码", "油卡", "实体卡", "联系我", "NFC",
                  "快手", "抖音", "抖币", "油", "华夏", "工商", "农行", "福利", "定制", "话术", "门路", "有效", "园区", "年龄", "拉群",
                  "散户", "境外", "礼品卡", "核销", "ATM", "取现", "柜台", "实物", "闲鱼", "BC", "同行", "自家", "大混料", "平台", "tg",
                  "聚合", "赚钱", "口令", "荷包","团队","个人","招人","机会", "赚米", "风口", "包养", "时时彩", "棋牌", "德州", "游戏",
                   "空降", "色", "教程", "风险", "汇率", "国内", "手机", "滴滴", "香水", "伟哥", "机房", "癌", "高进线", "币安", "出海", "社群",
                  "红包", "广告", "约", "交友", "信用", "会员", "日进", "口嗨", "短信", "正品", "低价", "码车", "卡车", "卡卡", "u", "U", "案底",
                  "直招", "上班", "新闻", "短视频", "进入", "直招", "安全","电子", "电子", "AG", "ag", "小白", "优惠", "真人", "茶", "垫资", "大事件",
                  "农商", "白名单", "奢侈品", "珠宝", "时代", "红红", "海外粉", "一手", "168", "138", "营业", "宵夜", "赛车", "飞艇", "别墅", "澳门"]

# 防抖缓存
debounce_cache = {}
DEBOUNCE_TIME = 20  # 20秒
CACHE_CLEAN_INTERVAL = 3600  # 1小时

client = TelegramClient("userbot_session", API_ID, API_HASH)

def is_white_message(text: str):
    """白名单检测"""
    return any(k in text for k in WHITE_KEYWORDS)
    
def clean_debounce_cache():
    """清理1小时以前的防抖缓存"""
    now = time.time()
    old_keys = [k for k, v in debounce_cache.items() if now - v > CACHE_CLEAN_INTERVAL]
    for k in old_keys:
        debounce_cache.pop(k, None)

def is_ad_message(text: str):
    """广告消息检测"""
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in AD_PATTERNS) or any(k in text for k in AD_KEYWORDS)


def is_blocked_message(text: str):
    """屏蔽词检测"""
    return any(k in text for k in BLOCK_KEYWORDS)


def is_target_message(text: str):
    """关键词检测"""
    return any(k in text for k in FILTER_KEYWORDS + COUNTRIES) or any(re.search(rgx, text) for rgx in FILTER_REGEXES)

async def update_current_groups():
    """启动时获取当前账号所有群组ID，存入 current_group_ids"""
    global current_group_ids
    print("🔄 正在更新当前账号所在群组列表...")
    current_group_ids.clear()
    async for dialog in client.iter_dialogs():
        # 只保留群组和超级群
        if dialog.is_group or dialog.is_channel:
            current_group_ids.add(dialog.id)
    print(f"✅ 已缓存 {len(current_group_ids)} 个群组/频道ID")

@client.on(events.NewMessage)
async def handler(event):
     # 只监听群组和频道，排除私聊
    if not (event.is_group or event.is_channel):
        return

    # 不监听转发目标群组消息，避免循环转发
    if event.chat_id == FORWARD_CHAT_ID:
        return

    if not event.message or not event.message.message:
        return

    text = event.message.message

    # 每次收到消息时清理旧缓存
    clean_debounce_cache()

    # ==== 白名单检测（优先级最高） ====
    if is_white_message(text):
        await forward_message(event, text)
        return
        
    # 如果消息包含屏蔽关键词，就直接跳过转发
    if is_blocked_message(text):
        return

    # 检测关键词
    if is_target_message(text):
        # 这里移除防抖代码，直接转发
        # 如果消息字数超过80个字符，不转发
        if len(text) > 200:
            return

        # === 新增防抖逻辑 ===
        now = time.time()
        msg_key = hash(text)  # 用消息内容做唯一标识

        # 如果该消息在20秒内已转发过，就跳过
        if msg_key in debounce_cache and now - debounce_cache[msg_key] < DEBOUNCE_TIME:
            return
        debounce_cache[msg_key] = now

        await forward_message(event, text)  # 这里要加上


# ======== 加载标记用户 ========
try:
    with open(MARKED_FILE, "r", encoding="utf-8") as f:
        marked_users = json.load(f)
except FileNotFoundError:
    marked_users = {}

def save_marked_users():
    with open(MARKED_FILE, "w", encoding="utf-8") as f:
        json.dump(marked_users, f, ensure_ascii=False, indent=2)

# ======== 私聊命令管理标记用户 ========
@client.on(events.NewMessage(pattern=r'^/mark_id (\d+) (.+)'))
async def mark_user(event):
    if not event.is_private:
        return
    user_id, remark = event.pattern_match.groups()
    marked_users[user_id] = remark
    save_marked_users()
    await event.reply(f"✅ 已标记用户 {user_id} 为：{remark}")

@client.on(events.NewMessage(pattern=r'^/unmark_id (\d+)'))
async def unmark_user(event):
    if not event.is_private:
        return
    user_id = event.pattern_match.group(1)
    if user_id in marked_users:
        del marked_users[user_id]
        save_marked_users()
        await event.reply(f"❌ 已移除标记用户 {user_id}")
    else:
        await event.reply(f"⚠️ 用户 {user_id} 不在标记列表")

@client.on(events.NewMessage(pattern=r'^/list_marked'))
async def list_marked(event):
    if not event.is_private:
        return
    if not marked_users:
        await event.reply("⚠️ 当前没有标记用户")
        return
    text = "📋 标记用户列表：\n"
    for uid, remark in marked_users.items():
        text += f"- {uid} ：{remark}\n"
    await event.reply(text)

# ======== 转发消息时显示标记备注 ========
async def forward_message(event, text):
    """封装转发逻辑，自动显示标记备注"""
    sender = await event.get_sender()
    try:
        sender = await client.get_entity(sender.id)
    except Exception:
        pass

    chat = await event.get_chat()
    chat_title = getattr(chat, "title", "私聊")

    chat_id_str = str(event.chat_id)
    if chat_id_str.startswith("-100"):
        tg_chat_id = chat_id_str[4:]
        chat_link = f"https://t.me/c/{tg_chat_id}"
    else:
        chat_link = f"https://t.me/{chat_title.replace(' ', '')}"

    if hasattr(sender, 'username') and sender.username:
        sender_display = f"{(sender.first_name or '')} [@{sender.username}](https://t.me/{sender.username})".strip()
    elif sender.first_name or sender.last_name:
        sender_display = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
    else:
        sender_display = f"User{sender.id}"

    # ======= 检查标记用户 =======
    remark_text = ""
    if str(sender.id) in marked_users:
        remark_text = f"\n❗️❗️❗️ 注意：{marked_users[str(sender.id)]} ❗️❗️❗️"

    forward_text = f"【[{chat_title}]({chat_link})】\n发信人：{sender_display}\n内容：{text}{remark_text}"
    await client.send_message(FORWARD_CHAT_ID, forward_text, parse_mode='md', link_preview=False)
    
async def main():
    print("✅ 连接成功，开始监听所有群消息...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
