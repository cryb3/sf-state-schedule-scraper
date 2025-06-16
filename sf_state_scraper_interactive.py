"""
SF State Class Schedule Scraper - Interactive Version
----------------------------------------------------
Double-click to run on Windows or macOS!
Prompts for term, subject, class category, and output location.
"""

import os
import sys
import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox
import re, time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def get_user_inputs():
    """Get user inputs for the scraper configuration."""
    print("🎓 SF State Class Schedule Scraper")
    print("=" * 50)
    print()
    
    # Get Term
    print("📅 TERM (4-digit code):")
    print("   Examples: 2253 (Spring 2025), 2251 (Fall 2024), 2254 (Summer 2025)")
    print("   Format: YYYY + S (where S is: 1=Fall, 2=Spring, 3=Summer, 4=Winter)")
    term = input("   Enter term: ").strip()
    
    if not re.match(r'^\d{4}$', term):
        print("   ❌ Invalid term format. Please use 4 digits (e.g., 2253)")
        return None
    print()
    
    # Get Subject
    print("📚 SUBJECT (department code):")
    print("   Examples: FIN, ACCT, MKTG, MGMT, BLAW, ECON, MATH, ENGL")
    print("   Note: Use 3-4 letter department codes")
    subject = input("   Enter subject: ").strip().upper()
    
    if not re.match(r'^[A-Z]{2,5}$', subject):
        print("   ❌ Invalid subject format. Please use 2-5 letters (e.g., FIN)")
        return None
    print()
    
    # Get Class Category
    print("🏫 CLASS CATEGORY:")
    print("   Examples: REG (Academic Regular Session), EXT (Extended Education)")
    print("   Most common: REG")
    classcat = input("   Enter class category [REG]: ").strip().upper()
    
    if not classcat:
        classcat = "REG"
    print()
    
    # Get output file location
    print("💾 OUTPUT FILE LOCATION:")
    print("   Click 'Choose Location' to select where to save the Excel file...")
    
    try:
        # Create a hidden tkinter root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Ask for save location
        output_file = filedialog.asksaveasfilename(
            title="Save Excel file as...",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"{subject.lower()}_{term}_instructor_load.xlsx"
        )
        
        root.destroy()
        
        if not output_file:
            print("   ❌ No output file selected. Exiting.")
            return None
            
        output_path = pathlib.Path(output_file)
        print(f"   ✅ Output file: {output_path}")
        
    except Exception as e:
        print(f"   ⚠️  Error with file dialog: {e}")
        print("   Using current directory as fallback...")
        filename = f"{subject.lower()}_{term}_instructor_load.xlsx"
        output_path = pathlib.Path(filename)
    
    print()
    print("📋 CONFIGURATION SUMMARY:")
    print(f"   Term: {term}")
    print(f"   Subject: {subject}")
    print(f"   Class Category: {classcat}")
    print(f"   Output File: {output_path}")
    print()
    
    confirm = input("   Continue with this configuration? [Y/n]: ").strip().lower()
    if confirm and confirm != 'y' and confirm != 'yes':
        print("   Operation cancelled.")
        return None
    
    return {
        'term': term,
        'subject': subject,
        'classcat': classcat,
        'output_file': output_path
    }

def setup_driver():
    """Set up Chrome driver with error handling."""
    try:
        chrome_opts = Options()
        chrome_opts.add_argument("--start-maximized")
        chrome_opts.add_argument("--no-sandbox")
        chrome_opts.add_argument("--disable-dev-shm-usage")
        
        # Try to create driver
        driver = webdriver.Chrome(options=chrome_opts)
        return driver
    except WebDriverException as e:
        print(f"❌ Error setting up Chrome driver: {e}")
        print("Please ensure Chrome and ChromeDriver are properly installed.")
        print("\nInstallation help:")
        print("1. Install Google Chrome browser")
        print("2. ChromeDriver should be automatically managed by Selenium 4+")
        print("3. If issues persist, try: pip install selenium --upgrade")
        return None

