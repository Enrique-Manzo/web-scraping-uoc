import requests
from bs4 import BeautifulSoup
import pandas as pd


class DrugsScraper:
    def __init__(self, base_url='https://www.drugs.com'):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.data = pd.DataFrame(columns=['name', 'molecule', 'dosage_form', 'date_of_approval', 'company', 'treatment_for', 'url'])

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

    def scrape_drugs_by_year(self, years: list, limit: int = None) -> None:
        for year in years:
            """Scrapes drugs released in a specific year from drugs.com"""
            url = f'{self.base_url}/newdrugs-archive/{year}.html'
            html = self.__get_html(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Encontrar todos los elementos de medicamentos en la página
                drugs = soup.find_all('div', class_='ddc-media-content')

                # Si hay un límite, restringimos el número de resultados
                if limit:
                    drugs = drugs[:limit]

                # Iterar sobre los elementos de medicamentos para extraer la información
                for drug in drugs:
                    name = drug.find('a').get_text(strip=True)
                    url = "https://www.drugs.com"+drug.find('a')['href']
                    title_text = drug.find('h3', class_='ddc-media-title').get_text(strip=True)

                    part_1 = title_text.split("(")[1]

                    part_2 = part_1.split(")")

                    drug_molecule = ""
                    dosage_form = ""

                    if len(part_2) > 1:
                        drug_molecule = part_2[0].strip()
                        dosage_form = part_2[1].strip()

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
                            'date_of_approval': date_of_approval,
                            'company': company,
                            'treatment_for': treatment_for,
                            'url': url
                        }
                    new_df = pd.DataFrame([new_row])
                    self.data = pd.concat([self.data, new_df], ignore_index=True)

    def get_newest_drugs(self, limit=None):
        """Fetches the newest drugs listed on drugs.com for the current year"""
        pass

    def get_related_drugs(self, drug_name, limit=None):
        """Fetches drugs related to a specified drug name"""
        pass

    def fetch_specifics(self):
        """
        Agrega los campos "drug_molecule_url", "drug_class", "image", "related_drugs", "rating",
        "reviews", "reviews_url", "url",
        pero demora más tiempo, ya que tiene que acceder a cada url por separado.
        """

        url_list = self.data['url']
        specifics = []

        if len(url_list) < 0:
            print("You must first call the method scrape_drugs_by_year to fetch the basic data.")
            return

        for url in url_list:
            html = self.__get_html(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Find the paragraph with class "drug-subtitle"
                drug_info = soup.find('p', class_='drug-subtitle')

                molecule_url = ""
                drug_class = ""
                # Check if the element was found
                if drug_info:
                    # Extract and print the dosage form
                    # The dosage form text is assumed to directly follow the <b>Dosage form:</b> element
                    links = drug_info.find_all('a')

                    try:
                        molecule_url = "https://www.drugs.com" + links[0]['href']
                    except IndexError:
                        molecule_url = None

                    try:
                        drug_class = links[1].get_text()
                    except IndexError:
                        drug_class = None

                image_container = soup.find('div', class_='drugImageHolder')

                image = ""

                if image_container:
                    # Find the 'img' element within the container
                    image = image_container.find('img')['src']

                # Find the 'blockquote' tag with id 'related-drugs'
                related_drugs_block = soup.find('blockquote', id='related-drugs')

                # Initialize a list to store drug names and their links
                related_drugs_list = []

                # Check if the block was found
                if related_drugs_block:
                    # Find all 'a' tags within the blockquote
                    drug_links = related_drugs_block.find_all('a')

                    # Extract the drug names and links
                    for link in drug_links:
                        related_drugs_list.append(link.text)
                # Join all drug names into a single string separated by commas
                related_drugs = ', '.join(related_drugs_list)

                rating_element = soup.select_one('.ddc-rating-summary div b')
                reviews_element = soup.select_one('.ddc-rating-summary em a')

                # Check if elements exist before trying to access properties or methods
                rating = rating_element.text if rating_element else None
                if reviews_element:
                    reviews = reviews_element.text.split(" ")[0]
                    reviews_url = "https://www.drugs.com" + reviews_element['href']
                else:
                    reviews = None
                    reviews_url = None

                specific_dic = {
                    "molecule_url": molecule_url,
                    "drug_class": drug_class,
                    "image": image,
                    "related_drugs": related_drugs,
                    "rating": rating,
                    "reviews": reviews,
                    "reviews_url": reviews_url,
                    "url": url
                }

                details = soup.select(".ddc-status-info-item")

                if details:
                    for detail in details:
                        label = detail.select_one("b").get_text()
                        value = detail.select_one(".ddc-display-block").get_text()
                        specific_dic[label] = value

                warnings = soup.select(".ddc-status-info .ddc-accordion-section")

                if warnings:
                    for warning in warnings:
                        label = warning.select_one("b").get_text()
                        value = warning.select_one(".ddc-display-block").get_text()
                        specific_dic[label] = value

                specifics.append(specific_dic)

        specifics_df = pd.DataFrame(specifics)

        self.data = pd.merge(self.data, specifics_df, on='url', how='outer')

        return

    def save_to_csv(self, file_name: str = 'drugs_data.csv'):
        dataset_destination = "dataset/"+file_name
        """Saves the data to a CSV file"""
        self.data.to_csv(dataset_destination, index=False)

