from source.scrapers.pharma import DrugsScraper
# Example usage
scraper = DrugsScraper()
scraper.scrape_drugs_by_year(years=list(range(2002, 2025)))
scraper.fetch_specifics()
scraper.get_review_data()
scraper.get_side_effects()
scraper.get_consumer_price()
scraper.save_to_csv(file_name="farmacos_2002_2025_v3.csv")