def get_course_enrollment(driver, course_link, class_number):
    """Click on course link and extract enrollment number."""
    if not course_link:
        return 0, ""
    
    try:
        print(f"   🔗 Getting enrollment for class {class_number}...")
        
        # Navigate to course detail page
        driver.get(course_link)
        
        # Wait for the enrollment section to load
        wait = WebDriverWait(driver, 10)
        
        enrolled = 0
        actual_course_code = ""
        
        try:
            # Try different positions to find the enrolled field (not capacity)
            selectors = [
                (By.CSS_SELECTOR, "#content > div > div.detail-container.row.class-details > div.col-md-4 > div > div:nth-child(7) > div.col-xs-5.col-md-6"),  # Try next field
                (By.CSS_SELECTOR, "#content > div > div.detail-container.row.class-details > div.col-md-4 > div > div:nth-child(5) > div.col-xs-5.col-md-6"),  # Try previous field  
                (By.XPATH, "/html/body/div[4]/section/div/div/div/div[3]/div[2]/div/div[3]/div[2]"),  # Try next XPath position
                (By.XPATH, "/html/body/div[4]/section/div/div/div/div[3]/div[2]/div/div[1]/div[2]"),  # Try previous XPath position
                (By.CSS_SELECTOR, "#content > div > div.detail-container.row.class-details > div.col-md-4 > div > div:nth-child(6) > div.col-xs-5.col-md-6"),  # Original (fallback)
            ]
            
            enrollment_element = None
            for selector_type, selector in selectors:
                try:
                    enrollment_element = wait.until(
                        EC.presence_of_element_located((selector_type, selector))
                    )
                    break
                except:
                    continue
            
            if enrollment_element:
                enrollment_text = enrollment_element.text.strip()
                
                # Extract number from the enrollment text
                numbers = re.findall(r'\d+', enrollment_text)
                if numbers:
                    enrolled = int(numbers[0])
                    
        except Exception as e:
            print(f"      ⚠️  Error finding enrollment element: {e}")
            
        # Try to extract course code from page title or header
        try:
            # Look for course code in various places
            page_source = driver.page_source
            course_code_patterns = [
                r"([A-Z]{2,4}\s+\d{3}[A-Z]?)",  # Like "FIN 350" or "MATH 115A"
                r"Course:\s*([A-Z]{2,4}\s+\d{3}[A-Z]?)",
            ]
            
            for pattern in course_code_patterns:
                match = re.search(pattern, page_source)
                if match:
                    actual_course_code = match.group(1)
                    break
        except:
            pass
        
        return enrolled, actual_course_code
        
    except Exception as e:
        print(f"   ⚠️  Error getting course details: {e}")
        return 0, ""

def scrape_schedule_data(driver, term, subject, classcat):
    """Scrape the schedule data from SF State website."""
    url = (f"https://webapps.sfsu.edu/public/classservices/classsearch/"
           f"results?term={term}&classCategory={classcat}&subject={subject}")
    
    print(f"🔄 Loading URL: {url}")
    driver.get(url)

    try:
        # Wait for the enrollment section to load
        wait = WebDriverWait(driver, 45)
        print("⏳ Waiting for page to load...")
        
        # Check if we need to handle a search form first
        try:
            # Look for search form elements that might need to be filled
            time.sleep(3)  # Give page a moment to load
            page_title = driver.title
            print(f"📄 Page title: {page_title}")
            
            # Check current URL to see if we were redirected
            current_url = driver.current_url
            print(f"📍 Current URL: {current_url}")
            
        except Exception as e:
            print(f"⚠️  Note: {e}")

        # Try multiple selectors to find class data
        print("🔍 Looking for class data table...")
        
        # Try different possible selectors for the class data
        selectors_to_try = [
            "tr[data-role='row']",  # Original selector
            "table tr",            # Any table rows
            ".course-row",         # Class-specific rows
            "tbody tr",            # Table body rows
            "[class*='row']"       # Any element with 'row' in class name
        ]
        
        found_data = False
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 1:  # More than just header
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    found_data = True
                    break
            except:
                continue
        
        if not found_data:
            # Try to wait a bit more and look for any table content
            time.sleep(5)
            print("🔄 Waiting a bit more for dynamic content...")
            
            # Look for any signs of data loading
            all_text = driver.page_source
            if f"{subject} " in all_text and ("class" in all_text.lower() or "course" in all_text.lower()):
                print("✅ Found course content in page source!")
                found_data = True
        
        if not found_data:
            raise TimeoutException("No class data found with any selector")
        
    except TimeoutException:
        print("❌ Timeout waiting for class data to load")
        print("🔍 Let's check what's on the page...")
        
        # Debug: check what's actually on the page
        page_title = driver.title
        current_url = driver.current_url
        print(f"   📄 Page title: {page_title}")
        print(f"   📍 Current URL: {current_url}")
        
        # Look for any tables or forms that might be present
        tables = driver.find_elements(By.TAG_NAME, "table")
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"   📊 Found {len(tables)} tables and {len(forms)} forms on page")
        
        # Check if there are any error messages
        try:
            error_msgs = driver.find_elements(By.CSS_SELECTOR, ".error, .alert, .warning")
            if error_msgs:
                print(f"   ⚠️  Found {len(error_msgs)} error/warning messages")
                for msg in error_msgs[:3]:  # Show first 3 messages
                    print(f"      - {msg.text[:100]}")
        except:
            pass
            
        print("💡 The website might be down, require different parameters, or the selectors may have changed.")
        print("🌐 Check the browser window to see what's displayed.")
        return None

    return driver.page_source

