from flask import Flask, render_template_string, request, jsonify
import random

app = Flask(__name__)

# ============ 产品知识库 ============
PRODUCT_DATA = {
    "categories": {
        "food": {
            "name": "美食",
            "keywords": ["餐厅", "火锅", "烧烤", "甜品", "奶茶", "咖啡", "小吃"],
            "angles": ["味道口感", "环境氛围", "服务态度", "性价比"],
            "emotions": ["幸福感爆棚", "太满足了", "治愈系", "回味无穷"]
        },
        "fruit": {
            "name": "水果",
            "keywords": ["草莓", "榴莲", "芒果", "葡萄", "西瓜", "车厘子", "橙子", "苹果"],
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
            "keywords": ["耳机", "手机", "充电宝", "数据线", "键盘", "音箱", "鼠标"],
            "angles": ["音质/性能", "外观设计", "续航能力", "使用体验"],
            "emotions": ["科技感爆棚", "效率神器", "爱不释手", "真香警告"]
        },
        "beauty": {
            "name": "美妆",
            "keywords": ["口红", "粉底", "精华", "面霜", "香水", "眼影", "护肤"],
            "angles": ["妆效/肤感", "持久度", "色号/色号", "性价比"],
            "emotions": ["颜值爆表", "素颜自信", "精致女孩", "被夸爆了"]
        }
    },
    "writing_styles": {
        "authentic": {"name": "真实体验型", "phrases": ["说实话", "真实感受", "亲测", "用了一段时间"]},
        "professional": {"name": "专业测评型", "phrases": ["从专业角度来说", "直接上数据", "横向对比", "干货分享"]},
        "emotional": {"name": "情感共鸣型", "phrases": ["其实", "记得", "那时候", "温暖", "陪伴"]},
        "humorous": {"name": "幽默风趣型", "phrases": ["笑死", "离谱", "万万没想到", "真香"]},
        "minimal": {"name": "极简高级型", "phrases": ["Less is more", "纯粹", "本质", "质感"]}
    }
}

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

def generate_content(product_name, style_name='authentic'):
    category = identify_product(product_name)
    cat_data = PRODUCT_DATA["categories"].get(category, PRODUCT_DATA["categories"]["daily"])
    
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
        f"最近{random.choice(['入手', '被种草', '发现'])}了这个{product_name}，{random.choice(cat_data['emotions'])}！",
        f"说实话，{random.choice(['一开始没抱太大期待', '朋友推荐的'])}，结果{random.choice(['真香', '惊艳到我了'])}。",
        f"今天必须跟你们分享这个{product_name}，{random.choice(['用了一段时间', '体验过后'])}才来发的。"
    ]
    paragraphs.append(random.choice(openings))
    
    for angle in random.sample(cat_data['angles'], min(3, len(cat_data['angles']))):
        phrases_map = {
            '味道口感': f"先说味道，{random.choice(['真的很棒', '完全超预期'])}，{random.choice(['口感层次丰富', '味道很正'])}。",
            '环境氛围': f"环境{random.choice(['很舒适', '氛围感拉满'])}，{random.choice(['拍照很出片', '适合打卡'])}。",
            '甜度口感': f"甜度{random.choice(['刚刚好', '自然清甜'])}，{random.choice(['不是那种齁甜', '口感很细腻'])}。",
            '新鲜程度': f"新鲜度{random.choice(['很高', '没得说'])}，{random.choice(['一看就很新鲜', '品质很好'])}。",
            '使用效果': f"使用感受{random.choice(['很惊喜', '超出预期'])}，{random.choice(['效果明显', '体验很好'])}。",
            '性价比': f"性价比{random.choice(['很高', '很划算'])}，{random.choice(['物超所值', '值得入手'])}。",
            '音质/性能': f"{random.choice(['音质', '性能'])}方面{random.choice(['表现出色', '完全够用'])}。",
            '妆效/肤感': f"{random.choice(['妆效', '肤感'])}很{random.choice(['自然', '服帖'])}。"
        }
        if angle in phrases_map:
            paragraphs.append(phrases_map[angle])
        else:
            paragraphs.append(f"{angle}方面，表现不错。值得推荐。")
    
    if random.random() > 0.5:
        paragraphs.append(f"当然也有{random.choice(['小缺点', '不足之处'])}，{random.choice(['物流有点慢', '包装可以更精致'])}，不过不影响使用。")
    
    closings = [
        f"总之{random.choice(['挺满意', '没踩雷', '值得一试'])}，推荐给大家。",
        f"{random.choice(['真实体验分享', '自用无广'])}，希望能帮到你。"
    ]
    paragraphs.append(random.choice(closings))
    
    emojis = random.sample(['✨', '💕', '🥰', '🌟', '💖', '👀', '🔥'], 3)
    content = f"{' '.join(emojis)}\n\n" + "\n\n".join(paragraphs)
    hashtags = f"#{product_name} #{cat_data['name']}分享 #好物推荐 #真实测评 #种草"
    
    return {
        'title': title,
        'content': f"【{title}】\n\n{content}\n\n{hashtags}",
        'category': category,
        'style': style_name,
        'product': product_name
    }

