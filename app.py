from flask import Flask, render_template_string, request, jsonify, session
import random
import time
import os
import requests
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'xiaohongshu-pro-secret-key')

# ============ Coze API 配置 ============
COZE_BOT_ID = os.environ.get('COZE_BOT_ID', '')
COZE_API_TOKEN = os.environ.get('COZE_API_TOKEN', '')
COZE_API_URL = 'https://api.coze.cn/open_api/v2/chat'

# ============ 爆款评分系统 ============
def calculate_score(content, title):
    """计算文案爆款潜力分数"""
    score = 60  # 基础分
    factors = []
    
    # 1. 标题长度（15-25字最佳）
    title_len = len(title)
    if 15 <= title_len <= 25:
        score += 10
        factors.append("✅ 标题长度适中")
    elif title_len < 10:
        score -= 5
        factors.append("⚠️ 标题过短")
    
    # 2. 是否有emoji
    emoji_count = content.count('🌟') + content.count('✨') + content.count('💕') + content.count('🔥') + content.count('💖')
    if 3 <= emoji_count <= 6:
        score += 8
        factors.append("✅ emoji数量合适")
    elif emoji_count > 8:
        score -= 3
        factors.append("⚠️ emoji过多")
    
    # 3. 是否有hashtag
    if '#' in content:
        hashtag_count = content.count('#')
        if 3 <= hashtag_count <= 6:
            score += 8
            factors.append("✅ 标签数量合适")
    
    # 4. 内容长度（300-800字最佳）
    content_len = len(content)
    if 300 <= content_len <= 800:
        score += 10
        factors.append("✅ 内容长度适中")
    elif content_len < 200:
        score -= 10
        factors.append("⚠️ 内容过短")
    
    # 5. 是否有数字（增加可信度）
    if any(c.isdigit() for c in content):
        score += 5
        factors.append("✅ 包含具体数据")
    
    # 6. 是否有互动引导
    interactive_words = ['评论', '点赞', '收藏', '关注', '交流', '问']
    if any(word in content for word in interactive_words):
        score += 7
        factors.append("✅ 有互动引导")
    
    # 7. 是否有真实感受词
    real_words = ['真的', '说实话', '亲测', '用了', '体验', '感受']
    if any(word in content for word in real_words):
        score += 5
        factors.append("✅ 真实感强")
    
    # 8. 是否有小缺点（增加真实度）
    drawback_words = ['缺点', '不足', '瑕疵', '问题', '但是', '不过']
    if any(word in content for word in drawback_words):
        score += 8
        factors.append("✅ 有真实缺点")
    
    score = max(0, min(100, score))
    
    # 评级
    if score >= 85:
        level = "🔥 爆款潜力"
        color = "#ff4757"
    elif score >= 70:
        level = "⭐ 优秀"
        color = "#ffa502"
    elif score >= 60:
        level = "✅ 良好"
        color = "#2ed573"
    else:
        level = "⚠️ 需要优化"
        color = "#747d8c"
    
    return {
        'score': score,
        'level': level,
        'color': color,
        'factors': factors,
        'suggestions': get_suggestions(score, factors)
    }

def get_suggestions(score, factors):
    """获取优化建议"""
    suggestions = []
    
    if score < 85:
        if "⚠️ 标题过短" in str(factors):
            suggestions.append("标题建议15-25字，增加吸引力")
        if "⚠️ 内容过短" in str(factors):
            suggestions.append("内容建议300-800字，详细描述体验")
        if "⚠️ emoji过多" in str(factors):
            suggestions.append("emoji建议3-6个，过多会显得杂乱")
        if not any("✅ 有真实缺点" in f for f in factors):
            suggestions.append("添加一个小缺点，增加真实感")
        if not any("✅ 有互动引导" in f for f in factors):
            suggestions.append("结尾添加互动引导，如'有用过的姐妹吗？'")
    
    return suggestions

# ============ 热门标签推荐 ============
HOT_TAGS = {
    '通用': ['#好物分享', '#种草', '#测评', '#推荐', '#宝藏', '#亲测好用', '#不踩雷', '#闭眼入'],
    '美食': ['#美食分享', '#探店', '#一人食', '#自制美食', '#美食测评', '#吃货日常', '#深夜食堂'],
    '水果': ['#水果自由', '#应季水果', '#新鲜水果', '#水果推荐', '#每日水果', '#水果测评'],
    '美妆': ['#美妆分享', '#护肤好物', '#化妆教程', '#口红试色', '#skincare', '#变美秘籍'],
    '数码': ['#数码好物', '#科技改变生活', '#数码测评', '#EDC', '#生产力工具', '#数码控'],
    '日用': ['#生活好物', '#居家必备', '#提升幸福感的小物', '#仪式感', '#租房好物', '#收纳整理']
}

