import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_URL = os.getenv("DATABASE_URL")

def initialize_database():
    print("🔌 Connecting to PostgreSQL...")
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    print("🏗️ Building schema...")
    
    # Create Inventory Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            asset_tag VARCHAR(50) PRIMARY KEY,
            employee_id VARCHAR(50),
            device_type VARCHAR(50),
            model VARCHAR(100),
            status VARCHAR(50)
        );
    """)

    # Create Tickets Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id SERIAL PRIMARY KEY,
            employee_id VARCHAR(50),
            issue_description TEXT,
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Clear existing data for clean testing
    cursor.execute("TRUNCATE TABLE inventory RESTART IDENTITY CASCADE;")
    cursor.execute("TRUNCATE TABLE tickets RESTART IDENTITY CASCADE;")

    print("🌱 Seeding initial data...")
    
    # Insert dummy inventory
    inventory_data = [
        ('LAP-1001', 'EMP-001', 'Laptop', 'HP EliteBook 840 G8', 'Active'),
        ('LAP-1002', 'EMP-002', 'Laptop', 'Dell Latitude 7420', 'Active'),
        ('MON-2001', 'EMP-001', 'Monitor', 'Dell UltraSharp 27', 'Active')
    ]
    
    cursor.executemany(
        "INSERT INTO inventory (asset_tag, employee_id, device_type, model, status) VALUES (%s, %s, %s, %s, %s)",
        inventory_data
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database initialization complete!")

if __name__ == "__main__":
    initialize_database()