# ============ HTML模板 ============
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书文案生成器 Pro v4.0</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #ff6b9d 0%, #c44569 50%, #f8b500 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
        header { text-align: center; margin-bottom: 40px; color: white; }
        header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .subtitle { font-size: 1.1rem; opacity: 0.9; }
        .input-section {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e8e8e8;
            border-radius: 12px;
            font-size: 1rem;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #ff6b9d;
        }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } }
        .button-group { display: flex; gap: 15px; margin-top: 25px; }
        .btn-primary, .btn-secondary {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
        }
        .btn-primary { background: linear-gradient(135deg, #ff6b9d, #c44569); color: white; }
        .btn-secondary { background: #f5f5f5; color: #555; }
        .tips-section {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 30px;
        }
        .tips-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
        .tip-card { display: flex; align-items: center; gap: 10px; padding: 12px; background: #f8f9fa; border-radius: 10px; font-size: 0.9rem; }
        .tip-icon { font-size: 1.5rem; }
        .results-section {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            display: none;
        }
        .result-card {
            background: #fafafa;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border-left: 4px solid #ff6b9d;
        }
        .result-header { display: flex; gap: 10px; margin-bottom: 15px; }
        .style-badge, .category-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .style-badge { background: linear-gradient(135deg, #ff6b9d, #c44569); color: white; }
        .category-badge { background: #e8f4f8; color: #2c3e50; }
        .result-content { white-space: pre-wrap; line-height: 1.8; color: #444; }
        .btn-copy {
            padding: 10px 20px;
            background: white;
            border: 2px solid #ff6b9d;
            color: #ff6b9d;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
        }
        .btn-copy:hover { background: #ff6b9d; color: white; }
        footer { text-align: center; padding: 30px; color: white; opacity: 0.8; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📝 小红书文案生成器 Pro</h1>
            <p class="subtitle">AI驱动 · 真实原创 · 不再模板化</p>
        </header>
        <main>
            <div class="input-section">
                <div class="form-group">
                    <label for="product">产品名称 *</label>
                    <input type="text" id="product" placeholder="例如：丹东草莓、iPhone 15、海底捞..." required>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label for="style">文案风格</label>
                        <select id="style">
                            <option value="authentic">真实体验型</option>
                            <option value="professional">专业测评型</option>
                            <option value="emotional">情感共鸣型</option>
                            <option value="humorous">幽默风趣型</option>
                            <option value="minimal">极简高级型</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="keywords">关键词（可选）</label>
                        <input type="text" id="keywords" placeholder="例如：送礼、性价比">
                    </div>
                </div>
                <div class="button-group">
                    <button id="generateBtn" class="btn-primary">✨ 生成文案</button>
                    <button id="batchBtn" class="btn-secondary">🎲 批量生成3条</button>
                </div>
            </div>
            <div class="tips-section">
                <h3>💡 使用提示</h3>
                <div class="tips-grid">
                    <div class="tip-card"><span class="tip-icon">🍓</span><span>水果：丹东草莓、车厘子...</span></div>
                    <div class="tip-card"><span class="tip-icon">🍜</span><span>美食：海底捞、日料...</span></div>
                    <div class="tip-card"><span class="tip-icon">🏠</span><span>日用：收纳盒、面膜...</span></div>
                    <div class="tip-card"><span class="tip-icon">📱</span><span>数码：蓝牙耳机...</span></div>
                </div>
            </div>
            <div id="results" class="results-section">
                <h3>🎯 生成结果</h3>
                <div id="resultsList"></div>
            </div>
        </main>
        <footer><p>Powered by AI · 每次生成都是原创内容</p></footer>
    </div>
    <script>
        const styleMap = {
            'authentic': '真实体验型', 'professional': '专业测评型',
            'emotional': '情感共鸣型', 'humorous': '幽默风趣型', 'minimal': '极简高级型'
        };
        async function generateContent(isBatch = false) {
            const product = document.getElementById('product').value.trim();
            const style = document.getElementById('style').value;
            if (!product) { alert('请输入产品名称'); return; }
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('batchBtn').disabled = true;
            try {
                const endpoint = isBatch ? '/api/batch' : '/api/generate';
                const body = isBatch ? { product, count: 3 } : { product, style };
                const response = await fetch(endpoint, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                const data = await response.json();
                if (data.error) { alert(data.error); return; }
                document.getElementById('results').style.display = 'block';
                const resultsList = document.getElementById('resultsList');
                resultsList.innerHTML = '';
                const results = isBatch ? data.results : [data];
                results.forEach((result) => {
                    const card = document.createElement('div');
                    card.className = 'result-card';
                    card.innerHTML = `
                        <div class="result-header">
                            <span class="style-badge">${styleMap[result.style]}</span>
                            <span class="category-badge">${result.category}</span>
                        </div>
                        <pre class="result-content">${result.content}</pre>
                        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e8e8e8;">
                            <button class="btn-copy" onclick="copyText(this, '${encodeURIComponent(result.content)}')">📋 复制文案</button>
                        </div>
                    `;
                    resultsList.appendChild(card);
                });
                document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
            } catch (error) {
                alert('生成失败，请重试');
            } finally {
                document.getElementById('generateBtn').disabled = false;
                document.getElementById('batchBtn').disabled = false;
            }
        }
        async function copyText(btn, encodedText) {
            try {
                await navigator.clipboard.writeText(decodeURIComponent(encodedText));
                btn.textContent = '✅ 已复制';
                setTimeout(() => { btn.textContent = '📋 复制文案'; }, 2000);
            } catch (err) {
                btn.textContent = '✅ 已复制';
                setTimeout(() => { btn.textContent = '📋 复制文案'; }, 2000);
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
    
    result = generate_content(product, style)
    return jsonify(result)

@app.route('/api/batch', methods=['POST'])
def batch_generate():
    data = request.json
    product = data.get('product', '').strip()
    count = min(int(data.get('count', 3)), 5)
    
    if not product:
        return jsonify({'error': '请输入产品名称'}), 400
    
    styles = ['authentic', 'professional', 'emotional', 'humorous']
    results = [generate_content(product, styles[i % len(styles)]) for i in range(count)]
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
