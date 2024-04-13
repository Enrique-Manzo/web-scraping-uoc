from source.scrapers.pharma import DrugsScraper
# Example usage
scraper = DrugsScraper()
scraper.scrape_drugs_by_year(years=[2024])
#scraper.fetch_specifics()
scraper.save_to_csv(file_name="farmacos_2024.csv")
