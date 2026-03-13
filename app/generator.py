import json
import os
import random
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ProductInfo:
    name: str
    category: str
    subcategory: str
    angles: List[str]
    emotions: List[str]

class ProductKnowledgeBase:
    def __init__(self):
        self.data = self._load_data()
    
    def _load_data(self):
        return {
            "categories": {
                "food": {
                    "name": "美食",
                    "keywords": ["餐厅", "火锅", "烧烤", "甜品", "奶茶", "咖啡", "小吃"],
                    "angles": ["味道口感", "环境氛围", "服务态度", "性价比"],
                    "emotions": ["幸福感爆棚", "太满足了", "治愈系", "回味无穷"]
                },
                "fruit": {
                    "name": "水果",
                    "keywords": ["草莓", "榴莲", "芒果", "葡萄", "西瓜", "车厘子", "橙子"],
                    "angles": ["甜度口感", "新鲜程度", "挑选技巧", "保存方法"],
                    "emotions": ["甜到心里", "汁水四溢", "清新爽口", "满满的维C"]
                },
                "daily": {
                    "name": "日用品",
                    "keywords": ["纸巾", "洗衣液", "洗发水", "面膜", "收纳", "清洁"],
                    "angles": ["使用效果", "性价比", "香味", "包装设计"],
                    "emotions": ["生活小确幸", "治愈强迫症", "提升幸福感", "相见恨晚"]
                },
                "digital": {
                    "name": "数码",
                    "keywords": ["耳机", "手机", "充电宝", "数据线", "键盘", "音箱"],
                    "angles": ["音质/性能", "外观设计", "续航能力", "使用体验"],
                    "emotions": ["科技感爆棚", "效率神器", "爱不释手", "真香警告"]
                },
                "beauty": {
                    "name": "美妆",
                    "keywords": ["口红", "粉底", "精华", "面霜", "香水", "眼影"],
                    "angles": ["妆效/肤感", "持久度", "色号/色号", "性价比"],
                    "emotions": ["颜值爆表", "素颜自信", "精致女孩", "被夸爆了"]
                }
            },
            "writing_styles": {
                "authentic": {
                    "name": "真实体验型",
                    "phrases": ["说实话", "真实感受", "亲测", "用了一段时间"]
                },
                "professional": {
                    "name": "专业测评型",
                    "phrases": ["从专业角度来说", "直接上数据", "横向对比", "干货分享"]
                },
                "emotional": {
                    "name": "情感共鸣型",
                    "phrases": ["其实", "记得", "那时候", "温暖", "陪伴"]
                },
                "humorous": {
                    "name": "幽默风趣型",
                    "phrases": ["笑死", "离谱", "万万没想到", "真香"]
                },
                "minimal": {
                    "name": "极简高级型",
                    "phrases": ["Less is more", "纯粹", "本质", "质感"]
                }
            }
        }
    
    def identify_product(self, product_name: str) -> Tuple[str, float]:
        product_lower = product_name.lower()
        best_match = None
        best_confidence = 0
        
        for cat_key, cat_data in self.data['categories'].items():
            for keyword in cat_data['keywords']:
                if keyword in product_lower:
                    confidence = len(keyword) / len(product_name)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = cat_key
        
        return best_match or 'daily', best_confidence
    
    def get_product_info(self, product_name: str, category: str) -> ProductInfo:
        cat_data = self.data['categories'].get(category, self.data['categories']['daily'])
        return ProductInfo(
            name=product_name,
            category=cat_data['name'],
            subcategory='通用',
            angles=cat_data['angles'],
            emotions=cat_data['emotions']
        )
    
    def get_style(self, style_name: str):
        return self.data['writing_styles'].get(style_name, self.data['writing_styles']['authentic'])