def get_recommended_tags(category, product_name):
    """获取推荐标签"""
    tags = HOT_TAGS.get('通用', [])
    
    category_map = {
        'food': '美食',
        'fruit': '水果',
        'beauty': '美妆',
        'digital': '数码',
        'daily': '日用'
    }
    
    cat_name = category_map.get(category, '')
    if cat_name and cat_name in HOT_TAGS:
        tags = HOT_TAGS[cat_name] + tags[:4]
    
    # 添加产品相关标签
    tags.append(f"#{product_name}")
    
    return tags[:8]  # 返回前8个标签

# [保留原有的 PRODUCT_DATA, TITLES, OPENINGS 等代码...]
# ============ 增强版产品知识库 ============
PRODUCT_DATA = {
    "categories": {
        "food": {
            "name": "美食",
            "keywords": ["餐厅", "火锅", "烧烤", "甜品", "奶茶", "咖啡", "小吃", "日料", "韩料", "粤菜", "川菜", "自助餐", "外卖", "早餐", "夜宵"],
            "angles": ["味道口感", "环境氛围", "服务态度", "性价比", "食材新鲜", "上菜速度", "特色菜品"],
            "emotions": ["幸福感爆棚", "太满足了", "治愈系", "回味无穷", "口水直流", "惊艳味蕾", "欲罢不能"],
            "scenes": ["约会聚餐", "闺蜜小聚", "家庭聚餐", "一人食", "工作餐", "周末探店", "深夜食堂"]
        },
        "fruit": {
            "name": "水果",
            "keywords": ["草莓", "榴莲", "芒果", "葡萄", "西瓜", "车厘子", "橙子", "苹果", "桃子", "蓝莓", "火龙果", "哈密瓜", "菠萝", "香蕉"],
            "angles": ["甜度口感", "新鲜程度", "挑选技巧", "保存方法", "营养价值", "产地来源", "季节时令"],
            "emotions": ["甜到心里", "汁水四溢", "清新爽口", "满满的维C", "大自然的味道", "甜蜜暴击", "一口爆汁"],
            "scenes": ["早餐搭配", "下午茶", "健身代餐", "宝宝辅食", "送礼佳品", "追剧零食", "餐后水果"]
        },
        "daily": {
            "name": "日用品",
            "keywords": ["纸巾", "洗衣液", "洗发水", "沐浴露", "牙膏", "洗面奶", "面膜", "护肤品", "收纳", "清洁", "香薰", "四件套", "毛巾", "拖鞋"],
            "angles": ["使用效果", "性价比", "香味", "包装设计", "成分安全", "耐用程度", "使用便捷"],
            "emotions": ["生活小确幸", "治愈强迫症", "提升幸福感", "相见恨晚", "居家必备", "精致生活", "品质感满满"],
            "scenes": ["租房改造", "新家布置", "日常补货", "囤货清单", "搬家必备", "宿舍好物", "办公室必备"]
        },
        "digital": {
            "name": "数码",
            "keywords": ["耳机", "手机", "充电宝", "数据线", "键盘", "鼠标", "支架", "音箱", "相机", "配件", "平板", "智能手表", "充电器"],
            "angles": ["音质/性能", "外观设计", "续航能力", "使用体验", "兼容性", "做工质量", "便携程度"],
            "emotions": ["科技感爆棚", "效率神器", "爱不释手", "真香警告", "生产力工具", "数码控必入", "幸福感提升"],
            "scenes": ["通勤路上", "办公室", "居家办公", "学习备考", "运动健身", "旅行出差", "游戏娱乐"]
        },
        "beauty": {
            "name": "美妆护肤",
            "keywords": ["口红", "粉底", "眼影", "精华", "面霜", "面膜", "防晒", "卸妆", "香水", "化妆刷", "眉笔", "睫毛膏", "护肤套装"],
            "angles": ["妆效/肤感", "持久度", "色号/香味", "性价比", "成分分析", "适合肤质", "使用手法"],
            "emotions": ["颜值爆表", "素颜自信", "精致女孩", "被夸爆了", "约会神器", "自拍必备", "变美秘籍"],
            "scenes": ["日常通勤", "约会聚会", "重要场合", "旅行出游", "居家护肤", "面试妆容", "拍照上镜"]
        }
    }
}

