from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv()

# General
PROJECT_PATH = Path(__file__).parent.parent.parent
DATE = datetime.now().strftime('%Y-%m-%d')
YEAR = datetime.now().strftime('%Y')
COURSE_WEBSITE = 'https://www.mcgill.ca/study/2024-2025/courses/search' # TODO

## Data
DATA_PATH = PROJECT_PATH / 'data'
CACHE_PATH = DATA_PATH / '.cache'
PLOTS_PATH = DATA_PATH / 'plots'
CSV_PATH = DATA_PATH / 'csv'

## Source
SRC_PATH = PROJECT_PATH / 'src'
NOTEBOOKS_PATH = SRC_PATH / 'notebooks'

# CSVs
RAW_COURSES_CSV = CSV_PATH / 'McGill_Courses_and_Prereqs9.csv'
COURSES_CSV = CSV_PATH / 'Formatted_McGill_Courses_and_Prereqs.csv'
