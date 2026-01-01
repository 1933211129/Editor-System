import re
from typing import List

class ReferenceChecker:
    """
    一个根据特定标准检查参考文献格式的类。
    该最终版本重构了作者解析和年份检测的核心逻辑，并完善了对各类文献的检查。
    """
    # 定义各类参考文献的正确格式示例
    FORMAT_EXAMPLES = {
        "authors_en": "YANG A X",
        "authors_en_many": "SHU K, SLIVA A, WANG S, et al.",
        "authors_cn_many": "张克亮, 李伟刚, 王慧兰, 等.",
        "title_en": "Learning robust uniform features for cross-media social data",
        "venue_en": "Computational Linguistics",
        "online": "[2025-01-01]. http://...",
        "journal": "GUO Q, JIA J, SHEN G, et al. Learning robust uniform features...[J]. Knowledge-Based Systems, 2016, 102(C): 64-75.",
        "conference": "SINGH G, SERRA L, PING W, et al. BrickNet...[C]//Proceedings of IEEE VRAIS’95. Piscataway, NJ: IEEE, 1995: 19-25.",
        "book": "ROMAN S. The Umbral Calcus [M]. New York: Academic Press, 1984: 100-130.",
        "dissertation_cn": "李刚. 知识发现的图模型方法[D]. 青岛: 中国海洋大学博士学位论文, 2001.",
        "dissertation_location": "青岛",
        "arxiv": "FONG E, HOLMES C. On the marginal likelihood...[J/OL]. arXiv preprint arXiv:1905.08737, 2019."
    }

    def __init__(self):
        """初始化，预编译常用的正则表达式并添加省份列表。"""
        self.ref_type_pattern = re.compile(r'\[([A-Z])(?:/([A-Z]+))?\]')
        self.chinese_char_pattern = re.compile(r'[\u4e00-\u9fa5]')
        self.provinces = [
                "河北", "山西", "辽宁", "吉林", "黑龙江","江苏", "浙江", "安徽", "福建", "江西",
                "山东", "河南", "湖北", "湖南", "广东","海南", "四川", "贵州", "云南", "陕西",
                "甘肃", "青海", "台湾","内蒙古", "广西", "西藏", "宁夏", "新疆"
                ]

    def _normalize_string(self, s: str) -> str:
        """规范化字符串，替换全角标点并处理空格。"""
        s = s.replace('，', ',').replace('：', ':').replace('．', '.').replace('（', '(').replace('）', ')')
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    def _check_authors(self, author_str: str, is_chinese: bool) -> List[str]:
        """[已重构] 检查作者部分的格式，采用更可靠的姓氏和名字解析逻辑。"""
        errors = []
        author_str = author_str.strip()

        if is_chinese:
            # 中文作者检查逻辑
            has_deng = '等' in author_str
            authors = [a.strip() for a in author_str.replace('等', '').split(',') if a.strip()]
            num_authors = len(authors)
            if has_deng and num_authors != 3:
                errors.append(f"作者问题: 中文文献使用'等'时，应只列出前3位作者，当前列出{num_authors}位。 (示例: {self.FORMAT_EXAMPLES['authors_cn_many']})")
            if not has_deng and num_authors > 3:
                errors.append(f"作者问题: 中文文献作者超过3位({num_authors}位)，应使用'等'。 (示例: {self.FORMAT_EXAMPLES['authors_cn_many']})")
        else: # 英文作者
            has_et_al = 'et al' in author_str.lower()
            cleaned_author_str = re.sub(r',?\s*et al\.?', '', author_str, flags=re.IGNORECASE)
            authors = [a.strip() for a in cleaned_author_str.split(',') if a.strip()]
            num_authors = len(authors)

            if has_et_al and num_authors != 3:
                errors.append(f"作者问题: 使用'et al.'时，应只列出前3位作者，当前列出{num_authors}位。 (示例: {self.FORMAT_EXAMPLES['authors_en_many']})")
            if not has_et_al and num_authors > 3:
                errors.append(f"作者问题: 作者超过3位({num_authors}位)，应使用'et al.'。 (示例: {self.FORMAT_EXAMPLES['authors_en_many']})")

            for author in authors:
                parts = author.split()
                if len(parts) < 2:
                    errors.append(f"作者格式问题: '{author}' 格式不完整。 (正确示例: {self.FORMAT_EXAMPLES['authors_en']})")
                    continue
                
                initials_list = []
                last_name_idx = len(parts) - 1
                for i in range(len(parts) - 1, -1, -1):
                    part = parts[i]
                    if part.isalpha() and len(part) == 1 and part.isupper():
                        initials_list.insert(0, part)
                        last_name_idx = i - 1
                    else:
                        break
                
                surname = " ".join(parts[:last_name_idx + 1])
                initials = "".join(initials_list)

                if not surname or not initials:
                    errors.append(f"作者格式问题: 无法从'{author}'中正确解析姓和名。 (正确示例: {self.FORMAT_EXAMPLES['authors_en']})")
                    continue

                if surname != surname.upper():
                    errors.append(f"作者格式问题: '{author}' 的姓氏部分 '{surname}' 应全部大写。 (正确示例: {self.FORMAT_EXAMPLES['authors_en']})")
                if '.' in initials:
                    errors.append(f"作者格式问题: '{author}' 的名字缩写 '{initials}' 后不应有缩写点。 (正确示例: {self.FORMAT_EXAMPLES['authors_en']})")
        return errors

    def _check_title_sentence_case(self, title_str: str) -> List[str]:
        errors = []
        words = title_str.split()
        if not words: return ["题名不能为空。"]
        if words[0][0] != words[0][0].upper():
            errors.append(f"题名大小写问题: 题名 '{title_str}' 的首词 '{words[0]}' 应首字母大写。 (示例: '{self.FORMAT_EXAMPLES['title_en']}')")
        for word in words[1:]:
            if word.isupper() or any(char.isdigit() for char in word): continue
            if word.lower() in ["a", "an", "the", "of", "in", "on", "for", "and", "or", "to", "with"]: continue
            if word == word.capitalize():
                errors.append(f"题名大小写警告: 单词 '{word}' 首字母大写。请确认其不是专有名词，否则除首词外，其余单词应为小写。")
        return errors

    def _check_venue_title_case(self, venue_str: str) -> List[str]:
        errors = []
        words = venue_str.split()
        stopwords = ["a", "an", "the", "of", "in", "on", "for", "and", "or", "to", "with"]
        for i, word in enumerate(words):
            if i == 0 or word.lower() not in stopwords:
                if word[0] != word[0].upper() and not word.isupper():
                     errors.append(f"期刊/会议名大小写问题: 实词 '{word}' 应首字母大写。 (示例: {self.FORMAT_EXAMPLES['venue_en']})")
        return errors

    def _check_online_requirements(self, ref_str: str) -> List[str]:
        errors = []
        if not re.search(r'\[\d{4}-\d{2}-\d{2}\]', ref_str):
            errors.append(f"联机文献问题: 缺少引用日期，或日期格式不正确。 (正确示例: {self.FORMAT_EXAMPLES['online']})")
        if 'http' not in ref_str:
            errors.append(f"联机文献问题: 缺少获取和访问路径 (URL)。 (正确示例: {self.FORMAT_EXAMPLES['online']})")
        return errors
        
    def _get_common_parts(self, ref_str: str):
        match = re.match(r'^\[\d+\]\s*(?P<authors>.*?)\.\s*(?P<title>.*?)\s*\[[A-Z](?:/[A-Z]+)?\]', ref_str)
        return match.groupdict() if match else None

    def _check_arxiv(self, ref_str: str, is_chinese: bool) -> List[str]:
        """[已重构] 检查arXiv预印本的格式，并强制检查[J/OL]标识。"""
        errors = []
        
        type_match = self.ref_type_pattern.search(ref_str)
        if not type_match or type_match.group(0).upper() != '[J/OL]':
            errors.append(f"arXiv文献标识问题: 预印本应使用 '[J/OL]' 标识。 (正确示例: {self.FORMAT_EXAMPLES['arxiv']})")

        parts = self._get_common_parts(ref_str)
        if not parts:
            errors.append("arXiv文献结构问题: 无法解析'作者. 题名'部分。")
            return errors
        errors.extend(self._check_authors(parts['authors'], is_chinese))
        if not is_chinese: errors.extend(self._check_title_sentence_case(parts['title']))
        
        arxiv_format_match = re.search(r'\]\.\s*arXiv preprint arXiv:[\d\.]+\s*,\s*\d{4}\.?$', ref_str)
        if not arxiv_format_match:
            errors.append(f"arXiv文献格式问题: 格式不正确。 (正确示例: {self.FORMAT_EXAMPLES['arxiv']})")
        return errors

    def _check_journal(self, ref_str: str, is_online: bool, is_chinese: bool) -> List[str]:
        errors = []
        parts = self._get_common_parts(ref_str)
        if not parts:
            errors.append("期刊[J]结构问题: 无法解析'作者. 题名'部分。")
            return errors
        errors.extend(self._check_authors(parts['authors'], is_chinese))
        if not is_chinese: errors.extend(self._check_title_sentence_case(parts['title']))
        journal_match = re.search(r'\]\.\s*(?P<journal_name>.*?),\s*(?P<year>\d{4})\s*,?\s*(?P<volume_issue>.*?):\s*(?P<pages>[\d-]+)\.?', ref_str)
        if not journal_match:
            errors.append(f"期刊[J]结构问题: 格式不正确，应包含'期刊名, 年, 卷(期):页码'。 (正确示例: {self.FORMAT_EXAMPLES['journal']})")
        else:
            if not is_chinese: errors.extend(self._check_venue_title_case(journal_match.group('journal_name')))
        return errors

    def _check_dissertation(self, ref_str: str, is_online: bool, is_chinese: bool) -> List[str]:
        errors = []
        parts = self._get_common_parts(ref_str)
        if not parts:
            errors.append("学位论文[D]结构问题: 无法解析'作者. 题名'部分。")
            return errors
        errors.extend(self._check_authors(parts['authors'], is_chinese))
        if not is_chinese: errors.extend(self._check_title_sentence_case(parts['title']))
        diss_match = re.search(r'\]\.\s*(?P<location>[^:]+):\s*(?P<university>[^,]+)', ref_str)
        if not diss_match:
            errors.append(f"学位论文[D]结构问题: 未能解析出'出版地: 单位'部分。 (正确示例: {self.FORMAT_EXAMPLES['dissertation_cn']})")
        else:
            location = diss_match.group('location').strip()
            if location in self.provinces:
                errors.append(f"学位论文[D]出版地问题: 检测到地点 '{location}' 是一个省份，通常应著录为城市。 (示例: '{self.FORMAT_EXAMPLES['dissertation_location']}')")
        return errors

    def _check_conference(self, ref_str: str, is_online: bool, is_chinese: bool) -> List[str]:
        errors = []
        parts = self._get_common_parts(ref_str)
        if not parts:
            errors.append("会议论文[C]结构问题: 无法解析'作者. 题名'部分。")
            return errors

        errors.extend(self._check_authors(parts['authors'], is_chinese))
        if not is_chinese:
            errors.extend(self._check_title_sentence_case(parts['title']))

        if '//' not in ref_str:
            errors.append(f"会议论文[C]结构问题: 缺少 '//' 分隔符。 (正确示例: {self.FORMAT_EXAMPLES['conference']})")
            return errors

        conf_details = ref_str.split('//', 1)[1]
        
        year_match = re.search(r'[,\.]\s*(\d{4})\s*[:\.]|\b(\d{4})\.$', conf_details)
        if not year_match:
            errors.append(f"会议论文[C]格式问题: 缺少格式正确的出版年份。年份应独立于会议名称，如 ', 1995:' 或在末尾 '... 2024.'. (完整示例: {self.FORMAT_EXAMPLES['conference']})")
            
        # [已修正] 采用更严格的页码检测逻辑，强制要求有冒号
        if not re.search(r':\s*[\d\-\u2013\u2014]+$', conf_details.strip().rstrip('.')):
            errors.append(f"会议论文[C]格式问题: 缺少页码信息。页码应由冒号引导，如 ': 22-36'. (正确示例: {self.FORMAT_EXAMPLES['conference']})")

        return errors

    def _check_book(self, ref_str: str, is_online: bool, is_chinese: bool) -> List[str]:
        errors = []
        parts = self._get_common_parts(ref_str)
        if not parts:
            errors.append("图书[M]结构问题: 无法解析'作者. 题名'部分。")
            return errors
        
        errors.extend(self._check_authors(parts['authors'], is_chinese))
        if not is_chinese:
            errors.extend(self._check_title_sentence_case(parts['title']))
        
        book_match = re.search(r'\]\.[^:]*:\s*[^,]+,\s*\d{4}', ref_str)
        if not book_match:
            errors.append(f"图书[M]结构问题: 格式不正确，应包含'出版地: 出版者, 出版年'。 (正确示例: {self.FORMAT_EXAMPLES['book']})")
        
        return errors

    def check_reference(self, ref_string: str) -> List[str]:
        """对单条参考文献字符串进行格式检查。"""
        errors = []
        norm_ref = self._normalize_string(ref_string)

        if not re.match(r'^\[\d+\]', norm_ref):
            errors.append("起始格式问题: 参考文献应以 '[序号]' 开头。")
            return errors

        type_match = self.ref_type_pattern.search(norm_ref)
        if not type_match:
            errors.append("类型标志问题: 未能识别参考文献类型标志，例如 [M], [J], [C/OL]。")
            return errors
        
        ref_type, carrier_type = type_match.groups()
        is_online = (carrier_type == 'OL')
        is_chinese = bool(self.chinese_char_pattern.search(norm_ref))

        # --- [已重构] 智能分派逻辑 ---
        if 'arxiv preprint' in norm_ref.lower():
            errors.extend(self._check_arxiv(norm_ref, is_chinese))
        elif ref_type == 'J':
            errors.extend(self._check_journal(norm_ref, is_online, is_chinese))
        elif ref_type == 'D':
            errors.extend(self._check_dissertation(norm_ref, is_online, is_chinese))
        elif ref_type == 'C':
            errors.extend(self._check_conference(norm_ref, is_online, is_chinese))
        elif ref_type == 'M':
            errors.extend(self._check_book(norm_ref, is_online, is_chinese))
            
        if is_online and 'arxiv preprint' not in norm_ref.lower():
            errors.extend(self._check_online_requirements(norm_ref))

        if not errors:
            return ["格式基本符合规范。"]
        return errors
