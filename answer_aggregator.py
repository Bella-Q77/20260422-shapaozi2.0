import re
from typing import Dict, List, Optional
from models import Event, Question, Answer, QuestionCategory, PersonAttribute


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
        
        self.cause_keywords = ["因为", "由于", "原因是", "为了", "所以", "因此", "于是", "结果", "导致", "引起", "造成", "使得", "以便", "以致"]
        self.result_keywords = ["结果", "最后", "终于", "最终", "于是", "因此", "所以", "最终", "最后"]
        
        self.time_patterns = [
            r'(\d{1,4}年\d{1,2}月\d{1,2}日)',
            r'(\d{1,4}年\d{1,2}月)',
            r'(\d{1,2}月\d{1,2}日)',
            r'(\d{1,2}点\d{1,2}分)',
            r'(\d{1,2}点)',
            r'(\d+)\s*个?\s*(小?时|分钟|秒|天|周|月|年)',
            r'(今天|明天|昨天|前天|后天|上周|下周|上月|下月|去年|今年|明年|上午|下午|晚上|凌晨|傍晚|深夜)',
        ]
        
        self.place_patterns = [
            r'在([\u4e00-\u9fa5]+?(?:餐厅|酒店|公司|学校|医院|商店|银行|邮局|车站|机场|公园|广场|街道|路|巷|楼|层|室|号|区|市|省|国|县|镇|村|小区|大厦|中心|市场|超市|商场|家))',
            r'到([\u4e00-\u9fa5]+?(?:餐厅|酒店|公司|学校|医院|商店|银行|邮局|车站|机场|公园|广场|街道|路|巷|楼|层|室|号|区|市|省|国|县|镇|村|小区|大厦|中心|市场|超市|商场|家))',
            r'去([\u4e00-\u9fa5]+?(?:餐厅|酒店|公司|学校|医院|商店|银行|邮局|车站|机场|公园|广场|街道|路|巷|楼|层|室|号|区|市|省|国|县|镇|村|小区|大厦|中心|市场|超市|商场|家))',
        ]
        
        self.duration_patterns = [
            r'(\d+)\s*个?\s*(小?时|分钟|秒|天|周|月|年)',
            r'持续了?\s*\d+',
            r'花了?\s*\d+',
            r'用了?\s*\d+',
        ]
    
    def analyze(self, text: str) -> Dict:
        result = {
            "original_text": text,
            "verbs": [],
            "subjects": [],
            "objects": [],
            "persons": [],
            "places": [],
            "times": [],
            "is_duration": False,
            "causes": [],
            "results": []
        }
        
        result["verbs"] = self._extract_verbs(text)
        result["subjects"] = self._extract_subjects(text, result["verbs"])
        result["objects"] = self._extract_objects(text, result["verbs"])
        result["persons"] = self._extract_persons(text)
        result["places"] = self._extract_places(text)
        result["times"] = self._extract_times(text)
        result["is_duration"] = self._is_duration(text)
        result["causes"] = self._extract_causes(text)
        result["results"] = self._extract_results(text)
        
        return result
    
    def _extract_verbs(self, text: str) -> List[str]:
        verbs = []
        for verb in sorted(self.common_verbs, key=len, reverse=True):
            if verb in text:
                verbs.append(verb)
        return verbs
    
    def _extract_subjects(self, text: str, verbs: List[str]) -> List[str]:
        subjects = []
        
        if not verbs:
            for pronoun in self.subject_pronouns:
                if pronoun in text:
                    subjects.append(pronoun)
            return subjects
        
        main_verb = verbs[0]
        verb_index = text.find(main_verb)
        
        if verb_index > 0:
            before_verb = text[:verb_index]
            for pronoun in self.subject_pronouns:
                if pronoun in before_verb:
                    subjects.append(pronoun)
            
            for title in self.person_titles:
                if title in before_verb:
                    subjects.append(title)
        
        if not subjects:
            subjects = self._extract_persons(text)
        
        return self._deduplicate(subjects)
    
    def _extract_objects(self, text: str, verbs: List[str]) -> List[str]:
        objects = []
        
        if not verbs:
            return objects
        
        main_verb = verbs[0]
        verb_index = text.find(main_verb)
        
        if verb_index >= 0:
            after_verb = text[verb_index + len(main_verb):]
            after_verb = re.sub(r'[。！？，、；\s]+$', '', after_verb)
            if after_verb and len(after_verb) >= 1:
                objects.append(after_verb.strip())
        
        return self._deduplicate(objects)
    
    def _extract_persons(self, text: str) -> List[str]:
        persons = []
        
        for pronoun in self.subject_pronouns:
            if pronoun in ["它", "它们"]:
                continue
            if pronoun in text:
                persons.append(pronoun)
        
        for title in self.person_titles:
            if title in text:
                persons.append(title)
        
        patterns = [
            r'([\u4e00-\u9fa5]{2,3})同学',
            r'([\u4e00-\u9fa5]{2,3})老师',
            r'([\u4e00-\u9fa5]{2,3})经理',
            r'([\u4e00-\u9fa5]{2,3})博士',
            r'([\u4e00-\u9fa5]{2,3})先生',
            r'([\u4e00-\u9fa5]{2,3})女士',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match not in persons:
                    persons.append(match)
        
        return self._deduplicate([p for p in persons if len(p) >= 1])
    
    def _extract_places(self, text: str) -> List[str]:
        places = []
        
        for pattern in self.place_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match and len(match) >= 2:
                    places.append(match)
        
        for keyword in ["小猪餐厅", "麦当劳", "肯德基", "星巴克", "沃尔玛", "家乐福", "淘宝", "京东"]:
            if keyword in text:
                places.append(keyword)
        
        return self._deduplicate(places)
    
    def _extract_times(self, text: str) -> List[str]:
        times = []
        
        for pattern in self.time_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    time_str = "".join(match)
                else:
                    time_str = match
                if time_str:
                    times.append(time_str)
        
        return self._deduplicate(times)
    
    def _is_duration(self, text: str) -> bool:
        if not text:
            return False
        
        for pattern in self.duration_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _extract_causes(self, text: str) -> List[str]:
        causes = []
        
        for keyword in self.cause_keywords:
            if keyword in text:
                index = text.find(keyword)
                cause_part = text[index + len(keyword):]
                cause_part = re.sub(r'[。！？，、；\s]+$', '', cause_part)
                if cause_part and len(cause_part) >= 2:
                    causes.append(cause_part)
        
        return self._deduplicate(causes)
    
    def _extract_results(self, text: str) -> List[str]:
        results = []
        
        for keyword in self.result_keywords:
            if keyword in text:
                index = text.find(keyword)
                result_part = text[index + len(keyword):]
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


class AnswerAggregator:
    def __init__(self):
        self._init_category_labels()
        self.grammar_analyzer = GrammarAnalyzer()
    
    def _init_category_labels(self):
        self.category_labels = {
            QuestionCategory.TIME: "时间",
            QuestionCategory.PLACE: "地点",
            QuestionCategory.PERSON: "人物",
            QuestionCategory.CAUSE: "起因",
            QuestionCategory.PROCESS: "经过",
            QuestionCategory.RESULT: "结果"
        }
        
        self.attribute_labels = {
            PersonAttribute.NAME: "姓名",
            PersonAttribute.GENDER: "性别",
            PersonAttribute.AGE: "年龄",
            PersonAttribute.ID_CARD: "身份证号",
            PersonAttribute.PHONE: "手机号",
            PersonAttribute.ADDRESS: "住址",
            PersonAttribute.OCCUPATION: "职业",
            PersonAttribute.EDUCATION: "学历",
            PersonAttribute.MARITAL_STATUS: "婚姻状况",
            PersonAttribute.NATIONALITY: "国籍",
            PersonAttribute.RELATIONSHIP: "与事件关系"
        }
        
        self.time_connectives = {
            "exact": ["于", "在"],
            "relative": ["当天", "那天", "当天早上", "当天下午", "当天晚上"],
        }
        
        self.place_connectives = {
            "default": ["在"],
            "movement": ["前往", "来到", "到达"],
        }
        
        self.cause_connectives = {
            "reason": ["因为", "由于"],
            "purpose": ["为了"],
            "explanation": ["原因是", "是因为"],
        }
        
        self.result_connectives = {
            "consequence": ["结果", "最后", "最终"],
            "conjunction": ["于是", "因此", "所以"],
        }
    
    def _collect_all_answers(self, event: Event) -> Dict[str, Dict]:
        all_answers = {}
        
        for question in event.questions:
            if question.is_answered:
                answer = event.get_answer_by_question_id(question.id)
                if answer and answer.text.strip():
                    all_answers[question.id] = {
                        "question": question,
                        "answer": answer,
                        "child_answers": {}
                    }
                    
                    for child_question in answer.child_questions:
                        if child_question.is_answered:
                            child_answer = event.get_answer_by_question_id(child_question.id)
                            if child_answer and child_answer.text.strip():
                                all_answers[question.id]["child_answers"][child_question.id] = {
                                    "question": child_question,
                                    "answer": child_answer,
                                    "sub_child_answers": {}
                                }
                                
                                for sub_child_question in child_answer.child_questions:
                                    if sub_child_question.is_answered:
                                        sub_child_answer = event.get_answer_by_question_id(sub_child_question.id)
                                        if sub_child_answer and sub_child_answer.text.strip():
                                            all_answers[question.id]["child_answers"][child_question.id]["sub_child_answers"][sub_child_question.id] = {
                                                "question": sub_child_question,
                                                "answer": sub_child_answer
                                            }
        
        return all_answers
    
    def _get_question_display_text(self, question: Question) -> str:
        if question.person_attribute and question.target_person:
            return f"{question.target_person}的{self.attribute_labels.get(question.person_attribute, question.person_attribute.value)}"
        return question.text
    
    def _group_by_category(self, all_answers: Dict) -> Dict[QuestionCategory, List]:
        grouped = {
            QuestionCategory.TIME: [],
            QuestionCategory.PLACE: [],
            QuestionCategory.PERSON: [],
            QuestionCategory.CAUSE: [],
            QuestionCategory.PROCESS: [],
            QuestionCategory.RESULT: []
        }
        
        for qid, ans_data in all_answers.items():
            question = ans_data["question"]
            category = question.category
            if category in grouped:
                grouped[category].append(ans_data)
        
        return grouped
    
    def _collect_person_info(self, all_answers: Dict) -> Dict[str, Dict]:
        person_info = {}
        
        for qid, ans_data in all_answers.items():
            question = ans_data["question"]
            
            if question.target_person and question.person_attribute:
                person = question.target_person
                if person not in person_info:
                    person_info[person] = {}
                
                attr_name = self.attribute_labels.get(question.person_attribute, question.person_attribute.value)
                person_info[person][attr_name] = ans_data["answer"].text
            
            for child_qid, child_data in ans_data.get("child_answers", {}).items():
                child_question = child_data["question"]
                if child_question.target_person and child_question.person_attribute:
                    person = child_question.target_person
                    if person not in person_info:
                        person_info[person] = {}
                    
                    attr_name = self.attribute_labels.get(child_question.person_attribute, child_question.person_attribute.value)
                    person_info[person][attr_name] = child_data["answer"].text
        
        return person_info
    
    def aggregate(self, event: Event) -> str:
        all_answers = self._collect_all_answers(event)
        
        if not all_answers:
            result = []
            result.append(f"事件：{event.initial_text}")
            result.append("")
            result.append("（暂无详细回答）")
            return "\n".join(result)
        
        grouped = self._group_by_category(all_answers)
        person_info = self._collect_person_info(all_answers)
        
        result_parts = []
        result_parts.append(f"事件：{event.initial_text}")
        result_parts.append("")
        
        if event.is_cycle_detected:
            result_parts.append("=" * 50)
            result_parts.append("【系统提示】")
            result_parts.append(event.cycle_message)
            result_parts.append("=" * 50)
            result_parts.append("")
        
        result_parts.append("【六要素信息】")
        result_parts.append("")
        
        for category in [QuestionCategory.TIME, QuestionCategory.PLACE, 
                         QuestionCategory.PERSON, QuestionCategory.CAUSE,
                         QuestionCategory.PROCESS, QuestionCategory.RESULT]:
            category_label = self.category_labels[category]
            answers = grouped[category]
            
            if answers:
                result_parts.append(f"【{category_label}】")
                
                for ans in answers:
                    question = ans["question"]
                    answer = ans["answer"]
                    
                    display_text = self._get_question_display_text(question)
                    result_parts.append(f"• {display_text}：{answer.text}")
                    
                    for child_ans in ans["child_answers"].values():
                        child_q = child_ans["question"]
                        child_a = child_ans["answer"]
                        child_display = self._get_question_display_text(child_q)
                        result_parts.append(f"  └─ {child_display}：{child_a.text}")
                        
                        for sub_child_ans in child_ans["sub_child_answers"].values():
                            sub_q = sub_child_ans["question"]
                            sub_a = sub_child_ans["answer"]
                            sub_display = self._get_question_display_text(sub_q)
                            result_parts.append(f"    └─ {sub_display}：{sub_a.text}")
                
                result_parts.append("")
        
        if person_info:
            result_parts.append("【人物详细信息】")
            result_parts.append("")
            
            for person, info in person_info.items():
                result_parts.append(f"【{person}】")
                for attr_name, attr_value in info.items():
                    result_parts.append(f"• {attr_name}：{attr_value}")
                result_parts.append("")
        
        result_parts.append("")
        result_parts.append("=" * 50)
        result_parts.append("【事件汇总（STAR法则）】")
        result_parts.append("")
        
        star_summary = self._generate_star_summary(event, grouped, person_info)
        result_parts.append(star_summary)
        
        return "\n".join(result_parts)
    
    def _generate_star_summary(self, event: Event, grouped: Dict, person_info: Dict) -> str:
        summary_parts = []
        
        time_info = self._extract_category_info(grouped, QuestionCategory.TIME)
        place_info = self._extract_category_info(grouped, QuestionCategory.PLACE)
        person_info_text = self._extract_category_info(grouped, QuestionCategory.PERSON)
        cause_info = self._extract_category_info(grouped, QuestionCategory.CAUSE)
        process_info = self._extract_category_info(grouped, QuestionCategory.PROCESS)
        result_info = self._extract_category_info(grouped, QuestionCategory.RESULT)
        
        summary_parts.append("S (Situation) - 情境：")
        situation_parts = []
        if time_info:
            situation_parts.append(f"时间：{time_info}")
        if place_info:
            situation_parts.append(f"地点：{place_info}")
        if person_info_text:
            situation_parts.append(f"涉及人物：{person_info_text}")
        if situation_parts:
            summary_parts.append("  " + "；".join(situation_parts))
        else:
            summary_parts.append("  （未提供详细情境信息）")
        
        summary_parts.append("")
        summary_parts.append("T (Task) - 任务/目标：")
        if cause_info:
            summary_parts.append(f"  {cause_info}")
        else:
            summary_parts.append("  （未提供任务/目标信息）")
        
        summary_parts.append("")
        summary_parts.append("A (Action) - 行动/经过：")
        if process_info:
            summary_parts.append(f"  {process_info}")
        else:
            summary_parts.append("  （未提供行动/经过信息）")
        
        summary_parts.append("")
        summary_parts.append("R (Result) - 结果：")
        if result_info:
            summary_parts.append(f"  {result_info}")
        else:
            summary_parts.append("  （未提供结果信息）")
        
        summary_parts.append("")
        summary_parts.append("-" * 40)
        summary_parts.append("完整事件描述：")
        
        narrative = self._generate_narrative(event, time_info, place_info, person_info_text, cause_info, process_info, result_info)
        summary_parts.append(narrative)
        
        return "\n".join(summary_parts)
    
    def _extract_category_info(self, grouped: Dict, category: QuestionCategory) -> str:
        answers = grouped.get(category, [])
        if not answers:
            return ""
        
        info_parts = []
        for ans in answers:
            answer = ans["answer"]
            if answer.text.strip():
                info_parts.append(answer.text.strip())
        
        return "；".join(info_parts)
    
    def _generate_narrative(self, event: Event, time_info: str, place_info: str, 
                            person_info: str, cause_info: str, process_info: str, 
                            result_info: str) -> str:
        base_text = event.initial_text
        
        base_analysis = self.grammar_analyzer.analyze(base_text)
        
        is_duration = False
        if time_info:
            is_duration = self.grammar_analyzer._is_duration(time_info)
        
        base_text = self._clean_base_text(base_text)
        
        narrative_parts = []
        
        if time_info and not is_duration:
            time_text = self._format_time(time_info, base_analysis)
            if time_text:
                narrative_parts.append(time_text)
        
        if person_info:
            person_text = self._format_person(person_info, base_text, base_analysis)
            if person_text:
                narrative_parts.append(person_text)
        
        if place_info:
            place_text = self._format_place(place_info, base_text, base_analysis)
            if place_text:
                narrative_parts.append(place_text)
        
        if base_text:
            narrative_parts.append(base_text)
        
        if cause_info:
            cause_text = self._format_cause(cause_info, base_text)
            if cause_text:
                narrative_parts.append(cause_text)
        
        if process_info:
            process_text = self._format_process(process_info, base_text)
            if process_text:
                narrative_parts.append(process_text)
        
        if result_info:
            result_text = self._format_result(result_info, base_text)
            if result_text:
                narrative_parts.append(result_text)
        
        if time_info and is_duration:
            duration_text = self._format_duration(time_info)
            if duration_text:
                narrative_parts.append(duration_text)
        
        narrative = self._join_parts(narrative_parts)
        
        if not narrative.endswith("。"):
            narrative += "。"
        
        return narrative
    
    def _clean_base_text(self, text: str) -> str:
        if not text:
            return text
        
        text = text.strip()
        text = text.rstrip("。！？，,")
        
        if text.startswith("去") and len(text) > 1:
            rest = text[1:]
            if rest.startswith("了"):
                rest = rest[1:]
            if rest:
                text = rest
        
        if text.endswith("了") and len(text) > 1:
            text = text[:-1]
        
        return text.strip()
    
    def _format_time(self, time_info: str, base_analysis: Dict) -> str:
        if not time_info:
            return ""
        
        if "年" in time_info or "月" in time_info or "日" in time_info or "号" in time_info:
            if time_info.startswith("在") or time_info.startswith("于"):
                return time_info
            return f"在{time_info}"
        
        if "点" in time_info or "时" in time_info or "分" in time_info:
            if time_info.startswith("在"):
                return time_info
            return f"在{time_info}"
        
        if time_info in ["今天", "明天", "昨天", "前天", "后天", "上周", "下周", "上月", "下月", "去年", "今年", "明年", "上午", "下午", "晚上", "凌晨", "傍晚", "深夜"]:
            return time_info
        
        return time_info
    
    def _format_person(self, person_info: str, base_text: str, base_analysis: Dict) -> str:
        if not person_info:
            return ""
        
        base_persons = base_analysis.get("persons", [])
        
        persons = re.split(r'[和与及跟、，,\s]+', person_info)
        persons = [p.strip() for p in persons if p.strip()]
        
        new_persons = []
        for p in persons:
            if p not in base_persons and p not in base_text:
                new_persons.append(p)
        
        if not new_persons:
            return ""
        
        if len(new_persons) == 1:
            return new_persons[0]
        else:
            return "和".join(new_persons)
    
    def _format_place(self, place_info: str, base_text: str, base_analysis: Dict) -> str:
        if not place_info:
            return ""
        
        base_places = base_analysis.get("places", [])
        
        places = re.split(r'[、，,\s]+', place_info)
        places = [p.strip() for p in places if p.strip()]
        
        new_places = []
        for p in places:
            if p not in base_places and p not in base_text:
                new_places.append(p)
        
        if not new_places:
            return ""
        
        place_str = "、".join(new_places)
        
        if "在" + place_str in base_text or place_str in base_text:
            return ""
        
        if base_text.startswith("去") or "去" in base_text:
            return f"到{place_str}"
        
        return f"在{place_str}"
    
    def _format_cause(self, cause_info: str, base_text: str) -> str:
        if not cause_info:
            return ""
        
        cause_keywords = ["因为", "由于", "原因是", "为了"]
        for kw in cause_keywords:
            if kw in base_text:
                return ""
        
        if cause_info.startswith("因为") or cause_info.startswith("由于") or cause_info.startswith("为了"):
            return f"，{cause_info}"
        
        if "原因是" in cause_info:
            return f"，{cause_info}"
        
        return f"，原因是{cause_info}"
    
    def _format_process(self, process_info: str, base_text: str) -> str:
        if not process_info:
            return ""
        
        process_keywords = ["首先", "然后", "接着", "最后", "步骤", "过程是", "经过是"]
        for kw in process_keywords:
            if kw in base_text:
                return ""
        
        if any(kw in process_info for kw in process_keywords):
            return f"，{process_info}"
        
        return f"，{process_info}"
    
    def _format_result(self, result_info: str, base_text: str) -> str:
        if not result_info:
            return ""
        
        result_keywords = ["结果", "最后", "终于", "最终", "于是", "因此", "所以"]
        for kw in result_keywords:
            if kw in base_text:
                return ""
        
        if result_info.startswith("结果") or result_info.startswith("最后") or result_info.startswith("于是") or result_info.startswith("因此"):
            return f"，{result_info}"
        
        return f"，结果是{result_info}"
    
    def _format_duration(self, time_info: str) -> str:
        if not time_info:
            return ""
        
        if time_info.startswith("持续") or time_info.startswith("花了") or time_info.startswith("用了"):
            return f"，{time_info}"
        
        return f"，持续了{time_info}"
    
    def _join_parts(self, parts: List[str]) -> str:
        if not parts:
            return ""
        
        result = []
        prev_needs_space = False
        
        for i, part in enumerate(parts):
            if not part:
                continue
            
            part = part.strip()
            
            if part.startswith("，") or part.startswith("。"):
                if result and result[-1].endswith("，"):
                    result[-1] = result[-1][:-1]
                result.append(part)
            else:
                if result:
                    if not result[-1].endswith("，") and not result[-1].endswith("。"):
                        last_part = result[-1]
                        if (last_part in ["我", "你", "他", "她", "我们", "你们", "他们", "她们"] or
                            any(title in last_part for title in ["老师", "经理", "医生", "同学", "同事", "朋友", "家人"])):
                            pass
                        elif "在" in last_part or "到" in last_part:
                            pass
                        else:
                            result.append("，")
                result.append(part)
        
        return "".join(result)
    
    def _person_in_text(self, person_info: str, text: str) -> bool:
        if not person_info or not text:
            return False
        
        persons = re.split(r'[和与及跟、，,\s]+', person_info)
        for person in persons:
            person = person.strip()
            if person and person in text:
                return True
        
        return False
    
    def _place_in_text(self, place_info: str, text: str) -> bool:
        if not place_info or not text:
            return False
        
        places = re.split(r'[、，,\s]+', place_info)
        for place in places:
            place = place.strip()
            if place and place in text:
                return True
        
        if "在" in text and any(p in text for p in place_info.split()):
            return True
        
        return False
    
    def _cause_in_text(self, cause_info: str, text: str) -> bool:
        if not cause_info or not text:
            return False
        
        cause_keywords = ["因为", "由于", "原因是", "为了", "原因是"]
        for keyword in cause_keywords:
            if keyword in text and any(c in text for c in cause_info.split()):
                return True
        
        return False
    
    def _process_in_text(self, process_info: str, text: str) -> bool:
        if not process_info or not text:
            return False
        
        process_keywords = ["过程是", "经过是", "首先", "然后", "接着", "最后", "步骤"]
        for keyword in process_keywords:
            if keyword in text:
                return True
        
        return False
    
    def _result_in_text(self, result_info: str, text: str) -> bool:
        if not result_info or not text:
            return False
        
        result_keywords = ["结果是", "最后", "终于", "最终"]
        for keyword in result_keywords:
            if keyword in text:
                return True
        
        return False
