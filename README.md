# ZionX - Specialized AI Healthcare Personal Assistant

> **Hackathon Theme**: *Data to Prevention; AI as your health personal*

## 🎯 Problem Statement

Most AI (LLM-based) systems designed for personal healthcare are built for **general-purpose use**, resulting in:
- ❌ **Broad, generic responses** that lack medical depth
- ❌ **Shallow guidance** not tailored to specific patient groups
- ❌ **Inappropriate advice** due to lack of domain-specific context
- ❌ **No preventive analysis** of health patterns over time

**Example**: A pregnant woman with headaches gets the same generic advice as anyone else, missing critical obstetric considerations.

---

## 💡 Our Solution

**ZionX** is an intelligent **multi-agent healthcare system** that routes queries to **specialized medical experts**, each optimized for specific patient groups and conditions.

### How It Works

```
User Query
    ↓
[Orchestrator Agent]
    ├─ Analyzes context & symptoms
    ├─ Assesses risk level
    └─ Routes to appropriate specialist
        ↓
[Specialist Tool] (with domain-specific prompt)
    ├─ 🤰 Pregnancy Advisor (ACOG/WHO guidelines)
    ├─ 🩸 Diabetes Advisor (ADA/IDF standards)
    ├─ 👶 Pediatrics Advisor (AAP guidelines)
    ├─ 🧠 Mental Health Advisor (DSM-5/NICE)
    ├─ 🚨 Emergency Triage (ATLS protocols)
    └─ 🔬 Preventive Health Analyzer (pattern detection)
        ↓
[Personalized Response]
    ├─ Uses patient history from memory
    ├─ Provides risk assessment (low/medium/high/critical)
    ├─ Recommends action (monitor/schedule_visit/seek_urgent_care/call_emergency)
    └─ Extracts long-term facts for future context
```

---

## 🚀 Key Features

### 1. **Smart Routing**
Routes queries to the most appropriate specialist based on context:
- **"I'm 7 months pregnant with headaches"** → Pregnancy Advisor
- **"My blood sugar is 280 mg/dL"** → Diabetes Advisor  
- **"My 3-year-old has a 39°C fever"** → Pediatrics Advisor
- **"Chest pain and difficulty breathing"** → Emergency Triage

### 2. **Long-Term Memory** 🧬
- Stores patient facts across sessions (medications, conditions, allergies)
- Document upload with AI-powered health fact extraction
- Personalized responses based on accumulated health history

### 3. **Preventive AI** 🛡️
- Analyzes health patterns over time
- Detects early warning signs (e.g., rising blood sugar trends)
- Recommends screenings based on risk factors
- Provides lifestyle interventions before conditions worsen

### 4. **Risk Assessment** ⚡
Every medical response includes:
- **Risk Level**: `low` | `medium` | `high` | `critical`
- **Urgency**: `monitor` | `schedule_visit` | `seek_urgent_care` | `call_emergency`

### 5. **Nigerian Context** 🇳🇬
- **Multi-language support**: Yoruba, Hausa, Igbo, English
- **Voice input/output** in local languages via Spitch API
- Translation pipeline: Local language → English → Specialist → Local language

---

## 🏗️ Architecture

### Backend (Flask + LangChain)
```
ZionX-Backend/
├── agent.py              # Orchestrator agent with routing logic
├── agent_config.py       # Configuration (model, temperature, context limits)
├── app.py                # Flask API endpoints
├── main.py               # Agent execution entry point
├── memory.py             # Long-term user memory (file-based)
├── users.py              # User authentication & session management
├── document_extractor.py # PDF/DOCX health fact extraction
└── tools/
    ├── pregnancy.py      # Pregnancy specialist (ACOG/WHO)
    ├── diabetes.py       # Diabetes specialist (ADA/IDF)
    ├── pediatrics.py     # Pediatric specialist (AAP)
    ├── mental_health.py  # Mental health specialist (DSM-5/NICE)
    ├── emergency.py      # Emergency triage (ATLS)
    ├── preventive.py     # Preventive health analyzer
    └── specialist_utils.py # Shared LLM instance manager
```

### Frontend (Next.js 14)
```
ZionX-Frontend/src/
├── components/
│   ├── ChatWindow.js       # Main chat interface
│   ├── SpecialistCards.js  # Specialist selection UI
│   ├── MessageBubble.js    # Message display with risk badges
│   ├── RiskPanel.js        # Risk level visualization
│   ├── DocumentUpload.js   # Health document upload
│   └── OnboardingModal.js  # User context collection
└── lib/
    └── api.js              # API client
```

---

## 📋 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login (returns session token)
- `POST /auth/logout` - Logout
- `GET /auth/verify` - Verify session

