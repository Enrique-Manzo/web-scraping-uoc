from source.scrapers.pharma import DrugsScraper
# Example usage
scraper = DrugsScraper()
scraper.scrape_drugs_by_year(years=[2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024])
scraper.fetch_specifics()
scraper.get_review_data()
scraper.save_to_csv(file_name="Base de datos de Medicamentos Aprobados por la FDA (2002-2024).csv")
