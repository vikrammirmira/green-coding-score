# 🌱 Green Coding Score

> Measuring and gamifying compute efficiency in modern software systems (especially AI/LLMs)

---

## 🚀 Problem

We optimize for:
- latency
- throughput
- cost

But ignore:

👉 **energy usage and carbon impact per request**

With AI workloads growing rapidly, this is becoming a blind spot in engineering systems.

---

## 💡 Solution

Green Coding Score introduces:

- 📊 Compute observability (tokens, execution)
- ⚡ Energy estimation layer
- 🌍 Carbon impact modeling
- 🏆 Gamified scoring system for developers

---

## 🧩 Architecture

Event-driven design:

Client → API → Event Ingestion → Scoring Engine → Gamification → APIs

---

## ⚙️ Core Concepts

- **Token Efficiency** → Less compute for same outcome
- **Energy Estimation** → tokens × factor
- **Carbon Signal** → energy × regional intensity
- **Composite Score (0–100)**

---

## 🧪 Example

| Scenario | Tokens | Score |
|--------|------|------|
| Baseline | 2000 | 62 |
| Optimized | 1200 | 88 |

👉 ~40% reduction → better efficiency + lower carbon

---

## 🔥 Why this matters

This project explores:

👉 Sustainability as a **first-class engineering metric**

---

## 🚧 Status

MVP implemented with:
- FastAPI services
- Modular routing
- Scoring + gamification

---

## 🚀 Next

- CI/CD integration (PR scoring)
- Real carbon intensity APIs
- Dashboard
- VS Code extension

---

## 🤝 Open to ideas & collaboration