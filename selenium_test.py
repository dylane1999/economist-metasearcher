from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd

KEYWORDS_FILE = 'textfile.txt'
RANKED_OUTPUT_FILE = 'Output.csv'


title_list = []
description_list = []
category_list = []
keyword_list = []
link_list = []

def read_keywords():
    with open(KEYWORDS_FILE) as fd:
        return [keyword.strip() for keyword in fd.readlines()]




def selenium_login():

    for keyword in read_keywords():
        driver = webdriver.Firefox(executable_path='/Users/dylanedwards/PycharmProjects/economist-metasearcher/geckodriver')
        driver.get("http://www.economist.com/historicalarchive")

        # tests to make sure we are on login page
        assert "Economist" in driver.title

        # inputs username
        username = driver.find_element_by_name("email")
        username.clear()
        username.send_keys("dylanedwards290@gmail.com")

        # inputs passwords
        password = driver.find_element_by_name("password")
        password.clear()
        password.send_keys("duDnis-0givza-carfed")

        # clicks log in button
        logIn = driver.find_element_by_xpath("/html/body/form/div[2]/table/tbody/tr[5]/td[2]/a")
        logIn.click()

        #waits for the presence of the search input area on new form page before running
        searchWait = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "inputFieldValue_0"))
        )



        #inputs search term
        searchTerm = driver.find_element_by_xpath("// *[ @ id = 'inputFieldValue_0']")
        searchTerm.clear()
        searchTerm.send_keys(keyword)

        #selects keyword radio button
        keywordButton = driver.find_element_by_xpath("/html/body/div[3]/form/div[1]/div[3]/input[2]")
        keywordButton.click()

        #select between date from drop down
        Between = Select(driver.find_element_by_xpath('//*[@id="dateLimiterValue_da_dateMode_0"]'))
        Between.select_by_value('4')    # select by value

        #select start day from drop down
        startDay = Select(driver.find_element_by_xpath('// *[ @ id = "dateLimiterValue_da_fromDay"]'))
        startDay.select_by_value('01')    # select by value

        #select start month from drop down
        startMonth = Select(driver.find_element_by_xpath('// *[ @ id = "dateLimiterValue_da_fromMonth"]'))
        startMonth.select_by_value('01')    # select by value

        #select start Year from drop down
        startYear = Select(driver.find_element_by_xpath('// *[ @ id = "dateLimiterValue_da_fromYear"]'))
        startYear.select_by_value('1917')    # select by value

        # select end day from drop down
        endDay = Select(driver.find_element_by_xpath('//*[@id="dateLimiterValue_da_toDay"]'))
        endDay.select_by_value('01')  # select by value

        # select end month from drop down
        endMonth = Select(driver.find_element_by_xpath('//*[@id="dateLimiterValue_da_toMonth"]'))
        endMonth.select_by_value('01')  # select by value

        # select end Year from drop down
        endYear = Select(driver.find_element_by_xpath('//*[@id="dateLimiterValue_da_toYear"]'))
        endYear.select_by_value('1971')  # select by value


        # clicks Search Submit button
        searchSubmit = driver.find_element_by_xpath("/html/body/div[3]/form/div[1]/div[2]/a")
        searchSubmit.click()

        #calls collect results on search results
        collectResults(driver, keyword)
        enabledButton = driver.find_elements(By.XPATH, '//*[@title="Next"]')
        hasNextPage = False
        if len(enabledButton) > 0:
            hasNextPage = True

        while hasNextPage:
            disabledButton = driver.find_elements(By.XPATH, "/html/body/div[4]/div[3]/form/div[3]/div/ul[2]/b")
            enabledButton = driver.find_elements(By.XPATH, '//*[@title="Next"]')
            print("Length of enabled button" +  str(len(enabledButton)))
            print("Length of diabled button" +  str(len(disabledButton)))

            if len(enabledButton) > 0:
                enabledButton[0].click()
                collectResults(driver, keyword)
                hasNextPage = True
            elif len(disabledButton) > 0:
                collectResults(driver,keyword)
                break

        df = pd.DataFrame(list(zip(title_list, description_list, category_list, keyword_list, link_list)),
                          columns=['Title', 'Description', 'Category', 'Keyword', "link"])

        df.to_csv('selenium-output.csv', index=False)








def collectResults(driver, keyword):
    # waits for the presence of the Ul item  on new results page
    resultsWait = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[3]/form/ul[1]"))
    )

    # grabs list item search results
    resultItems = driver.find_elements_by_class_name("resultsListBox")


    for result in resultItems:
        title = result.find_element_by_class_name("articleTitle").text
        description = result.find_element_by_class_name("description").text
        category = result.find_element_by_class_name("articleType").text
        link = result.find_element_by_class_name("articleTitle").find_element_by_css_selector('a').get_attribute('href')



        title_list.append(title)
        description_list.append(description)
        category_list.append(category)
        keyword_list.append(keyword)
        link_list.append(link)


    # waits for the presence of the mark all button on new results page
    markerWait = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='iteratorBar-selectAll_1']"))
    )

    # checks the mark all button
    #markAll = driver.find_element_by_xpath("//*[@id='iteratorBar-selectAll_1']")
    #markAll.click()





def groupResults():
    df = pd.read_csv('selenium-output.csv', delimiter='|', sep='\s+')
    df.columns = df.columns.str.strip()
    out = df.astype(str).groupby(['Title']).agg(', '.join)
    out.to_csv('file.csv')


def main():
    selenium_login()
    groupResults()



if __name__ == "__main__":
    main()