### Chat
- `POST /chat` - Send message to orchestrator
  ```json
  {
    "message": "I'm 7 months pregnant with headaches",
    "thread_id": "session-123"
  }
  ```
  **Response**:
  ```json
  {
    "response": "Detailed pregnancy-specific advice...",
    "risk_level": "medium",
    "urgency": "schedule_visit"
  }
  ```

### Memory & Documents
- `GET /memory?user_id=<id>` - Get user's health facts
- `POST /upload` - Upload health document (PDF/DOCX)
- `DELETE /memory?user_id=<id>` - Clear user memory

### Voice (Nigerian Languages)
- `POST /speech/transcribe` - Convert speech to text (Yoruba/Hausa/Igbo/English)
- `POST /speech/generate` - Convert text to speech in target language
- `GET /speech/languages` - List supported languages

### Onboarding & Profile
- `POST /onboarding/profile` - Update user's health profile
  ```json
  {
    "allergies": ["Penicillin", "Peanuts"],
    "medications_to_avoid": ["Aspirin"],
    "blood_group": "O+",
    "conditions": ["Type 2 Diabetes", "Hypertension"],
    "ongoing_issues": ["Recurring headaches"],
    "emergency_contacts": {
      "consent_given": true,
      "doctor": {
        "name": "Dr. Adeyemi",
        "email": "dr.adeyemi@hospital.ng",
        "phone": "+234-xxx-xxxx"
      },
      "loved_ones": [
        {"name": "John Doe", "email": "john@example.com", "relation": "Spouse"}
      ]
    },
    "language": "yo",
    "output_mode": "voice"
  }
  ```
- `GET /onboarding/profile` - Get user's profile

### Daily Health Tracking
- `POST /tracking/daily` - Submit daily health update
  ```json
  {
    "mood": "good",
    "symptoms": ["mild headache"],
    "energy": "7/10",
    "medications": ["Metformin 500mg"],
    "notes": "Slept well, ate healthy meals"
  }
  ```
- `GET /tracking/history?days=30` - Get tracking history
- `GET /tracking/summary?days=7` - Get formatted summary

---

## 📱 Platform Overview

### 1. Onboarding Process
During onboarding, users provide personal information to give the AI context about their health and background. **This step is optional but highly recommended** for better personalization.

**Users can provide:**
- **Medical Personal Data**
  - Allergies
  - Medications to avoid
  - Blood group
- **Medical Reports**
  - Existing medical conditions
  - Ongoing health issues
  - Upload PDF/DOCX documents for automatic extraction
- **Emergency Contacts** *(Requires explicit user consent)*
  - Personal doctor's email
  - Loved ones or trusted contacts

This information helps the model deliver safer and more context-aware support.

### 2. Tracking & Daily Updates
Users can provide daily updates about their wellbeing or activities:
- The AI extracts key insights from these updates
- Important information is stored in **long-term memory** for future context
- Patterns are analyzed for preventive health opportunities

### 3. Memory System
The platform uses **two types of memory**:

**Short-Term Memory:**
- Stores information from the current conversation
- Maintained per thread/session (via `thread_id`)
- Enables contextual follow-up questions

**Long-Term Memory:**
- Stores relevant insights from past interactions
- Includes onboarding data (allergies, conditions, medications)
- Includes daily tracking history
- Includes extracted facts from uploaded documents
- Persists across all sessions

### 4. Input Modes (User → Platform)
Users can communicate through multiple channels:
1. **Text** - Direct text input
2. **Voice** - Speech-to-text in Yoruba, Hausa, Igbo, or English
3. **Video** *(Planned)* - Future enhancement

All inputs are converted to English text before being processed by the specialized agents.

### 5. Output Modes (Platform → User)
Users can choose their preferred response format:
1. **Text** - Written response
2. **Voice** - Text-to-speech in user's preferred language
3. **Video** *(Planned)* - Future enhancement with avatar

The platform adapts to the user's `output_mode` preference set during onboarding.

### 6. Normal Usage Flow

When a user interacts with the platform, the AI uses:
1. **Onboarding data** (allergies, conditions, medications)
2. **Long-term memory** (past interactions and extracted facts)
3. **Daily tracking data** (recent health updates)
4. **Short-term memory** (current conversation context)

**Response Behavior:**
- The AI may ask follow-up questions for clarification before answering
- If the AI does not know the answer, it will clearly say so
- **Emergency situations** with prior consent → Platform can alert emergency contacts (doctor or loved ones) via email
- Risk assessment is provided with every medical query
- Urgency level guides appropriate action (monitor, visit doctor, seek urgent care, call emergency)
- `GET /speech/languages` - List supported languages

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Google Gemini API key
- (Optional) Spitch API key for voice features

