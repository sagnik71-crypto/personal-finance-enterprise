# Personal-finance-enterprise 📈

A secure, cloud-hosted personal finance dashboard designed for tracking spending, setting custom budgets, analyzing expenses via interactive charts, and managing personal financial data.

---

## ✨ Key Features

* **Authentication:** Google OAuth 2.0 integration for seamless user login.
* **Multi-Tiered Data Persistence:** Custom Python backend utilizing SQLite3 for main storage, CSV exports, plain text logs, and `pickle` serialization.
* **Interactive Visualization:** Dynamic financial charts built with Chart.js and Tailwind CSS.
* **Data Management:** Filter expenses by custom date ranges and export transactions directly to CSV files.
* **SEO & Indexing:** Optimized with structured meta tags, `robots.txt`, and XML sitemap support, fully indexed via Google Search Console.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, Tailwind CSS, Chart.js, Google Identity Services (GIS)
* **Backend:** Python (`http.server`, custom REST API handlers)
* **Database & Storage:** SQLite3, CSV, Pickle
* **Deployment:** Render (`https://personal-finance-enterprise.onrender.com`)

---

## 📁 Repository Structure

```text
.
├── index.html       # Web dashboard frontend & Tailwind UI
├── backend.py       # Python HTTP server & API routes
├── exporter.py      # CSV export & date-filtering logic
├── database.db      # SQLite relational database
├── sitemap.xml      # Google indexing site map
└── robots.txt       # Search engine crawler directives