# [保留原有的生成函数...]
TITLES = {
    "suspense": [
        "挖到宝了！这个{product}真的绝了",
        "被问爆的{product}，今天终于分享",
        "还有人不知道这个{product}吗？",
        "后悔没早买！{product}太香了",
        "发现了{product}的秘密，太惊艳了",
        "{product}｜这次真的挖到宝了",
        "藏不住了！这个{product}必须分享",
        "意外发现的{product}，结果..."
    ],
    "number": [
        "{product}的5个隐藏亮点，90%的人不知道",
        "用了30天，总结出{product}的优缺点",
        "关于{product}，新手必看的3个坑",
        "{product}使用报告｜7天真实体验",
        "对比了10款，为什么选{product}",
        "{product}值不值得买？看完这5点再决定"
    ],
    "comparison": [
        "{product}平替找到了！省下一大笔",
        "网红{product}真实测评，不吹不黑",
        "专柜vs平价，{product}真的值得吗？",
        "{product}对比测评｜哪款更值得入",
        "为什么我选择{product}而不是XX"
    ],
    "pain_point": [
        "{product}困扰多年，终于找到解决方案",
        "如果你也有XX问题，一定要试试{product}",
        "告别XX，从{product}开始",
        "拯救XX的{product}，亲测有效"
    ],
    "story": [
        "从嫌弃到真香，{product}改变了我的想法",
        "关于{product}，我有一个故事要讲",
        "朋友推荐的{product}，结果...",
        "为了{product}，我特意..."
    ]
}

OPENINGS = [
    "最近{scene}时发现这个{product}，{emotion}！",
    "说实话，一开始对{product}没抱期待，结果{emotion}！",
    "{scene}必备！今天必须分享这个{product}",
    "被{scene}的姐妹安利了{product}，{emotion}！",
    "用了一周{product}，忍不住来分享真实感受",
    "最近{scene}都在用{product}，真的{emotion}！",
    "跟风入的{product}，没想到这么{emotion}",
    "关于{product}，我有很多话想说...",
    "今天{scene}，带上了心爱的{product}",
    "终于找到适合{scene}的{product}了！"
]

BODY_TEMPLATES = {
    "味道口感": [
        "先说{product}的味道，入口{desc1}，{desc2}。{desc3}，回味{desc4}。",
        "{product}的口感{desc1}，{desc2}。每一口都能感受到{desc3}，{desc4}。",
        "尝过{product}之后，{desc1}。{desc2}，{desc3}，真的{desc4}！"
    ],
    "环境氛围": [
        "{product}的环境{desc1}，{desc2}。{desc3}，非常适合{desc4}。",
        "一进门就被{product}的氛围吸引了，{desc1}。{desc2}，{desc3}。",
        "{product}的装修{desc1}，{desc2}。{desc3}，{desc4}。"
    ],
    "甜度口感": [
        "{product}的甜度{desc1}，{desc2}。{desc3}，不是那种{desc4}。",
        "第一口{product}就{desc1}，{desc2}。{desc3}，{desc4}。",
        "{product}的口感{desc1}，{desc2}。{desc3}，真的{desc4}！"
    ],
    "新鲜程度": [
        "{product}的新鲜度{desc1}，{desc2}。{desc3}，{desc4}。",
        "拿到{product}的第一感觉就是{desc1}。{desc2}，{desc3}，{desc4}。",
        "这次买的{product}真的{desc1}！{desc2}，{desc3}。"
    ],
    "使用效果": [
        "用了{product}之后，{desc1}。{desc2}，{desc3}，{desc4}。",
        "{product}的效果{desc1}，{desc2}。坚持使用一段时间后，{desc3}。",
        "入手{product}已经{time}了，{desc1}。{desc2}，{desc3}。"
    ],
    "性价比": [
        "{product}的性价比真的{desc1}，{desc2}。{desc3}，{desc4}。",
        "对比了很多款，{product}{desc1}。{desc2}，{desc3}。",
        "这个价格能买到{product}真的{desc1}！{desc2}，{desc3}。"
    ],
    "音质/性能": [
        "{product}的{feature}{desc1}，{desc2}。{desc3}，{desc4}。",
        "用{product}{scene}的时候，{desc1}。{desc2}，{desc3}。",
        "{product}的{feature}表现{desc1}，{desc2}。{desc3}，{desc4}。"
    ],
    "妆效/肤感": [
        "{product}上脸{desc1}，{desc2}。{desc3}，{desc4}。",
        "用了{product}之后，{desc1}。{desc2}，{desc3}，{desc4}。",
        "{product}的妆效{desc1}，{desc2}。{desc3}，真的{desc4}！"
    ]
}

DRAWBACKS = [
    "当然也有小缺点，{issue}，不过{solution}。",
    "如果非要挑毛病的话，{issue}，但{solution}。",
    "{issue}可能是个小问题，不过{solution}。",
    "要说不足的话，{issue}，但{solution}。"
]

CLOSINGS = [
    "总之{product}真的{conclusion}！{cta}",
    "{summary}，{product}真的值得一试！{cta}",
    "用了一段时间{product}，{conclusion}。{cta}",
    "如果你也在找{product_type}，真的推荐试试这款！{cta}",
    "{product}已经成为我的{scene}必备了，{cta}"
]