class XiaohongshuGenerator:
    def __init__(self):
        self.kb = ProductKnowledgeBase()
    
    def generate_local(self, product_name: str, style_name: str = 'authentic', user_keywords: str = None) -> Dict:
        category, _ = self.kb.identify_product(product_name)
        product_info = self.kb.get_product_info(product_name, category)
        style = self.kb.get_style(style_name)
        
        # 生成标题
        titles = [
            f"挖到宝了！这个{product_name}真的绝了",
            f"被问爆的{product_name}，今天终于分享",
            f"{product_name}｜这个真的闭眼入",
            f"后悔没早买！{product_name}太香了",
            f"用了{random.choice(['一周', '一个月'])}，说说{product_name}的真实感受",
            f"{product_name}测评｜不吹不黑版"
        ]
        title = random.choice(titles)
        
        # 生成正文
        paragraphs = []
        
        openings = [
            f"最近{random.choice(['入手', '被种草', '发现'])}了这个{product_name}，{random.choice(product_info.emotions)}！",
            f"说实话，{random.choice(['一开始没抱太大期待', '朋友推荐的'])}，结果{random.choice(['真香', '惊艳到我了'])}。",
            f"今天必须跟你们分享这个{product_name}，{random.choice(['用了一段时间', '体验过后'])}才来发的。"
        ]
        paragraphs.append(random.choice(openings))
        
        for angle in random.sample(product_info.angles, min(3, len(product_info.angles))):
            phrases = {
                '味道口感': f"先说味道，{random.choice(['真的很棒', '完全超预期'])}，{random.choice(['口感层次丰富', '味道很正'])}。",
                '环境氛围': f"环境{random.choice(['很舒适', '氛围感拉满'])}，{random.choice(['拍照很出片', '适合打卡'])}。",
                '甜度口感': f"甜度{random.choice(['刚刚好', '自然清甜'])}，{random.choice(['不是那种齁甜', '口感很细腻'])}。",
                '新鲜程度': f"新鲜度{random.choice(['很高', '没得说'])}，{random.choice(['一看就很新鲜', '品质很好'])}。",
                '使用效果': f"使用感受{random.choice(['很惊喜', '超出预期'])}，{random.choice(['效果明显', '体验很好'])}。",
                '性价比': f"性价比{random.choice(['很高', '很划算'])}，{random.choice(['物超所值', '值得入手'])}。",
                '音质/性能': f"{random.choice(['音质', '性能'])}方面{random.choice(['表现出色', '完全够用'])}，{random.choice(['细节到位', '体验流畅'])}。",
                '妆效/肤感': f"{random.choice(['妆效', '肤感'])}很{random.choice(['自然', '服帖'])}，{random.choice(['持久度不错', '很舒适'])}。"
            }
            if angle in phrases:
                paragraphs.append(phrases[angle])
            else:
                paragraphs.append(f"{angle}方面，表现不错。{random.choice(['在同类型产品里有竞争力', '值得推荐'])}。")
        
        # 小缺点
        if random.random() > 0.5:
            paragraphs.append(f"当然也有{random.choice(['小缺点', '不足之处'])}，{random.choice(['物流有点慢', '包装可以更精致'])}，不过{random.choice(['不影响使用', '瑕不掩瑜'])}。")
        
        # 结尾
        closings = [
            f"总之{random.choice(['挺满意', '没踩雷', '值得一试'])}，{random.choice(['推荐给大家', '分享给你们'])}。",
            f"{random.choice(['真实体验分享', '自用无广'])}，{random.choice(['希望能帮到你', '仅供参考'])}。"
        ]
        paragraphs.append(random.choice(closings))
        
        # 组合
        emojis = random.sample(['✨', '💕', '🥰', '🌟', '💖', '👀', '🔥'], 3)
        content = f"{' '.join(emojis)}\n\n" + "\n\n".join(paragraphs)
        
        hashtags = f"#{product_name} #{product_info.category}分享 #好物推荐 #真实测评 #种草"
        
        return {
            'title': title,
            'content': f"【{title}】\n\n{content}\n\n{hashtags}",
            'category': category,
            'style': style_name,
            'product': product_name,
            'is_ai_generated': False
        }
    
    def generate_with_coze(self, product_name: str, style_name: str = 'authentic', user_keywords: str = None) -> Dict:
        # 暂时使用本地生成（Coze API可在后续接入）
        return self.generate_local(product_name, style_name, user_keywords)
    
    def batch_generate(self, product_name: str, count: int = 3) -> List[Dict]:
        styles = ['authentic', 'professional', 'emotional', 'humorous']
        return [self.generate_local(product_name, styles[i % len(styles)]) for i in range(count)]
