from typing import List, Dict, Optional, Tuple
from models import Question, QuestionCategory, PersonAttribute, Event
import uuid
import re


class QuestionGenerator:
    MAX_QUESTIONS_PER_LEVEL = 10
    
    def __init__(self):
        self.question_counter = 0
        self._init_patterns()
        self._init_templates()
        self._init_question_transformers()
    
    def _init_patterns(self):
        self.person_titles = [
            "总", "经理", "总监", "老板", "老师", "教授", "医生", "护士",
            "工程师", "设计师", "会计", "律师", "警察", "消防员", "司机",
            "同学", "同事", "朋友", "家人", "亲戚", "领导", "下属", "员工",
            "主管", "主任", "部长", "局长", "厅长", "主席", "书记", "委员",
            "董事", "监事", "总裁", "CEO", "CTO", "CFO", "创始人", "合伙人",
            "爸爸", "妈妈", "父亲", "母亲", "爷爷", "奶奶", "外公", "外婆",
            "哥哥", "姐姐", "弟弟", "妹妹", "儿子", "女儿", "丈夫", "妻子",
            "先生", "女士", "小姐", "同志", "师傅", "客户", "顾客", "患者"
        ]
        
        self.person_prefixes = ["老", "小", "大", "阿"]
        self.conjunctions = ["和", "与", "及", "跟", "、", "，", ",", "；", ";", "还有", "以及", "同"]
        
        self.event_verbs = [
            "吃", "喝", "玩", "乐", "买", "卖", "去", "来", "走", "跑",
            "跳", "飞", "游", "睡", "工作", "学习", "上班", "下班", "开会",
            "吃饭", "睡觉", "旅游", "购物", "运动", "休息", "娱乐", "看",
            "听", "说", "读", "写", "做", "打", "踢", "送", "收", "借", "还",
            "签", "订", "报", "申", "办", "理", "处", "罚", "奖", "评", "审",
            "批", "核", "查", "验", "检", "试", "考", "学", "教", "发", "邮",
            "寄", "领", "拿", "带", "搬", "运", "改", "变", "调", "整", "管",
            "组", "织", "安", "排", "计", "划", "策", "划", "设", "开", "研",
            "生", "产", "制", "造", "加", "工", "包", "装", "销", "售", "推",
            "宣", "传", "营", "销", "促", "销", "维", "修", "保", "养", "清",
            "整", "理", "摆", "介", "讲", "解", "说", "推", "荐", "教", "育",
            "培", "训", "指", "导", "帮", "助", "协", "支", "援", "救", "助",
            "捐", "赠", "分", "配", "发", "放", "共", "享", "合", "作", "联",
            "兼", "并", "收", "购", "租", "入", "住", "离", "开", "进", "入",
            "出", "发", "旅", "行", "出", "差", "探", "访", "拜", "会", "见",
            "见", "面", "约", "会", "聚", "宴", "请", "聚", "餐", "用", "餐",
            "进", "食", "饮", "用", "服", "用", "使", "用", "操", "作", "管",
            "负", "责", "主", "管", "经", "办", "承", "办", "接", "办", "督",
            "查", "答", "复", "回", "应", "反", "馈", "处", "理", "解", "决",
            "审", "核", "查", "阅", "查", "找", "查", "询", "查", "证", "核",
            "落", "实", "执", "行", "实", "施", "实", "践", "实", "现", "达",
            "成", "完", "成", "结", "束", "结", "果", "结", "论", "结", "算",
            "付", "款", "收", "款", "交", "款", "还", "款", "借", "款", "贷",
            "存", "款", "取", "款", "转", "款", "汇", "款", "兑", "换", "提",
            "配", "送", "发", "货", "收", "货", "交", "货", "提", "货", "装",
            "卸", "搬", "运", "转", "运", "中", "转", "调", "拨", "调", "度",
            "调", "查", "调", "研", "协", "调", "协", "商", "协", "作", "配",
            "安", "装", "调", "试", "测", "试", "试", "用", "验", "收", "交",
            "移", "交", "接", "管", "接", "收", "接", "待", "招", "聘", "招",
            "投", "标", "开", "标", "评", "标", "中", "标", "签", "约", "填",
            "编", "制", "撰", "写", "创", "作", "制", "作", "打", "印", "复",
            "扫", "描", "传", "真", "邮", "件", "邮", "递", "快", "递", "分",
            "整", "理", "归", "档", "存", "档", "保", "管", "储", "存", "维",
            "护", "维", "修", "保", "养", "清", "洁", "打", "扫", "拖", "地",
            "擦", "洗", "清", "洗", "整", "治", "整", "顿", "整", "改", "改",
            "造", "改", "进", "优", "化", "提", "高", "提", "升", "降", "低",
            "减", "少", "增", "加", "扩", "大", "缩", "小", "开", "展", "开",
            "启", "关", "闭", "停", "止", "暂", "停", "中", "断", "继", "续",
            "持", "续", "延", "长", "缩", "短", "加", "快", "减", "慢", "加",
            "启", "动", "开", "机", "关", "机", "锁", "开", "解", "锁"
        ]
        
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
            "买车", "修车", "保养", "加油", "停车", "开车", "打车", "乘车",
            "吃饭", "喝酒", "喝茶", "喝咖啡", "购物", "逛街", "看电影", "看电视",
            "看书", "读报", "上网", "聊天", "打电话", "发邮件", "发短信", "发微信"
        ]
    
    def _init_templates(self):
        self.six_elements_templates = {
            QuestionCategory.TIME: [
                "这个事件发生在什么时候？",
                "具体时间是几点几分？",
                "是哪个日期？星期几？",
                "持续了多长时间？",
                "从什么时候开始，到什么时候结束？"
            ],
            QuestionCategory.PLACE: [
                "这个事件发生在哪里？",
                "具体地点是哪里？",
                "在哪个城市哪个区域？",
                "具体地址是什么？",
                "现场环境如何？"
            ],
            QuestionCategory.PERSON: [
                "谁参与了这个事件？",
                "这个事件的主体是谁？",
                "涉及哪些人物？",
                "各方人员有哪些？",
                "关键人物是谁？"
            ],
            QuestionCategory.CAUSE: [
                "这个事件为什么会发生？",
                "事件的起因是什么？",
                "是什么原因导致了这个事件？",
                "触发事件的因素有哪些？",
                "背景原因是什么？"
            ],
            QuestionCategory.PROCESS: [
                "这个事件是如何发生的？",
                "事件的经过是怎样的？",
                "具体过程是什么？",
                "有哪些关键步骤？",
                "事情是如何发展的？"
            ],
            QuestionCategory.RESULT: [
                "这个事件的结果是什么？",
                "事件最终如何结束？",
                "产生了什么后果？",
                "有什么影响？",
                "各方的得失是什么？"
            ]
        }
        
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
        
        self.smart_event_patterns = {
            "上课": {
                QuestionCategory.TIME: ["什么时候上课？", "上课持续了多久？"],
                QuestionCategory.PLACE: ["在哪个教室上课？", "上课地点在哪里？"],
                QuestionCategory.PERSON: ["谁上课了？", "老师是谁？", "和谁一起上课？"],
                QuestionCategory.CAUSE: ["为什么要上这节课？", "这节课的目的是什么？"],
                QuestionCategory.PROCESS: ["上课的内容是什么？", "老师讲了什么？"],
                QuestionCategory.RESULT: ["上课收获了什么？", "布置了什么作业？"]
            },
            "吃饭": {
                QuestionCategory.TIME: ["什么时候吃的饭？", "吃饭花了多长时间？"],
                QuestionCategory.PLACE: ["在哪里吃的饭？", "具体是哪家餐厅？"],
                QuestionCategory.PERSON: ["谁吃饭了？", "和谁一起吃的饭？"],
                QuestionCategory.CAUSE: ["为什么要吃这顿饭？", "是什么场合？"],
                QuestionCategory.PROCESS: ["吃了什么？", "饭菜味道如何？"],
                QuestionCategory.RESULT: ["花费了多少钱？", "谁结的账？"]
            },
            "工作": {
                QuestionCategory.TIME: ["什么时候开始工作的？", "工作了多长时间？"],
                QuestionCategory.PLACE: ["在哪里工作？", "工作地点具体在哪里？"],
                QuestionCategory.PERSON: ["谁在工作？", "同事有哪些？", "领导是谁？"],
                QuestionCategory.CAUSE: ["为什么要做这项工作？", "工作的目的是什么？"],
                QuestionCategory.PROCESS: ["工作内容是什么？", "具体做了什么？"],
                QuestionCategory.RESULT: ["工作完成情况如何？", "有什么成果？"]
            },
            "开会": {
                QuestionCategory.TIME: ["什么时候开的会？", "会议持续了多久？"],
                QuestionCategory.PLACE: ["在哪里开的会？", "会议地点具体在哪里？"],
                QuestionCategory.PERSON: ["谁参加了会议？", "主持人是谁？"],
                QuestionCategory.CAUSE: ["为什么要开这个会？", "会议目的是什么？"],
                QuestionCategory.PROCESS: ["会议内容是什么？", "讨论了什么议题？"],
                QuestionCategory.RESULT: ["会议决议是什么？", "达成了什么共识？"]
            },
            "旅游": {
                QuestionCategory.TIME: ["什么时候去旅游的？", "旅游了几天？"],
                QuestionCategory.PLACE: ["去哪里旅游了？", "具体去了哪些景点？"],
                QuestionCategory.PERSON: ["谁去旅游了？", "和谁一起去的？"],
                QuestionCategory.CAUSE: ["为什么选择去这里旅游？", "旅游目的是什么？"],
                QuestionCategory.PROCESS: ["旅游行程是怎样的？", "每天做了什么？"],
                QuestionCategory.RESULT: ["旅游感受如何？", "花费了多少钱？"]
            },
            "购物": {
                QuestionCategory.TIME: ["什么时候购物的？", "购物花了多长时间？"],
                QuestionCategory.PLACE: ["在哪里购物的？", "具体是哪家商店？"],
                QuestionCategory.PERSON: ["谁购物了？", "和谁一起购物的？"],
                QuestionCategory.CAUSE: ["为什么要买这些东西？", "购物目的是什么？"],
                QuestionCategory.PROCESS: ["买了什么东西？", "购物过程如何？"],
                QuestionCategory.RESULT: ["花费了多少钱？", "对商品满意吗？"]
            },
            "运动": {
                QuestionCategory.TIME: ["什么时候运动的？", "运动了多长时间？"],
                QuestionCategory.PLACE: ["在哪里运动的？", "具体是哪个场地？"],
                QuestionCategory.PERSON: ["谁运动了？", "和谁一起运动的？"],
                QuestionCategory.CAUSE: ["为什么要运动？", "运动目的是什么？"],
                QuestionCategory.PROCESS: ["做了什么运动？", "运动过程如何？"],
                QuestionCategory.RESULT: ["运动效果如何？", "有什么感受？"]
            }
        }
    
    def _init_question_transformers(self):
        self.time_transformers = [
            (r'我([\u4e00-\u9fa5]{1,4})[了过]', lambda m: f"什么时候{m.group(1)}的？"),
            (r'([\u4e00-\u9fa5]{1,4})了[我他她它]', lambda m: f"什么时候{m.group(1)}的？"),
            (r'听说', lambda m: "什么时候听说的？"),
            (r'看到', lambda m: "什么时候看到的？"),
            (r'发现', lambda m: "什么时候发现的？"),
            (r'知道', lambda m: "什么时候知道的？"),
            (r'了解', lambda m: "什么时候了解的？"),
            (r'收到', lambda m: "什么时候收到的？"),
            (r'接到', lambda m: "什么时候接到的？"),
            (r'接到', lambda m: "什么时候接到的？"),
            (r'收到', lambda m: "什么时候收到的？"),
            (r'去了', lambda m: "什么时候去的？"),
            (r'来了', lambda m: "什么时候来的？"),
            (r'走了', lambda m: "什么时候走的？"),
            (r'买了', lambda m: "什么时候买的？"),
            (r'卖了', lambda m: "什么时候卖的？"),
            (r'吃了', lambda m: "什么时候吃的？"),
            (r'喝了', lambda m: "什么时候喝的？"),
            (r'玩了', lambda m: "什么时候玩的？"),
            (r'工作了', lambda m: "什么时候工作的？"),
            (r'学习了', lambda m: "什么时候学习的？"),
            (r'开会了', lambda m: "什么时候开会的？"),
            (r'旅游了', lambda m: "什么时候旅游的？"),
            (r'购物了', lambda m: "什么时候购物的？"),
            (r'运动了', lambda m: "什么时候运动的？"),
        ]
        
        self.place_transformers = [
            (r'我([\u4e00-\u9fa5]{1,4})[了过]', lambda m: f"在哪里{m.group(1)}的？"),
            (r'去了', lambda m: "去了哪里？"),
            (r'来了', lambda m: "来自哪里？"),
            (r'在', lambda m: "具体在哪里？"),
            (r'到', lambda m: "到了哪里？"),
        ]
        
        self.person_transformers = [
            (r'和([\u4e00-\u9fa5]{1,4})一起', lambda m: f"{m.group(1)}是谁？"),
            (r'跟([\u4e00-\u9fa5]{1,4})一起', lambda m: f"{m.group(1)}是谁？"),
            (r'被([\u4e00-\u9fa5]{1,4})', lambda m: f"{m.group(1)}是谁？"),
            (r'([\u4e00-\u9fa5]{2,3}[老师经理老板医生])', lambda m: f"{m.group(1)}是谁？"),
        ]
        
        self.cause_transformers = [
            (r'因为', lambda m: "具体原因是什么？"),
            (r'由于', lambda m: "具体原因是什么？"),
            (r'为了', lambda m: "目的是什么？"),
            (r'想要', lambda m: "为什么想要？"),
            (r'需要', lambda m: "为什么需要？"),
        ]
        
        self.process_transformers = [
            (r'如何', lambda m: "具体是如何做的？"),
            (r'怎么', lambda m: "具体是怎么做的？"),
        ]
        
        self.result_transformers = [
            (r'结果', lambda m: "具体结果是什么？"),
            (r'最后', lambda m: "最后怎么样了？"),
            (r'终于', lambda m: "终于怎么样了？"),
        ]
    
    def _generate_question_id(self) -> str:
        self.question_counter += 1
        return f"q_{self.question_counter}_{uuid.uuid4().hex[:8]}"
    
    def _extract_person_entities(self, text: str) -> List[str]:
        entities = []
        
        for conj in self.conjunctions:
            text = text.replace(conj, "|")
        
        parts = re.split(r'[|、，,；;\s]+', text)
        parts = [p.strip() for p in parts if p.strip()]
        
        for part in parts:
            if len(part) >= 1:
                for title in self.person_titles:
                    if title in part and len(part) > len(title):
                        entities.append(part)
                        break
                else:
                    if len(part) >= 2 or (len(part) == 1 and part[0] in self.person_prefixes):
                        entities.append(part)
        
        entities = [e for e in entities if len(e) >= 1]
        return entities
    
    def _extract_event_entities(self, text: str) -> List[str]:
        events = []
        sentences = re.split(r'[。！？；;.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            has_event_verb = any(verb in sentence for verb in self.event_verbs)
            has_event_keyword = any(kw in sentence for kw in self.event_keywords)
            
            if has_event_verb or has_event_keyword:
                if len(sentence) >= 4:
                    events.append(sentence)
        
        return events
    
    def _generate_natural_question(self, event_text: str, category: QuestionCategory) -> str:
        transformers = {
            QuestionCategory.TIME: self.time_transformers,
            QuestionCategory.PLACE: self.place_transformers,
            QuestionCategory.PERSON: self.person_transformers,
            QuestionCategory.CAUSE: self.cause_transformers,
            QuestionCategory.PROCESS: self.process_transformers,
            QuestionCategory.RESULT: self.result_transformers,
        }
        
        transformer_list = transformers.get(category, [])
        
        for pattern, transformer in transformer_list:
            match = re.search(pattern, event_text)
            if match:
                result = transformer(match)
                if result and len(result) > 0:
                    return result
        
        simplified = self._simplify_event(event_text)
        
        category_suffixes = {
            QuestionCategory.TIME: "发生在什么时候？",
            QuestionCategory.PLACE: "发生在哪里？",
            QuestionCategory.PERSON: "谁参与了？",
            QuestionCategory.CAUSE: "为什么会发生？",
            QuestionCategory.PROCESS: "具体是怎样的？",
            QuestionCategory.RESULT: "结果是什么？",
        }
        
        default_questions = {
            QuestionCategory.TIME: "这个事件发生在什么时候？",
            QuestionCategory.PLACE: "这个事件发生在哪里？",
            QuestionCategory.PERSON: "谁参与了这个事件？",
            QuestionCategory.CAUSE: "这个事件为什么会发生？",
            QuestionCategory.PROCESS: "这个事件是如何发生的？",
            QuestionCategory.RESULT: "这个事件的结果是什么？",
        }
        
        if simplified and len(simplified) <= 15:
            return f"{simplified}{category_suffixes.get(category, default_questions.get(category, ''))}"
        
        return default_questions.get(category, "请提供更多信息。")
    
    def _simplify_event(self, event_text: str) -> str:
        event_text = event_text.strip()
        
        event_text = re.sub(r'^我', '', event_text)
        event_text = re.sub(r'^他', '', event_text)
        event_text = re.sub(r'^她', '', event_text)
        event_text = re.sub(r'^它', '', event_text)
        event_text = re.sub(r'^我们', '', event_text)
        event_text = re.sub(r'^他们', '', event_text)
        event_text = re.sub(r'^她们', '', event_text)
        
        event_text = re.sub(r'[了过]$', '', event_text)
        event_text = re.sub(r'[了过]\s*$', '', event_text)
        
        return event_text.strip()
    
    def generate_level1_questions(self, event_text: str) -> List[Question]:
        questions = []
        
        matched_pattern = None
        for keyword, pattern in self.smart_event_patterns.items():
            if keyword in event_text:
                matched_pattern = pattern
                break
        
        if matched_pattern:
            for category in [QuestionCategory.TIME, QuestionCategory.PLACE, 
                             QuestionCategory.PERSON, QuestionCategory.CAUSE,
                             QuestionCategory.PROCESS, QuestionCategory.RESULT]:
                if category in matched_pattern:
                    for q_text in matched_pattern[category][:2]:
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
                templates = self.six_elements_templates[category]
                for q_text in templates[:2]:
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
        
        if not person or len(person) < 2:
            return questions
        
        if any(title in person for title in self.person_titles):
            pass
        elif len(person) == 2 and person[0] in self.person_prefixes:
            pass
        else:
            if not re.match(r'^[\u4e00-\u9fa5]{2,4}$', person):
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
        
        for category in [QuestionCategory.TIME, QuestionCategory.PLACE, 
                         QuestionCategory.PERSON, QuestionCategory.CAUSE,
                         QuestionCategory.PROCESS, QuestionCategory.RESULT]:
            q_text = self._generate_natural_question(event_text, category)
            
            if q_text:
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
        
        persons = self._extract_person_entities(answer_text)
        for person in persons:
            if person and len(person) >= 2:
                person_questions = self.generate_person_attribute_questions(
                    person, next_level, answer_id
                )
                questions.extend(person_questions)
        
        if parent_category in [QuestionCategory.CAUSE, QuestionCategory.PROCESS, QuestionCategory.RESULT]:
            events = self._extract_event_entities(answer_text)
            for event in events:
                if event and len(event) >= 4:
                    event_questions = self.generate_questions_for_event(
                        event, next_level, answer_id
                    )
                    questions.extend(event_questions)
        
        return questions[:self.MAX_QUESTIONS_PER_LEVEL]
    
    def has_new_events(self, answer_text: str) -> bool:
        if not answer_text or not answer_text.strip():
            return False
        
        events = self._extract_event_entities(answer_text)
        return len(events) > 0
