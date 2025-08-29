from sqlalchemy import (
    create_engine, MetaData, Column, Integer, String, Text, 
    ARRAY, DateTime, Boolean, Float, Index, select, and_, func
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timedelta
import random
import json

# Database connection
engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
Base = declarative_base()
Session = sessionmaker(bind=engine)

# ORM Model for demonstration table
class IndexDemo(Base):
    __tablename__ = 'index_demo_orm'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(255))
    age = Column(Integer)
    salary = Column(Float)
    tags = Column(ARRAY(String))
    metadata_json = Column(JSONB)
    description = Column(Text)
    search_vector = Column(TSVECTOR)
    created_at = Column(DateTime)
    is_active = Column(Boolean)
    score = Column(Float)
    large_text = Column(Text)

def create_indexes_orm():
    """Create different types of PostgreSQL indexes using SQLAlchemy"""
    
    print("=== CREATING DIFFERENT INDEX TYPES WITH ORM ===\n")
    
    # Create indexes using SQLAlchemy Index objects
    indexes = [
        # 1. B-Tree Index (Default)
        Index('idx_orm_btree_age', IndexDemo.age),
        
        # 2. Composite B-Tree Index
        Index('idx_orm_btree_name_age', IndexDemo.name, IndexDemo.age),
        
        # 3. Hash Index
        Index('idx_orm_hash_email', IndexDemo.email, postgresql_using='hash'),
        
        # 4. GIN Index for arrays
        Index('idx_orm_gin_tags', IndexDemo.tags, postgresql_using='gin'),
        
        # 5. GIN Index for JSONB
        Index('idx_orm_gin_json', IndexDemo.metadata_json, postgresql_using='gin'),
        
        # 6. GIN Index for full-text search
        Index('idx_orm_gin_fts', IndexDemo.search_vector, postgresql_using='gin'),
        
        # 7. GiST Index for full-text search
        Index('idx_orm_gist_fts', IndexDemo.search_vector, postgresql_using='gist'),
        
        # 8. SP-GiST Index
        Index('idx_orm_spgist_name', IndexDemo.name, postgresql_using='spgist'),
        
        # 9. BRIN Index for timestamps
        Index('idx_orm_brin_created_at', IndexDemo.created_at, postgresql_using='brin'),
        
        # 10. BRIN Index for salary
        Index('idx_orm_brin_salary', IndexDemo.salary, postgresql_using='brin'),
        
        # 11. Partial Index
        Index('idx_orm_partial_active_score', IndexDemo.score, 
              postgresql_where=(IndexDemo.is_active == True)),
        
        # 12. Expression Index
        Index('idx_orm_expr_lower_name', func.lower(IndexDemo.name)),
        
        # 13. Unique Index
        Index('idx_orm_unique_email', IndexDemo.email, unique=True)
    ]
    
    # Create all indexes
    for i, index in enumerate(indexes, 1):
        print(f"{i}. Creating {index.name}...")
        index.create(engine, checkfirst=True)
    
    print("\n=== ALL ORM INDEXES CREATED SUCCESSFULLY ===\n")

def insert_sample_data_orm():
    """Insert sample data using SQLAlchemy ORM"""
    
    print("=== INSERTING SAMPLE DATA WITH ORM ===\n")
    
    session = Session()
    
    try:
        # Clear existing data
        session.query(IndexDemo).delete()
        session.commit()
        
        # Generate sample data
        base_date = datetime.now() - timedelta(days=365)
        batch_size = 100
        total_records = 1000  # Smaller dataset for demo
        
        for batch_start in range(0, total_records, batch_size):
            batch_objects = []
            
            for i in range(batch_start, min(batch_start + batch_size, total_records)):
                description_text = f'This is a description for user {i} with various keywords and content.'
                
                demo_obj = IndexDemo(
                    name=f'User_{random.randint(1, 200)}',
                    email=f'user{i}@example.com',
                    age=random.randint(18, 80),
                    salary=random.uniform(30000, 150000),
                    tags=[f'tag{random.randint(1, 20)}' for _ in range(random.randint(1, 5))],
                    metadata_json={
                        'department': random.choice(['IT', 'HR', 'Finance', 'Marketing']),
                        'level': random.randint(1, 10),
                        'skills': [f'skill{random.randint(1, 50)}' for _ in range(random.randint(1, 3))]
                    },
                    description=description_text,
                    search_vector=func.to_tsvector('english', description_text),
                    created_at=base_date + timedelta(days=random.randint(0, 365)),
                    is_active=random.choice([True, False]),
                    score=random.uniform(0, 100),
                    large_text=f'Large text content for user {i} ' * 10
                )
                batch_objects.append(demo_obj)
            
            session.add_all(batch_objects)
            session.commit()
        
        print(f"Inserted {total_records} records successfully using ORM.\n")
        
    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")
    finally:
        session.close()