### Backend Setup
```bash
cd ZionX-Backend

# Install dependencies
uv sync

# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=your_gemini_api_key_here
SPECIALIST_MODEL=gemini-2.0-flash-exp
SPECIALIST_TEMPERATURE=0.1
SPITCH_API_KEY=your_spitch_key  # Optional for voice
EOF

# Run development server
uv run python3 -m app
# Server runs on http://localhost:5000
```

### Frontend Setup
```bash
cd ZionX-Frontend

# Install dependencies
npm install

# Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:5000
EOF

# Run development server
npm run dev
# App runs on http://localhost:3000
```

---

## 🎬 Demo Scenarios

### Scenario 1: Pregnancy with Context
**User**: "I'm 7 months pregnant and have been getting headaches"  
**ZionX**:
- Routes to **pregnancy_advisor**
- Checks blood pressure concerns specific to third trimester
- Risk: `medium`, Urgency: `schedule_visit`
- Extracts fact: "User is pregnant, 28 weeks gestation"

### Scenario 2: Emergency Detection
**User**: "Severe chest pain and difficulty breathing"  
**ZionX**:
- Routes to **emergency_triage**
- Immediately flags as life-threatening
- Risk: `critical`, Urgency: `call_emergency`
- Provides FAST stroke protocol and tells user to call ambulance NOW

### Scenario 3: Preventive Analysis
**User uploads** multiple blood sugar readings (120 → 135 → 148 mg/dL)  
**User**: "What do you see in my health patterns?"  
**ZionX**:
- Routes to **preventive_health_analyzer**
- Detects rising glucose trend → pre-diabetes risk
- Risk: `medium`, Urgency: `schedule_visit`
- Recommends: HbA1c test, dietary changes, exercise plan

### Scenario 4: Nigerian Language
**User** (speaks in Yoruba): *"Mo ni ibà, ara mi kò balẹ́"*  
**ZionX**:
1. Transcribes: "I have a fever, I don't feel well"
2. Translates to English
3. Routes to appropriate specialist
4. Translates response back to Yoruba
5. Generates Yoruba speech output

---

## 🧪 Testing

```bash
# Backend tests
cd ZionX-Backend

# Test orchestrator routing
uv run python3 -c "
from main import run
print(run('I\\'m 7 months pregnant with headaches', user_id='test'))
"

# Test emergency detection
uv run python3 -c "
from main import run
result = run('Severe chest pain and shortness of breath', user_id='test')
print(f'Risk: {result[\"risk_level\"]}, Urgency: {result[\"urgency\"]}')
"

# Run API
uv run python3 -m app
```

```bash
# Frontend - Open browser
http://localhost:3000
```

---

## 📊 Impact & Innovation

### What Makes ZionX Different?

| Feature | Generic AI Chatbots | ZionX |
|---------|---------------------|-------|
| Medical depth | Shallow, general advice | Domain-specific guidelines (ACOG, ADA, AAP) |
| Personalization | One-size-fits-all | Uses patient history + context |
| Prevention | Reactive only | Proactive pattern detection |
| Risk assessment | None | Dynamic risk + urgency scoring |
| Nigerian context | English only | 4 languages + local health context |
| Emergency handling | Unreliable | Dedicated triage with protocols |

### Real-World Impact
- **Reduces unnecessary ER visits** via appropriate triage
- **Improves health outcomes** through personalized, guideline-based advice
- **Increases accessibility** in Nigeria via local language support
- **Enables early intervention** through preventive pattern detection
- **Empowers patients** with clear risk assessments and action plans

---

## 🔐 Safety & Disclaimers

Every response includes:
> ⚠️ **This is not a substitute for professional medical advice. Always consult with your healthcare provider.**

### Safety Features
- Emergency symptoms trigger immediate escalation
- Risk levels guide appropriate care-seeking behavior
- Medical guidelines prevent dangerous advice
- Disclaimers on every specialist response

---

## 🚧 Future Enhancements

- [ ] **Risk calculators**: Framingham CVD, ASCVD, QRISK3
- [ ] **Integration**: Wearables (glucose monitors, fitness trackers)
- [ ] **Visual analytics**: Health trend dashboards
- [ ] **Telemedicine**: Direct booking with local clinics
- [ ] **Nigerian health database**: Malaria, typhoid, sickle cell awareness
- [ ] **Family profiles**: Manage multiple dependents

---

## 👥 Team

Built for the **"Data to Prevention; AI as your health personal"** hackathon.

---

## 📄 License

Proprietary - Hackathon Project 2026

---

## 🙏 Acknowledgments

- **LangChain** for agentic framework
- **Google Gemini** for multi-modal LLM capabilities
- **Spitch** for Nigerian language voice support
- Medical guidelines: ACOG, WHO, ADA, IDF, AAP, DSM-5, NICE, ATLS, USPSTF

---

## 📞 Support

For questions or demo requests, contact the development team.

**ZionX** - *Your specialized AI health companion, powered by intelligence, guided by science.*
