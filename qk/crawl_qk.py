from flask import Flask, Response, request
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from collections import OrderedDict

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # 必须的配置

# 自定义JSON序列化器处理OrderedDict
class OrderedJsonEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, OrderedDict):
            return super().encode(dict(obj))
        return super().encode(obj)

def process_journal(url="http://jcip.cipsc.org.cn/CN/home"):
    # 使用双重有序结构
    final_data = OrderedDict()  # 外层有序字典
    
    # 原始解析逻辑
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    current_section = None
    for element in soup.find_all(['h3', 'li'], class_=['j-column', 'noselectrow']):
        if element.name == 'h3':
            current_section = element.get_text(strip=True)
            final_data[current_section] = []  # 保持栏目顺序
        elif element.name == 'li' and current_section:
            title_div = element.find('div', class_='j-title-1')
            if title_div:
                title = title_div.get_text(strip=True)
                link = title_div.find('a')['href'] if title_div.find('a') else None
                # 每篇文章用OrderedDict保持字段顺序
                article = OrderedDict()
                article['title'] = title
                article['url'] = link
                final_data[current_section].append(article)  # 保持文章顺序

    # 补充文章详情（保持原有字段顺序）
    for section in final_data:
        for article in final_data[section]:
            url = article['url']
            if not url.startswith('http'):
                continue
                
            try:
                resp = requests.get(url)
                resp.encoding = 'utf-8'
                
                # 元数据提取到有序字典
                meta_match = re.search(r'window\.metaData\s*=\s*({.*?});', resp.text, re.DOTALL)
                if meta_match:
                    meta_data = json.loads(meta_match.group(1))['article']
                    # 按原有字段顺序添加
                    article.update(OrderedDict([
                        ('title_cn', meta_data.get('title_cn', article['title'])),
                        ('title_en', meta_data.get('title_en', '')),
                        ('abstract_cn', meta_data.get('zhaiyao_cn', '')),
                        ('keywords_cn', meta_data.get('keywordList_cn', [])),
                        ('author_cn', meta_data.get('zuoZheCn_L', '')),
                        ('author_en', meta_data.get('zuoZheEn_L', ''))
                    ]))
                
                # 参考文献处理
                if ref_match := re.search(r'<meta name="article_references" content="(.*?)"', resp.text):
                    references = ref_match.group(1)
                    article['references'] = references
                    # 保持字段添加顺序
                    article['reference_cn'] = re.sub(r'\.\s*(中文信息学报)', r'[J]. \1', references)
                    if date_match := re.search(r'中文信息学报\.(.*)', references):
                        date = date_match.group(1).strip()
                        article['reference_en'] = f"{article['author_en']}. {article['title_en']}[J]. Journal of Chinese Information Processing. {date}"
                time.sleep(0.5)
            except Exception as e:
                article['error'] = str(e)
    
    return final_data  # 返回结构完全不变：{栏目: [文章...]}

@app.route('/crawl')
def api():
    try:
        data = process_journal(request.args.get('url'))
        # 手动构建JSON响应确保顺序
        return Response(
            json.dumps({'status': 'success', 'data': data}, cls=OrderedJsonEncoder, ensure_ascii=False),
            mimetype='application/json; charset=utf-8'
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)
