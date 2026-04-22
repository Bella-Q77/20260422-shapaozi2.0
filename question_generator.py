from typing import List, Dict, Optional, Tuple
from models import Question, QuestionCategory, PersonAttribute, Event
import uuid
import re


class GrammarAnalyzer:
    def __init__(self):
        self._init_patterns()
    
    def _init_patterns(self):
        self.subject_pronouns = ["我", "你", "他", "她", "它", "我们", "你们", "他们", "她们", "它们", "自己", "别人", "大家", "谁"]
        
        self.person_titles = [
            "经理", "总监", "老板", "老师", "教授", "医生", "护士",
            "工程师", "设计师", "会计", "律师", "警察", "消防员", "司机",
            "同学", "同事", "朋友", "家人", "亲戚", "领导", "下属", "员工",
            "主管", "主任", "部长", "局长", "厅长", "主席", "书记", "委员",
            "董事", "监事", "总裁", "CEO", "CTO", "CFO", "创始人", "合伙人",
            "爸爸", "妈妈", "父亲", "母亲", "爷爷", "奶奶", "外公", "外婆",
            "哥哥", "姐姐", "弟弟", "妹妹", "儿子", "女儿", "丈夫", "妻子",
            "先生", "女士", "小姐", "同志", "师傅", "客户", "顾客", "患者",
            "学生", "家长", "孩子", "儿童", "老人", "年轻人", "工人", "农民",
            "商人", "服务员", "厨师", "飞行员", "演员", "歌手", "作家",
            "画家", "艺术家", "科学家", "研究员", "顾问", "专家", "学者"
        ]
        
        self.person_prefixes = ["老", "小", "大", "阿"]
        
        self.conjunctions = ["和", "与", "及", "跟", "、", "，", ",", "；", ";", "还有", "以及", "同"]
        
        self.time_keywords = ["今天", "明天", "昨天", "前天", "后天", "上周", "下周", "上月", "下月",
                              "去年", "今年", "明年", "上午", "下午", "晚上", "凌晨", "傍晚", "深夜",
                              "现在", "刚才", "马上", "立刻", "已经", "曾经", "正在", "将", "要", "会",
                              "年月日", "点", "分", "秒", "时", "星期", "周", "月", "年", "日", "号"]
        
        self.place_keywords = ["在", "到", "去", "从", "往", "向", "于", "处", "里", "内", "外", "上", "下",
                               "家", "公司", "学校", "医院", "商店", "餐厅", "酒店", "银行", "邮局", "车站",
                               "机场", "公园", "广场", "街道", "路", "巷", "楼", "层", "室", "号", "区", "市",
                               "省", "国", "县", "镇", "村", "小区", "大厦", "中心", "市场", "超市", "商场"]
        
        self.common_verbs = [
            "吃", "喝", "玩", "乐", "买", "卖", "去", "来", "走", "跑",
            "跳", "飞", "游", "睡", "醒", "工作", "学习", "上班", "下班", "开会",
            "吃饭", "睡觉", "旅游", "购物", "运动", "休息", "娱乐", "看", "听", "说",
            "读", "写", "做", "打", "踢", "送", "收", "借", "还", "签", "订",
            "报", "申", "办", "理", "处", "罚", "奖", "评", "审", "批", "核",
            "查", "验", "检", "试", "考", "学", "教", "发", "邮", "寄", "领",
            "拿", "带", "搬", "运", "改", "变", "调", "整", "管", "组", "织",
            "安", "排", "计", "划", "策", "划", "设", "开", "研", "生", "产",
            "制", "造", "加", "工", "包", "装", "销", "售", "推", "宣", "传",
            "营", "销", "促", "销", "维", "修", "保", "养", "清", "整", "理",
            "摆", "介", "讲", "解", "说", "推", "荐", "教", "育", "培", "训",
            "指", "导", "帮", "助", "协", "支", "援", "救", "助", "捐", "赠",
            "分", "配", "发", "放", "共", "享", "合", "作", "联", "兼", "并",
            "收", "购", "租", "入", "住", "离", "开", "进", "入", "出", "发",
            "旅", "行", "出", "差", "探", "访", "拜", "会", "见", "见", "面",
            "约", "会", "聚", "宴", "请", "聚", "餐", "用", "餐", "进", "食",
            "饮", "用", "服", "用", "使", "用", "操", "作", "管", "负", "责",
            "主", "管", "经", "办", "承", "办", "接", "办", "督", "查", "答",
            "复", "回", "应", "反", "馈", "处", "理", "解", "决", "审", "核",
            "查", "阅", "查", "找", "查", "询", "查", "证", "核", "落", "实",
            "执", "行", "实", "施", "实", "践", "实", "现", "达", "成", "完",
            "成", "结", "束", "结", "果", "结", "论", "结", "算", "付", "款",
            "收", "款", "交", "款", "还", "款", "借", "款", "贷", "存", "款",
            "取", "款", "转", "款", "汇", "款", "兑", "换", "提", "听说",
            "看到", "发现", "知道", "了解", "收到", "接到", "告诉", "介绍",
            "推荐", "认识", "遇见", "聊天", "打电话", "发邮件", "发短信",
            "看电影", "看电视", "看书", "上网"
        ]
        
        self.auxiliary_verbs = ["是", "有", "会", "能", "可以", "应该", "要", "想", "愿意", "可能", "必须", "得"]
        
        self.prepositions = ["在", "于", "从", "到", "往", "向", "对", "为", "给", "跟", "和", "与", "同", "被", "把", "将", "叫", "让", "给"]
        
        self.measure_words = ["个", "只", "条", "件", "本", "张", "片", "块", "辆", "架", "艘", "台", "部", "篇", "首", "幅", "朵", "棵", "株"]
        
        self.demonstratives = ["这", "那", "这些", "那些", "这个", "那个", "这里", "那里", "这儿", "那儿", "这么", "那么", "这样", "那样"]
        
        self.adverbs = ["很", "非常", "特别", "比较", "相当", "更", "最", "太", "真", "确实", "已经", "曾经", "正在", "将要", "马上", "立刻", "就", "才", "还", "也", "都", "又", "再", "一直", "总是", "从来", "曾经"]
        
        self.adjectives = ["好", "坏", "大", "小", "多", "少", "高", "低", "长", "短", "快", "慢", "新", "旧", "美", "丑", "聪明", "愚蠢", "高兴", "难过", "开心", "伤心", "美丽", "漂亮", "丑陋", "优秀", "良好", "一般", "差", "棒", "厉害", "普通", "特别", "普通", "特殊"]
        
        self.cause_keywords = ["因为", "由于", "原因是", "为了", "所以", "因此", "于是", "结果", "导致", "引起", "造成", "使得", "以便", "以致"]
        
        self.event_keywords = [
            "会议", "聚会", "活动", "事件", "事故", "案件", "项目", "任务",
            "计划", "安排", "决定", "决策", "协议", "合同", "交易", "买卖",
            "投资", "融资", "贷款", "借款", "还款", "付款", "收款", "转账",
            "出差", "旅行", "旅游", "访问", "拜访", "会见", "见面", "约会",
            "聚餐", "宴会", "婚礼", "葬礼", "生日", "庆祝", "纪念", "节日",
            "考试", "考核", "评估", "评审", "审计", "检查", "调查", "研究",
            "开发", "设计", "生产", "制造", "加工", "销售", "采购", "购买",
            "招聘", "面试", "培训", "学习", "上课", "听课", "讲座", "报告",
            "比赛", "竞赛", "运动", "锻炼", "健身", "娱乐", "休息", "休假",
            "生病", "就医", "治疗", "手术", "检查", "诊断", "康复", "出院",
            "入职", "离职", "辞职", "退休", "升职", "降职", "调动", "晋升",
            "结婚", "离婚", "生子", "生育", "搬家", "装修", "买房", "租房",
            "买车", "修车", "保养", "加油", "停车", "开车", "打车", "乘车"
        ]
    
    def analyze(self, text: str) -> Dict:
        result = {
            "original_text": text,
            "sentences": [],
            "words": [],
            "subjects": [],
            "verbs": [],
            "objects": [],
            "persons": [],
            "places": [],
            "times": [],
            "events": [],
            "causes": [],
            "results": [],
            "svo_structures": []
        }
        
        sentences = self._split_sentences(text)
        result["sentences"] = sentences
        
        for sentence in sentences:
            sentence_analysis = self._analyze_sentence(sentence)
            result["words"].extend(sentence_analysis["words"])
            result["subjects"].extend(sentence_analysis["subjects"])
            result["verbs"].extend(sentence_analysis["verbs"])
            result["objects"].extend(sentence_analysis["objects"])
            result["persons"].extend(sentence_analysis["persons"])
            result["places"].extend(sentence_analysis["places"])
            result["times"].extend(sentence_analysis["times"])
            result["events"].extend(sentence_analysis["events"])
            result["causes"].extend(sentence_analysis["causes"])
            result["results"].extend(sentence_analysis["results"])
            result["svo_structures"].extend(sentence_analysis["svo_structures"])
        
        result["subjects"] = self._deduplicate(result["subjects"])
        result["verbs"] = self._deduplicate(result["verbs"])
        result["objects"] = self._deduplicate(result["objects"])
        result["persons"] = self._deduplicate(result["persons"])
        result["places"] = self._deduplicate(result["places"])
        result["times"] = self._deduplicate(result["times"])
        result["events"] = self._deduplicate(result["events"])
        result["causes"] = self._deduplicate(result["causes"])
        result["results"] = self._deduplicate(result["results"])
        
        return result
    
    def _split_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'[。！？；;.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _analyze_sentence(self, sentence: str) -> Dict:
        result = {
            "words": [],
            "subjects": [],
            "verbs": [],
            "objects": [],
            "persons": [],
            "places": [],
            "times": [],
            "events": [],
            "causes": [],
            "results": [],
            "svo_structures": []
        }
        
        words = self._segment_words(sentence)
        result["words"] = words
        
        result["verbs"] = self._extract_verbs(sentence)
        
        result["subjects"] = self._extract_subjects(sentence, result["verbs"])
        
        result["objects"] = self._extract_objects(sentence, result["verbs"])
        
        result["persons"] = self._extract_persons(sentence)
        
        result["places"] = self._extract_places(sentence)
        
        result["times"] = self._extract_times(sentence)
        
        result["events"] = self._extract_events(sentence)
        
        result["causes"] = self._extract_causes(sentence)
        
        result["results"] = self._extract_results(sentence)
        
        if result["verbs"]:
            main_verb = result["verbs"][0] if result["verbs"] else ""
            subject = result["subjects"][0] if result["subjects"] else ""
            obj = result["objects"][0] if result["objects"] else ""
            
            if main_verb:
                svo = {
                    "subject": subject,
                    "verb": main_verb,
                    "object": obj,
                    "sentence": sentence
                }
                result["svo_structures"].append(svo)
        
        return result
    
    def _segment_words(self, text: str) -> List[str]:
        words = []
        i = 0
        text_len = len(text)
        
        while i < text_len:
            matched = False
            
            for length in range(min(4, text_len - i), 1, -1):
                substring = text[i:i+length]
                
                if substring in self.common_verbs:
                    words.append(substring)
                    i += length
                    matched = True
                    break
                    
                if substring in self.person_titles:
                    words.append(substring)
                    i += length
                    matched = True
                    break
                    
                if substring in self.time_keywords:
                    words.append(substring)
                    i += length
                    matched = True
                    break
            
            if not matched:
                words.append(text[i])
                i += 1
        
        return words
    
    def _extract_verbs(self, sentence: str) -> List[str]:
        verbs = []
        
        for verb in sorted(self.common_verbs, key=len, reverse=True):
            if verb in sentence:
                verbs.append(verb)
        
        return verbs
    
    def _extract_subjects(self, sentence: str, verbs: List[str]) -> List[str]:
        subjects = []
        
        if not verbs:
            for pronoun in self.subject_pronouns:
                if pronoun in sentence:
                    subjects.append(pronoun)
            
            for title in self.person_titles:
                for prefix in [""] + self.person_prefixes:
                    pattern = prefix + title
                    if pattern in sentence:
                        subjects.append(pattern)
            
            chinese_name_match = re.search(r'[\u4e00-\u9fa5]{2,4}(?=[，。、！？；\s]|$)', sentence)
            if chinese_name_match:
                name = chinese_name_match.group()
                if (name not in self.common_verbs and 
                    name not in self.time_keywords and 
                    name not in self.place_keywords and
                    name not in self.adverbs and
                    name not in self.adjectives):
                    subjects.append(name)
            
            return self._deduplicate(subjects)
        
        main_verb = verbs[0]
        verb_index = sentence.find(main_verb)
        
        if verb_index > 0:
            before_verb = sentence[:verb_index]
            
            for pronoun in self.subject_pronouns:
                if pronoun in before_verb:
                    subjects.append(pronoun)
            
            for title in self.person_titles:
                for prefix in [""] + self.person_prefixes:
                    pattern = prefix + title
                    if pattern in before_verb:
                        subjects.append(pattern)
            
            matches = re.findall(r'([\u4e00-\u9fa5]{2,4})', before_verb)
            for match in matches:
                if (match not in self.common_verbs and 
                    match not in self.time_keywords and 
                    match not in self.place_keywords and
                    match not in self.adverbs and
                    match not in self.adjectives and
                    len(match) >= 2):
                    subjects.append(match)
        
        if not subjects:
            subjects = self._extract_persons(sentence)
        
        return self._deduplicate(subjects)
    
    def _extract_objects(self, sentence: str, verbs: List[str]) -> List[str]:
        objects = []
        
        if not verbs:
            return objects
        
        main_verb = verbs[0]
        verb_index = sentence.find(main_verb)
        
        if verb_index >= 0:
            after_verb = sentence[verb_index + len(main_verb):]
            
            after_verb = re.sub(r'[。！？，、；\s]+$', '', after_verb)
            
            if after_verb and len(after_verb) >= 1:
                objects.append(after_verb.strip())
        
        return self._deduplicate(objects)
    
    def _extract_persons(self, sentence: str) -> List[str]:
        persons = []
        
        for pronoun in self.subject_pronouns:
            if pronoun in ["它", "它们"]:
                continue
            if pronoun in sentence:
                persons.append(pronoun)
        
        for title in self.person_titles:
            for prefix in [""] + self.person_prefixes:
                pattern = prefix + title
                if pattern in sentence and len(pattern) >= 2:
                    if pattern not in persons:
                        persons.append(pattern)
        
        patterns = [
            r'([\u4e00-\u9fa5]{2,3})同学',
            r'([\u4e00-\u9fa5]{2,3})老师',
            r'([\u4e00-\u9fa5]{2,3})经理',
            r'([\u4e00-\u9fa5]{2,3})博士',
            r'([\u4e00-\u9fa5]{2,3})先生',
            r'([\u4e00-\u9fa5]{2,3})女士',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, sentence)
            for match in matches:
                if match not in persons:
                    persons.append(match)
        
        return self._deduplicate([p for p in persons if len(p) >= 1])
    
    def _extract_places(self, sentence: str) -> List[str]:
        places = []
        
        place_patterns = [
            r'在([\u4e00-\u9fa5]+?(?:餐厅|酒店|公司|学校|医院|商店|银行|邮局|车站|机场|公园|广场|街道|路|巷|楼|层|室|号|区|市|省|国|县|镇|村|小区|大厦|中心|市场|超市|商场|家))',
            r'到([\u4e00-\u9fa5]+?(?:餐厅|酒店|公司|学校|医院|商店|银行|邮局|车站|机场|公园|广场|街道|路|巷|楼|层|室|号|区|市|省|国|县|镇|村|小区|大厦|中心|市场|超市|商场|家))',
            r'去([\u4e00-\u9fa5]+?(?:餐厅|酒店|公司|学校|医院|商店|银行|邮局|车站|机场|公园|广场|街道|路|巷|楼|层|室|号|区|市|省|国|县|镇|村|小区|大厦|中心|市场|超市|商场|家))',
        ]
        
        for pattern in place_patterns:
            matches = re.findall(pattern, sentence)
            for match in matches:
                if match and len(match) >= 2:
                    places.append(match)
        
        for keyword in ["小猪餐厅", "麦当劳", "肯德基", "星巴克", "沃尔玛", "家乐福", "淘宝", "京东"]:
            if keyword in sentence:
                places.append(keyword)
        
        return self._deduplicate(places)
    
    def _extract_times(self, sentence: str) -> List[str]:
        times = []
        
        time_patterns = [
            r'(\d{1,4}年\d{1,2}月\d{1,2}日)',
            r'(\d{1,4}年\d{1,2}月)',
            r'(\d{1,2}月\d{1,2}日)',
            r'(\d{1,2}点\d{1,2}分)',
            r'(\d{1,2}点)',
            r'(\d+)\s*个?\s*(小?时|分钟|秒|天|周|月|年)',
            r'(今天|明天|昨天|前天|后天|上周|下周|上月|下月|去年|今年|明年|上午|下午|晚上|凌晨|傍晚|深夜)',
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, sentence)
            for match in matches:
                if isinstance(match, tuple):
                    time_str = "".join(match)
                else:
                    time_str = match
                if time_str:
                    times.append(time_str)
        
        return self._deduplicate(times)
    
    def _extract_events(self, sentence: str) -> List[str]:
        events = []
        
        has_verb = any(verb in sentence for verb in self.common_verbs)
        has_event_keyword = any(kw in sentence for kw in self.event_keywords)
        
        if has_verb or has_event_keyword:
            if len(sentence) >= 4:
                events.append(sentence)
        
        return events
    
    def _extract_causes(self, sentence: str) -> List[str]:
        causes = []
        
        for keyword in self.cause_keywords:
            if keyword in sentence:
                index = sentence.find(keyword)
                cause_part = sentence[index + len(keyword):]
                cause_part = re.sub(r'[。！？，、；\s]+$', '', cause_part)
                if cause_part and len(cause_part) >= 2:
                    causes.append(cause_part)
        
        return self._deduplicate(causes)
    
    def _extract_results(self, sentence: str) -> List[str]:
        results = []
        
        result_keywords = ["结果", "最后", "终于", "最终", "于是", "因此", "所以"]
        for keyword in result_keywords:
            if keyword in sentence:
                index = sentence.find(keyword)
                result_part = sentence[index + len(keyword):]
                result_part = re.sub(r'[。！？，、；\s]+$', '', result_part)
                if result_part and len(result_part) >= 2:
                    results.append(result_part)
        
        return self._deduplicate(results)
    
    def _deduplicate(self, items: List[str]) -> List[str]:
        seen = set()
        result = []
        for item in items:
            if item and item not in seen:
                seen.add(item)
                result.append(item)
        return result
    
    def is_person_candidate(self, text: str) -> bool:
        if not text or len(text) < 1:
            return False
        
        if text in self.subject_pronouns and text not in ["它", "它们"]:
            return True
        
        for title in self.person_titles:
            if title in text:
                return True
        
        for prefix in self.person_prefixes:
            if text.startswith(prefix) and len(text) == 2:
                return True
        
        if re.match(r'^[\u4e00-\u9fa5]{2,4}$', text):
            if (text not in self.common_verbs and 
                text not in self.time_keywords and 
                text not in self.place_keywords and
                text not in self.event_keywords):
                return True
        
        return False
    
    def is_event_candidate(self, text: str) -> bool:
        if not text or len(text) < 4:
            return False
        
        has_verb = any(verb in text for verb in self.common_verbs)
        has_event_keyword = any(kw in text for kw in self.event_keywords)
        
        return has_verb or has_event_keyword


