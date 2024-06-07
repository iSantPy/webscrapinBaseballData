from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os


def main():
    ROOT = os.path.dirname(__file__)

    url = "https://www.baseball-reference.com/"

    service = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get(url=url)

    try:
        # total data by player in his carrear
        input_field = WebDriverWait(driver=driver, timeout=10).until(
            EC.presence_of_element_located((By.NAME, "search"))
        )

        input_field.send_keys("venezuela" + Keys.RETURN)

        xpath = '//*[@id="bio_batting"]'
        table = driver.find_element(by=By.XPATH, value=xpath)

        table_html = table.get_attribute("outerHTML")

        soup = BeautifulSoup(table_html, "html.parser")

        thead = soup.find("thead")
        headers = [th.get_text(strip=True) for th in thead.find_all("th")]
        headers.pop(0)  # delete first column

        tbody_main = soup.find("tbody") 
        rows = tbody_main.find_all("tr")

        data = []

        for i, row in enumerate(rows):
            cells = row.find_all("td")

            row_data = [cell.text for cell in cells]
            data.append(row_data)
            
            link = row.find("a", href=True)

            try:
                # data details by player
                if link:
                    link_url = link["href"]
                    full_url = "https://www.baseball-reference.com" + link_url

                    driver.execute_script("window.open("");")
                    driver.switch_to.window(driver.window_handles[-1])
                    driver.get(full_url)

                    n_seconds = random.randint(1, 5)
                    time.sleep(n_seconds)

                    h1 = driver.find_element(by=By.TAG_NAME, value="h1")
                    name = h1.text

                    # standard batting
                    xpath_standard_batting = '//*[@id="batting_standard"]'
                    standard_batting = driver.find_element(by=By.XPATH, value=xpath_standard_batting)

                    standard_batting_html = standard_batting.get_attribute("outerHTML")

                    standard_batting_soup = BeautifulSoup(standard_batting_html, "html.parser")

                    thead = standard_batting_soup.find("thead")
                    headers_standard_batting = [th.get_text(strip=True) for th in thead.find_all("th")]

                    tbody = standard_batting_soup.find("tbody")

                    standard_batting_rows = tbody.find_all("tr", class_="full")
                    
                    standard_batting_list = []
                    for row in standard_batting_rows:
                        tds = row.find_all("td")
                        year = row.find("th").get_text()
                        cols = [td.get_text(strip=True) for td in tds]
                        cols.insert(0, year)
                        standard_batting_list.append(cols)

                    # player_value_batting
                    xpath_player_value_batting = '//*[@id="batting_value"]'
                    player_value_batting = driver.find_element(by=By.XPATH, value=xpath_player_value_batting)

                    player_value_batting_html = player_value_batting.get_attribute("outerHTML")

                    player_value_batting_soup = BeautifulSoup(player_value_batting_html, "html.parser")

                    thead_ = player_value_batting_soup.find("thead")
                    headers_player_value_batting = [th.get_text(strip=True) for th in thead_.find_all("th")]

                    tbody_ = player_value_batting_soup.find("tbody")

                    player_value_batting_rows = tbody_.find_all("tr", class_="full")

                    player_value_batting_list = []
                    for row_ in player_value_batting_rows:
                        tds_ = row_.find_all("td")
                        year_ = row_.find("th").get_text()
                        cols_ = [td_.get_text(strip=True) for td_ in tds_]
                        cols_.insert(0, year_)
                        player_value_batting_list.append(cols_)

                    # store results in a csv file
                    df_standard_bating = pd.DataFrame(data=standard_batting_list, columns=headers_standard_batting)
                    df_standard_bating_cleaned = df_standard_bating.dropna(how="all")

                    df_player_value_batting = pd.DataFrame(data=player_value_batting_list, columns=headers_player_value_batting)
                    df_player_value_batting_cleaned = df_player_value_batting.dropna(how="all")

                    results = pd.concat([df_standard_bating_cleaned, df_player_value_batting_cleaned], axis=1)
                    path = os.path.join(ROOT, "personal_data", name + ".csv")
                    results.to_csv(path, index=False)

                    print(f"player: {name} and uploading: {round((i * 100) / 502, 2)} %\n")

                    time.sleep(n_seconds)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

            except:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                print(f"player {name} has no the requested tables. Uploading: {round((i * 100) / 502, 2)} %\n")

        batting_players = pd.DataFrame(data=data, columns=headers)
        batting_players_cleaned = batting_players.dropna(how="all")

        batting_players_cleaned.to_csv("batting_players.csv", index=False)

        # pitching players
        xpath2 = '//*[@id="bio_pitching"]'

        table2 = driver.find_element(by=By.XPATH, value=xpath2)

        table2_html = table2.get_attribute("outerHTML")

        soup2 = BeautifulSoup(table2_html, "html.parser")

        thead2 = soup2.find("thead")
        headers2 = [th2.get_text(strip=True) for th2 in thead2.find_all("th")]
        headers2.pop(0)

        tbody_main2 = soup2.find("tbody") 
        rows2 = tbody_main2.find_all("tr", class_=lambda x: x != "minor_table hidden")

        data2 = []

        for row2 in rows2:
            cells2 = row2.find_all("td")
            row_data2 = [cell2.text for cell2 in cells2]
            data2.append(row_data2)

        pitching_players = pd.DataFrame(data=data2, columns=headers2)
        pitching_players_cleaned = pitching_players.dropna(how="all")    

        pitching_players_cleaned.to_csv("pitching_players.csv", index=False)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()