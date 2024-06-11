import csv
import requests
from bs4 import BeautifulSoup
from src.utils.settings import RAW_COURSES_CSV, COURSE_WEBSITE
from concurrent.futures import ThreadPoolExecutor
import re  # Regular expression module to help extract course codes
import cProfile
import pstats

def fetch_course_prerequisites(course_url):
    response = requests.get(course_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    prereq_tag = soup.find('ul', class_='catalog-notes')
    prerequisites = []
    if prereq_tag:
        prereq_items = prereq_tag.find_all('li')
        for item in prereq_items:
            if 'Prerequisite' in item.text:
                links = item.find_all('a')
                for link in links:
                    if link.text:
                        prerequisites.append(link.text.strip())
    return prerequisites

def fetch_course_details(course):
    title_tag = course.find('h4', class_='field-content')
    if title_tag and title_tag.a:
        full_course_name = title_tag.a.text.strip()
        course_url = "https://www.mcgill.ca" + title_tag.a['href']
        # Update regular expression to capture courses with sequences like AERO 460D2
        course_code_match = re.search(r'\b[A-Z]{2,4}\s\d{3,4}[A-Z]?\d?\b', full_course_name)
        if course_code_match:
            course_name = course_code_match.group()
        else:
            course_name = full_course_name  # Fallback to the full name if no code pattern is found

        if 'not-offered' in course.get('class', []):
            course_name = "*" + course_name  # Maintain the asterisk notation for not offered courses
        prerequisites = fetch_course_prerequisites(course_url)
        return (course_name, prerequisites)
    return None

def fetch_courses(base_url, start_page=0):
    course_data = []
    page = start_page
    with ThreadPoolExecutor(max_workers=20) as executor:
        while True:
            url = f"{base_url}?page={page}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            courses = soup.find_all('div', class_='views-row')
            if not courses:
                break

            if page > 1:
                break


            # Use threading to fetch course details concurrently
            futures = [executor.submit(fetch_course_details, course) for course in courses]
            for future in futures:
                result = future.result()
                if result:
                    course_data.append(result)

            page += 1
    return course_data

def save_to_csv(course_data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Course Code', 'Prerequisites'])
        for course_name, prerequisites in course_data:
            prerequisites_str = ', '.join(prerequisites)
            writer.writerow([course_name, prerequisites_str])
    print(f"Data successfully saved to {filename}")



if __name__ == '__main__':
    courses = fetch_courses(COURSE_WEBSITE)
    save_to_csv(courses, RAW_COURSES_CSV)