def demonstrate_index_usage_orm():
    """Demonstrate different index access methods using SQLAlchemy ORM"""
    
    print("=== DEMONSTRATING INDEX USAGE WITH ORM ===\n")
    
    session = Session()
    
    try:
        # 1. B-Tree Index Usage - Range Query
        print("1. B-Tree Index Usage - Range Query on Age (ORM):")
        query = session.query(IndexDemo).filter(IndexDemo.age.between(25, 35))
        print(f"   Found {query.count()} records")
        print(f"   Query: {query}")
        print()
        
        # 2. Hash Index Usage - Equality Query
        print("2. Hash Index Usage - Equality Query on Email (ORM):")
        query = session.query(IndexDemo).filter(IndexDemo.email == 'user100@example.com')
        result = query.first()
        print(f"   Found: {'Yes' if result else 'No'}")
        print(f"   Query: {query}")
        print()
        
        # 3. JSONB Query using ORM
        print("3. JSONB Query - Department filter (ORM):")
        query = session.query(IndexDemo).filter(
            IndexDemo.metadata_json['department'].astext == 'IT'
        )
        print(f"   Found {query.count()} IT department records")
        print(f"   Query: {query}")
        print()
        
        # 4. Array Contains Query
        print("4. Array Contains Query (ORM):")
        # Note: SQLAlchemy ORM doesn't have direct array contains, but we can use func
        query = session.query(IndexDemo).filter(
            IndexDemo.tags.any('tag1')
        )
        print(f"   Found {query.count()} records with 'tag1'")
        print(f"   Query: {query}")
        print()
        
        # 5. Partial Index Usage
        print("5. Partial Index Usage - Active Users with High Score (ORM):")
        query = session.query(IndexDemo).filter(
            and_(IndexDemo.is_active == True, IndexDemo.score > 50)
        )
        print(f"   Found {query.count()} active users with score > 50")
        print(f"   Query: {query}")
        print()
        
        # 6. Expression Index Usage
        print("6. Expression Index Usage - Case Insensitive Search (ORM):")
        query = session.query(IndexDemo).filter(
            func.lower(IndexDemo.name) == 'user_100'
        )
        print(f"   Found {query.count()} records with name 'User_100' (case insensitive)")
        print(f"   Query: {query}")
        print()
        
        # 7. Date Range Query (BRIN Index)
        print("7. Date Range Query using BRIN Index (ORM):")
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 6, 1)
        query = session.query(IndexDemo).filter(
            and_(IndexDemo.created_at >= start_date, IndexDemo.created_at < end_date)
        )
        print(f"   Found {query.count()} records in date range")
        print(f"   Query: {query}")
        print()
        
        # 8. Complex Query combining multiple indexes
        print("8. Complex Query - Multiple Index Usage (ORM):")
        query = session.query(IndexDemo).filter(
            and_(
                IndexDemo.age.between(30, 50),
                IndexDemo.is_active == True,
                IndexDemo.metadata_json['department'].astext.in_(['IT', 'Finance'])
            )
        )
        print(f"   Found {query.count()} records matching complex criteria")
        print(f"   Query: {query}")
        print()
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
    finally:
        session.close()

def show_index_information_orm():
    """Display information about created indexes using SQLAlchemy"""
    
    print("=== INDEX INFORMATION (ORM TABLE) ===\n")
    
    session = Session()
    
    try:
        # Get index information using raw SQL (no choice here for metadata)
        result = session.execute("""
            SELECT 
                indexname,
                indexdef,
                pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_indexes 
            WHERE tablename = 'index_demo_orm'
            ORDER BY indexname
        """)
        
        print("Indexes on 'index_demo_orm' table:")
        for row in result:
            print(f"\nIndex: {row[0]}")
            print(f"Size: {row[2]}")
            print(f"Definition: {row[1]}")
        
    except Exception as e:
        print(f"Error getting index information: {e}")
    finally:
        session.close()

def cleanup_orm():
    """Clean up - drop the demo table and indexes"""
    
    print("\n=== CLEANING UP ORM TABLE ===")
    IndexDemo.__table__.drop(engine, checkfirst=True)
    print("ORM demo table and indexes dropped successfully.")

def main():
    """Main function to run the ORM index demonstration"""
    
    print("PostgreSQL Index Types Demonstration - ORM Version")
    print("="*60)
    
    # Create table
    Base.metadata.create_all(engine)
    print("ORM demo table created successfully.\n")
    
    # Create various types of indexes
    create_indexes_orm()
    
    # Insert sample data
    insert_sample_data_orm()
    
    # Show index information
    show_index_information_orm()
    
    # Demonstrate index usage
    demonstrate_index_usage_orm()
    
    # Ask user if they want to cleanup
    try:
        cleanup_choice = input("\nDo you want to cleanup (drop the ORM demo table)? (y/n): ")
        if cleanup_choice.lower() == 'y':
            cleanup_orm()
        else:
            print("ORM demo table preserved for further testing.")
    except EOFError:
        print("ORM demo table preserved for further testing.")

if __name__ == "__main__":
    main()