HASHTAGS_POOL = [
    "#好物分享", "#种草", "#测评", "#推荐", "#宝藏", 
    "#亲测好用", "#不踩雷", "#闭眼入", "#真实分享", "#自用推荐",
    "#生活好物", "#提升幸福感", "#精致生活", "#日常分享", "#必入"
]

DESC_WORDS = {
    "味道": ["层次丰富", "很正", "浓郁", "清新", "地道", "独特", "惊艳", "上头"],
    "口感": ["细腻", "顺滑", "Q弹", "软糯", "酥脆", "绵密", "清爽", "醇厚"],
    "甜度": ["刚刚好", "自然清甜", "不腻", "适中", "恰到好处", "甜蜜适中"],
    "新鲜": ["没得说", "超高", "肉眼可见", "一流", "在线", "完美"],
    "效果": ["超预期", "惊喜", "明显", "惊艳", "显著", "令人满意"],
    "性价比": ["很高", "很划算", "超值", "无敌", "没谁了", "良心"],
    "音质": ["出色", "惊艳", "沉浸感强", "清晰", "震撼", "细腻"],
    "妆效": ["自然", "服帖", "持久", "精致", "高级", "清透"]
}

TIME_WORDS = ["一周", "半个月", "一个月", "两个月", "一段时间"]
ISSUES = [
    "物流稍微有点慢", "包装可以更精致", "说明书不够详细", 
    "价格稍微贵了点", "颜色选择不够多", "配送时间有点长"
]
SOLUTIONS = [
    "瑕不掩瑜，整体还是很满意", "不影响使用体验", "可以接受", 
    "这点小问题挡不住它的好", "性价比已经很高了"
]
CONCLUSIONS = [
    "超级推荐", "值得一试", "没踩雷", "闭眼入", "真香", "超出预期"
]
CTAS = [
    "姐妹们冲鸭！", "有需要的姐妹可以看看！", "喜欢记得点赞收藏！",
    "有问题评论区见！", "用过的姐妹来交流一下！"
]

def identify_product(product_name):
    product_lower = product_name.lower()
    best_match = 'daily'
    best_confidence = 0
    
    for cat_key, cat_data in PRODUCT_DATA["categories"].items():
        for keyword in cat_data["keywords"]:
            if keyword in product_lower:
                confidence = len(keyword) / len(product_name)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = cat_key
    
    return best_match

def generate_title(product_name, category):
    cat_data = PRODUCT_DATA["categories"].get(category, PRODUCT_DATA["categories"]["daily"])
    title_type = random.choice(list(TITLES.keys()))
    title_template = random.choice(TITLES[title_type])
    title = title_template.format(product=product_name)
    
    if random.random() > 0.5:
        emojis = ['✨', '💕', '🔥', '🌟', '💖', '🎉', '💯']
        title = random.choice(emojis) + " " + title
    
    return title

def generate_opening(product_name, category):
    cat_data = PRODUCT_DATA["categories"].get(category, PRODUCT_DATA["categories"]["daily"])
    template = random.choice(OPENINGS)
    scene = random.choice(cat_data.get("scenes", ["日常使用"]))
    emotion = random.choice(cat_data["emotions"])
    return template.format(product=product_name, scene=scene, emotion=emotion)

