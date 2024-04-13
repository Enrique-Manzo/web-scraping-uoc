import requests
from bs4 import BeautifulSoup
import pandas as pd

# Clase principal del scraper


class DrugsScraper:
    def __init__(self, base_url='https://www.drugs.com'):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        # Guarda en memoria un dataframe de pandas, que es fácil de trabajar y eficiente
        self.data = pd.DataFrame(columns=['name', 'molecule', 'dosage_form', 'date_of_approval', 'company', 'treatment_for', 'url'])

    def __get_html(self, url):
        """Método privado para hacer el pedido al servidor y traer el HTML"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Exepción en caso de respuesta de error
            return response.text
        except requests.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        return None

    def show_data(self):
        print(self.data)

    # Scraping básico - solamente los datos básicos de los fármacos
    def scrape_drugs_by_year(self, years: list, limit: int = None) -> None:
        for year in years:
            """Genera datos básicos sobre los fármacos en drugs.com"""

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

                    # Generamos diccionario para agregarlo a la lista que será nuestro nuevo dataframe
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


    # Permite extraer datos más específicos
    def fetch_specifics(self):
        """
        Agrega los campos "drug_molecule_url", "drug_class", "image", "related_drugs", "rating",
        "reviews", "reviews_url", "url",
        pero demora más tiempo, ya que tiene que acceder a cada url por separado.
        """

        url_list = self.data['url']
        specifics = []

        # Se asegura de que haya datos en el dataframe
        if len(url_list) == 0:
            print("You must first call the method scrape_drugs_by_year to fetch the basic data.")
            return

        for url in url_list:
            html = self.__get_html(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Encontrar el párrafo con la cse "drug-subtitle"
                drug_info = soup.find('p', class_='drug-subtitle')

                molecule_url = ""
                drug_class = ""

                if drug_info:
                    # Extrae el dosage form
                    links = drug_info.find_all('a')

                    # Puede ser que no existan algunos elementos, aunque esto es raro. En ese caso gestionamos el error
                    try:
                        molecule_url = "https://www.drugs.com" + links[0]['href']
                    except IndexError:
                        molecule_url = None

                    try:
                        drug_class = links[1].get_text()
                    except IndexError:
                        drug_class = None

                # Gestión de contenido multimedia
                image_container = soup.find('div', class_='drugImageHolder')

                image = ""

                if image_container:
                    image = image_container.find('img')['src']

                # Encontramos fármacos relacionados
                related_drugs_block = soup.find('blockquote', id='related-drugs')

                # Listado de fármacos relacionados
                related_drugs_list = []

                if related_drugs_block:
                    drug_links = related_drugs_block.find_all('a')

                    # Extraemos los nombres de los links
                    for link in drug_links:
                        related_drugs_list.append(link.text)
                # Finalmente se guarda como un string
                related_drugs = ', '.join(related_drugs_list)

                # Buscamos información sobre los ratings y reviews
                rating_element = soup.select_one('.ddc-rating-summary div b')
                reviews_element = soup.select_one('.ddc-rating-summary em a')

                # Vemos si hay reviews - 50/50 que hay, por eso no usamos un error handling
                rating = rating_element.text if rating_element else None
                if reviews_element:
                    reviews = reviews_element.text.split(" ")[0]
                    reviews_url = "https://www.drugs.com" + reviews_element['href']
                else:
                    reviews = None
                    reviews_url = None

                # Diccionario
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

                # Buscamos detalles como información sobre lactancia y embarazo. Puede variar el dato
                details = soup.select(".ddc-status-info-item")

                if details:
                    for detail in details:
                        label = detail.select_one("b").get_text()
                        value = detail.select_one(".ddc-display-block").get_text()
                        specific_dic[label] = value

                # Buscamos alertas - también pueden variar
                warnings = soup.select(".ddc-status-info .ddc-accordion-section")

                if warnings:
                    for warning in warnings:
                        label = warning.select_one("b").get_text()
                        value = warning.select_one(".ddc-display-block").get_text()
                        specific_dic[label] = value

                specifics.append(specific_dic)

        # Creamos el dataset con los datos específicos solamente
        specifics_df = pd.DataFrame(specifics)

        # Hacemos un join con el dataset general
        self.data = pd.merge(self.data, specifics_df, on='url', how='outer')

        return

    # Busca específicamente datos sobre reviews
    def get_review_data(self):
        """
        Busca datos sobre reseñas. Si el conjunto de datos específicos arrojó datos con reseñas, puede
        ser interesante recabar esos datos. Agrega al dataset: "most_reviewed_condition",
        "most_reviewed_rating", "n_reviews"
        """

        url_list = self.data['reviews_url']
        reviews = []

        # Verificamos que tengamos las URLs de las reseñas
        if len(url_list) == 0:
            print("You must first call the method fetch_specifics to fetch the detailed data.")
            return

        for url in url_list:
            if url is None:
                continue
            html = self.__get_html(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # Tomamos información sobre la tabla con los trastornos
                conditions_table = soup.select(".ddc-table-sortable tr")

                # Verificamos que existan suficientes elementos en conditions_table antes de acceder a ellos
                if len(conditions_table) > 1:
                    most_reviewed = conditions_table[1]

                    # Generamos las tres variables que nos interesan
                    condition = most_reviewed.select_one("th").text
                    most_reviewed_rating = most_reviewed.select_one(".ddc-text-right").text
                    n_reviews = most_reviewed.select_one("a").text.split(" ")[0]

                    reviews_dict = {
                        "most_reviewed_condition": condition,
                        "most_reviewed_rating": most_reviewed_rating,
                        "n_reviews": n_reviews,
                        "url": url
                    }

                    reviews.append(reviews_dict)
                else:
                    print("No hay suficientes elementos en conditions_table para acceder a la información.")


        reviews_df = pd.DataFrame(reviews)

        # Agregamos los datos al dataset
        self.data = pd.merge(self.data, reviews_df, left_on='reviews_url', right_on="url", how='outer')

        return


    def save_to_csv(self, file_name: str = 'drugs_data.csv'):
        """Saves the data to a CSV file"""

        # Como se indica en el enunciado, los datos se guardan en la carpeta "dataset"
        dataset_destination = "dataset/" + file_name
        self.data.to_csv(dataset_destination, index=False)

