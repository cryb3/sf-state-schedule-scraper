# SF State Schedule Scraper - Web App

🌐 **Live Web App**: [Coming Soon - Deploy to Streamlit Cloud]

## Overview

This is a web-based version of the SF State Class Schedule Scraper that allows users to generate instructor workload reports directly from their browser without any software installation.

## Features

- 🌐 **Web-based**: No installation required - just visit the website
- 📊 **Interactive**: Real-time progress updates and data visualization
- 📥 **Direct Download**: Generate and download Excel reports instantly
- 🎯 **User-friendly**: Simple sidebar interface with helpful tooltips
- 📱 **Responsive**: Works on desktop, tablet, and mobile devices

## How to Use

1. Visit the web app URL
2. Enter the **Term Code** (e.g., 2253 for Spring 2025)
3. Enter the **Subject Code** (e.g., FIN, ACCT, MGMT)
4. Select **Class Category** filter (optional)
5. Click **🚀 Run Scraper**
6. Wait for the scraping to complete (2-5 minutes)
7. View results and download the Excel file

## Deployment Instructions

### Deploy to Streamlit Cloud (Free)

1. **Fork/Clone this repository**
2. **Sign up for Streamlit Cloud**: https://streamlit.io/cloud
3. **Connect your GitHub account**
4. **Create new app**:
   - Repository: `your-username/sf-state-schedule-scraper`
   - Branch: `main`
   - Main file path: `app.py`
5. **Deploy**: The app will automatically deploy and be available at your custom URL

### Alternative Deployment Options

#### Heroku
1. Create a `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Add buildpacks:
   - `heroku/python`
   - `https://github.com/heroku/heroku-buildpack-chromedriver.git`
   - `https://github.com/heroku/heroku-buildpack-google-chrome.git`

#### Railway
1. Create `railway.toml`:
   ```toml
   [build]
   builder = "NIXPACKS"
   
   [deploy]
   startCommand = "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"
   ```

## Technical Details

### Dependencies
- **Streamlit**: Web app framework
- **Selenium**: Web scraping automation
- **Pandas**: Data manipulation
- **openpyxl**: Excel file generation
- **BeautifulSoup**: HTML parsing

### System Requirements
- **Chrome/Chromium**: Required for web scraping
- **Python 3.8+**: Runtime environment

### Files Structure
```
├── app.py                 # Main Streamlit web app
├── requirements.txt       # Python dependencies
├── packages.txt          # System dependencies (for Streamlit Cloud)
├── sf_state_scraper_interactive.py  # Original desktop version
├── run_scraper.bat       # Windows launcher
├── run_scraper.command   # macOS launcher
└── README.md            # Main documentation
```

## Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/cryb3/sf-state-schedule-scraper.git
   cd sf-state-schedule-scraper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run locally**:
   ```bash
   streamlit run app.py
   ```

4. **Open browser**: Visit `http://localhost:8501`

## Troubleshooting

### Common Issues

1. **Chrome Driver Error**: Ensure Chrome/Chromium is installed
2. **Deployment Timeout**: Large datasets may take 5+ minutes to process
3. **No Classes Found**: Verify term code and subject code are correct

### Support

- **GitHub Issues**: Report bugs or request features
- **Documentation**: Check the main README.md for detailed information
- **SF State**: Verify term codes on the official class schedule website

## Privacy & Usage

- **No Data Storage**: All processing happens in real-time, no data is stored
- **Rate Limiting**: Small delays between requests to be respectful to SF State servers
- **Academic Use**: Intended for institutional workload planning and analysis

---

**Built with ❤️ using Streamlit** | [GitHub Repository](https://github.com/cryb3/sf-state-schedule-scraper) 