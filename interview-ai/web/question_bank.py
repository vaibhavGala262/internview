import chromadb
from chromadb.utils import embedding_functions
import os
import json
import threading

_QB_DIR = os.path.dirname(os.path.abspath(__file__))
_DB_DIR = os.path.join(_QB_DIR, "chroma_db")

SEED_QUESTIONS = {
    "software_engineer": [
        {"question": "Describe the difference between a process and a thread. When would you choose multi-processing over multi-threading?", "type": "technical", "tags": ["os", "concurrency"], "difficulty": 2},
        {"question": "Walk me through how you would design a URL shortening service like bit.ly. What database would you use and why?", "type": "technical", "tags": ["system design", "databases"], "difficulty": 3},
        {"question": "What is the difference between REST and GraphQL? When would you choose one over the other?", "type": "technical", "tags": ["api design"], "difficulty": 2},
        {"question": "Explain how garbage collection works in a language of your choice. What are the trade-offs?", "type": "technical", "tags": ["programming languages", "memory management"], "difficulty": 3},
        {"question": "Write a function to check if a binary tree is balanced. What is the time and space complexity?", "type": "technical", "tags": ["data structures", "algorithms"], "difficulty": 3},
        {"question": "How would you debug a production issue where the API is returning 503 errors intermittently?", "type": "technical", "tags": ["debugging", "production"], "difficulty": 3},
        {"question": "Describe a time you had to refactor a large piece of code. How did you ensure you didn't introduce bugs?", "type": "behavioral", "tags": ["maintainability", "testing"], "difficulty": 2},
        {"question": "What is the CAP theorem? How does it influence your choice of database in a distributed system?", "type": "technical", "tags": ["distributed systems", "databases"], "difficulty": 4},
        {"question": "How do you write testable code? Give an example of a pattern you use to make unit testing easier.", "type": "technical", "tags": ["testing", "design patterns"], "difficulty": 2},
        {"question": "Tell me about a project where you had to make a significant technical trade-off. What did you decide and why?", "type": "behavioral", "tags": ["decision making", "trade-offs"], "difficulty": 3},
    ],
    "ai_engineer": [
        {"question": "Explain the bias-variance tradeoff. How do you detect whether your model is underfitting or overfitting?", "type": "technical", "tags": ["ml fundamentals"], "difficulty": 2},
        {"question": "Describe the Transformer architecture. Why is self-attention better than RNNs for sequence tasks?", "type": "technical", "tags": ["deep learning", "nlp"], "difficulty": 4},
        {"question": "How would you handle an imbalanced dataset for a binary classification problem?", "type": "technical", "tags": ["data preprocessing", "classification"], "difficulty": 3},
        {"question": "What evaluation metrics would you use for a fraud detection model and why?", "type": "technical", "tags": ["evaluation", "metrics"], "difficulty": 2},
        {"question": "Explain how gradient descent works. What is the role of the learning rate?", "type": "technical", "tags": ["optimization"], "difficulty": 2},
        {"question": "Walk me through an end-to-end ML project you've worked on, from data collection to deployment.", "type": "behavioral", "tags": ["mlops", "lifecycle"], "difficulty": 3},
        {"question": "What is the difference between bagging and boosting? Give an example of each.", "type": "technical", "tags": ["ensemble methods"], "difficulty": 2},
        {"question": "How do you detect and mitigate data drift in a production model?", "type": "technical", "tags": ["mlops", "monitoring"], "difficulty": 4},
        {"question": "Compare CNNs and Vision Transformers for image classification. What are the trade-offs?", "type": "technical", "tags": ["computer vision"], "difficulty": 4},
        {"question": "Tell me about a time your model performed poorly in production. How did you diagnose and fix it?", "type": "behavioral", "tags": ["debugging", "production"], "difficulty": 3},
    ],
    "data_scientist": [
        {"question": "Explain p-value and confidence intervals to a non-technical stakeholder.", "type": "technical", "tags": ["statistics", "communication"], "difficulty": 2},
        {"question": "How do you design an A/B test? What are common pitfalls to avoid?", "type": "technical", "tags": ["experimentation"], "difficulty": 3},
        {"question": "What is feature engineering and why is it important? Give an example of a feature you created.", "type": "technical", "tags": ["feature engineering"], "difficulty": 2},
        {"question": "Describe a project where you used data to drive a business decision. What was the impact?", "type": "behavioral", "tags": ["business impact"], "difficulty": 3},
        {"question": "What is the difference between correlation and causation? How do you establish causality?", "type": "technical", "tags": ["statistics"], "difficulty": 3},
        {"question": "Write a SQL query to find the top 3 products by revenue in each category for the last month.", "type": "technical", "tags": ["sql"], "difficulty": 3},
        {"question": "How do you handle missing data in a dataset? Compare imputation strategies.", "type": "technical", "tags": ["data cleaning"], "difficulty": 2},
        {"question": "Explain regularization — L1 vs L2. When would you use each?", "type": "technical", "tags": ["regularization", "ml"], "difficulty": 2},
        {"question": "Walk me through how you would build a customer churn prediction model.", "type": "technical", "tags": ["classification", "end-to-end"], "difficulty": 3},
        {"question": "Tell me about a time you had to persuade a team to adopt a different analytical approach.", "type": "behavioral", "tags": ["communication", "leadership"], "difficulty": 2},
    ],
    "iot_engineer": [
        {"question": "Explain the difference between MQTT and HTTP for IoT communication. When would you use each?", "type": "technical", "tags": ["protocols", "communication"], "difficulty": 2},
        {"question": "How would you design a sensor data collection system for 10000 devices with minimal power consumption?", "type": "technical", "tags": ["system design", "power optimization"], "difficulty": 4},
        {"question": "Describe the ESP32 architecture. What are its key features for IoT applications?", "type": "technical", "tags": ["microcontrollers"], "difficulty": 2},
        {"question": "What is the difference between BLE and Zigbee? Which one would you use for a smart home project?", "type": "technical", "tags": ["wireless protocols"], "difficulty": 2},
        {"question": "How do you handle firmware updates over the air (OTA) for devices in the field?", "type": "technical", "tags": ["ota", "firmware"], "difficulty": 3},
        {"question": "Explain the role of an RTOS in an embedded system. What is a real-time constraint?", "type": "technical", "tags": ["rtos", "real-time"], "difficulty": 3},
        {"question": "Describe a project where you integrated a sensor with a microcontroller. What challenges did you face?", "type": "behavioral", "tags": ["sensor integration"], "difficulty": 2},
        {"question": "How would you secure an IoT device with limited compute and memory resources?", "type": "technical", "tags": ["security"], "difficulty": 4},
        {"question": "What is edge computing and why is it important for IoT systems?", "type": "technical", "tags": ["edge computing"], "difficulty": 2},
        {"question": "Tell me about a time you debugged a hardware-software interface issue.", "type": "behavioral", "tags": ["debugging", "hw-sw co-design"], "difficulty": 3},
    ],
    "frontend_engineer": [
        {"question": "Explain the box model in CSS. How does `box-sizing: border-box` change element sizing?", "type": "technical", "tags": ["css"], "difficulty": 1},
        {"question": "What is the Virtual DOM and how does React use it to improve performance?", "type": "technical", "tags": ["react", "performance"], "difficulty": 2},
        {"question": "How would you optimize a web page that loads slowly on mobile devices?", "type": "technical", "tags": ["performance", "mobile"], "difficulty": 3},
        {"question": "Explain closures in JavaScript. Give an example of when you would use one.", "type": "technical", "tags": ["javascript"], "difficulty": 2},
        {"question": "What is the difference between controlled and uncontrolled components in React?", "type": "technical", "tags": ["react"], "difficulty": 2},
        {"question": "How do you ensure your web application is accessible to users with disabilities?", "type": "technical", "tags": ["accessibility", "a11y"], "difficulty": 3},
        {"question": "Describe a situation where you had to improve the performance of a React application.", "type": "behavioral", "tags": ["optimization", "react"], "difficulty": 3},
        {"question": "What is a Promise and how does async/await work in JavaScript?", "type": "technical", "tags": ["javascript", "async"], "difficulty": 1},
        {"question": "How would you implement state management in a large frontend application?", "type": "technical", "tags": ["state management", "architecture"], "difficulty": 3},
        {"question": "Tell me about a challenging UI problem you solved. What was your approach?", "type": "behavioral", "tags": ["problem solving", "ui"], "difficulty": 2},
    ],
    "backend_engineer": [
        {"question": "Explain the difference between SQL and NoSQL databases. When would you choose each?", "type": "technical", "tags": ["databases"], "difficulty": 2},
        {"question": "How does indexing work in a relational database? What are the trade-offs?", "type": "technical", "tags": ["databases", "performance"], "difficulty": 2},
        {"question": "Design a rate limiter for a REST API. What algorithms would you consider?", "type": "technical", "tags": ["system design", "api"], "difficulty": 3},
        {"question": "What is idempotency in REST APIs and why does it matter?", "type": "technical", "tags": ["api design"], "difficulty": 2},
        {"question": "Explain how you would implement caching for a high-traffic read-heavy API.", "type": "technical", "tags": ["caching", "performance"], "difficulty": 3},
        {"question": "What is a message queue and when would you use one? Compare RabbitMQ and Kafka.", "type": "technical", "tags": ["message queues", "architecture"], "difficulty": 3},
        {"question": "How do you handle authentication and authorization in a microservices architecture?", "type": "technical", "tags": ["security", "microservices"], "difficulty": 4},
        {"question": "Describe a time you optimized a slow database query. What tools and techniques did you use?", "type": "behavioral", "tags": ["optimization", "databases"], "difficulty": 3},
        {"question": "What is the difference between horizontal and vertical scaling?", "type": "technical", "tags": ["scalability"], "difficulty": 1},
        {"question": "Tell me about a project where you designed a backend service from scratch.", "type": "behavioral", "tags": ["system design", "project"], "difficulty": 3},
    ],
    "devops_engineer": [
        {"question": "Explain the difference between Docker and a virtual machine. When would you use each?", "type": "technical", "tags": ["containers", "virtualization"], "difficulty": 1},
        {"question": "How would you design a CI/CD pipeline for a microservices application?", "type": "technical", "tags": ["ci/cd", "pipelines"], "difficulty": 3},
        {"question": "What is Kubernetes and what problem does it solve? Explain pods, deployments, and services.", "type": "technical", "tags": ["kubernetes"], "difficulty": 2},
        {"question": "Describe the difference between a liveness probe and a readiness probe in Kubernetes.", "type": "technical", "tags": ["kubernetes", "monitoring"], "difficulty": 3},
        {"question": "What is Infrastructure as Code? Compare Terraform and Ansible.", "type": "technical", "tags": ["iac", "terraform", "ansible"], "difficulty": 2},
        {"question": "How would you monitor a production system? What metrics would you track?", "type": "technical", "tags": ["monitoring", "observability"], "difficulty": 2},
        {"question": "Explain the concept of 'immutable infrastructure'. What are the benefits?", "type": "technical", "tags": ["infrastructure", "best practices"], "difficulty": 3},
        {"question": "Describe an incident where you had to respond to a production outage. What was your process?", "type": "behavioral", "tags": ["incident response", "production"], "difficulty": 3},
        {"question": "How do you manage secrets and configuration across different environments?", "type": "technical", "tags": ["security", "configuration management"], "difficulty": 2},
        {"question": "Tell me about a time you automated a manual operational process. What was the impact?", "type": "behavioral", "tags": ["automation", "impact"], "difficulty": 2},
    ],
    "product_manager": [
        {"question": "How do you decide which features to build when you have limited engineering resources?", "type": "behavioral", "tags": ["prioritization", "roadmap"], "difficulty": 2},
        {"question": "Explain the difference between a KPI and an OKR. Give an example of each for a product.", "type": "technical", "tags": ["metrics", "strategy"], "difficulty": 2},
        {"question": "Walk me through how you would conduct user research for a new feature.", "type": "behavioral", "tags": ["user research"], "difficulty": 3},
        {"question": "How do you measure the success of a product launch? What metrics do you look at?", "type": "technical", "tags": ["analytics", "success metrics"], "difficulty": 2},
        {"question": "Describe a time you had to kill a feature you had invested significant effort in. How did you handle it?", "type": "behavioral", "tags": ["decision making", "stakeholder management"], "difficulty": 3},
        {"question": "What is the Minimum Viable Product concept and how do you apply it in practice?", "type": "technical", "tags": ["mvp", "methodology"], "difficulty": 1},
        {"question": "How do you handle competing priorities from different stakeholders?", "type": "behavioral", "tags": ["stakeholder management", "communication"], "difficulty": 3},
        {"question": "Explain how you use data to make product decisions. Give a specific example.", "type": "behavioral", "tags": ["data-driven", "decision making"], "difficulty": 2},
        {"question": "What is the role of a Product Manager in an Agile team? How is it different from a Project Manager?", "type": "technical", "tags": ["agile", "roles"], "difficulty": 1},
        {"question": "Tell me about a product you shipped that did not meet expectations. What did you learn?", "type": "behavioral", "tags": ["failure", "learning"], "difficulty": 3},
    ],
    "cx_associate": [
        {"question": "A customer calls in frustrated because they received the wrong product. How would you handle this?", "type": "behavioral", "tags": ["complaint resolution", "empathy"], "difficulty": 2},
        {"question": "How do you maintain a positive attitude during a long shift of back-to-back customer calls?", "type": "behavioral", "tags": ["resilience", "attitude"], "difficulty": 2},
        {"question": "Describe a time you went above and beyond for a customer. What did you do?", "type": "behavioral", "tags": ["initiative", "customer satisfaction"], "difficulty": 2},
        {"question": "What is the first thing you do when you receive a customer complaint via email?", "type": "behavioral", "tags": ["email etiquette", "process"], "difficulty": 1},
        {"question": "A customer asks for a refund for a service they have already used. How do you respond?", "type": "behavioral", "tags": ["policy adherence", "communication"], "difficulty": 2},
        {"question": "How do you handle a situation where you don't know the answer to a customer's question?", "type": "behavioral", "tags": ["problem solving", "escalation"], "difficulty": 1},
        {"question": "Tell me about a time you had to deal with an angry customer. What was the outcome?", "type": "behavioral", "tags": ["conflict resolution", "de-escalation"], "difficulty": 2},
        {"question": "What does good customer service mean to you? Give an example.", "type": "behavioral", "tags": ["service philosophy"], "difficulty": 1},
        {"question": "How do you prioritize when multiple customers are waiting for your response?", "type": "behavioral", "tags": ["time management", "prioritization"], "difficulty": 2},
        {"question": "Describe your experience with CRM tools. Which ones have you used and how?", "type": "behavioral", "tags": ["crm", "tools"], "difficulty": 1},
    ],
    "customer_support": [
        {"question": "A customer's internet service has been down for 24 hours and they are very upset. How do you handle the call?", "type": "behavioral", "tags": ["escalation handling", "empathy"], "difficulty": 2},
        {"question": "How do you ensure you understand a customer's issue correctly before providing a solution?", "type": "behavioral", "tags": ["active listening", "clarification"], "difficulty": 1},
        {"question": "Describe a time you received positive feedback from a customer. What did you do?", "type": "behavioral", "tags": ["positive feedback", "customer satisfaction"], "difficulty": 1},
        {"question": "What is the most important metric for a support team and why?", "type": "behavioral", "tags": ["kpi awareness"], "difficulty": 2},
        {"question": "How do you handle a situation where the solution requires multiple follow-ups?", "type": "behavioral", "tags": ["follow-up", "process adherence"], "difficulty": 2},
        {"question": "A customer wants a refund that is against company policy. How do you say no without damaging the relationship?", "type": "behavioral", "tags": ["objection handling", "communication"], "difficulty": 3},
        {"question": "How do you stay updated on product knowledge for the products you support?", "type": "behavioral", "tags": ["product knowledge", "learning"], "difficulty": 1},
        {"question": "Tell me about a time you had to handle a high volume of tickets simultaneously.", "type": "behavioral", "tags": ["time management", "pressure"], "difficulty": 2},
        {"question": "What would you do if a customer asks for a manager immediately?", "type": "behavioral", "tags": ["escalation", "de-escalation"], "difficulty": 2},
        {"question": "Describe your process for documenting a customer interaction in a ticketing system.", "type": "behavioral", "tags": ["documentation", "crm"], "difficulty": 1},
    ],
    "office_assistant": [
        {"question": "How do you prioritize multiple tasks when your manager gives you several assignments at once?", "type": "behavioral", "tags": ["prioritization", "time management"], "difficulty": 2},
        {"question": "Describe your proficiency with Microsoft Excel. What are the most useful functions you know?", "type": "technical", "tags": ["excel", "ms office"], "difficulty": 1},
        {"question": "How do you maintain confidentiality when handling sensitive company documents?", "type": "behavioral", "tags": ["confidentiality", "ethics"], "difficulty": 2},
        {"question": "Tell me about a time you had to coordinate a meeting across multiple schedules. How did you manage it?", "type": "behavioral", "tags": ["scheduling", "coordination"], "difficulty": 1},
        {"question": "What is your process for organizing and filing digital documents so they are easy to find?", "type": "behavioral", "tags": ["document management", "organization"], "difficulty": 1},
        {"question": "How do you handle a situation where you notice a mistake in an important document before it is sent?", "type": "behavioral", "tags": ["attention to detail", "initiative"], "difficulty": 2},
        {"question": "Describe your experience with scheduling tools like Outlook Calendar or Google Calendar.", "type": "technical", "tags": ["scheduling tools"], "difficulty": 1},
        {"question": "A visitor arrives at the office for a meeting with your manager who is running late. What do you do?", "type": "behavioral", "tags": ["hospitality", "problem solving"], "difficulty": 1},
        {"question": "How do you ensure accuracy when entering large amounts of data into a system?", "type": "behavioral", "tags": ["data entry", "accuracy"], "difficulty": 2},
        {"question": "Tell me about a time you improved an office process. What was the result?", "type": "behavioral", "tags": ["process improvement", "initiative"], "difficulty": 2},
    ],
    "data_entry_operator": [
        {"question": "What is your average typing speed? How do you maintain accuracy under tight deadlines?", "type": "behavioral", "tags": ["typing", "speed vs accuracy"], "difficulty": 1},
        {"question": "How do you ensure data accuracy when entering hundreds of records in a shift?", "type": "behavioral", "tags": ["accuracy", "quality control"], "difficulty": 2},
        {"question": "Describe a time you found a data discrepancy. How did you resolve it?", "type": "behavioral", "tags": ["problem solving", "attention to detail"], "difficulty": 2},
        {"question": "What is your process for cross-checking data after entry?", "type": "behavioral", "tags": ["verification", "process"], "difficulty": 1},
        {"question": "How do you handle repetitive data entry tasks without losing focus?", "type": "behavioral", "tags": ["focus", "consistency"], "difficulty": 1},
        {"question": "Are you familiar with data validation in Excel? Give an example of when you used it.", "type": "technical", "tags": ["excel", "data validation"], "difficulty": 2},
        {"question": "What would you do if you noticed the source data you were given had errors?", "type": "behavioral", "tags": ["initiative", "escalation"], "difficulty": 2},
        {"question": "How do you handle pressure when there is a large backlog of data to enter by end of day?", "type": "behavioral", "tags": ["time management", "pressure"], "difficulty": 1},
        {"question": "Describe your experience with any database entry systems or ERP software.", "type": "technical", "tags": ["software", "erp"], "difficulty": 1},
        {"question": "Tell me about a time you exceeded your daily data entry target. How did you achieve it?", "type": "behavioral", "tags": ["performance", "motivation"], "difficulty": 1},
    ],
    "bpo_executive": [
        {"question": "How do you handle a customer who is shouting and using abusive language on a call?", "type": "behavioral", "tags": ["de-escalation", "call handling"], "difficulty": 2},
        {"question": "What is Average Handle Time and why is it important in a BPO environment?", "type": "technical", "tags": ["kpi", "aht"], "difficulty": 1},
        {"question": "Describe a time you achieved a high CSAT score. What did you do differently?", "type": "behavioral", "tags": ["csat", "performance"], "difficulty": 2},
        {"question": "How do you build rapport quickly with a customer at the start of a call?", "type": "behavioral", "tags": ["rapport building", "communication"], "difficulty": 1},
        {"question": "What is the difference between inbound and outbound calling? Which do you prefer and why?", "type": "behavioral", "tags": ["call types", "preference"], "difficulty": 1},
        {"question": "How do you handle rejection when a customer refuses your offer or solution?", "type": "behavioral", "tags": ["objection handling", "resilience"], "difficulty": 2},
        {"question": "What would you do if you did not meet your daily KPI targets?", "type": "behavioral", "tags": ["self-improvement", "accountability"], "difficulty": 2},
        {"question": "How do you maintain energy and enthusiasm during back-to-back calls for 8 hours?", "type": "behavioral", "tags": ["stamina", "attitude"], "difficulty": 1},
        {"question": "Describe your experience with CRM software for call logging and follow-ups.", "type": "technical", "tags": ["crm", "software"], "difficulty": 1},
        {"question": "Tell me about a time you convinced a hesitant customer to take an offer. What was your approach?", "type": "behavioral", "tags": ["persuasion", "sales"], "difficulty": 2},
    ],
}


