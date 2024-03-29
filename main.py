import logging, argparse, datetime
import src.seleniumScraper as scraper
from src.lobbyingDataPage import PageFactory
from src.sql_manager import execute_query

########################
# COMMAND LINE METHODS #
########################
# -a --all
def pull_and_process_all_disclosure_urls():
    current_year = datetime.datetime.now().year
    scrape_disclosure_urls(end_year=current_year)
    process_disclosure_urls()

# -r --recent
def pull_and_process_recent_disclosure_urls():
    current_year = datetime.datetime.now().year
    scrape_disclosure_urls(current_year-1, current_year)
    process_disclosure_urls()



###############################
# Command line Helper Methods #
###############################

def scrape_disclosure_urls(start_year=2005, end_year=2023):
    driver = scraper.create_driver()
    for year in range(start_year, end_year + 1):
        logging.info(f"Pulling disclosure report urls from {year}")
        scraper.get_disclosures_by_year(year,driver)
    driver.close()

def process_disclosure_urls():
    all_disclosures = set(execute_query("SELECT url FROM disclosure_urls;"))
    print(len(all_disclosures))
    processed_disclosures = set(execute_query("SELECT url FROM headers;"))
    print(len(processed_disclosures))
    new_disclosures = all_disclosures - processed_disclosures
    num_processed = len(processed_disclosures)
    num_total = len(all_disclosures)

    driver = scraper.create_driver()
    for disclosure_url in new_disclosures:
        print(f"Processed {num_processed} of {num_total}, {round((num_processed/num_total)*100, 2)}% complete")
        PageFactory(disclosure_url[0], driver).save()
        num_processed += 1
    driver.close()

def parse_arguments():
    verbosity_levels = [logging.WARNING, logging.INFO, logging.DEBUG]

    all_help = """Scrape, process, and save all disclosure reports from sec.state.ma.us"""
    recent_help = """Scrape, process and save disclosure reports from the last 2 years."""
    process_help = """Process saved disclosure url's to extract tables"""
    verbose_help = "set logging level. Default = 0, max = 2"

    help_msg = f"""Maple Lobbying Scraper"""

    parser = argparse.ArgumentParser(description = help_msg)
    parser.add_argument('-a', '--all', help = all_help, action = 'store_true')
    parser.add_argument('-r', '--recent', help = recent_help, action='store_true')
    parser.add_argument('-p', '--process', help = process_help, action = 'store_true')
    parser.add_argument('-v', '--verbose', help=verbose_help, action='count', default=0)

    args = parser.parse_args()
    logging.basicConfig(level=verbosity_levels[args.verbose])

    if args.all:
        pull_and_process_all_disclosure_urls()
    elif args.recent:
        pull_and_process_recent_disclosure_urls()
    elif args.process:
        process_disclosure_urls()
    else:
        parser.print_help()


# Main
if __name__ == "__main__":
    parse_arguments()


