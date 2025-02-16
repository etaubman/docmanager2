# Document Manager

A document management system built with FastAPI.

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Database Setup and Seeding

The application uses SQLite as its database. To set up the database with sample data:

1. First ensure the application dependencies are installed
2. Run the database seeder:
```bash
python -m app.database_seeder
```

This will create:
- 5 metadata field types (department, document date, confidential status, tags, and revision number)
- 3 document types (Contract, Report, Policy) with associated metadata fields
- 50 sample documents (default) with realistic metadata and 1-3 versions each

You can customize the number of sample documents by passing a parameter:
```bash
python -m app.database_seeder 100
```

## Using the CLI

The Document Manager includes a command-line interface for common operations:

### Document Management
```bash
# List all documents
docmanager documents list

# Upload a new document
docmanager documents upload path/to/file.txt

# Upload with category
docmanager documents upload path/to/file.txt -c "Important Documents"

# Delete a document
docmanager documents delete document-id
```

### Category Management
```bash
# List all categories
docmanager categories list

# Create a new category
docmanager categories create "Important Documents"
```

## API Usage

See the API documentation at `/api/docs` when running the server.

## Running Tests

To run the test suite:
```bash
pytest
```

This includes test coverage for the API endpoints, database seeder, and CLI functionality.