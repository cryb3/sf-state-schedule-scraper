import streamlit as st
import pandas as pd
import io
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import base64

# Configure Streamlit page
st.set_page_config(
    page_title="SF State Class Schedule Scraper",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📚 SF State Class Schedule Scraper")
st.markdown("Generate instructor workload reports from SF State class schedules")

@st.cache_resource
def get_webdriver():
    """Initialize Chrome WebDriver with headless options for deployment"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    
    # Try different Chrome binary locations for different deployment platforms
    import os
    import shutil
    
    # Check for Chrome/Chromium in common locations
    chrome_paths = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser", 
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/opt/chrome/chrome",
        "/opt/google/chrome/chrome",
        shutil.which("chromium"),
        shutil.which("google-chrome"),
        shutil.which("chrome")
    ]
    
    chrome_binary = None
    for path in chrome_paths:
        if path and os.path.exists(path):
            chrome_binary = path
            st.info(f"Found Chrome at: {chrome_binary}")
            break
    
    if chrome_binary:
        chrome_options.binary_location = chrome_binary
    
    # For Railway and other cloud platforms, try to use system Chrome
    from selenium.webdriver.chrome.service import Service
    
    try:
        # Try to create driver with default settings first
        driver = webdriver.Chrome(options=chrome_options)
        st.success("✅ Chrome WebDriver initialized successfully!")
        return driver
    except Exception as e:
        error_msg = str(e)
        st.error(f"Failed to initialize Chrome WebDriver: {error_msg}")
        
        # Provide helpful error information
        if "chrome" in error_msg.lower() or "chromedriver" in error_msg.lower():
            st.error("❌ Chrome/ChromeDriver not found")
            st.markdown("""
            **This error means Chrome is not installed on the server.** 
            
            **For Railway deployment:**
            1. Chrome needs to be installed via system packages
            2. The current Railway deployment may not have Chrome available
            3. Try using a different deployment platform like Heroku
            
            **Alternative solutions:**
            - Deploy to Heroku (has Chrome buildpacks)
            - Use a Docker-based deployment with Chrome pre-installed
            - Deploy to a platform that supports custom system packages
            """)
        
        if chrome_binary:
            st.info(f"Found Chrome at: {chrome_binary}")
        else:
            st.warning("No Chrome binary found in standard locations.")
            
        # List what we checked
        st.markdown("**Checked locations:**")
        for path in chrome_paths:
            exists = "✅" if path and os.path.exists(path) else "❌"
            st.text(f"{exists} {path}")
        
        return None

def extract_enrollment_from_detail_page(driver, class_nbr):
    """Extract actual enrollment from the class detail page"""
    try:
        detail_url = f"https://prd-wlssb.sfsu.edu/psp/csprd/EMPLOYEE/SA/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL?Page=SSR_CLSRCH_ENTRY&Action=U&ACAD_CAREER=UGRD&INSTITUTION=SFSU0&TERM=2253&CLASS_NBR={class_nbr}"
        driver.get(detail_url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "content"))
        )
        
        # Try multiple selectors for enrollment
        enrollment_selectors = [
            "#content > div > div.detail-container.row.class-details > div.col-md-4 > div > div:nth-child(6) > div.col-xs-5.col-md-6",
            "div.col-xs-5.col-md-6",
            "span[id*='ENRL_TOT']"
        ]
        
        for selector in enrollment_selectors:
            try:
                enrollment_element = driver.find_element(By.CSS_SELECTOR, selector)
                enrollment_text = enrollment_element.text.strip()
                if enrollment_text.isdigit():
                    return int(enrollment_text)
            except NoSuchElementException:
                continue
        
        # Fallback: parse page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Look for enrollment in various ways
        enrollment_divs = soup.find_all('div', class_='col-xs-5 col-md-6')
        for div in enrollment_divs:
            text = div.get_text().strip()
            if text.isdigit() and 0 <= int(text) <= 500:
                return int(text)
        
        return 0
        
    except Exception as e:
        st.warning(f"Could not extract enrollment for class {class_nbr}: {e}")
        return 0

def scrape_sf_state_schedule(term, subject, class_category="All"):
    """Main scraping function"""
    driver = get_webdriver()
    if not driver:
        return None
    
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Navigate to the search page
        status_text.text("🌐 Navigating to SF State schedule page...")
        progress_bar.progress(10)
        
        url = "https://prd-wlssb.sfsu.edu/psp/csprd/EMPLOYEE/SA/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL"
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "CLASS_SRCH_WRK2_INSTITUTION"))
        )
        
        status_text.text("🔍 Setting up search parameters...")
        progress_bar.progress(20)
        
        # Set search parameters
        term_dropdown = driver.find_element(By.ID, "CLASS_SRCH_WRK2_STRM")
        term_dropdown.send_keys(term)
        
        subject_field = driver.find_element(By.ID, "SSR_CLSRCH_WRK_SUBJECT_SRCH")
        subject_field.clear()
        subject_field.send_keys(subject)
        
        if class_category != "All":
            class_dropdown = driver.find_element(By.ID, "SSR_CLSRCH_WRK_SSR_OPEN_ONLY")
            class_dropdown.send_keys(class_category)
        
        # Click search button
        search_button = driver.find_element(By.ID, "CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH")
        search_button.click()
        
        status_text.text("⏳ Waiting for search results...")
        progress_bar.progress(30)
        
        # Wait for results
        WebDriverWait(driver, 30).until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table[id*='ACE_']")),
                EC.presence_of_element_located((By.ID, "DERIVED_CLSMSG_ERROR_TEXT"))
            )
        )
        
        # Check for "no classes found" message
        try:
            error_element = driver.find_element(By.ID, "DERIVED_CLSMSG_ERROR_TEXT")
            if "No classes were found" in error_element.text:
                st.error("No classes were found for the specified criteria.")
                return None
        except NoSuchElementException:
            pass
        
        status_text.text("📊 Extracting class data...")
        progress_bar.progress(50)
        
        # Parse the results table
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find the results table
        table = soup.find('table', {'id': lambda x: x and 'ACE_' in x and '$ICField' in x})
        if not table:
            st.error("Could not find results table on the page.")
            return None
        
        rows = table.find_all('tr')
        data = []
        
        for i, row in enumerate(rows[1:], 1):  # Skip header row
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 8:
                try:
                    # Check if this is a header row (course title)
                    first_cell_text = cells[0].get_text().strip()
                    if not first_cell_text or any(keyword in first_cell_text.lower() 
                                                for keyword in ['select', 'class', 'course']):
                        continue
                    
                    class_nbr = cells[1].get_text().strip()
                    section = cells[2].get_text().strip()
                    component = cells[3].get_text().strip()
                    
                    # Skip if class number is not numeric
                    if not class_nbr.isdigit():
                        continue
                    
                    # Extract instructor from multiple possible cells
                    instructor = ""
                    for cell_idx in [7, 8, 9]:
                        if cell_idx < len(cells):
                            instructor_text = cells[cell_idx].get_text().strip()
                            if instructor_text and instructor_text not in ['TBA', 'Staff', '']:
                                instructor = instructor_text
                                break
                    
                    if not instructor or instructor in ['TBA', 'Staff']:
                        instructor = "TBA"
                    
                    # Get course number from the first cell
                    course_match = first_cell_text.split()
                    course_number = course_match[1] if len(course_match) > 1 else "000"
                    
                    data.append({
                        'Class Nbr': class_nbr,
                        'Section': section,
                        'Component': component,
                        'Course Number': course_number,
                        'Instructor': instructor,
                        'Course Title': first_cell_text,
                        'Enrollment': 0  # Will be filled later
                    })
                    
                except Exception as e:
                    continue
        
        if not data:
            st.error("No valid class data found in the results.")
            return None
        
        st.success(f"Found {len(data)} classes. Now extracting enrollment data...")
        
        # Extract enrollment for each class
        status_text.text("👥 Extracting enrollment data from individual class pages...")
        
        for i, class_data in enumerate(data):
            progress = 50 + (i / len(data)) * 40
            progress_bar.progress(int(progress))
            status_text.text(f"👥 Getting enrollment for class {i+1}/{len(data)}: {class_data['Class Nbr']}")
            
            enrollment = extract_enrollment_from_detail_page(driver, class_data['Class Nbr'])
            class_data['Enrollment'] = enrollment
            
            time.sleep(0.5)  # Small delay to be respectful
        
        progress_bar.progress(90)
        status_text.text("📈 Processing instructor workload data...")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Create instructor workload summary
        workload_data = []
        
        for instructor in df['Instructor'].unique():
            if instructor == 'TBA':
                continue
                
            instructor_classes = df[df['Instructor'] == instructor]
            
            # Split name
            name_parts = instructor.replace(',', '').split()
            if len(name_parts) >= 2:
                last_name = name_parts[0]
                first_name = ' '.join(name_parts[1:])
            else:
                last_name = instructor
                first_name = ""
            
            # Categorize classes
            ug_classes = instructor_classes[instructor_classes['Course Number'].astype(str).str[:1].astype(int) <= 6]
            grad_classes = instructor_classes[instructor_classes['Course Number'].astype(str).str[:1].astype(int) >= 7]
            
            # Count supervision classes (typically independent study, thesis, etc.)
            ug_supervision = ug_classes[ug_classes['Component'].str.contains('IND|THE|SUP', case=False, na=False)]
            grad_supervision = grad_classes[grad_classes['Component'].str.contains('IND|THE|SUP', case=False, na=False)]
            
            workload_data.append({
                'Last Name': last_name,
                'First Name': first_name,
                'Total # of UG classes': len(ug_classes),
                'Total # of UG students from Column D': int(ug_classes['Enrollment'].sum()),
                'Total # of UG supervion classes': len(ug_supervision),
                'Total # of UG students from Column F': int(ug_supervision['Enrollment'].sum()),
                'Total # of Grad classes': len(grad_classes),
                'Total # of Grad students from Colum H': int(grad_classes['Enrollment'].sum()),
                'Total # of Grad supervion classes': len(grad_supervision),
                'Total # of Grad student from Column J': int(grad_supervision['Enrollment'].sum())
            })
        
        workload_df = pd.DataFrame(workload_data)
        
        progress_bar.progress(100)
        status_text.text("✅ Scraping completed successfully!")
        
        return df, workload_df
        
    except Exception as e:
        st.error(f"An error occurred during scraping: {e}")
        return None
    finally:
        driver.quit()

def create_download_link(df, filename):
    """Create a download link for the Excel file"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Instructor Workload')
    
    output.seek(0)
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Download Excel File</a>'
    return href

# Sidebar inputs
st.sidebar.header("📋 Scraper Configuration")

# Term input
term = st.sidebar.text_input(
    "Term Code", 
    value="2253", 
    help="Example: 2253 for Spring 2025"
)

# Subject input
subject = st.sidebar.text_input(
    "Subject Code", 
    value="FIN", 
    help="Example: FIN, ACCT, MGMT"
)

# Class category
class_category = st.sidebar.selectbox(
    "Class Category",
    ["All", "Open", "Closed", "Cancelled"],
    help="Filter by class availability"
)

# Run button
if st.sidebar.button("🚀 Run Scraper", type="primary"):
    if not term or not subject:
        st.error("Please provide both Term Code and Subject Code")
    else:
        st.info("🔄 Starting scraper... This may take a few minutes.")
        
        with st.spinner("Scraping data..."):
            result = scrape_sf_state_schedule(term, subject, class_category)
        
        if result:
            class_df, workload_df = result
            
            # Display results
            st.success(f"✅ Successfully scraped {len(class_df)} classes for {len(workload_df)} instructors!")
            
            # Show workload summary
            st.subheader("👨‍🏫 Instructor Workload Summary")
            st.dataframe(workload_df, use_container_width=True)
            
            # Show detailed class data
            with st.expander("📚 Detailed Class Data"):
                st.dataframe(class_df, use_container_width=True)
            
            # Download link
            filename = f"SF_State_{subject}_{term}_Workload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            download_link = create_download_link(workload_df, filename)
            st.markdown(download_link, unsafe_allow_html=True)
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Classes", len(class_df))
            with col2:
                st.metric("Total Instructors", len(workload_df))
            with col3:
                st.metric("Total Students", int(class_df['Enrollment'].sum()))
            with col4:
                st.metric("Avg Class Size", f"{class_df['Enrollment'].mean():.1f}")

# Information section
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ How to Use")
st.sidebar.markdown("""
1. Enter the **Term Code** (e.g., 2253 for Spring 2025)
2. Enter the **Subject Code** (e.g., FIN, ACCT, MGMT)
3. Select **Class Category** filter (optional)
4. Click **Run Scraper**
5. Wait for results and download Excel file
""")

st.sidebar.markdown("### 📖 Term Codes")
st.sidebar.markdown("""
- **2253**: Spring 2025
- **2252**: Fall 2024
- **2251**: Summer 2024
- **2249**: Spring 2024
""")

# Footer
st.markdown("---")
st.markdown("**SF State Class Schedule Scraper** | Built with Streamlit | [GitHub Repository](https://github.com/cryb3/sf-state-schedule-scraper)") 