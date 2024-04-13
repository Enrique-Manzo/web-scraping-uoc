# Web Scrapting de la pagina web Drugs.com

## ¿ En qué consiste este proyecto?

Los datos que podemos extraer de un sitio web de este tipo pueden ser muy útiles para muchas organizaciones que necesiten información actualizada sobre fármacos. Este podría ser un sitio web entre muchos dentro de un proyecto más grande de scraping y podría servir para alimentar una base de datos sobre fármacos recientes. Tomemos por caso un centro de investigación que se está planteando comenzar el desarrollo de un nuevo fármaco para combatir el malestar estomacal. Los investigadores ahorrarían mucho tiempo buscando en la base de datos del centro de investigación directamente, por medio de la cual obtendrían información detallada sobre fármacos recientes, el origen de los datos obtenidos, su fecha, etc. De este modo se ahorrarían tener que consultar una multiplicidad de páginas web para poder iniciar el planteo de su proyecto de investigación. También podríamos imaginar el caso de una empresa que se especializa en comercializar un cierto tipo de fármaco. Esta empresa podría valerse de los datos recabados en este proyecto de web scraping para analizar los fármacos comercializados por la competencia y así proponerse hacer un proyecto de data analysis que tenga como objetivo conocer la mejor manera de canalizar su estrategia de ventas.

## Columnas del dataset:

Extracción de los datos varios de la página web drugs.com sobre los nuevos medicamentos aprobados por la FDA. 
Los datos están guardados en formato CSV con los siguientes campos de interés:

Nombre del medicamento: Identificación única del producto farmacéutico.
Principio activo: Compuesto responsable del efecto terapéutico.
Forma farmacéutica: Presentación del medicamento (comprimido, cápsula, jarabe, etc.).
Año de aprobación: Fecha en que la FDA aprobó el medicamento.
Empresa solicitante: Laboratorio o compañía farmacéutica responsable de la solicitud de aprobación.
Indicación terapéutica: Enfermedad o condición que el medicamento trata.

## Visión general del scraper

`DrugsScraper` es una clase de Python diseñada para el scraping de datos relacionados con medicamentos del sitio web [Drugs.com](https://www.drugs.com). Recopila información como nombres de medicamentos, moléculas, formas de dosificación, fechas de aprobación, compañías, propósitos de tratamiento y URLs para obtener información más detallada.

## Requisitos
- Python 3.6 o superior
- Bibliotecas: `requests`, `beautifulsoup4`, `pandas`
  Instálalas usando pip:
  
  ```bash
  pip install requests beautifulsoup4 pandas
  ```

## Características

Debido a que el scraping puede hacer un uso intensivo del servidor y del dispositivo del cliente, se ha modularizado el comportamiento del scraper en diferentes métodos de la clase. Cada método recopila datos de manera incremental (no sobreescribe los anteriores, sino que aumenta el dataset). Esto es debido a que se deben consultar, en ciertos casos, varias páginas para obtener información detallada. La modularización permite reducir este coste si así se lo desea. Por la misma razón, la función básica tiene un límite que se le puede agregar al scrapper.

`scrape_drugs_by_year`: este método recibe un una lista con los años de los que se quiere recopilar datos. Devuelve la serie de datos básicos.  
`fetch_specifics`: este método agrega al dataframe la serie de datos específicos. Obligatoriamente se debe llamar después de scrape_drugs_by_year y sirve para incrementar los datos.  
`get_review_data`: es el último método de scraping incremental. Permite revisar todas las URLs con reseñas y agregar datos de las reseñas al datafram.  
`show_data`: imprime el dataframe por consola. Es útil si se quiere ver el estado del dataframe.  
`get_dataframe`: devuelve un dataframe de pandas. Es útil si se quieren manipular los datos antes de guardarlos.  
`save_to_csv`: guarda los datos en un archivo CSV en el directorio "dataset". Recibe un string como parámetro, el cual debe contener el nombre del archivo y la extensión "csv".  

## USO

### Inicialización

Primero importa el scraper.

```python
from DrugsScraper import DrugsScraper

scraper = DrugsScraper()
```

### Scraping de la información básica

Después de raspar la información básica, obtén datos detallados del medicamento:

```python
scraper.scrape_drugs_by_year(years=[2020, 2021], limit=50)
```

`years`: Lista de años para raspar.  
`limit`: Número máximo de medicamentos para raspar por año (opcional).  

### Scraping de la información detallada

```python
scraper.fetch_specifics()
```

### Recolección de Datos de Reseñas

Para recopilar datos de reseñas:

```python
scraper.get_review_data()
```

### Ejemplo

Ejemplo de cómo usar `DrugScraper` para recopilar datos de fármacos aprobados entre 2018 y 2019:

```python
scraper = DrugsScraper()
scraper.scrape_drugs_by_year(years=[2018, 2019])
scraper.fetch_specifics()
scraper.get_review_data()
scraper.save_to_csv(file_name='datos_medicamentos_2018_2019.csv')
```