def parse_rows(page_source, subject):
    """Parse HTML and extract course data."""
    soup = BeautifulSoup(page_source, "html.parser")
    
    rows = []
    
    # Try different selectors to find course data
    selectors_to_try = [
        "tr[data-role='row']",  # Original selector
        "tbody tr",            # Table body rows
        "table tr"             # Any table rows
    ]
    
    course_rows = []
    for selector in selectors_to_try:
        course_rows = soup.select(selector)
        if course_rows:
            print(f"🔍 Using selector: {selector} (found {len(course_rows)} rows)")
            break
    
    if not course_rows:
        return rows
    
    for i, tr in enumerate(course_rows):  # Process all rows
        tds = [td.get_text(strip=True, separator=" ") for td in tr.select("td")]
        
        # Skip header rows and rows with too few columns
        if not tds or len(tds) < 3:  # Even more flexible
            continue
            
        # Only skip very obvious header rows
        row_text = " ".join(tds).lower()
        if "course type" in row_text and "class number" in row_text:
            continue
        
        # Flexible unpacking - adapt to different column orders
        td_data = tds + [""] * (12 - len(tds))  # Pad to 12 columns
        
        # Try to identify key columns by content patterns
        course_type = td_data[0] if td_data[0] else ""
        title = td_data[1] if len(td_data) > 1 else ""
        units = td_data[2] if len(td_data) > 2 else ""
        
        # Extract course info from the data structure
        course_title = td_data[1] if len(td_data) > 1 else ""
        class_number = td_data[3] if len(td_data) > 3 else ""
        
        # Look for clickable course link to get course details
        course_link = None
        try:
            # Find the course link in the original tr element
            link_element = tr.select("a")
            if link_element:
                course_link = link_element[0].get('href')
                if course_link and not course_link.startswith('http'):
                    course_link = f"https://webapps.sfsu.edu{course_link}"
        except:
            pass
        
        # For now, create a generic course code - we'll extract the real one from course details
        course_code = f"{subject} {class_number}"
        
        # Extract instructor from column 5 (Instructors: Name ...)
        instructor_col = td_data[5] if len(td_data) > 5 else ""
        instructor = ""
        
        if "Instructors:" in instructor_col:
            # Extract name after "Instructors: "
            instructor_text = instructor_col.replace("Instructors:", "").strip()
            # Split by space and take first two parts (should be "FirstName LastName")
            name_parts = instructor_text.split()
            if len(name_parts) >= 2:
                # Convert "FirstName LastName" to "LastName, FirstName" format
                instructor = f"{name_parts[1]}, {name_parts[0]}"
            elif len(name_parts) == 1:
                instructor = name_parts[0]  # Single name
        
        # We'll extract enrollment from course detail page later
        enrolled = 0  # Placeholder

        # Skip rows without key data
        if not course_code and not instructor:
            continue
            
        if not instructor or instructor.strip() == "":
            continue

        # Create note from course type
        note_parts = []
        if "Cross-Listed" in course_type:
            note_parts.append("cross-listed")
        if "Paired" in course_type:
            note_parts.append("paired")
        
        note = "; ".join(note_parts)

        rows.append({
            "course_type": course_type,
            "title": title,
            "units": units,
            "course_code": course_code,        # e.g. FIN 350
            "instructor": instructor,          # "Smith, Jane"
            "enrolled": enrolled,
            "note": note,
            "course_link": course_link,        # Link to course details
            "class_number": class_number,      # For tracking
        })

    print(f"📊 Parsed {len(rows)} valid course rows")
    return rows

