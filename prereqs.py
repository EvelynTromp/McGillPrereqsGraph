import requests
from bs4 import BeautifulSoup
import csv

def fetch_course_prerequisites(course_url, base_url):
    # Complete the relative URL if needed
    if course_url.startswith('/'):
        course_url = base_url + course_url
    
    response = requests.get(course_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the prerequisite information
    prerequisites = []
    prerequisite_list = soup.find('ul', class_='catalog-notes')
    if prerequisite_list:
        for li in prerequisite_list.find_all('li'):
            if 'Prerequisite:' in li.text:
                links = li.find_all('a')
                for link in links:
                    if link.text.strip():  # Ensure the link contains text
                        prerequisites.append(link.text.strip())
    return prerequisites

def fetch_courses(base_url, start_page=1):
    course_data = []
    page = start_page
    while True:
        url = f"{base_url}?page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        courses = soup.find_all('div', class_='views-row')
        
        if not courses:
            break

        if page > 10:
            break

        for course in courses:
            if 'not-offered' in course.get('class', []):
                continue

            title_tag = course.find('h4', class_='field-content')
            if title_tag and title_tag.a:
                course_name = title_tag.a.text.strip()
                course_url = title_tag.a['href']
                prerequisites = fetch_course_prerequisites(course_url, 'https://www.mcgill.ca')
                course_data.append((course_name, prerequisites))
        
        page += 1
    return course_data

def save_to_csv(course_data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Course Name', 'Prerequisites'])
        for course_name, prerequisites in course_data:
            prerequisites_str = ', '.join(prerequisites)
            writer.writerow([course_name, prerequisites_str])

# Base URL for course search pages
base_url = 'https://www.mcgill.ca/study/2024-2025/courses/search'
courses = fetch_courses(base_url)

# Save the data to CSV
save_to_csv(courses, 'C:\\Users\\evely\\OneDrive\\Desktop\\McGill Courses and Prereqs2.csv')
