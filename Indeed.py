from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import warnings
import csv


warnings.filterwarnings("ignore")
csv.register_dialect(
    "escaped", escapechar="\\", doublequote=True, quoting=csv.QUOTE_ALL
)

query = "web developer"
location = "India"


url = f"https://in.indeed.com/jobs?q={query.replace(' ','+')}&l={location}"
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("start-maximized")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
driver = webdriver.Chrome(executable_path="chromedriver", options=chrome_options)
stealth(
    driver,
    user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.3",
    # user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36",
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)
driver.get(url)
try:
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "nav#gnav-main-container"))
    )
except:
    print("Connection slow; Timed out")
    exit()
script = """
window.scrollTo(0, document.body.scrollHeight);
"""
driver.execute_script(script)

job_cards = driver.find_elements(
    By.CSS_SELECTOR, "div.cardOutline.tapItem.fs-unmask.result"
)
job_links = []
jobs_page_source = []
# job_cards = job_cards[:4]
for card in job_cards:
    flag = False
    try:
        card.click()
        sleep(1.5)
        driver.switch_to.window(driver.window_handles[-1])
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.jobsearch-CompanyInfoContainer")
            )
        )
        job_links.append(driver.current_url)
        jobs_page_source.append(driver.page_source)
        flag = True
    except:
        print("Open failed")
    
    try:
        driver.close()
        sleep(1.5)
        print(len(driver.window_handles))
        driver.switch_to.window(driver.window_handles[0])
        sleep(1.5)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.cardOutline.tapItem.fs-unmask.result")
            )
        )
    except Exception as e:
        print(e)
        print("Close failed")


driver.quit()

# filename = filename = f"{query} jobs in {location} indeed.csv"
filename = "indeed.csv"
myfile = open(filename, "w", newline="")
spamWriter = csv.writer(myfile, dialect="excel")

header = ["Job Title", "Company", "Salary", "URL"]
spamWriter.writerow(header)


entries = []
for i in range(0, len(jobs_page_source)):
    page = jobs_page_source[i]
    url = job_links[i]
    soup = BeautifulSoup(page, "html.parser")
    try:
        details = soup.find("div", id="jobDetailsSection")
        details = details.children  # type: ignore
        details = [x for x in details][1:]
        entry = {}
        companyinfo = soup.find("div", {"data-company-name": "true"}).text
        entry["Company"] = companyinfo
        entry["URL"] = url
        # l=["WEB DEVELOPER","NA","NA","NA","NA"]
        for detail in details:
            try:
                field, value = [x for x in detail.children]  # type: ignore
                field = field.text
                value = value.text
                entry[field] = value
            except:
                entry = {}
                break
        if entry:
            entries.append(entry)
    except Exception as e:
        print(e)

for entry in entries:
    l = ["Web Developer"]
    for column in header[1:]:
        try:
            l.append(entry[column])
        except:
            l.append("NA")
    spamWriter.writerow(l)

myfile.close()
