import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


class DrugsScraper:
    def __init__(self, base_url='https://www.drugs.com'):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.data = pd.DataFrame(columns=['name', 'molecule', 'dosage_form', 'date_of_approval', 'company', 'treatment_for'])

    def __get_html(self, url):
        """Private method to fetch HTML content of a given URL"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # raise exception for bad responses
            return response.text
        except requests.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        return None

    def show_data(self):
        print(self.data)

    def scrape_drugs_by_year(self, year, limit=None):
        """Scrapes drugs released in a specific year from drugs.com"""
        url = f'{self.base_url}/newdrugs-archive/{year}.html'
        html = self.__get_html(url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')

            # Encontrar todos los elementos de medicamentos en la página
            drugs = soup.find_all('div', class_='ddc-media-content')

            # Iterar sobre los elementos de medicamentos para extraer la información
            for drug in drugs:
                name = drug.find('a').get_text(strip=True)
                title_text = drug.find('h3', class_='ddc-media-title').get_text(strip=True)

                # Extraer Drug molecule y Dosage Form
                match = re.search(r'\((.*?)\)', title_text)
                if match:
                    drug_molecule = match.group(1).strip()
                    dosage_form = title_text.replace(match.group(0), "").strip()
                else:
                    drug_molecule = ""
                    dosage_form = title_text.strip()

                # Extraer otros detalles
                company = drug.find('b', string='Company:')
                if company:
                    company = company.next_sibling.strip()
                else:
                    company = ""

                # Verificar si 'Treatment for:' está presente antes de intentar extraerlo
                treatment_element = drug.find('b', string='Treatment for:')
                if treatment_element:
                    treatment_for = treatment_element.next_sibling.strip()
                else:
                    treatment_for = ""
                date_of_approval = drug.find('b', string='Date of Approval:').next_sibling.strip()
                # Escribir los datos en el archivo CSV

                new_row = {
                        'name': name,
                        'molecule': drug_molecule,
                        'dosage_form': dosage_form,
                        'date_of_approval': date_of_approval, 'company': company,
                        'treatment_for': treatment_for
                    }
                new_df = pd.DataFrame([new_row])
                self.data = pd.concat([self.data, new_df], ignore_index=True)

    def get_newest_drugs(self, limit=None):
        """Fetches the newest drugs listed on drugs.com for the current year"""
        pass

    def get_related_drugs(self, drug_name, limit=None):
        """Fetches drugs related to a specified drug name"""
        pass

    def save_to_csv(self, file_name='drugs_data.csv'):
        """Saves the data to a CSV file"""
        self.data.to_csv(file_name, index=False)

