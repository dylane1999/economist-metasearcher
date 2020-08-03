from csv import DictWriter
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
import os


KEYWORDS_FILE = 'textfile.txt'
LOGIN_FILE = 'login.txt'
RANKED_OUTPUT_FILE = 'Output.csv'
START_YEAR = "1917"
END_YEAR = "1971"


class Articles:
    def __init__(self, Title, Description, Category, Keyword, Link ):
        self.Title = Title
        self.Description = Description
        self.Category = Category
        self.Keyword = Keyword
        self.Link = Link

    def to_dict(self):
        return {
            'Title': self.Title,
            'Description': self.Description,
            'Category': self.Category,
            'Keyword': self.Keyword,
            'Link': self.Link,

        }





def read_login_info():
    with open(LOGIN_FILE) as text_file:
        loginInfo = text_file.read().split(',')
        return loginInfo


def read_keywords():
    with open(KEYWORDS_FILE) as fd:
        return [keyword.strip() for keyword in fd.readlines()]


def scrape_economist(keyword, allResults):


    path = os.getcwd() + "/geckodriver"
    driver = webdriver.Firefox(executable_path=path)
    driver.get("http://www.economist.com/historicalarchive")

    # tests to make sure we are on login page
    assert "Economist" in driver.title

    email, loginPassword = read_login_info()

    # inputs username
    username = driver.find_element_by_name("email")
    username.clear()
    username.send_keys(email)

    # inputs passwords
    password = driver.find_element_by_name("password")
    password.clear()
    password.send_keys(loginPassword)

    # clicks log in button
    logIn = driver.find_element_by_xpath("/html/body/form/div[2]/table/tbody/tr[5]/td[2]/a")
    logIn.click()


    searchForm(driver, keyword)


    # calls collect results on search results
    collectResults(driver, keyword, allResults)
    enabledButton = driver.find_elements(By.XPATH, '//*[@title="Next"]')
    hasNextPage = len(enabledButton) > 0

    while hasNextPage:
        disabledButton = driver.find_elements(By.XPATH, "/html/body/div[4]/div[3]/form/div[3]/div/ul[2]/b")
        enabledButton = driver.find_elements(By.XPATH, '//*[@title="Next"]')


        if len(enabledButton) > 0:
            enabledButton[0].click()
            collectResults(driver, keyword, allResults)
            hasNextPage = True
        elif len(disabledButton) > 0:
            collectResults(driver, keyword, allResults)
            break

    download(driver)















def collectResults(driver, keyword, allResults):
    # waits for the presence of the Ul item  on new results page
    time.sleep(1)
    resultsWait = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "resultsListBox"))
    )

    # grabs list item search results
    resultItems = driver.find_elements_by_class_name("resultsListBox")


    for result in resultItems:

        title = result.find_element_by_class_name("articleTitle").text
        description = result.find_element_by_class_name("description").text
        category = result.find_element_by_class_name("articleType").text
        link = result.find_element_by_class_name("articleTitle").find_element_by_css_selector('a').get_attribute('href')
        #time.sleep(.1)
        titleWait = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "articleTitle"))
        )
        markItem = result.find_element_by_class_name("markItem")
        markItem.click()
        allResults.append(Articles(title, description, category, keyword, link))


    return allResults

        #return

        #lists.link_list.append(link)
       # lists.title_list.append(title)
       # lists.description_list.append(description)
       # lists.category_list.append(category)
      #  lists.keyword_list.append(keyword)

def searchForm(driver, keyword, startyear=START_YEAR, endyear=END_YEAR):

    # waits for the presence of the search input area on new form page before running
    searchWait = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "inputFieldValue_0"))
    )

    # inputs search term
    searchTerm = driver.find_element_by_xpath("// *[ @ id = 'inputFieldValue_0']")
    searchTerm.clear()
    searchTerm.send_keys(keyword)

    # selects keyword radio button
    keywordButton = driver.find_element_by_xpath("/html/body/div[3]/form/div[1]/div[3]/input[2]")
    keywordButton.click()

    # select between date from drop down
    Between = Select(driver.find_element_by_xpath('//*[@id="dateLimiterValue_da_dateMode_0"]'))
    Between.select_by_value('4')  # select by value

    # select start day from drop down
    startDay = Select(driver.find_element_by_xpath('// *[ @ id = "dateLimiterValue_da_fromDay"]'))
    startDay.select_by_value('01')  # select by value

    # select start month from drop down
    startMonth = Select(driver.find_element_by_xpath('// *[ @ id = "dateLimiterValue_da_fromMonth"]'))
    startMonth.select_by_value('01')  # select by value

    # select start Year from drop down
    startYear = Select(driver.find_element_by_xpath('// *[ @ id = "dateLimiterValue_da_fromYear"]'))
    startYear.select_by_value(startyear)  # select by value

    # select end day from drop down
    endDay = Select(driver.find_element_by_xpath('//*[@id="dateLimiterValue_da_toDay"]'))
    endDay.select_by_value('01')  # select by value

    # select end month from drop down
    endMonth = Select(driver.find_element_by_xpath('//*[@id="dateLimiterValue_da_toMonth"]'))
    endMonth.select_by_value('01')  # select by value

    # select end Year from drop down
    endYear = Select(driver.find_element_by_xpath('//*[@id="dateLimiterValue_da_toYear"]'))
    endYear.select_by_value(endyear)  # select by value

    # clicks Search Submit button
    searchSubmit = driver.find_element_by_xpath("/html/body/div[3]/form/div[1]/div[2]/a")
    searchSubmit.click()




def download(driver):
    # waits for the marked all menu item
    markedWait = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "markListSpan"))
    )

    # clicks marked items button
    markedItems = driver.find_element_by_class_name("markListSpan")
    markedItems.click()

    # clicks marked items button
    download = driver.find_element_by_id("download")
    download.click()

    currentWindow = driver.current_window_handle
    downloadPage = driver.window_handles[1]
    driver.switch_to.window(downloadPage)

    # waits for the rollover download
    resultsWait = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "rolloverdownload"))
    )

    # clicks marked items button
    rolloverdownload = driver.find_element_by_class_name("rolloverdownload")
    rolloverdownload.click()

    driver.switch_to.window(currentWindow)



def groupResults(allResults):

    df = pd.DataFrame.from_records([result.to_dict() for result in allResults])

    df['length'] = df['Keyword'].str.len()
    out = df.astype(str).groupby(['Title']).agg(', '.join)
    out.sort_values('length', ascending=False, inplace=True)

    out.to_csv('output.csv')



def main():
    allResults = []
    for keyword in read_keywords():
        scrape_economist(keyword,allResults)
    groupResults(allResults)




if __name__ == "__main__":
    main()
