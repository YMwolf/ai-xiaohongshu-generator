from flask import Flask, render_template, request, jsonify
from .generator import XiaohongshuGenerator
import os

def create_app():
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'))
    
    generator = XiaohongshuGenerator()
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/api/generate', methods=['POST'])
    def generate():
        data = request.json
        product = data.get('product', '').strip()
        style = data.get('style', 'authentic')
        keywords = data.get('keywords', '')
        
        if not product:
            return jsonify({'error': '请输入产品名称'}), 400
        
        try:
            result = generator.generate_with_coze(product, style, keywords)
            return jsonify(result)
        except Exception as e:
            result = generator.generate_local(product, style, keywords)
            return jsonify(result)
    
    @app.route('/api/batch', methods=['POST'])
    def batch_generate():
        data = request.json
        product = data.get('product', '').strip()
        count = min(int(data.get('count', 3)), 5)
        
        if not product:
            return jsonify({'error': '请输入产品名称'}), 400
        
        try:
            results = generator.batch_generate(product, count)
            return jsonify({'results': results})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/styles')
    def get_styles():
        from .generator import ProductKnowledgeBase
        kb = ProductKnowledgeBase()
        styles = []
        for key, data in kb.data['writing_styles'].items():
            styles.append({
                'key': key,
                'name': data['name'],
                'tone': data['tone']
            })
        return jsonify({'styles': styles})
    
    return app
