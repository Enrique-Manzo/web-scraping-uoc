from source.scrapers.pharma import DrugsScraper
# Example usage
scraper = DrugsScraper()
scraper.scrape_drugs_by_year(years=[2024])
scraper.fetch_specifics()
scraper.get_review_data()
scraper.save_to_csv(file_name="Farmacos_2024.csv")
