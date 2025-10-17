#!/bin/bash

# Exit on any error
set -e

echo "=== eTech Academy Launch Script ==="
echo ""

# 0. Install system dependencies if needed (Debian/Ubuntu)
if command -v apt-get &> /dev/null; then
    echo "Checking system dependencies..."
    if ! dpkg -s python3-pip python3-venv postgresql build-essential libpq-dev &> /dev/null; then
        echo "Installing system dependencies..."
        sudo apt-get update
        sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib \
            libpq-dev build-essential python3-dev gcc
    else
        echo "System dependencies are installed."
    fi
fi

# 1. Check if PostgreSQL is running
echo "Checking PostgreSQL status..."
if ! sudo systemctl is-active --quiet postgresql 2>/dev/null && ! pgrep -x postgres > /dev/null 2>&1; then
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql 2>/dev/null || sudo service postgresql start 2>/dev/null || {
        echo "Warning: Could not start PostgreSQL automatically. Please start it manually."
    }
else
    echo "PostgreSQL is running."
fi

# 2. Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# 3. Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# 4. Install/Update dependencies
echo "Installing Python dependencies..."
pip install -q --upgrade pip

# Try to install requirements, if psycopg2 fails, it will use psycopg2-binary
if ! pip install -q -r requirements.txt 2>/dev/null; then
    echo "Standard installation failed, trying with psycopg2-binary..."
    sed -i 's/psycopg2==/psycopg2-binary==/g' requirements.txt 2>/dev/null || sed -i '' 's/psycopg2==/psycopg2-binary==/g' requirements.txt
    pip install -q -r requirements.txt
fi

# 5. Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=etechacademy
DB_USER=etech_user
DB_PASSWORD=your_secure_password
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
FLASK_DEBUG=False
EOF
    echo "WARNING: Please update the .env file with your actual database credentials!"
else
    echo ".env file already exists."
fi

# 6. Check if database exists and setup if needed
echo "Checking database setup..."
if python3 -c "from app.database import get_db_connection; get_db_connection()" 2>/dev/null; then
    echo "Database connection successful."
else
    echo "Setting up database..."
    python3 main.py setup-db || {
        echo "WARNING: Database setup failed. You may need to:"
        echo "  1. Create the database: sudo -u postgres createdb etechacademy"
        echo "  2. Create the user: sudo -u postgres psql -c \"CREATE USER etech_user WITH PASSWORD 'your_secure_password';\""
        echo "  3. Grant privileges: sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE etechacademy TO etech_user;\""
        echo "  4. Run: python3 main.py setup-db"
    }
fi

# 7. Launch the Flask application
echo ""
echo "=== Launching Flask Application ==="
echo "The application will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server."
echo ""

export FLASK_APP=main.py
flask run --host=0.0.0.0 --port=5000