def generate_body_paragraph(product_name, category, angle):
    cat_data = PRODUCT_DATA["categories"].get(category, PRODUCT_DATA["categories"]["daily"])
    
    if angle == "味道口感":
        desc1 = random.choice(DESC_WORDS["味道"])
        desc2 = random.choice(DESC_WORDS["口感"])
        desc3 = random.choice(["每一口都是享受", "吃得出用心", "食材很讲究"])
        desc4 = random.choice(["无穷", "很久", "让人难忘"])
        return f"先说{product_name}的味道，入口{desc1}，{desc2}。{desc3}，回味{desc4}。"
    
    elif angle == "环境氛围":
        desc1 = random.choice(["很舒适", "氛围感拉满", "特别温馨"])
        desc2 = random.choice(["装修很有格调", "灯光恰到好处", "音乐也很好听"])
        desc3 = random.choice(["细节处处用心", "拍照超级出片", "适合待一下午"])
        desc4 = random.choice(["约会", "闺蜜聚会", "一个人放松", "拍照打卡"])
        return f"{product_name}的环境{desc1}，{desc2}。{desc3}，非常适合{desc4}。"
    
    elif angle == "甜度口感":
        desc1 = random.choice(DESC_WORDS["甜度"])
        desc2 = random.choice(DESC_WORDS["口感"])
        desc3 = random.choice(["汁水很足", "果肉饱满", "口感细腻"])
        desc4 = random.choice(["齁甜", "腻", "人工糖精味"])
        return f"{product_name}的甜度{desc1}，{desc2}。{desc3}，不是那种{desc4}。"
    
    elif angle == "新鲜程度":
        desc1 = random.choice(DESC_WORDS["新鲜"])
        desc2 = random.choice(["一看就知道品质好", "能感受到用心挑选", "没有任何瑕疵"])
        desc3 = random.choice(["保存得当", "包装很用心", "配送很快"])
        desc4 = random.choice(["吃起来特别放心", "品质有保证", "值得信赖"])
        return f"{product_name}的新鲜度{desc1}，{desc2}。{desc3}，{desc4}。"
    
    elif angle == "使用效果":
        time = random.choice(TIME_WORDS)
        desc1 = random.choice(DESC_WORDS["效果"])
        desc2 = random.choice(["效果肉眼可见", "体验感拉满", "真的好用"])
        desc3 = random.choice(["已经回购了", "推荐给朋友了", "离不开它了"])
        return f"用了{time}{product_name}，效果{desc1}。{desc2}，{desc3}。"
    
    elif angle == "性价比":
        desc1 = random.choice(DESC_WORDS["性价比"])
        desc2 = random.choice(["这个价位很难找到更好的", "同等价位里算顶级的", "买到就是赚到"])
        desc3 = random.choice(["学生党也能入手", "打工人无压力", "值得投资"])
        return f"{product_name}的性价比真的{desc1}，{desc2}。{desc3}。"
    
    elif angle == "音质/性能":
        feature = random.choice(["音质", "性能", "续航"])
        desc1 = random.choice(DESC_WORDS["音质"] if feature == "音质" else DESC_WORDS["效果"])
        desc2 = random.choice(["细节表现到位", "超出预期", "同价位无敌"])
        desc3 = random.choice(["日常使用完全够用", "专业需求也能满足", "体验感很好"])
        desc4 = random.choice(["强烈推荐", "入手不亏", "真的香"])
        scene = random.choice(cat_data.get("scenes", ["使用"]))
        return f"{product_name}的{feature}{desc1}，{desc2}。{scene}的时候{desc3}，{desc4}。"
    
    elif angle == "妆效/肤感":
        desc1 = random.choice(DESC_WORDS["妆效"])
        desc2 = random.choice(["不卡粉不假面", "肤色提亮明显", "质地很细腻"])
        desc3 = random.choice(["持妆一整天", "越夜越美丽", "定妆效果很好"])
        desc4 = random.choice(["爱了爱了", "想囤货", "会回购"])
        return f"{product_name}上脸{desc1}，{desc2}。{desc3}，真的{desc4}！"
    
    else:
        return f"{angle}方面，{product_name}表现{random.choice(['出色', '优秀', '令人满意'])}。{random.choice(['在同类型产品里有竞争力', '值得推荐', '超出预期'])}。"

def generate_drawback():
    template = random.choice(DRAWBACKS)
    issue = random.choice(ISSUES)
    solution = random.choice(SOLUTIONS)
    return template.format(issue=issue, solution=solution)

def generate_closing(product_name, category):
    cat_data = PRODUCT_DATA["categories"].get(category, PRODUCT_DATA["categories"]["daily"])
    template = random.choice(CLOSINGS)
    conclusion = random.choice(CONCLUSIONS)
    cta = random.choice(CTAS)
    scene = random.choice(cat_data.get("scenes", ["日常"]))
    product_type = cat_data["name"]
    summary = random.choice(["用了一段时间", "体验过后", "对比了很多款"])
    return template.format(
        product=product_name,
        conclusion=conclusion,
        cta=cta,
        summary=summary,
        product_type=product_type,
        scene=scene
    )

def generate_content_v2(product_name, style_name='authentic'):
    """增强版文案生成"""
    category = identify_product(product_name)
    cat_data = PRODUCT_DATA["categories"].get(category, PRODUCT_DATA["categories"]["daily"])
    
    # 生成标题
    title = generate_title(product_name, category)
    
    # 生成开头
    opening = generate_opening(product_name, category)
    
    # 生成正文（3-4个段落）
    paragraphs = [opening]
    
    # 随机选择3-4个角度
    angles = random.sample(cat_data["angles"], min(random.randint(3, 4), len(cat_data["angles"])))
    for angle in angles:
        paragraphs.append(generate_body_paragraph(product_name, category, angle))
    
    # 偶尔添加小缺点（60%概率）
    if random.random() > 0.4:
        paragraphs.append(generate_drawback())
    
    # 生成结尾
    closing = generate_closing(product_name, category)
    paragraphs.append(closing)
    
    # 组合正文
    emoji_count = random.randint(3, 5)
    emoji_pool = ['✨', '💕', '🥰', '🌟', '💖', '👀', '🔥', '🎉', '💯', '👍', '🌈', '💫', '⭐', '❤️']
    emojis = ' '.join(random.sample(emoji_pool, emoji_count))
    
    content = f"{emojis}\n\n" + "\n\n".join(paragraphs)
    
    # 生成hashtag
    base_hashtags = [f"#{product_name}", f"#{cat_data['name']}分享", "#好物推荐", "#真实测评"]
    extra_hashtags = random.sample(HASHTAGS_POOL, 2)
    hashtags = ' '.join(base_hashtags + extra_hashtags)
    
    full_content = f"【{title}】\n\n{content}\n\n{hashtags}"
    
    # 计算爆款评分
    score_data = calculate_score(full_content, title)
    
    # 获取推荐标签
    recommended_tags = get_recommended_tags(category, product_name)
    
    return {
        'title': title,
        'content': full_content,
        'category': category,
        'style': style_name,
        'product': product_name,
        'score': score_data,
        'recommended_tags': recommended_tags,
        'source': 'local'
    }

