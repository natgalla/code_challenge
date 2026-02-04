# Star Wars Starship Browser

A Flask app that lets you browse Star Wars starships by manufacturer, using data from the [SWAPI](https://www.swapi.tech/) API.

## Features

- User authentication (register/login)
- Browse all starships or filter by manufacturer
- Data cached in SQLite database on first startup

## Project Structure

```
code_challenge/
├── app/
│   ├── __init__.py      # App factory
│   ├── extensions.py    # Flask extensions (db, login_manager)
│   ├── models.py        # Database models
│   ├── routes.py        # Route handlers
│   ├── services.py      # SWAPI data fetching
│   └── templates/       # Jinja templates
├── config.py            # Configuration
├── requirements.txt
├── run.py               # Entry point
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.x

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd code_challenge
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   python run.py
   ```

5. Open http://127.0.0.1:5000 in your browser

### First Startup

On first startup, the app will fetch starship data from SWAPI and populate the database. This may take a moment.

## Usage

1. Register a new account or login
2. Use the dropdown to filter starships by manufacturer, or select "All" to view all starships

## License

MIT
