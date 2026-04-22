import re
from typing import Dict, List, Optional
from models import Event, Question, Answer, QuestionCategory, PersonAttribute


class AnswerAggregator:
    def __init__(self):
        self._init_category_labels()
    
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
        
        base_text = self._clean_base_text(base_text)
        
        is_duration = self._is_duration(time_info)
        
        parts = []
        
        if person_info:
            if not self._person_in_text(person_info, base_text):
                parts.append(person_info)
        
        if place_info and not is_duration:
            if not self._place_in_text(place_info, base_text):
                parts.append(f"在{place_info}")
        
        parts.append(base_text)
        
        if cause_info:
            if not self._cause_in_text(cause_info, base_text):
                parts.append(f"，原因是{cause_info}")
        
        if process_info:
            if not self._process_in_text(process_info, base_text):
                parts.append(f"，{process_info}")
        
        if result_info:
            if not self._result_in_text(result_info, base_text):
                parts.append(f"，结果是{result_info}")
        
        if time_info and is_duration:
            parts.append(f"，{time_info}")
        
        narrative = "".join(parts)
        if not narrative.endswith("。"):
            narrative += "。"
        
        return narrative
    
    def _clean_base_text(self, text: str) -> str:
        if not text:
            return text
        
        text = text.strip()
        
        text = text.rstrip("。！？，,")
        
        if text.startswith("我") or text.startswith("我们"):
            pass
        elif text.startswith("去"):
            text = text[1:]
            if text.startswith("了"):
                text = text[1:]
        elif text.endswith("了"):
            text = text[:-1]
        
        return text.strip()
    
    def _is_duration(self, time_info: str) -> bool:
        if not time_info:
            return False
        
        duration_patterns = [
            r"(\d+)\s*个?\s*(小?时|分钟|秒|天|周|月|年)",
            r"持续了?\s*\d+",
            r"花了?\s*\d+",
            r"用了?\s*\d+",
        ]
        
        for pattern in duration_patterns:
            if re.search(pattern, time_info):
                return True
        
        return False
    
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
