from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from enum import Enum


class QuestionCategory(Enum):
    TIME = "时间"
    PLACE = "地点"
    PERSON = "人物"
    CAUSE = "起因"
    PROCESS = "经过"
    RESULT = "结果"


class PersonAttribute(Enum):
    NAME = "姓名"
    GENDER = "性别"
    AGE = "年龄"
    ID_CARD = "身份证号"
    PHONE = "手机号"
    ADDRESS = "住址"
    OCCUPATION = "职业"
    EDUCATION = "学历"
    MARITAL_STATUS = "婚姻状况"
    NATIONALITY = "国籍"
    RELATIONSHIP = "与事件关系"


@dataclass
class EventNode:
    id: str
    text: str
    level: int
    parent_event_id: Optional[str] = None
    is_cycle: bool = False


@dataclass
class Question:
    id: str
    text: str
    category: QuestionCategory
    level: int
    target_event_id: Optional[str] = None
    target_person: Optional[str] = None
    person_attribute: Optional[PersonAttribute] = None
    parent_answer_id: Optional[str] = None
    is_answered: bool = False


@dataclass
class Answer:
    id: str
    question_id: str
    text: str
    level: int
    detected_events: List[str] = field(default_factory=list)
    detected_persons: List[str] = field(default_factory=list)
    child_questions: List[Question] = field(default_factory=list)


