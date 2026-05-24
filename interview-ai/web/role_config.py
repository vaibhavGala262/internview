CATEGORIES = {
    "technical": {
        "label": "Technical",
        "roles": [
            "software_engineer",
            "ai_engineer",
            "data_scientist",
            "iot_engineer",
            "frontend_engineer",
            "backend_engineer",
            "devops_engineer",
            "product_manager",
        ],
    },
    "cx": {
        "label": "CX / Non-Technical",
        "roles": [
            "cx_associate",
            "customer_support",
            "office_assistant",
            "data_entry_operator",
            "bpo_executive",
        ],
    },
}

ROLES = {
    # ── TECHNICAL ──────────────────────────────────────────────────────────
    "software_engineer": {
        "title": "Software Engineer",
        "context": "Software Engineer — focus: system design, data structures, algorithms, clean code, API architecture, testing, debugging, performance optimization",
        "skills": ["system design", "algorithms", "data structures", "API design", "testing", "code optimization"],
        "hiring_bar": {
            "high_wage": {"communication": 70, "technical": 75, "problem_solving": 75, "behavioral": 65, "delivery": 65},
            "low_wage": {"communication": 60, "technical": 50, "problem_solving": 55, "behavioral": 60, "delivery": 55},
        },
    },
    "ai_engineer": {
        "title": "AI / ML Engineer",
        "context": "AI Engineer — focus: machine learning algorithms, deep learning (CNNs, RNNs, Transformers), NLP, computer vision, model training & deployment, MLOps, data pipelines, model evaluation & optimization",
        "skills": ["ML algorithms", "deep learning", "NLP", "computer vision", "model deployment", "MLOps", "data pipelines"],
        "hiring_bar": {
            "high_wage": {"communication": 70, "technical": 85, "problem_solving": 80, "behavioral": 65, "delivery": 65},
            "low_wage": {"communication": 60, "technical": 55, "problem_solving": 60, "behavioral": 60, "delivery": 55},
        },
    },
    "data_scientist": {
        "title": "Data Scientist",
        "context": "Data Scientist — focus: statistics & probability, hypothesis testing, regression & classification, feature engineering, data visualization, SQL, experimentation (A/B testing), storytelling with data",
        "skills": ["statistics", "machine learning", "SQL", "data visualization", "A/B testing", "feature engineering"],
        "hiring_bar": {
            "high_wage": {"communication": 75, "technical": 80, "problem_solving": 80, "behavioral": 65, "delivery": 65},
            "low_wage": {"communication": 65, "technical": 50, "problem_solving": 60, "behavioral": 60, "delivery": 55},
        },
    },
    "iot_engineer": {
        "title": "IoT / Embedded Engineer",
        "context": "IoT Engineer — focus: embedded systems, microcontrollers (ESP32, Arduino), sensor integration, communication protocols (MQTT, BLE, Zigbee), RTOS, hardware-software co-design, edge computing, power optimization",
        "skills": ["embedded systems", "sensors", "microcontrollers", "communication protocols", "edge computing", "RTOS"],
        "hiring_bar": {
            "high_wage": {"communication": 65, "technical": 80, "problem_solving": 75, "behavioral": 60, "delivery": 65},
            "low_wage": {"communication": 55, "technical": 55, "problem_solving": 60, "behavioral": 60, "delivery": 55},
        },
    },
    "frontend_engineer": {
        "title": "Frontend Engineer",
        "context": "Frontend Engineer — focus: HTML/CSS, JavaScript/TypeScript, React/Vue/Angular, responsive design, web performance optimization, accessibility, state management, browser APIs",
        "skills": ["HTML/CSS", "JavaScript", "React/Vue/Angular", "responsive design", "web performance", "accessibility"],
        "hiring_bar": {
            "high_wage": {"communication": 70, "technical": 70, "problem_solving": 70, "behavioral": 65, "delivery": 70},
            "low_wage": {"communication": 60, "technical": 45, "problem_solving": 55, "behavioral": 60, "delivery": 55},
        },
    },
    "backend_engineer": {
        "title": "Backend Engineer",
        "context": "Backend Engineer — focus: server-side languages (Python/Java/Go/Node.js), databases (SQL & NoSQL), RESTful & GraphQL API design, caching (Redis), message queues, microservices, security, authentication, scalability",
        "skills": ["server-side development", "databases", "API design", "caching", "microservices", "security", "scalability"],
        "hiring_bar": {
            "high_wage": {"communication": 65, "technical": 78, "problem_solving": 75, "behavioral": 60, "delivery": 65},
            "low_wage": {"communication": 55, "technical": 50, "problem_solving": 55, "behavioral": 60, "delivery": 55},
        },
    },
    "devops_engineer": {
        "title": "DevOps Engineer",
        "context": "DevOps Engineer — focus: CI/CD pipelines, Docker & Kubernetes, infrastructure as code (Terraform), cloud services (AWS/GCP/Azure), monitoring & observability, scripting, configuration management, security practices",
        "skills": ["CI/CD", "containers", "Kubernetes", "cloud services", "infrastructure as code", "monitoring", "scripting"],
        "hiring_bar": {
            "high_wage": {"communication": 65, "technical": 75, "problem_solving": 75, "behavioral": 60, "delivery": 65},
            "low_wage": {"communication": 55, "technical": 50, "problem_solving": 60, "behavioral": 60, "delivery": 55},
        },
    },
    "product_manager": {
        "title": "Product Manager",
        "context": "Product Manager — focus: product strategy, user research & interviews, roadmap prioritization, stakeholder management, data-driven decision making, A/B testing, Agile/Scrum, market analysis, OKR & KPI definition",
        "skills": ["product strategy", "user research", "roadmap planning", "stakeholder management", "data analysis", "Agile"],
        "hiring_bar": {
            "high_wage": {"communication": 80, "technical": 50, "problem_solving": 75, "behavioral": 80, "delivery": 70},
            "low_wage": {"communication": 70, "technical": 35, "problem_solving": 60, "behavioral": 70, "delivery": 60},
        },
    },
    # ── CX / NON-TECHNICAL ────────────────────────────────────────────────
    "cx_associate": {
        "title": "CX Associate",
        "context": "CX Associate — focus: customer service, complaint resolution, communication skills, empathy, basic computer literacy, data entry, CRM tools, teamwork, time management",
        "skills": ["customer service", "communication", "problem resolution", "CRM tools", "data entry"],
        "hiring_bar": {
            "high_wage": {"communication": 75, "technical": 40, "problem_solving": 65, "behavioral": 75, "delivery": 65},
            "low_wage": {"communication": 60, "technical": 40, "problem_solving": 55, "behavioral": 65, "delivery": 55},
        },
    },
    "customer_support": {
        "title": "Customer Support Executive",
        "context": "Customer Support Executive — focus: handling customer inquiries via phone/email/chat, ticket management, product knowledge, escalation handling, SLA adherence, customer satisfaction, active listening",
        "skills": ["ticketing systems", "active listening", "email etiquette", "product knowledge", "escalation handling"],
        "hiring_bar": {
            "high_wage": {"communication": 75, "technical": 30, "problem_solving": 65, "behavioral": 75, "delivery": 65},
            "low_wage": {"communication": 60, "technical": 30, "problem_solving": 55, "behavioral": 65, "delivery": 55},
        },
    },
    "office_assistant": {
        "title": "Office Assistant",
        "context": "Office Assistant — focus: administrative support, document management, scheduling & calendar management, MS Office (Word, Excel, PowerPoint), data entry, filing, coordination, email correspondence",
        "skills": ["MS Office", "data entry", "scheduling", "document management", "email correspondence"],
        "hiring_bar": {
            "high_wage": {"communication": 65, "technical": 30, "problem_solving": 55, "behavioral": 65, "delivery": 60},
            "low_wage": {"communication": 55, "technical": 30, "problem_solving": 50, "behavioral": 60, "delivery": 50},
        },
    },
    "data_entry_operator": {
        "title": "Data Entry Operator",
        "context": "Data Entry Operator — focus: accurate data entry, typing speed & accuracy, data validation, spreadsheet management, database updates, attention to detail, meeting daily targets, basic Excel formulas",
        "skills": ["typing", "data validation", "Excel", "data management", "attention to detail"],
        "hiring_bar": {
            "high_wage": {"communication": 55, "technical": 35, "problem_solving": 50, "behavioral": 55, "delivery": 60},
            "low_wage": {"communication": 50, "technical": 35, "problem_solving": 45, "behavioral": 55, "delivery": 50},
        },
    },
    "bpo_executive": {
        "title": "BPO / Call Center Executive",
        "context": "BPO Executive — focus: inbound/outbound calling, customer query resolution, call handling & documentation, rapport building, objection handling, achieving KPIs (AHT, CSAT, FCR), process adherence",
        "skills": ["call handling", "objection handling", "KPI achievement", "CRM usage", "process adherence"],
        "hiring_bar": {
            "high_wage": {"communication": 75, "technical": 30, "problem_solving": 60, "behavioral": 70, "delivery": 65},
            "low_wage": {"communication": 60, "technical": 30, "problem_solving": 50, "behavioral": 65, "delivery": 55},
        },
    },
}


def get_role_config(role_key: str) -> dict:
    return ROLES.get(role_key, ROLES["software_engineer"])


def get_enriched_role(role_key: str) -> str:
    cfg = get_role_config(role_key)
    return cfg["context"]


def get_hiring_bar(role_key: str, icp_type: str) -> dict:
    cfg = get_role_config(role_key)
    return cfg["hiring_bar"].get(icp_type, cfg["hiring_bar"]["high_wage"])


def get_category_roles(category_key: str) -> list:
    cat = CATEGORIES.get(category_key)
    if not cat:
        return []
    return [ROLES[rk] for rk in cat["roles"] if rk in ROLES]
