# economist-metasearcher
A selenium script to find Economist articles in the historical based on keywords. Returns an output csv with the results collated by keyword 

Scrape_economist( ) is the function that starts the selenium webdriver, it takes the parameters keyword, a list for all articles allResults, and the start and end years. It also takes the default parameters username and password that are read in from a .txt file. 

This function calls searchForm( ) which contains the info to fill out the query for each keyword

collectResults( ) is then called on the yield from searchForm( ), and it is tasked with scraping all of the information from the articles for each page in the search query.  


After Scrape_economist( ) is finished, the function groupResults( ) is called which uses pandas to sort the results, and to join and sort them by keyword. 

Next, the function saveArticles( ) is called, which goes into the page for each article in each query, and downloads the article as an html file. 

