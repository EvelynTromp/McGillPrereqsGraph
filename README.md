# McGill Courses and Prerequisites

This project automates the process of fetching, processing, and visualizing course prerequisites for McGill University courses. The project uses a command-line interface (CLI) to interact with different functionalities such as fetching course data, formatting the data, and visualizing it using a graph.

## Getting Started

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/EvelynTromp/McGillPrereqsGraph.git
   ```

2. Navigate to the project directory:

   ```bash
   cd McGillPrereqsGraph
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

Note: You may run `pipreqs . --force` in `/McGillPrereqsGraph` to update the requirements.txt file with the latest dependencies.

### Configuration

- Rename the `.env.example` file to `.env` and populate it with the necessary values. Example of necessary environment variables:
  - `COURSE_WEBSITE`: URL of the McGill course search page.

### Usage

Run the application using:

```bash
python main.py [command]
```

### Available Commands

- `fetch_and_save_courses`: Fetches courses and their prerequisites from the website and saves them to a CSV file.
  
  Example:
  
  ```bash
  python main.py fetch_and_save_courses
  ```

- `process_courses_csv`: Processes the raw courses CSV to format the course codes and prerequisites.

  Example:

  ```bash
  python main.py process_courses_csv
  ```

- `run_graph_app`: Runs the Dash graph visualization application.

  Example:

  ```bash
  python main.py run_graph_app
  ```

### Testing

Run unit tests using:

```bash
python -m unittest discover
```

## Project Structure

```
McGillPrereqsGraph/
│
├── main.py                # Main entry point for the application
├── requirements.txt       # Project dependencies
├── .env.example           # Example environment file
├── data/                  # Directory to store data files
│   ├── .cache/            # Cache directory
│   ├── csv/               # CSV files directory
│   └── plots/             # Plots directory
├── src/                   # Source code directory
│   ├── prereqs.py         # Fetch and save course prerequisites
│   ├── graph_maker.py     # Create and run the Dash graph visualization app
│   ├── csv_fixer.py       # Process and format CSV files
│   └── utils/             # Utility files
│       └── settings.py    # Configuration settings
└── tests/                 # Unit tests directory
```

## Contribute

This project is actively developed. Below is a list of tasks and areas that need attention.

- [ ] Add more unit tests to increase code coverage.
- [ ] Add more features to the Dash graph visualization app.
- [ ] Improve the code quality and structure.
- [ ] Add more error handling and logging.
- [ ] Add more documentation and comments.

(Thank you to the amazing Henri Lemoine (https://github.com/henri123lemoine) for helping me with organizing this repository!)