class QuestionBank:
    _lock = threading.Lock()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        os.makedirs(_DB_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(path=_DB_DIR)
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self._seed()

    def _get_or_create_collection(self, role_key: str):
        name = f"qbank_{role_key}"
        try:
            return self.client.get_collection(name)
        except Exception:
            return self.client.create_collection(name, embedding_function=self.ef)

    def _seed(self):
        for role_key, questions in SEED_QUESTIONS.items():
            coll = self._get_or_create_collection(role_key)
            if coll.count() >= len(questions):
                continue
            existing_ids = set(coll.get()["ids"]) if coll.count() > 0 else set()
            for i, q in enumerate(questions):
                qid = f"{role_key}_{i}"
                if qid not in existing_ids:
                    coll.add(
                        documents=[q["question"]],
                        metadatas=[{
                            "type": q["type"],
                            "tags": ",".join(q["tags"]),
                            "difficulty": q["difficulty"],
                            "role_key": role_key,
                        }],
                        ids=[qid],
                    )

    def search(self, role_key: str, query_text: str, n: int = 3) -> list[dict]:
        coll = self._get_or_create_collection(role_key)
        if coll.count() == 0:
            return []
        try:
            results = coll.query(
                query_texts=[query_text],
                n_results=min(n, coll.count()),
            )
            out = []
            for i in range(len(results["ids"][0])):
                out.append({
                    "question": results["documents"][0][i],
                    "type": results["metadatas"][0][i].get("type", "technical"),
                    "difficulty": results["metadatas"][0][i].get("difficulty", 2),
                    "tags": results["metadatas"][0][i].get("tags", "").split(","),
                })
            return out
        except Exception:
            return []

    def get_question_context(self, role_key: str, previous_qa_pairs: list, n: int = 3) -> str:
        if not previous_qa_pairs:
            query = f"Opening questions for {role_key} interview"
        else:
            last_qa = previous_qa_pairs[-1]
            query = f"{last_qa.get('question', '')} {last_qa.get('answer_transcript', '')}"

        results = self.search(role_key, query, n)
        if not results:
            return ""

        lines = ["REFERENCE QUESTIONS FROM OUR CURATED QUESTION BANK (adapt these for the interview):"]
        for i, r in enumerate(results, 1):
            lines.append(f"  {i}. [{r['type'].upper()}, difficulty {r['difficulty']}] {r['question']}")
        return "\n".join(lines)