@dataclass
class Event:
    id: str
    initial_text: str
    initial_event_id: str
    level: int = 0
    max_level: int = 100
    questions: List[Question] = field(default_factory=list)
    answers: Dict[str, Answer] = field(default_factory=dict)
    event_nodes: Dict[str, EventNode] = field(default_factory=dict)
    event_history: List[str] = field(default_factory=list)
    is_cycle_detected: bool = False
    cycle_message: str = ""
    
    def __post_init__(self):
        if self.initial_event_id not in self.event_nodes:
            self.event_nodes[self.initial_event_id] = EventNode(
                id=self.initial_event_id,
                text=self.initial_text,
                level=0
            )
            self.event_history.append(self.initial_text)
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        for q in self.questions:
            if q.id == question_id:
                return q
        for answer in self.answers.values():
            for q in answer.child_questions:
                if q.id == question_id:
                    return q
        return None
    
    def get_answer_by_question_id(self, question_id: str) -> Optional[Answer]:
        return self.answers.get(question_id)
    
    def add_answer(self, question_id: str, answer_text: str, level: int) -> Answer:
        answer_id = f"answer_{question_id}"
        answer = Answer(
            id=answer_id,
            question_id=question_id,
            text=answer_text,
            level=level
        )
        self.answers[question_id] = answer
        
        question = self.get_question_by_id(question_id)
        if question:
            question.is_answered = True
        
        return answer
    
    def add_child_questions(self, parent_answer_id: str, questions: List[Question]) -> None:
        for answer in self.answers.values():
            if answer.id == parent_answer_id:
                answer.child_questions.extend(questions)
                break
    
    def add_event_node(self, event_text: str, level: int, parent_event_id: Optional[str] = None) -> Optional[EventNode]:
        if self.is_same_event(event_text, self.initial_text):
            self.is_cycle_detected = True
            self.cycle_message = f"检测到循环：新事件\"{event_text}\"与初始事件\"{self.initial_text}\"重合，提问终止。"
            return None
        
        if event_text in self.event_history:
            self.is_cycle_detected = True
            self.cycle_message = f"检测到循环：事件\"{event_text}\"已在之前的层级中出现过，提问终止。"
            return None
        
        event_id = f"event_{len(self.event_nodes)}"
        event_node = EventNode(
            id=event_id,
            text=event_text,
            level=level,
            parent_event_id=parent_event_id
        )
        self.event_nodes[event_id] = event_node
        self.event_history.append(event_text)
        return event_node
    
    def is_same_event(self, event1: str, event2: str) -> bool:
        if not event1 or not event2:
            return False
        
        e1 = event1.strip().lower()
        e2 = event2.strip().lower()
        
        if e1 == e2:
            return True
        
        stop_words = {"了", "的", "是", "在", "有", "和", "与", "及", "跟", "我", "你", "他", "她", "它", "们"}
        
        words1 = set(e1.replace("，", " ").replace(",", " ").replace("。", " ").split()) - stop_words
        words2 = set(e2.replace("，", " ").replace(",", " ").replace("。", " ").split()) - stop_words
        
        if words1 == words2 and len(words1) > 0:
            return True
        
        if len(words1) >= 2 and len(words2) >= 2:
            intersection = words1 & words2
            if len(intersection) >= min(len(words1), len(words2)) * 0.8:
                return True
        
        return False
    
    def get_all_questions(self) -> List[Question]:
        all_questions = list(self.questions)
        for answer in self.answers.values():
            all_questions.extend(answer.child_questions)
        return all_questions
    
    def get_questions_by_level(self, level: int) -> List[Question]:
        return [q for q in self.get_all_questions() if q.level == level]
    
    def get_unanswered_questions(self) -> List[Question]:
        return [q for q in self.get_all_questions() if not q.is_answered]
    
    def get_answered_questions(self) -> List[Question]:
        return [q for q in self.get_all_questions() if q.is_answered]
    
    def get_max_level(self) -> int:
        all_questions = self.get_all_questions()
        if not all_questions:
            return 0
        return max(q.level for q in all_questions)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "initial_text": self.initial_text,
            "initial_event_id": self.initial_event_id,
            "level": self.level,
            "max_level": self.max_level,
            "is_cycle_detected": self.is_cycle_detected,
            "cycle_message": self.cycle_message,
            "event_history": self.event_history,
            "event_nodes": {
                eid: {
                    "id": en.id,
                    "text": en.text,
                    "level": en.level,
                    "parent_event_id": en.parent_event_id,
                    "is_cycle": en.is_cycle
                }
                for eid, en in self.event_nodes.items()
            },
            "questions": [
                {
                    "id": q.id,
                    "text": q.text,
                    "category": q.category.value,
                    "level": q.level,
                    "target_event_id": q.target_event_id,
                    "target_person": q.target_person,
                    "person_attribute": q.person_attribute.value if q.person_attribute else None,
                    "parent_answer_id": q.parent_answer_id,
                    "is_answered": q.is_answered
                }
                for q in self.questions
            ],
            "answers": {
                qid: {
                    "id": a.id,
                    "question_id": a.question_id,
                    "text": a.text,
                    "level": a.level,
                    "detected_events": a.detected_events,
                    "detected_persons": a.detected_persons,
                    "child_questions": [
                        {
                            "id": cq.id,
                            "text": cq.text,
                            "category": cq.category.value,
                            "level": cq.level,
                            "target_event_id": cq.target_event_id,
                            "target_person": cq.target_person,
                            "person_attribute": cq.person_attribute.value if cq.person_attribute else None,
                            "parent_answer_id": cq.parent_answer_id,
                            "is_answered": cq.is_answered
                        }
                        for cq in a.child_questions
                    ]
                }
                for qid, a in self.answers.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        event = cls(
            id=data["id"],
            initial_text=data["initial_text"],
            initial_event_id=data["initial_event_id"],
            level=data.get("level", 0),
            max_level=data.get("max_level", 100)
        )
        
        event.is_cycle_detected = data.get("is_cycle_detected", False)
        event.cycle_message = data.get("cycle_message", "")
        event.event_history = data.get("event_history", [])
        
        for eid, en_data in data.get("event_nodes", {}).items():
            event.event_nodes[eid] = EventNode(
                id=en_data["id"],
                text=en_data["text"],
                level=en_data["level"],
                parent_event_id=en_data.get("parent_event_id"),
                is_cycle=en_data.get("is_cycle", False)
            )
        
        for q_data in data["questions"]:
            person_attr = None
            if q_data.get("person_attribute"):
                try:
                    person_attr = PersonAttribute(q_data["person_attribute"])
                except ValueError:
                    pass
            
            question = Question(
                id=q_data["id"],
                text=q_data["text"],
                category=QuestionCategory(q_data["category"]),
                level=q_data["level"],
                target_event_id=q_data.get("target_event_id"),
                target_person=q_data.get("target_person"),
                person_attribute=person_attr,
                parent_answer_id=q_data.get("parent_answer_id"),
                is_answered=q_data["is_answered"]
            )
            event.questions.append(question)
        
        for qid, a_data in data["answers"].items():
            answer = Answer(
                id=a_data["id"],
                question_id=a_data["question_id"],
                text=a_data["text"],
                level=a_data["level"],
                detected_events=a_data.get("detected_events", []),
                detected_persons=a_data.get("detected_persons", [])
            )
            
            for cq_data in a_data.get("child_questions", []):
                person_attr = None
                if cq_data.get("person_attribute"):
                    try:
                        person_attr = PersonAttribute(cq_data["person_attribute"])
                    except ValueError:
                        pass
                
                child_question = Question(
                    id=cq_data["id"],
                    text=cq_data["text"],
                    category=QuestionCategory(cq_data["category"]),
                    level=cq_data["level"],
                    target_event_id=cq_data.get("target_event_id"),
                    target_person=cq_data.get("target_person"),
                    person_attribute=person_attr,
                    parent_answer_id=cq_data.get("parent_answer_id"),
                    is_answered=cq_data["is_answered"]
                )
                answer.child_questions.append(child_question)
            
            event.answers[qid] = answer
        
        return event
