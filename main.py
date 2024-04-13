from scrapers.pharma import DrugsScraper
# Example usage
scraper = DrugsScraper()
scraper.scrape_drugs_by_year(years=[2018,2019])
scraper.fetch_specifics()
scraper.save_to_csv(file_name="farmacos_2018_2019.csv")
