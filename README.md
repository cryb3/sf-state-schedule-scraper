# SF State Class Schedule Scraper

🎓 A cross-platform tool to scrape SF State class schedules and generate instructor workload reports.

## 🚀 Quick Start

### Windows Users
1. **Double-click** `run_scraper.bat`
2. Follow the prompts to enter:
   - Term (e.g., `2253` for Spring 2025)
   - Subject (e.g., `FIN` for Finance)
   - Class Category (usually `REG`)
3. Choose save location when prompted
4. Wait for completion!

### macOS Users
1. **Double-click** `run_scraper.command`
2. If prompted about security, go to System Preferences → Security & Privacy → Allow
3. Follow the same prompts as Windows users

## 📝 Input Examples

### Term Codes
- `2253` = Spring 2025
- `2251` = Fall 2024  
- `2254` = Summer 2025
- `2261` = Fall 2025

**Format:** `YYYY` + `S` where:
- `1` = Fall
- `2` = Spring  
- `3` = Summer
- `4` = Winter

### Subject Codes
- `FIN` = Finance
- `ACCT` = Accounting
- `MKTG` = Marketing
- `MGMT` = Management
- `BLAW` = Business Law
- `ECON` = Economics
- `MATH` = Mathematics
- `ENGL` = English

### Class Categories
- `REG` = Academic Regular Session (most common)
- `EXT` = Extended Education

## 📊 Output

The tool generates an Excel file with columns:
- Last Name, First Name
- Total # of UG classes
- Total # of UG students from Column D
- Total # of UG supervion classes  
- Total # of UG students from Column F
- Total # of Grad classes
- Total # of Grad students from Colum H
- Total # of Grad supervion classes
- Total # of Grad student from Column J
- Note

## 🔧 Requirements

### Automatic Installation
The launcher scripts will automatically install required packages:
- `selenium` (web scraping)
- `pandas` (data processing)
- `openpyxl` (Excel files)
- `beautifulsoup4` (HTML parsing)

### Prerequisites
- **Python 3.7+** installed
- **Google Chrome** browser
- **Internet connection**

### Manual Installation (if needed)
```bash
pip install -r requirements.txt
```

## 📁 File Structure

```
SF_State_Scraper/
├── run_scraper.bat          # Windows launcher
├── run_scraper.command      # macOS launcher  
├── sf_state_scraper_interactive.py  # Main script
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── output_files/           # Generated Excel files (created automatically)
```

## 🐛 Troubleshooting

### Chrome Driver Issues
- Chrome and ChromeDriver are automatically managed by Selenium 4+
- If issues persist: `pip install selenium --upgrade`

### Python Not Found
**Windows:**
- Install Python from [python.org](https://python.org)
- ✅ Check "Add Python to PATH" during installation

**macOS:**
- Install Python from [python.org](https://python.org)
- Or use Homebrew: `brew install python`

### Permission Denied (macOS)
```bash
chmod +x run_scraper.command
```

### Package Installation Issues
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 🔄 Course Classification

- **Undergraduate:** Course numbers 600 and below
- **Graduate:** Course numbers 700 and above
- **Supervision:** Courses with "Independent", "Internship", "Supervision", "Thesis", "Field", or "Research" in title

## 💡 Tips

1. **Large Departments:** Processing may take several minutes for departments with many courses
2. **Browser Window:** Keep the Chrome window open during processing (it closes automatically when done)
3. **Network:** Ensure stable internet connection
4. **Multiple Runs:** You can run the tool multiple times for different subjects/terms

## 📞 Support

If you encounter issues:
1. Check internet connection
2. Verify SF State website is accessible
3. Ensure Chrome browser is installed and up to date
4. Try running with administrator/sudo privileges if needed

---

**Created for SF State faculty workload analysis** 