# ============ HTML模板（全新升级版） ============
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书文案生成器 Pro v4.0 - 爆款文案一键生成</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        
        /* Header */
        header { 
            text-align: center; 
            margin-bottom: 30px; 
            color: white;
            padding: 20px 0;
        }
        header h1 { 
            font-size: 2.2rem; 
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .subtitle { 
            font-size: 1rem; 
            opacity: 0.9;
            margin-bottom: 20px;
        }
        
        /* Stats Bar */
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        .stat-item {
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        .stat-number { font-weight: bold; font-size: 1.2rem; }
        
        /* Input Section */
        .input-section {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }
        .form-group { margin-bottom: 20px; }
        .form-group label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 600; 
            color: #555;
            font-size: 0.95rem;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid #e8e8e8;
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102,126,234,0.1);
        }
        .form-row { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 20px; 
        }
        @media (max-width: 600px) { 
            .form-row { grid-template-columns: 1fr; } 
            header h1 { font-size: 1.8rem; }
        }
        
        /* Buttons */
        .button-group { 
            display: flex; 
            gap: 15px; 
            margin-top: 25px; 
        }
        .btn-primary, .btn-secondary {
            flex: 1;
            padding: 16px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .btn-primary { 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
            box-shadow: 0 4px 15px rgba(102,126,234,0.4);
        }
        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102,126,234,0.5);
        }
        .btn-secondary { 
            background: linear-gradient(135deg, #f093fb, #f5576c); 
            color: white;
            box-shadow: 0 4px 15px rgba(245,87,108,0.4);
        }
        .btn-secondary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(245,87,108,0.5);
        }
        .btn-primary:disabled, .btn-secondary:disabled { 
            opacity: 0.6; 
            cursor: not-allowed;
            transform: none;
        }
        
        /* Quick Tags */
        .quick-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        .quick-tag {
            padding: 6px 12px;
            background: #f0f0f0;
            border-radius: 15px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
        }
        .quick-tag:hover {
            background: #667eea;
            color: white;
        }
        
        /* Tips Section */
        .tips-section {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
        }
        .tips-section h3 { margin-bottom: 15px; color: #333; }
        .tips-grid { 
            display: grid; 
            grid-template-columns: repeat(2, 1fr); 
            gap: 12px; 
        }
        @media (max-width: 500px) { .tips-grid { grid-template-columns: 1fr; } }
        .tip-card { 
            display: flex; 
            align-items: center; 
            gap: 10px; 
            padding: 12px; 
            background: #f8f9fa; 
            border-radius: 10px; 
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .tip-card:hover {
            background: #e8e8e8;
            transform: translateX(5px);
        }
        .tip-icon { font-size: 1.5rem; }
        
        /* Results Section */
        .results-section {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            display: none;
        }
        .results-section h3 { margin-bottom: 20px; color: #333; }
        
        /* Score Card */
        .score-card {
            background: linear-gradient(135deg, #f5f7fa, #e4e8ec);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 5px solid #667eea;
        }
        .score-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .score-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
        }
        .score-level {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        .score-factors {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }
        .score-factor {
            padding: 5px 10px;
            background: white;
            border-radius: 12px;
            font-size: 0.8rem;
        }
        .score-suggestions {
            background: #fff3cd;
            border-radius: 10px;
            padding: 12px;
            margin-top: 10px;
        }
        .score-suggestions h4 {
            font-size: 0.9rem;
            margin-bottom: 8px;
            color: #856404;
        }
        .score-suggestions ul {
            margin-left: 18px;
            font-size: 0.85rem;
            color: #856404;
        }
        
        /* Result Card */
        .result-card {
            background: #fafafa;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }
        .result-header { 
            display: flex; 
            gap: 10px; 
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .style-badge, .category-badge {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .style-badge { 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
        }
        .category-badge { 
            background: #e8f4f8; 
            color: #2c3e50; 
        }
        .result-content {
            white-space: pre-wrap;
            line-height: 1.8;
            color: #444;
            font-size: 0.95rem;
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        
        /* Recommended Tags */
        .recommended-tags {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e8e8e8;
        }
        .recommended-tags h4 {
            font-size: 0.9rem;
            margin-bottom: 10px;
            color: #555;
        }
        .tag-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .rec-tag {
            padding: 5px 12px;
            background: #e3f2fd;
            color: #1976d2;
            border-radius: 15px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .rec-tag:hover {
            background: #1976d2;
            color: white;
        }
        
        /* Action Buttons */
        .result-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .btn-copy, .btn-regenerate, .btn-share {
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.9rem;
        }
        .btn-copy {
            background: white;
            border: 2px solid #667eea;
            color: #667eea;
        }
        .btn-copy:hover {
            background: #667eea;
            color: white;
        }
        .btn-regenerate {
            background: #f0f0f0;
            border: none;
            color: #555;
        }
        .btn-regenerate:hover {
            background: #e0e0e0;
        }
        
        /* Loading */
        .loading {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        
        /* Footer */
        footer { 
            text-align: center; 
            padding: 30px; 
            color: white; 
            opacity: 0.8;
        }
        
        /* History Section */
        .history-section {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            display: none;
        }
        .history-item {
            padding: 12px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            transition: all 0.2s;
        }
        .history-item:hover {
            background: #f5f5f5;
        }
        .history-title {
            font-weight: 600;
            margin-bottom: 5px;
        }
        .history-meta {
            font-size: 0.8rem;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📝 小红书文案生成器 Pro</h1>
            <p class="subtitle">AI驱动 · 爆款评分 · 智能优化</p>
            <div class="stats-bar">
                <div class="stat-item"><span class="stat-number">5</span> 种风格</div>
                <div class="stat-item"><span class="stat-number">200+</span> 产品库</div>
                <div class="stat-item"><span class="stat-number">100%</span> 原创</div>
            </div>
        </header>

        <main>
            <div class="input-section">
                <div class="form-group">
                    <label for="product">产品名称 *</label>
                    <input type="text" id="product" placeholder="例如：丹东草莓、iPhone 15、海底捞..." required>
                    <div class="quick-tags">
                        <span class="quick-tag" onclick="fillProduct('榴莲')">🥭 榴莲</span>
                        <span class="quick-tag" onclick="fillProduct('面膜')">🧖‍♀️ 面膜</span>
                        <span class="quick-tag" onclick="fillProduct('耳机')">🎧 耳机</span>
                        <span class="quick-tag" onclick="fillProduct('奶茶')">🧋 奶茶</span>
                        <span class="quick-tag" onclick="fillProduct('口红')">💄 口红</span>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="style">文案风格</label>
                        <select id="style">
                            <option value="authentic">真实体验型 - 像朋友聊天</option>
                            <option value="professional">专业测评型 - 数据说话</option>
                            <option value="emotional">情感共鸣型 - 走心温暖</option>
                            <option value="humorous">幽默风趣型 - 轻松搞笑</option>
                            <option value="minimal">极简高级型 - 克制留白</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="keywords">关键词（可选）</label>
                        <input type="text" id="keywords" placeholder="例如：送礼、性价比、学生党">
                    </div>
                </div>

                <div class="button-group">
                    <button id="generateBtn" class="btn-primary">
                        <span>✨ 生成爆款文案</span>
                    </button>
                    <button id="batchBtn" class="btn-secondary">
                        <span>🎲 批量生成3条</span>
                    </button>
                </div>
            </div>

            <div class="tips-section">
                <h3>💡 热门推荐</h3>
                <div class="tips-grid">
                    <div class="tip-card" onclick="fillProduct('丹东草莓')">
                        <span class="tip-icon">🍓</span>
                        <span>丹东草莓 - 冬季爆款</span>
                    </div>
                    <div class="tip-card" onclick="fillProduct('海底捞')">
                        <span class="tip-icon">🍜</span>
                        <span>海底捞 - 聚会首选</span>
                    </div>
                    <div class="tip-card" onclick="fillProduct('收纳盒')">
                        <span class="tip-icon">🏠</span>
                        <span>收纳盒 - 居家必备</span>
                    </div>
                    <div class="tip-card" onclick="fillProduct('蓝牙耳机')">
                        <span class="tip-icon">📱</span>
                        <span>蓝牙耳机 - 数码好物</span>
                    </div>
                </div>
            </div>

            <div id="results" class="results-section">
                <h3>🎯 生成结果</h3>
                <div id="resultsList"></div>
            </div>
        </main>

        <footer>
            <p>Powered by AI · 每次生成都是原创内容 · 爆款潜力智能评分</p>
        </footer>
    </div>

    <script>
        const styleMap = {
            'authentic': '真实体验型', 'professional': '专业测评型',
            'emotional': '情感共鸣型', 'humorous': '幽默风趣型', 'minimal': '极简高级型'
        };
        
        function fillProduct(name) {
            document.getElementById('product').value = name;
        }
        
        async function generateContent(isBatch = false) {
            const product = document.getElementById('product').value.trim();
            const style = document.getElementById('style').value;
            
            if (!product) { alert('请输入产品名称'); return; }
            
            const generateBtn = document.getElementById('generateBtn');
            const batchBtn = document.getElementById('batchBtn');
            generateBtn.disabled = true;
            batchBtn.disabled = true;
            generateBtn.innerHTML = '<span class="loading"></span> 生成中...';
            
            try {
                const endpoint = isBatch ? '/api/batch' : '/api/generate';
                const body = isBatch ? { product, count: 3 } : { product, style };
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                
                const data = await response.json();
                if (data.error) { alert(data.error); return; }
                
                document.getElementById('results').style.display = 'block';
                const resultsList = document.getElementById('resultsList');
                resultsList.innerHTML = '';
                
                const results = isBatch ? data.results : [data];
                
                results.forEach((result) => {
                    // 评分卡片
                    const scoreCard = document.createElement('div');
                    scoreCard.className = 'score-card';
                    scoreCard.innerHTML = `
                        <div class="score-header">
                            <div>
                                <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">爆款潜力评分</div>
                                <div class="score-value" style="color: ${result.score.color};">${result.score.score}</div>
                            </div>
                            <div class="score-level" style="background: ${result.score.color}; color: white;">${result.score.level}</div>
                        </div>
                        <div class="score-factors">
                            ${result.score.factors.map(f => `<span class="score-factor">${f}</span>`).join('')}
                        </div>
                        ${result.score.suggestions.length > 0 ? `
                            <div class="score-suggestions">
                                <h4>💡 优化建议</h4>
                                <ul>${result.score.suggestions.map(s => `<li>${s}</li>`).join('')}</ul>
                            </div>
                        ` : ''}
                    `;
                    resultsList.appendChild(scoreCard);
                    
                    // 文案卡片
                    const card = document.createElement('div');
                    card.className = 'result-card';
                    card.innerHTML = `
                        <div class="result-header">
                            <span class="style-badge">${styleMap[result.style]}</span>
                            <span class="category-badge">${result.category}</span>
                        </div>
                        <pre class="result-content">${result.content}</pre>
                        <div class="recommended-tags">
                            <h4>🏷️ 推荐标签（点击复制）</h4>
                            <div class="tag-list">
                                ${result.recommended_tags.map(tag => `<span class="rec-tag" onclick="copyText(this, '${encodeURIComponent(tag)}')">${tag}</span>`).join('')}
                            </div>
                        </div>
                        <div class="result-actions">
                            <button class="btn-copy" onclick="copyText(this, '${encodeURIComponent(result.content)}')">📋 复制完整文案</button>
                            <button class="btn-regenerate" onclick="fillProduct('${result.product}'); generateContent(false);">🔄 重新生成</button>
                        </div>
                    `;
                    resultsList.appendChild(card);
                });
                
                document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
                
            } catch (error) {
                alert('生成失败，请重试');
            } finally {
                generateBtn.disabled = false;
                batchBtn.disabled = false;
                generateBtn.innerHTML = '<span>✨ 生成爆款文案</span>';
            }
        }
        
        async function copyText(btn, encodedText) {
            try {
                await navigator.clipboard.writeText(decodeURIComponent(encodedText));
                const original = btn.textContent;
                btn.textContent = '✅ 已复制';
                setTimeout(() => { btn.textContent = original; }, 2000);
            } catch (err) {
                btn.textContent = '✅ 已复制';
                setTimeout(() => { btn.textContent = original; }, 2000);
            }
        }
        
        document.getElementById('generateBtn').addEventListener('click', () => generateContent(false));
        document.getElementById('batchBtn').addEventListener('click', () => generateContent(true));
        document.getElementById('product').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') generateContent(false);
        });
    </script>
</body>
</html>
'''

# ============ 路由 ============
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    product = data.get('product', '').strip()
    style = data.get('style', 'authentic')
    
    if not product:
        return jsonify({'error': '请输入产品名称'}), 400
    
    result = generate_content_v2(product, style)
    return jsonify(result)

@app.route('/api/batch', methods=['POST'])
def batch_generate():
    data = request.json
    product = data.get('product', '').strip()
    count = min(int(data.get('count', 3)), 5)
    
    if not product:
        return jsonify({'error': '请输入产品名称'}), 400
    
    styles = ['authentic', 'professional', 'emotional', 'humorous']
    results = [generate_content_v2(product, styles[i % len(styles)]) for i in range(count)]
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
