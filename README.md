<div align="center">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=Playwright&logoColor=white" alt="Playwright"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
  
  <h1>📍 Google Maps High-Speed Lead Scraper</h1>
  <p><strong>A highly concurrent, stealthy, and professional Google Maps scraper built with Streamlit and Playwright.</strong></p>
</div>

<br />

Extract high-quality leads directly from Google Maps in real-time. This tool automates the process of finding local businesses, enriching them with accurate contact information (including phones and emails scraped from their websites), and exporting them to clean CSV or Excel formats.

## ✨ Key Features

- **🚀 High-Speed Asynchronous Scraping:** Utilizes `asyncio` and `playwright.async_api` for rapid, non-blocking data extraction.
- **🕵️‍♂️ Anti-Bot & Stealth:** Bypasses basic bot detection using `playwright-stealth` and human-like jitter/mouse movements.
- **📧 Deep Enrichment:** Doesn't just scrape maps—automatically visits the business's website in the background to scrape public Email Addresses.
- **📞 Robust Contact Extraction:** Clicks into business profiles to fetch hidden phone numbers and full postal addresses.
- **🧹 Advanced Filtering:** Only keep the leads that matter. Instantly filter for businesses that have valid Emails and/or Phone Numbers.
- **💾 One-Click Export:** Download your generated leads directly to `.xlsx` (Excel) or `.csv` with a single click.
- **🐳 Deployment Ready:** Comes with a pre-configured `Dockerfile` for instant deployment on cloud platforms like Hugging Face Spaces or Render.

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **Scraping Engine:** [Playwright](https://playwright.dev/python/) (Chromium) + [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- **Network / Async:** `aiohttp`, `asyncio`
- **Data Manipulation:** `pandas`, `openpyxl`

---

## 💻 Local Installation

### Prerequisites
- Python 3.9+ installed on your system.
- Node.js (Optional, but recommended for Playwright dependencies on some systems).

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/iamribas12/lead-scraper.git
   cd lead-scraper
   ```

2. **Create a Virtual Environment (Recommended):**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Browsers:**
   ```bash
   playwright install chromium
   ```

5. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
   The UI will open automatically in your browser at `http://localhost:8501`.

---

## ☁️ Cloud Deployment (Hugging Face Spaces)

This project is 100% ready to be hosted for free on Hugging Face Spaces using Docker.

1. Create a free account at [Hugging Face](https://huggingface.co/).
2. Create a new **Space**.
3. For the **Space SDK**, select **Docker** > **Blank**.
4. Connect your GitHub repository (`iamribas12/lead-scraper`) OR upload the project files manually.
5. The platform will automatically build the environment using the provided `Dockerfile`. Once the build is complete (2-5 mins), your scraper will be live on a public URL!

---

## 🎯 How to Use

1. **Search Query:** Enter your target niche and location (e.g., `Roofers in Dallas, Texas`).
2. **Target Lead Limit:** Use the slider to set the maximum number of leads you want to extract (up to 500 per search).
3. **Headless Mode:** Keep checked (recommended) to hide the browser window in the background, or uncheck to watch the bot work in real-time.
4. **Advanced Filtering:** Use the sidebar toggles if you strictly require leads to have an Email or a Phone Number.
5. **Start:** Click `🚀 Start Search & Extraction`.
6. **Export:** Once finished, use the red download buttons to save your `.csv` or `.xlsx` file.

---

## ⚠️ Disclaimer

This tool is for educational and personal use only. Web scraping may violate the Terms of Service of certain websites. Always ensure you have the right to scrape, store, and use the data you collect, and comply with all local laws and regulations (such as GDPR or CCPA) regarding data privacy and cold outreach. The developers of this tool assume no liability for misuse.