def classify_courses(df):
    """Add classification columns for level and supervision type."""
    def is_grad(row):
        # SF State catalog: course numbers 700+ are graduate, 600 and below are undergraduate
        m = re.search(r"\b(\d{3})\b", row["course_code"])
        if m:
            course_num = int(m.group(1))
            return course_num >= 700
        return False

    def is_supervision(row):
        return bool(re.search(r"Independent|Internship|Supervision|Thesis|Field|Research", 
                            row["title"], re.I))

    df["level"] = df.apply(lambda r: "grad" if is_grad(r) else "ug", axis=1)
    df["supervision"] = df.apply(is_supervision, axis=1)
    return df

def process_instructor_names(df):
    """Split instructor names into first and last name."""
    # Handle cases where instructor might have format issues
    def split_name(instructor):
        if not instructor or pd.isna(instructor):
            return "", ""
        
        parts = instructor.split(",", 1)
        if len(parts) >= 2:
            last_name = parts[0].strip()
            first_name = parts[1].strip()
        else:
            # If no comma, assume it's all last name
            last_name = instructor.strip()
            first_name = ""
        
        return last_name, first_name

    df[["Last Name", "First Name"]] = df["instructor"].apply(
        lambda x: pd.Series(split_name(x))
    )
    return df

def create_summary_table(df):
    """Create the final summary table with instructor workloads."""
    # Add helper columns
    df["class_count"] = 1
    df["student_count"] = df["enrolled"]

    # Create bucket classification
    def bucket(r):
        if r["level"] == "ug" and not r["supervision"]: 
            return "ug_lecture"
        elif r["level"] == "ug" and r["supervision"]:    
            return "ug_superv"
        elif r["level"] == "grad" and not r["supervision"]: 
            return "grad_lecture"
        else:
            return "grad_superv"

    df["bucket"] = df.apply(bucket, axis=1)

    # Create pivot table
    pivot = df.pivot_table(
        index=["Last Name", "First Name"],
        columns="bucket",
        values=["class_count", "student_count"],
        aggfunc="sum",
        fill_value=0,
        observed=True
    )

    # Flatten the MultiIndex columns
    pivot.columns = [f"{v}_{k}" for k, v in pivot.columns]
    pivot = pivot.reset_index()

    # Rename to match the exact Excel header spec (keeping user's specified typos)
    column_mapping = {
        "ug_lecture_class_count":   "Total # of UG classes",
        "ug_lecture_student_count": "Total # of UG students from Column D",
        "ug_superv_class_count":    "Total # of UG supervion classes",  # User's typo: "supervion"
        "ug_superv_student_count":  "Total # of UG students from Column F",
        "grad_lecture_class_count": "Total # of Grad classes",
        "grad_lecture_student_count": "Total # of Grad students from Colum H",  # User's typo: "Colum"
        "grad_superv_class_count":  "Total # of Grad supervion classes",  # User's typo: "supervion"
        "grad_superv_student_count": "Total # of Grad student from Column J",   # User's spec: "student" not "students"
    }
    
    pivot = pivot.rename(columns=column_mapping)

    # Collect notes per instructor
    notes = (
        df.groupby(["Last Name", "First Name"])["note"]
          .apply(lambda s: "; ".join(sorted(set(filter(None, s)))))
          .reset_index()
    )

    # Merge with notes
    final_df = pivot.merge(notes, on=["Last Name", "First Name"], how="left")
    final_df = final_df.fillna(0)
    
    # Ensure note column exists and is properly filled
    if 'note' not in final_df.columns:
        final_df['note'] = ""
    final_df['note'] = final_df['note'].fillna("")
    
    # Reorder columns to match user's specified order
    column_order = [
        "Last Name",
        "First Name", 
        "Total # of UG classes",
        "Total # of UG students from Column D",
        "Total # of UG supervion classes",
        "Total # of UG students from Column F",
        "Total # of Grad classes",
        "Total # of Grad students from Colum H",
        "Total # of Grad supervion classes",
        "Total # of Grad student from Column J",
        "note"
    ]
    
    # Only include columns that exist in the dataframe
    existing_columns = [col for col in column_order if col in final_df.columns]
    final_df = final_df[existing_columns]
    
    return final_df

