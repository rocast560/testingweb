#!/bin/bash

# Exit on any error
set -e

echo "========================================="
echo "  eTech Academy - Kali Linux Deployment"
echo "========================================="
echo ""

# Configuration
REPO_URL="https://github.com/rocast560/testingweb.git"
PROJECT_DIR="$HOME/etechacademy"
DB_NAME="etechacademy"
DB_USER="etech_user"
DB_PASSWORD="SecureP@ssw0rd123"

# 1. Update system and install dependencies
echo "[1/8] Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv git postgresql postgresql-contrib \
    build-essential libpq-dev python3-dev gcc

# 2. Start PostgreSQL service
echo "[2/8] Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 3. Clone the repository
echo "[3/8] Cloning repository..."
if [ -d "$PROJECT_DIR" ]; then
    echo "Directory $PROJECT_DIR already exists. Removing it..."
    rm -rf "$PROJECT_DIR"
fi
git clone "$REPO_URL" "$PROJECT_DIR"
cd "$PROJECT_DIR/etechacademy"

# 4. Create Python virtual environment
echo "[4/8] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 5. Install Python dependencies
echo "[5/8] Installing Python dependencies..."
pip install --upgrade pip setuptools wheel

# Install psycopg2-binary with verbose output to catch errors
echo "Installing psycopg2-binary..."
if ! pip install psycopg2-binary==2.9.9; then
    echo "Failed to install psycopg2-binary, trying psycopg2..."
    pip install psycopg2==2.9.9
fi

# Install remaining dependencies
echo "Installing remaining Python packages..."
pip install blinker==1.7.0 click==8.1.7 Flask==3.0.0 Flask-Bootstrap==3.3.7 \
    itsdangerous==2.1.2 Jinja2==3.1.2 MarkupSafe==2.1.3 \
    python-dotenv==1.0.0 Werkzeug==3.0.1

# 6. Set up PostgreSQL database
echo "[6/8] Setting up PostgreSQL database..."

# Check if database exists, if not create it
sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME" || {
    echo "Creating database: $DB_NAME"
    sudo -u postgres createdb "$DB_NAME"
}

# Check if user exists, if not create it
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || {
    echo "Creating database user: $DB_USER"
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
}

# Grant privileges
echo "Granting privileges..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

# 7. Create .env file
echo "[7/8] Creating .env configuration file..."
cat > .env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_DEBUG=False
EOF

# 8. Initialize database with tables and data
echo "[8/8] Initializing database..."
python3 main.py setup-db

# Display completion message
echo ""
echo "========================================="
echo "  ✓ Deployment Complete!"
echo "========================================="
echo ""
echo "Database Credentials:"
echo "  Database: $DB_NAME"
echo "  Username: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo "To launch the application:"
echo "  cd $PROJECT_DIR/etechacademy"
echo "  source venv/bin/activate"
echo "  flask run --host=0.0.0.0 --port=5000"
echo ""
echo "Or simply run:"
echo "  cd $PROJECT_DIR/etechacademy && ./launch.sh"
echo ""
echo "The application will be available at:"
echo "  http://localhost:5000"
echo "  http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "========================================="
echo ""

# Ask if user wants to start the application now
read -p "Do you want to start the application now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting Flask application..."
    echo "Press Ctrl+C to stop the server."
    echo ""
    export FLASK_APP=main.py
    flask run --host=0.0.0.0 --port=5000
fi
