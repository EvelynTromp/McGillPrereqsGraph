import requests
from bs4 import BeautifulSoup

# URL of the page to scrape
url = 'https://www.mcgill.ca/study/2024-2025/faculties/science/undergraduate/programs/bachelor-science-bsc-major-computer-science' # Change this to the actual URL

# Send a GET request to the webpage
response = requests.get(url)

# Parse the HTML content of the page with Beautiful Soup
soup = BeautifulSoup(response.text, 'html.parser')

# Find all course listings
courses = soup.find_all('li', class_='program-course')

# Dictionary to hold course data
course_data = {}

for course in courses:
    title_tag = course.find('a', class_='program-course-title')
    if title_tag:
        course_name = title_tag.text.strip()
        prerequisites = []
        # Attempt to find prerequisites
        prereq_list = course.find('ul', class_='catalog-notes')
        if prereq_list:
            prereq_items = prereq_list.find_all('li')
            for item in prereq_items:
                if 'Prerequisite' in item.text:
                    # Extract and clean the prerequisite text
                    prereq_links = item.find_all('a')
                    for link in prereq_links:
                        prereq_course = link.text.strip()
                        if prereq_course:
                            prerequisites.append(prereq_course)
        
        # Store data in dictionary
        course_data[course_name] = {
            'prerequisites': prerequisites
        }

# Display the scraped data
for course, details in course_data.items():
    print(f"{course}: Prerequisites: {details['prerequisites']}")