def main():
    """Main execution function."""
    try:
        # Get user configuration
        config = get_user_inputs()
        if not config:
            input("\nPress Enter to exit...")
            return
        
        print(f"🚀 Starting SF State {config['subject']} Schedule Scraper")
        print(f"   Term: {config['term']} | Subject: {config['subject']} | Class Category: {config['classcat']}")
        print("-" * 60)
        
        # Set up driver
        driver = setup_driver()
        if not driver:
            input("\nPress Enter to exit...")
            return
        
        try:
            # Scrape data
            page_source = scrape_schedule_data(driver, config['term'], config['subject'], config['classcat'])
            if not page_source:
                return
            
            # Parse the HTML
            print("🔄 Parsing course data...")
            rows = parse_rows(page_source, config['subject'])
            
            if not rows:
                print("❌ No course data found. Check if the term/subject combination exists.")
                return
            
            print(f"✅ Found {len(rows)} course rows")
            
            # Extract enrollment from individual course pages
            print("🔄 Extracting enrollment data from course detail pages...")
            for i, row in enumerate(rows):
                if row.get('course_link'):
                    try:
                        enrolled, actual_course_code = get_course_enrollment(
                            driver, row['course_link'], row['class_number']
                        )
                        row['enrolled'] = enrolled
                        if actual_course_code:
                            row['course_code'] = actual_course_code
                        
                        # Add small delay to avoid overwhelming the server
                        time.sleep(1)
                        
                        if (i + 1) % 5 == 0:  # Progress update every 5 courses
                            print(f"   📊 Processed {i + 1}/{len(rows)} courses...")
                            
                    except Exception as e:
                        print(f"   ⚠️  Error processing course {row['class_number']}: {e}")
                        continue
            
            # Navigate back to main results page
            main_url = (f"https://webapps.sfsu.edu/public/classservices/classsearch/"
                       f"results?term={config['term']}&classCategory={config['classcat']}&subject={config['subject']}")
            print("🔄 Returning to main results page...")
            driver.get(main_url)
            time.sleep(2)
            
            # Create DataFrame and process
            raw_df = pd.DataFrame(rows)
            raw_df = classify_courses(raw_df)
            raw_df = process_instructor_names(raw_df)
            
            # Create summary
            print("🔄 Creating instructor summary...")
            final_df = create_summary_table(raw_df)
            
            # Write to Excel
            print("🔄 Writing to Excel...")
            with pd.ExcelWriter(config['output_file'], engine="openpyxl") as xl:
                final_df.to_excel(xl, index=False, sheet_name=f"{config['subject']}_{config['term']}")
            
            print(f"\n✅ Successfully created {config['output_file'].resolve()}")
            print(f"   📊 Unique instructors: {len(final_df)}")
            print(f"   📚 Total courses processed: {len(raw_df)}")
            
            # Display summary
            print("\n📋 Summary by instructor:")
            for _, row in final_df.head(10).iterrows():  # Show first 10
                ug_classes = int(row.get('Total # of UG classes', 0))
                grad_classes = int(row.get('Total # of Grad classes', 0))
                ug_students = int(row.get('Total # of UG students from Column D', 0))
                grad_students = int(row.get('Total # of Grad students from Colum H', 0))
                print(f"   {row['Last Name']}, {row['First Name']}: "
                      f"UG={ug_classes} classes ({ug_students} students), "
                      f"Grad={grad_classes} classes ({grad_students} students)")
            
            if len(final_df) > 10:
                print(f"   ... and {len(final_df) - 10} more instructors")
            
            print(f"\n💾 Excel file saved to: {config['output_file']}")
            
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            raise
        finally:
            # Close browser
            try:
                driver.quit()
            except:
                pass
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("\nIf you continue to have issues, please check:")
        print("1. Chrome browser is installed")
        print("2. Internet connection is working")
        print("3. SF State website is accessible")
    
    finally:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 