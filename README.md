# 🚀 AI Money Mentor

An AI-powered personal finance assistant that helps users analyze their financial health, plan for financial independence (FIRE), and receive actionable investment advice — all in seconds.

---

## 📌 Problem

95% of individuals lack structured financial planning. Traditional financial advisors are expensive (₹25,000+/year) and inaccessible to most people.

---

## 💡 Solution

AI Money Mentor provides a **free, intelligent financial advisor** that:

* Evaluates financial health
* Generates a Money Health Score
* Projects retirement (FIRE)
* Provides personalized financial advice

---

## ⚙️ Features

### 📊 Money Health Score

* Multi-dimensional scoring (0–100)
* Covers savings, debt, expenses, and net worth

### 🔥 FIRE Planner

* Calculates retirement corpus
* Estimates years to financial independence
* Suggests investment strategy

### 🤖 AI Financial Advisor

* Personalized financial insights
* Actionable steps
* Risk identification

---

## 🧠 Architecture

* **Frontend:** Next.js + Tailwind
* **Backend:** FastAPI
* **AI Layer:** LLM (OpenAI / Gemini)
* **Core Logic:** Rule-based financial engine

The system uses a **hybrid architecture**:

* Deterministic financial calculations for accuracy
* AI for personalized recommendations

---

## 🔄 Workflow

1. User inputs financial data
2. Backend validates and processes data
3. Financial metrics are calculated
4. Score and FIRE plan are generated
5. AI provides insights and recommendations
6. Results displayed on dashboard

---

## 🛠️ Tech Stack

* Next.js (Frontend)
* FastAPI (Backend)
* Axios
* Tailwind CSS
* Recharts
* OpenAI / Gemini API

---

## 🚀 How to Run Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🌐 Deployment

* Frontend: Vercel
* Backend: Render

---

## 📈 Impact

* Reduces dependency on expensive financial advisors
* Provides instant financial insights
* Makes financial planning accessible to everyone

---

## 🎯 Future Improvements

* Tax optimization module
* Mutual fund portfolio analysis
* Real-time market data integration
* User accounts and tracking

---

## 👨‍💻 Team

Built during a hackathon to democratize financial planning using AI.
