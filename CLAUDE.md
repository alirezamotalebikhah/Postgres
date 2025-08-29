# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a PostgreSQL learning project implemented in Python using SQLAlchemy ORM. The codebase consists of sequential tutorial videos demonstrating database operations, connections, and advanced PostgreSQL features.

### Core Components

- **Database Connection**: PostgreSQL database accessed via SQLAlchemy and psycopg2
- **ORM Models**: SQLAlchemy declarative models for tables (Customer, Product, OrderApp)
- **Tutorial Scripts**: Sequential Python files (Video 1.py through Video 11.py) demonstrating progressive database concepts
- **Database Schema**: Three main tables with relationships:
  - Customer (CustomerId, Name, Surname)
  - Product (ProductId, Name, Price) 
  - OrderApp (OrderId, CustomerId, ProductId, DateSent) with foreign key constraints

### Database Configuration

- **Connection String**: `postgresql://myuser:mypassword@localhost:5432/mydatabase`
- **Docker Setup**: PostgreSQL container configured in docker-compose.yml
- **Database User**: `myuser` with superuser privileges (see roles.sql)

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Start PostgreSQL container
docker-compose up -d

# Check container status
docker ps
```

### Running Scripts
```bash
# Run individual tutorial scripts
python "Video 1.py"
python "Video 2-1.py" 
# etc.

# Run main application
python main.py
```

### Database Operations
```bash
# Connect to PostgreSQL container
docker exec -it postgres_container_name psql -U myuser -d mydatabase

# Restore database dump
psql -U myuser -d mydatabase < mydatabase.dump

# Apply role configurations
psql -U myuser -d mydatabase < roles.sql
```

## Key Dependencies

- SQLAlchemy 2.0.43 - ORM and database toolkit
- psycopg2-binary 2.9.10 - PostgreSQL adapter
- psycopg 3.2.9 - Modern PostgreSQL adapter
- python-dotenv 1.1.1 - Environment variable management

## Project Structure

- Sequential tutorial files demonstrate database concepts in order
- Each video file focuses on specific database operations:
  - Video 1: Basic connection and table creation
  - Video 2: CRUD operations  
  - Video 5: Delete and insert operations
  - Video 7: Product table manipulation with random data
  - Video 8: Foreign key constraints and relationships
  - And so on...

## Tutorial Context

This project follows a YouTube playlist tutorial series on PostgreSQL with Python. Each numbered file corresponds to a specific video lesson, building database knowledge progressively from basic connections to advanced features like indexing and collation.