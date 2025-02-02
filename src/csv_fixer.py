import csv
import re
from src.utils.settings import RAW_COURSES_CSV, COURSES_CSV


def format_course_code(course_code):
    # Remove dashes and replace with spaces
    course_code = course_code.replace('-', ' ')
    # Ensure there is a space between letters and numbers
    course_code = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", course_code)
    course_code = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", course_code)
    return course_code

def process_courses(input_file_path, output_file_path):
    with open(input_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        courses = list(reader)
    
    with open(output_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(courses[0])
        # Process each row except the header
        for course_code, prerequisites in courses[1:]:
            formatted_course_code = format_course_code(course_code)
            formatted_prerequisites = [format_course_code(code) for code in prerequisites.split(',')]
            writer.writerow([formatted_course_code, ','.join(formatted_prerequisites)])


if __name__ == '__main__':
    process_courses(RAW_COURSES_CSV, COURSES_CSV)
