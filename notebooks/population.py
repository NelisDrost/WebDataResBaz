import json
from bs4 import BeautifulSoup
import requests
import pandas as pd
import io

if __name__ == '__main__':
    url = 'https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population#cite_note-7'
    headers = {'User-Agent': 'nelis.drost@auckland.ac.nz'}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table containing the country names and links
    table = soup.find('table', class_='wikitable')
    rows = table.find_all('tr')

    # Print the first 10 rows
    df = pd.read_html(io.StringIO(str(table)))[0]
    print(df.head())
    
    # Iterate over the first 20 rows (excluding the header row)
    for row in rows[1:10]:
        # Find the link to the country page
        links = row.find_all('a')
        # Filter out internal links
        links = [link for link in links if link['href'].startswith('/wiki/')]
        if len(links) == 0:
            continue

        link = links[0]
        country_url = 'https://en.wikipedia.org' + link['href']
        print(f"\nCountry: {link.get_text()}\n")

        
        # Visit the country page
        country_response = requests.get(country_url, headers=headers)
        country_soup = BeautifulSoup(country_response.text, 'html.parser')
        
        # Find the link to the population page
        population_link = country_soup.find('a', href=lambda href: href and 'Demographics_of_' in href)
        population_url = 'https://en.wikipedia.org' + population_link['href']
        
        # Visit the population page
        population_response = requests.get(population_url, headers=headers)
        population_soup = BeautifulSoup(population_response.text, 'html.parser')
        
        # Retrieve the population history
        vital_statistics = population_soup.find_all('span', class_='mw-headline', string=lambda t: t and 'vital statistics' in t.lower())[0]
        
        def is_population_table(table):
            if table is None:
                return False
            if table.name != 'table':
                return False
            population_header = table.find('th', string=lambda t: t and 'population' in t.lower())
            return population_header is not None

        # Find all tables between vital statistics and the next h2
        next_h2 = vital_statistics.find_next('h2')
        tables_between = vital_statistics.find_all_next(is_population_table, until=next_h2)

        if len(tables_between) == 0:
            continue
        else:
            population_table = tables_between[0]

            df = pd.read_html(io.StringIO(str(population_table)))[0]
            print(df.head())