class QuestionGenerator:
    MAX_QUESTIONS_PER_LEVEL = 10
    
    def __init__(self):
        self.question_counter = 0
        self.grammar_analyzer = GrammarAnalyzer()
        self._init_question_templates()
        self._init_person_attribute_templates()
    
    def _init_question_templates(self):
        self.action_question_templates = {
            "听说": {
                QuestionCategory.TIME: "什么时候听说的？",
                QuestionCategory.PERSON: "听谁说的？",
                QuestionCategory.PLACE: "在哪里听说的？",
                QuestionCategory.CAUSE: "为什么会听说这件事？",
                QuestionCategory.PROCESS: "是怎么听说的？",
                QuestionCategory.RESULT: "听说后有什么反应？"
            },
            "看到": {
                QuestionCategory.TIME: "什么时候看到的？",
                QuestionCategory.PERSON: "谁看到的？",
                QuestionCategory.PLACE: "在哪里看到的？",
                QuestionCategory.CAUSE: "为什么会看到？",
                QuestionCategory.PROCESS: "是怎么看到的？",
                QuestionCategory.RESULT: "看到后有什么反应？"
            },
            "发现": {
                QuestionCategory.TIME: "什么时候发现的？",
                QuestionCategory.PERSON: "谁发现的？",
                QuestionCategory.PLACE: "在哪里发现的？",
                QuestionCategory.CAUSE: "为什么会发现？",
                QuestionCategory.PROCESS: "是怎么发现的？",
                QuestionCategory.RESULT: "发现后有什么反应？"
            },
            "知道": {
                QuestionCategory.TIME: "什么时候知道的？",
                QuestionCategory.PERSON: "怎么知道的？",
                QuestionCategory.PLACE: "在哪里知道的？",
                QuestionCategory.CAUSE: "为什么会知道？",
                QuestionCategory.PROCESS: "是怎么知道的？",
                QuestionCategory.RESULT: "知道后有什么反应？"
            },
            "了解": {
                QuestionCategory.TIME: "什么时候了解的？",
                QuestionCategory.PERSON: "怎么了解的？",
                QuestionCategory.PLACE: "在哪里了解的？",
                QuestionCategory.CAUSE: "为什么要了解？",
                QuestionCategory.PROCESS: "是怎么了解的？",
                QuestionCategory.RESULT: "了解后有什么收获？"
            },
            "收到": {
                QuestionCategory.TIME: "什么时候收到的？",
                QuestionCategory.PERSON: "谁收到的？",
                QuestionCategory.PLACE: "在哪里收到的？",
                QuestionCategory.CAUSE: "为什么会收到？",
                QuestionCategory.PROCESS: "是怎么收到的？",
                QuestionCategory.RESULT: "收到后有什么反应？"
            },
            "接到": {
                QuestionCategory.TIME: "什么时候接到的？",
                QuestionCategory.PERSON: "谁接到的？",
                QuestionCategory.PLACE: "在哪里接到的？",
                QuestionCategory.CAUSE: "为什么会接到？",
                QuestionCategory.PROCESS: "是怎么接到的？",
                QuestionCategory.RESULT: "接到后有什么反应？"
            },
            "告诉": {
                QuestionCategory.TIME: "什么时候告诉的？",
                QuestionCategory.PERSON: "谁告诉的？",
                QuestionCategory.PLACE: "在哪里告诉的？",
                QuestionCategory.CAUSE: "为什么要告诉？",
                QuestionCategory.PROCESS: "是怎么告诉的？",
                QuestionCategory.RESULT: "告诉后有什么反应？"
            },
            "介绍": {
                QuestionCategory.TIME: "什么时候介绍的？",
                QuestionCategory.PERSON: "谁介绍的？",
                QuestionCategory.PLACE: "在哪里介绍的？",
                QuestionCategory.CAUSE: "为什么要介绍？",
                QuestionCategory.PROCESS: "是怎么介绍的？",
                QuestionCategory.RESULT: "介绍后有什么反应？"
            },
            "推荐": {
                QuestionCategory.TIME: "什么时候推荐的？",
                QuestionCategory.PERSON: "谁推荐的？",
                QuestionCategory.PLACE: "在哪里推荐的？",
                QuestionCategory.CAUSE: "为什么要推荐？",
                QuestionCategory.PROCESS: "是怎么推荐的？",
                QuestionCategory.RESULT: "推荐后有什么反应？"
            },
            "认识": {
                QuestionCategory.TIME: "什么时候认识的？",
                QuestionCategory.PERSON: "怎么认识的？",
                QuestionCategory.PLACE: "在哪里认识的？",
                QuestionCategory.CAUSE: "为什么会认识？",
                QuestionCategory.PROCESS: "是怎么认识的？",
                QuestionCategory.RESULT: "认识后有什么交流？"
            },
            "遇见": {
                QuestionCategory.TIME: "什么时候遇见的？",
                QuestionCategory.PERSON: "遇见了谁？",
                QuestionCategory.PLACE: "在哪里遇见的？",
                QuestionCategory.CAUSE: "为什么会遇见？",
                QuestionCategory.PROCESS: "是怎么遇见的？",
                QuestionCategory.RESULT: "遇见后有什么交流？"
            },
            "吃饭": {
                QuestionCategory.TIME: "什么时候吃的饭？",
                QuestionCategory.PERSON: "和谁一起吃饭？",
                QuestionCategory.PLACE: "在哪里吃饭？",
                QuestionCategory.CAUSE: "为什么要吃饭？",
                QuestionCategory.PROCESS: "吃了什么？",
                QuestionCategory.RESULT: "花了多少钱？"
            },
            "开会": {
                QuestionCategory.TIME: "什么时候开的会？",
                QuestionCategory.PERSON: "谁参加了会议？",
                QuestionCategory.PLACE: "在哪里开的会？",
                QuestionCategory.CAUSE: "为什么要开会？",
                QuestionCategory.PROCESS: "会议内容是什么？",
                QuestionCategory.RESULT: "会议决议是什么？"
            },
            "上班": {
                QuestionCategory.TIME: "什么时候上班的？",
                QuestionCategory.PERSON: "谁上班了？",
                QuestionCategory.PLACE: "在哪里上班？",
                QuestionCategory.CAUSE: "为什么要上班？",
                QuestionCategory.PROCESS: "上班做了什么？",
                QuestionCategory.RESULT: "上班有什么收获？"
            },
            "旅游": {
                QuestionCategory.TIME: "什么时候旅游的？",
                QuestionCategory.PERSON: "和谁一起旅游？",
                QuestionCategory.PLACE: "去哪里旅游？",
                QuestionCategory.CAUSE: "为什么要旅游？",
                QuestionCategory.PROCESS: "旅游行程是怎样的？",
                QuestionCategory.RESULT: "旅游感受如何？"
            },
            "购物": {
                QuestionCategory.TIME: "什么时候购物的？",
                QuestionCategory.PERSON: "和谁一起购物？",
                QuestionCategory.PLACE: "在哪里购物？",
                QuestionCategory.CAUSE: "为什么要购物？",
                QuestionCategory.PROCESS: "买了什么东西？",
                QuestionCategory.RESULT: "花了多少钱？"
            },
            "运动": {
                QuestionCategory.TIME: "什么时候运动的？",
                QuestionCategory.PERSON: "和谁一起运动？",
                QuestionCategory.PLACE: "在哪里运动？",
                QuestionCategory.CAUSE: "为什么要运动？",
                QuestionCategory.PROCESS: "做了什么运动？",
                QuestionCategory.RESULT: "运动效果如何？"
            },
            "学习": {
                QuestionCategory.TIME: "什么时候学习的？",
                QuestionCategory.PERSON: "和谁一起学习？",
                QuestionCategory.PLACE: "在哪里学习？",
                QuestionCategory.CAUSE: "为什么要学习？",
                QuestionCategory.PROCESS: "学习了什么内容？",
                QuestionCategory.RESULT: "学习效果如何？"
            },
            "工作": {
                QuestionCategory.TIME: "什么时候工作的？",
                QuestionCategory.PERSON: "和谁一起工作？",
                QuestionCategory.PLACE: "在哪里工作？",
                QuestionCategory.CAUSE: "为什么要工作？",
                QuestionCategory.PROCESS: "工作内容是什么？",
                QuestionCategory.RESULT: "工作成果如何？"
            },
            "睡觉": {
                QuestionCategory.TIME: "什么时候睡觉的？",
                QuestionCategory.PERSON: "谁睡觉了？",
                QuestionCategory.PLACE: "在哪里睡觉？",
                QuestionCategory.CAUSE: "为什么要睡觉？",
                QuestionCategory.PROCESS: "睡得怎么样？",
                QuestionCategory.RESULT: "睡醒后感觉如何？"
            },
            "休息": {
                QuestionCategory.TIME: "什么时候休息的？",
                QuestionCategory.PERSON: "谁休息了？",
                QuestionCategory.PLACE: "在哪里休息？",
                QuestionCategory.CAUSE: "为什么要休息？",
                QuestionCategory.PROCESS: "怎么休息的？",
                QuestionCategory.RESULT: "休息效果如何？"
            },
            "看电影": {
                QuestionCategory.TIME: "什么时候看的电影？",
                QuestionCategory.PERSON: "和谁一起看电影？",
                QuestionCategory.PLACE: "在哪里看的电影？",
                QuestionCategory.CAUSE: "为什么要看电影？",
                QuestionCategory.PROCESS: "看的什么电影？",
                QuestionCategory.RESULT: "电影好看吗？"
            },
            "看电视": {
                QuestionCategory.TIME: "什么时候看的电视？",
                QuestionCategory.PERSON: "和谁一起看电视？",
                QuestionCategory.PLACE: "在哪里看电视？",
                QuestionCategory.CAUSE: "为什么要看电视？",
                QuestionCategory.PROCESS: "看的什么节目？",
                QuestionCategory.RESULT: "节目好看吗？"
            },
            "看书": {
                QuestionCategory.TIME: "什么时候看的书？",
                QuestionCategory.PERSON: "和谁一起看书？",
                QuestionCategory.PLACE: "在哪里看书？",
                QuestionCategory.CAUSE: "为什么要看书？",
                QuestionCategory.PROCESS: "看的什么书？",
                QuestionCategory.RESULT: "书好看吗？"
            },
            "上网": {
                QuestionCategory.TIME: "什么时候上网的？",
                QuestionCategory.PERSON: "和谁一起上网？",
                QuestionCategory.PLACE: "在哪里上网？",
                QuestionCategory.CAUSE: "为什么要上网？",
                QuestionCategory.PROCESS: "上网做了什么？",
                QuestionCategory.RESULT: "上网有什么收获？"
            },
            "聊天": {
                QuestionCategory.TIME: "什么时候聊天的？",
                QuestionCategory.PERSON: "和谁聊天？",
                QuestionCategory.PLACE: "在哪里聊天？",
                QuestionCategory.CAUSE: "为什么要聊天？",
                QuestionCategory.PROCESS: "聊了什么内容？",
                QuestionCategory.RESULT: "聊天有什么收获？"
            },
            "打电话": {
                QuestionCategory.TIME: "什么时候打的电话？",
                QuestionCategory.PERSON: "给谁打电话？",
                QuestionCategory.PLACE: "在哪里打电话？",
                QuestionCategory.CAUSE: "为什么要打电话？",
                QuestionCategory.PROCESS: "电话内容是什么？",
                QuestionCategory.RESULT: "电话结果如何？"
            },
            "发邮件": {
                QuestionCategory.TIME: "什么时候发的邮件？",
                QuestionCategory.PERSON: "给谁发邮件？",
                QuestionCategory.PLACE: "在哪里发邮件？",
                QuestionCategory.CAUSE: "为什么要发邮件？",
                QuestionCategory.PROCESS: "邮件内容是什么？",
                QuestionCategory.RESULT: "邮件结果如何？"
            },
            "发短信": {
                QuestionCategory.TIME: "什么时候发的短信？",
                QuestionCategory.PERSON: "给谁发短信？",
                QuestionCategory.PLACE: "在哪里发短信？",
                QuestionCategory.CAUSE: "为什么要发短信？",
                QuestionCategory.PROCESS: "短信内容是什么？",
                QuestionCategory.RESULT: "短信结果如何？"
            }
        }
        
        self.default_question_templates = {
            QuestionCategory.TIME: [
                "这个事件发生在什么时候？",
                "具体时间是几点几分？",
                "是哪个日期？星期几？"
            ],
            QuestionCategory.PLACE: [
                "这个事件发生在哪里？",
                "具体地点是哪里？",
                "在哪个城市哪个区域？"
            ],
            QuestionCategory.PERSON: [
                "谁参与了这个事件？",
                "这个事件的主体是谁？",
                "涉及哪些人物？"
            ],
            QuestionCategory.CAUSE: [
                "这个事件为什么会发生？",
                "事件的起因是什么？",
                "是什么原因导致了这个事件？"
            ],
            QuestionCategory.PROCESS: [
                "这个事件是如何发生的？",
                "事件的经过是怎样的？",
                "具体过程是什么？"
            ],
            QuestionCategory.RESULT: [
                "这个事件的结果是什么？",
                "事件最终如何结束？",
                "产生了什么后果？"
            ]
        }
    
    def _init_person_attribute_templates(self):
        self.person_attribute_templates = {
            PersonAttribute.NAME: "{person}的姓名是什么？",
            PersonAttribute.GENDER: "{person}的性别是什么？",
            PersonAttribute.AGE: "{person}的年龄是多少？",
            PersonAttribute.ID_CARD: "{person}的身份证号是多少？",
            PersonAttribute.PHONE: "{person}的手机号是多少？",
            PersonAttribute.ADDRESS: "{person}的住址是哪里？",
            PersonAttribute.OCCUPATION: "{person}的职业是什么？",
            PersonAttribute.EDUCATION: "{person}的学历是什么？",
            PersonAttribute.MARITAL_STATUS: "{person}的婚姻状况是什么？",
            PersonAttribute.NATIONALITY: "{person}的国籍是什么？",
            PersonAttribute.RELATIONSHIP: "{person}与这个事件有什么关系？"
        }
    
    def _generate_question_id(self) -> str:
        self.question_counter += 1
        return f"q_{self.question_counter}_{uuid.uuid4().hex[:8]}"
    
    def _find_main_action(self, text: str) -> Optional[str]:
        for action in self.action_question_templates.keys():
            if action in text:
                return action
        return None
    
    def _generate_optimized_question(self, category: QuestionCategory, analysis: Dict, 
                                      main_action: Optional[str] = None) -> str:
        if main_action and main_action in self.action_question_templates:
            templates = self.action_question_templates[main_action]
            if category in templates:
                return templates[category]
        
        verbs = analysis.get("verbs", [])
        subjects = analysis.get("subjects", [])
        objects = analysis.get("objects", [])
        
        if verbs:
            main_verb = verbs[0]
            subject = subjects[0] if subjects else ""
            obj = objects[0] if objects else ""
            
            if category == QuestionCategory.TIME:
                if main_verb.endswith("了"):
                    return f"什么时候{main_verb}的？"
                return f"什么时候{main_verb}？"
            
            elif category == QuestionCategory.PLACE:
                return f"在哪里{main_verb}？"
            
            elif category == QuestionCategory.PERSON:
                if subject and subject not in ["我", "你", "他", "她", "我们", "你们", "他们", "她们"]:
                    return f"{main_verb}的是谁？"
                return f"和谁一起{main_verb}？"
            
            elif category == QuestionCategory.CAUSE:
                return f"为什么要{main_verb}？"
            
            elif category == QuestionCategory.PROCESS:
                return f"是怎么{main_verb}的？"
            
            elif category == QuestionCategory.RESULT:
                return f"{main_verb}的结果是什么？"
        
        return self.default_question_templates[category][0]
    
    def generate_level1_questions(self, event_text: str) -> List[Question]:
        questions = []
        
        analysis = self.grammar_analyzer.analyze(event_text)
        main_action = self._find_main_action(event_text)
        
        if main_action and main_action in self.action_question_templates:
            templates = self.action_question_templates[main_action]
            for category, q_text in templates.items():
                question = Question(
                    id=self._generate_question_id(),
                    text=q_text,
                    category=category,
                    level=1
                )
                questions.append(question)
        else:
            for category in [QuestionCategory.TIME, QuestionCategory.PLACE, 
                             QuestionCategory.PERSON, QuestionCategory.CAUSE,
                             QuestionCategory.PROCESS, QuestionCategory.RESULT]:
                q_text = self._generate_optimized_question(category, analysis, main_action)
                question = Question(
                    id=self._generate_question_id(),
                    text=q_text,
                    category=category,
                    level=1
                )
                questions.append(question)
        
        return questions[:self.MAX_QUESTIONS_PER_LEVEL]
    
    def generate_person_attribute_questions(self, person: str, level: int, 
                                            parent_answer_id: str) -> List[Question]:
        questions = []
        
        if not self.grammar_analyzer.is_person_candidate(person):
            return questions
        
        if len(person) < 2 and person not in ["我", "你", "他", "她"]:
            return questions
        
        key_attributes = [
            PersonAttribute.NAME,
            PersonAttribute.GENDER,
            PersonAttribute.AGE,
            PersonAttribute.PHONE,
            PersonAttribute.OCCUPATION,
            PersonAttribute.RELATIONSHIP
        ]
        
        for attr in key_attributes:
            template = self.person_attribute_templates[attr]
            q_text = template.replace("{person}", person)
            
            question = Question(
                id=self._generate_question_id(),
                text=q_text,
                category=QuestionCategory.PERSON,
                level=level,
                target_person=person,
                person_attribute=attr,
                parent_answer_id=parent_answer_id
            )
            questions.append(question)
        
        return questions
    
    def generate_questions_for_event(self, event_text: str, level: int,
                                       parent_answer_id: str) -> List[Question]:
        questions = []
        
        if not self.grammar_analyzer.is_event_candidate(event_text):
            return questions
        
        analysis = self.grammar_analyzer.analyze(event_text)
        main_action = self._find_main_action(event_text)
        
        if main_action and main_action in self.action_question_templates:
            templates = self.action_question_templates[main_action]
            for category, q_text in templates.items():
                question = Question(
                    id=self._generate_question_id(),
                    text=q_text,
                    category=category,
                    level=level,
                    target_event_id=parent_answer_id,
                    parent_answer_id=parent_answer_id
                )
                questions.append(question)
        else:
            for category in [QuestionCategory.TIME, QuestionCategory.PLACE, 
                             QuestionCategory.PERSON, QuestionCategory.CAUSE,
                             QuestionCategory.PROCESS, QuestionCategory.RESULT]:
                q_text = self._generate_optimized_question(category, analysis, main_action)
                question = Question(
                    id=self._generate_question_id(),
                    text=q_text,
                    category=category,
                    level=level,
                    target_event_id=parent_answer_id,
                    parent_answer_id=parent_answer_id
                )
                questions.append(question)
        
        return questions[:self.MAX_QUESTIONS_PER_LEVEL]
    
    def generate_questions_for_answer(self, answer_id: str, answer_text: str,
                                        parent_category: QuestionCategory,
                                        current_level: int,
                                        parent_question_text: str = "") -> List[Question]:
        questions = []
        
        if not answer_text or not answer_text.strip():
            return questions
        
        next_level = current_level + 1
        
        analysis = self.grammar_analyzer.analyze(answer_text)
        
        persons = analysis.get("persons", [])
        for person in persons:
            if self.grammar_analyzer.is_person_candidate(person):
                person_questions = self.generate_person_attribute_questions(
                    person, next_level, answer_id
                )
                questions.extend(person_questions)
        
        if parent_category in [QuestionCategory.CAUSE, QuestionCategory.PROCESS, QuestionCategory.RESULT]:
            events = analysis.get("events", [])
            for event in events:
                if self.grammar_analyzer.is_event_candidate(event):
                    event_questions = self.generate_questions_for_event(
                        event, next_level, answer_id
                    )
                    questions.extend(event_questions)
        
        return questions[:self.MAX_QUESTIONS_PER_LEVEL]
    
    def has_new_events(self, answer_text: str) -> bool:
        if not answer_text or not answer_text.strip():
            return False
        
        analysis = self.grammar_analyzer.analyze(answer_text)
        events = analysis.get("events", [])
        
        return len(events) > 0
    
    def analyze_text(self, text: str) -> Dict:
        return self.grammar_analyzer.analyze(text)
