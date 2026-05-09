# Add a dimension to Kompassi with values. The input file should follow this format:

# first-value-slug;English title for first value;Finnish title for first value
# second-value-slug;English title for second value;Finnish title for second value
# ...

import argparse
import csv
import os
from dotenv import load_dotenv
from gql import Client, gql

# Parse command-line arguments
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("slug", help="slug of the dimension")
arg_parser.add_argument("title_finnish", help="Finnish title of the dimension")
arg_parser.add_argument("title_english", help="English title of the dimension")
arg_parser.add_argument("path_to_file", help="path to semicolon-separated dimension value CSV file, relative to location of this script")
args = arg_parser.parse_args()

slug = args.slug
title_english = args.title_english
title_finnish = args.title_finnish
path_to_file = args.path_to_file

with open(path_to_file) as f:
    reader = csv.DictReader(f, fieldnames=["slug", "title_english", "title_finnish"])
    values = [row for row in reader]

# Get environment file
load_dotenv()
base_url = os.getenv("KOMPASSI_BASE_URL")
event_slug = os.getenv("EVENT_SLUG")

# Create dimension
print(f'Creating dimension {slug} with Finnish title {title_finnish} and English title {title_english}')
print(f'Writing to {base_url} for event {event_slug}')



# TODO Create
# TODO If already exists, report and continue



# TODO

print(f'Adding {len(values)} dimension values')


# TODO



exit(0)