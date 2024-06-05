
import requests
from bs4 import BeautifulSoup

# URL of the page to scrape
url = 'https://www.mcgill.ca/study/2024-2025/courses/search?page=3'


# Send a GET request to the webpage
response = requests.get(url)

# Parse the HTML content of the page with Beautiful Soup
soup = BeautifulSoup(response.text, 'html.parser')

# Find all course listings using the appropriate div class from the HTML structure provided
courses = soup.find_all('div', class_='views-row')

# Dictionary to hold course data
course_data = {}

for course in courses:
    # Check if the course is not offered
    if 'not-offered' in course.get('class', []):
        continue  # Skip this course because it's not offered

    # Find the course title and link
    title_tag = course.find('h4', class_='field-content')
    if title_tag and title_tag.a:
        course_name = title_tag.a.text.strip()
        
        # Since no specific details on prerequisites are given, assuming an empty list:
        prerequisites = []

        # Store data in dictionary
        course_data[course_name] = {
            'prerequisites': prerequisites
        }

# Display the scraped data
for course, details in course_data.items():
    print(f"{course}: Prerequisites: {details['prerequisites']}")
