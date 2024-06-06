import fire
import logging
from dataclasses import dataclass
from src.prereqs import fetch_courses, save_to_csv
from src.csv_fixer import process_courses
from src.graph_maker import app
from src.utils.settings import RAW_COURSES_CSV, COURSES_CSV, COURSE_WEBSITE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class CourseManager:
    """Handles course data operations including fetching prerequisites, saving to CSV, formatting data, and visualizing with a graph."""

    def fetch_and_save_courses(self) -> None:
        """Fetch courses and their prerequisites from the website and save them to a CSV file."""
        logger.info("Fetching courses and prerequisites...")
        courses = fetch_courses(COURSE_WEBSITE)
        save_to_csv(courses, RAW_COURSES_CSV)
        logger.info(f"Courses and prerequisites saved to {RAW_COURSES_CSV}")

    def process_courses_csv(self) -> None:
        """Process the raw courses CSV to format the course codes and prerequisites."""
        logger.info("Processing courses CSV to format course codes and prerequisites...")
        process_courses(RAW_COURSES_CSV, COURSES_CSV)
        logger.info(f"Formatted courses CSV saved to {COURSES_CSV}")

    def run_graph_app(self) -> None:
        """Run the Dash graph visualization application."""
        logger.info("Running the graph visualization app...")
        app.run_server(debug=True)


if __name__ == '__main__':
    fire.Fire(CourseManager)
