import csv
import requests
from bs4 import BeautifulSoup
from src.utils.settings import RAW_COURSES_CSV, COURSE_WEBSITE


def fetch_course_prerequisites(course_url):
    # Send a GET request to the course detail page
    response = requests.get(course_url)
    # Parse the HTML content of the page with Beautiful Soup
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the prerequisites section (assuming similar HTML structure as provided)
    prereq_tag = soup.find('ul', class_='catalog-notes')
    prerequisites = []
    if prereq_tag:
        prereq_items = prereq_tag.find_all('li')
        for item in prereq_items:
            if 'Prerequisite' in item.text:
                # Extract just the prerequisite course codes from the text
                links = item.find_all('a')
                for link in links:
                    if link.text:  # Ensure that the link text is not empty
                        prerequisites.append(link.text.strip())
    return prerequisites

def fetch_courses(base_url, start_page=1):
    course_data = []
    page = start_page
    while True:
        # Construct URL for the current page
        url = f"{base_url}?page={page}"
        # Send a GET request to the webpage
        response = requests.get(url)
        # Parse the HTML content of the page with Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all course listings using the appropriate div class
        courses = soup.find_all('div', class_='views-row')
        # Check if there are no courses listed on the page
        if not courses:
            break  # Exit the loop if no courses are found
          
        if page > 10:
            break #debug 
        
        for course in courses:
            # Check if the course is not offered
            if 'not-offered' not in course.get('class', []):
                title_tag = course.find('h4', class_='field-content')
                if title_tag and title_tag.a:
                    course_name = title_tag.a.text.strip()
                    course_url = "https://www.mcgill.ca" + title_tag.a['href']
                    # Fetch prerequisites by visiting the course detail page
                    prerequisites = fetch_course_prerequisites(course_url)
                    # Store data in list as tuple
                    course_data.append((course_name, prerequisites))
        # Increment page number to fetch the next page
        page += 1
    return course_data

def save_to_csv(course_data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Course Name', 'Prerequisites'])  # Writing headers
        for course_name, prerequisites in course_data:
            # Join prerequisites list into a comma-separated string for CSV output
            prerequisites_str = ', '.join(prerequisites)
            writer.writerow([course_name, prerequisites_str])
    print(f"Data successfully saved to {filename}")


if __name__ == '__main__':
    # Base URL for course search pages
    courses = fetch_courses(COURSE_WEBSITE)

    # Save the data to CSV
    save_to_csv(courses, RAW_COURSES_CSV)
