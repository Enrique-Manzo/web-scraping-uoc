from scrapers.pharma import DrugsScraper
# Example usage
scraper = DrugsScraper()
scraper.scrape_drugs_by_year(2023, limit=10)
scraper.show_data()
scraper.save_to_csv()