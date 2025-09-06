from sqlalchemy import create_engine, MetaData, inspect, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import sys

def connect_to_database():
    """Connect to PostgreSQL database"""
    try:
        engine = create_engine('postgresql://myuser:mypassword@localhost:5432/mydatabase')
        return engine
    except SQLAlchemyError as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def get_all_tables(inspector):
    """Get all table names from the database"""
    try:
        return inspector.get_table_names()
    except SQLAlchemyError as e:
        print(f"Error getting table names: {e}")
        return []

def show_table_structure(inspector, table_name):
    """Show detailed structure of a table including columns, constraints, and indexes"""
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name.upper()}")
    print(f"{'='*80}")
    
    # Get columns
    try:
        columns = inspector.get_columns(table_name)
        print(f"\nCOLUMNS ({len(columns)}):")
        print("-" * 50)
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f", DEFAULT: {col['default']}" if col['default'] else ""
            print(f"  • {col['name']} - {col['type']} ({nullable}){default}")
            if col.get('comment'):
                print(f"    Comment: {col['comment']}")
    except Exception as e:
        print(f"Error getting columns for {table_name}: {e}")
    
    # Get primary keys
    try:
        pk_constraint = inspector.get_pk_constraint(table_name)
        if pk_constraint and pk_constraint['constrained_columns']:
            print(f"\nPRIMARY KEY:")
            print("-" * 50)
            print(f"  • Columns: {', '.join(pk_constraint['constrained_columns'])}")
            if pk_constraint.get('name'):
                print(f"  • Constraint name: {pk_constraint['name']}")
    except Exception as e:
        print(f"Error getting primary key for {table_name}: {e}")
    
    # Get foreign keys
    try:
        foreign_keys = inspector.get_foreign_keys(table_name)
        if foreign_keys:
            print(f"\nFOREIGN KEYS ({len(foreign_keys)}):")
            print("-" * 50)
            for fk in foreign_keys:
                print(f"  • {', '.join(fk['constrained_columns'])} → {fk['referred_table']}.{', '.join(fk['referred_columns'])}")
                if fk.get('name'):
                    print(f"    Constraint name: {fk['name']}")
                if fk.get('options'):
                    print(f"    Options: {fk['options']}")
    except Exception as e:
        print(f"Error getting foreign keys for {table_name}: {e}")
    
    # Get unique constraints
    try:
        unique_constraints = inspector.get_unique_constraints(table_name)
        if unique_constraints:
            print(f"\nUNIQUE CONSTRAINTS ({len(unique_constraints)}):")
            print("-" * 50)
            for uc in unique_constraints:
                print(f"  • Columns: {', '.join(uc['column_names'])}")
                if uc.get('name'):
                    print(f"    Constraint name: {uc['name']}")
    except Exception as e:
        print(f"Error getting unique constraints for {table_name}: {e}")
    
    # Get check constraints
    try:
        check_constraints = inspector.get_check_constraints(table_name)
        if check_constraints:
            print(f"\nCHECK CONSTRAINTS ({len(check_constraints)}):")
            print("-" * 50)
            for cc in check_constraints:
                print(f"  • {cc['name']}: {cc['sqltext']}")
    except Exception as e:
        print(f"Error getting check constraints for {table_name}: {e}")
    
    # Get indexes
    try:
        indexes = inspector.get_indexes(table_name)
        if indexes:
            print(f"\nINDEXES ({len(indexes)}):")
            print("-" * 50)
            for idx in indexes:
                unique_text = " (UNIQUE)" if idx.get('unique') else ""
                print(f"  • {idx['name']}: [{', '.join(idx['column_names'])}]{unique_text}")
    except Exception as e:
        print(f"Error getting indexes for {table_name}: {e}")

def show_table_relationships(engine, inspector, all_tables):
    """Show relationships between all tables"""
    print(f"\n{'='*80}")
    print("DATABASE RELATIONSHIPS")
    print(f"{'='*80}")
    
    relationships = []
    
    for table_name in all_tables:
        try:
            foreign_keys = inspector.get_foreign_keys(table_name)
            for fk in foreign_keys:
                relationships.append({
                    'from_table': table_name,
                    'from_columns': fk['constrained_columns'],
                    'to_table': fk['referred_table'],
                    'to_columns': fk['referred_columns'],
                    'constraint_name': fk.get('name', 'unnamed'),
                    'options': fk.get('options', {})
                })
        except Exception as e:
            print(f"Error getting relationships for {table_name}: {e}")
    
    if relationships:
        print(f"\nFOREIGN KEY RELATIONSHIPS ({len(relationships)}):")
        print("-" * 60)
        for rel in relationships:
            from_cols = ', '.join(rel['from_columns'])
            to_cols = ', '.join(rel['to_columns'])
            print(f"  {rel['from_table']}.{from_cols} → {rel['to_table']}.{to_cols}")
            print(f"    Constraint: {rel['constraint_name']}")
            if rel['options']:
                options_str = ', '.join([f"{k}: {v}" for k, v in rel['options'].items()])
                print(f"    Options: {options_str}")
            print()
    else:
        print("\nNo foreign key relationships found.")
    
    # Show table dependency tree
    print(f"\nTABLE DEPENDENCY TREE:")
    print("-" * 40)
    referenced_tables = set()
    referencing_tables = set()
    
    for rel in relationships:
        referenced_tables.add(rel['to_table'])
        referencing_tables.add(rel['from_table'])
    
    independent_tables = set(all_tables) - referencing_tables
    leaf_tables = referencing_tables - referenced_tables
    
    if independent_tables:
        print("📋 Independent Tables (no foreign keys):")
        for table in independent_tables:
            print(f"  • {table}")
    
    if referenced_tables - referencing_tables:
        print("\n🏛️  Parent Tables (referenced by others, no foreign keys):")
        for table in referenced_tables - referencing_tables:
            print(f"  • {table}")
    
    if leaf_tables:
        print("\n🍃 Leaf Tables (have foreign keys, not referenced by others):")
        for table in leaf_tables:
            print(f"  • {table}")
    
    middle_tables = referenced_tables & referencing_tables
    if middle_tables:
        print("\n🔗 Middle Tables (both reference others and are referenced):")
        for table in middle_tables:
            print(f"  • {table}")

def show_sample_data_with_sqlalchemy(engine, all_tables):
    """Show sample data using SQLAlchemy ORM without raw queries"""
    print(f"\n{'='*80}")
    print("SAMPLE DATA FROM TABLES (Using SQLAlchemy ORM)")
    print(f"{'='*80}")
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    metadata = MetaData()
    
    try:
        for table_name in sorted(all_tables):
            print(f"\n--- SAMPLE DATA FROM {table_name.upper()} ---")
            
            try:
                # Reflect the table structure
                table = Table(table_name, metadata, autoload_with=engine)
                
                # Use SQLAlchemy select to get first 3 rows
                from sqlalchemy import select
                stmt = select(table).limit(3)
                result = session.execute(stmt)
                rows = result.fetchall()
                
                if rows:
                    for i, row in enumerate(rows, 1):
                        print(f"Row {i}:")
                        # Get column names from the table object
                        for column in table.columns:
                            col_name = column.name
                            col_value = getattr(row, col_name) if hasattr(row, col_name) else row[col_name]
                            print(f"  {col_name}: {col_value}")
                        print()
                else:
                    print("  (No data found)")
                
                # Clear metadata for next table to avoid conflicts
                metadata.clear()
                
            except Exception as e:
                print(f"Error retrieving data with SQLAlchemy ORM: {e}")
                
                # Fallback: Try using core SQLAlchemy without ORM
                try:
                    metadata_fallback = MetaData()
                    table_fallback = Table(table_name, metadata_fallback, autoload_with=engine)
                    
                    from sqlalchemy import select
                    stmt_fallback = select(table_fallback).limit(3)
                    
                    with engine.connect() as conn:
                        result_fallback = conn.execute(stmt_fallback)
                        rows_fallback = result_fallback.fetchall()
                        
                        if rows_fallback:
                            print("  (Retrieved using SQLAlchemy Core)")
                            for i, row in enumerate(rows_fallback, 1):
                                print(f"Row {i}:")
                                for column in table_fallback.columns:
                                    col_name = column.name
                                    col_value = row[col_name]
                                    print(f"  {col_name}: {col_value}")
                                print()
                        else:
                            print("  (No data found with fallback)")
                    
                    metadata_fallback.clear()
                    
                except Exception as e2:
                    print(f"  Fallback also failed: {e2}")
                    
    except Exception as e:
        print(f"Session error: {e}")
    finally:
        session.close()

def show_database_summary(engine, inspector, all_tables):
    """Show overall database summary"""
    print(f"\n{'='*80}")
    print("DATABASE SUMMARY")
    print(f"{'='*80}")
    
    total_tables = len(all_tables)
    total_columns = 0
    total_indexes = 0
    total_constraints = 0
    
    # Get database size using SQLAlchemy
    metadata = MetaData()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Use SQLAlchemy to get database size
        from sqlalchemy import func
        size_result = session.execute(func.pg_size_pretty(func.pg_database_size(func.current_database()))).scalar()
        print(f"Database Size: {size_result}")
    except:
        print("Database Size: Unable to determine")
    finally:
        session.close()
    
    print(f"Total Tables: {total_tables}")
    
    for table_name in all_tables:
        try:
            columns = inspector.get_columns(table_name)
            total_columns += len(columns)
            
            indexes = inspector.get_indexes(table_name)
            total_indexes += len(indexes)
            
            # Count constraints
            fks = inspector.get_foreign_keys(table_name)
            ucs = inspector.get_unique_constraints(table_name)
            ccs = inspector.get_check_constraints(table_name)
            pk = inspector.get_pk_constraint(table_name)
            
            total_constraints += len(fks) + len(ucs) + len(ccs)
            if pk and pk['constrained_columns']:
                total_constraints += 1
                
        except Exception as e:
            print(f"Error processing {table_name}: {e}")
    
    print(f"Total Columns: {total_columns}")
    print(f"Total Indexes: {total_indexes}")
    print(f"Total Constraints: {total_constraints}")
    
    print(f"\nTables in database:")
    for i, table in enumerate(sorted(all_tables), 1):
        print(f"  {i:2d}. {table}")

def main():
    """Main function to analyze PostgreSQL database structure"""
    print("🔍 PostgreSQL Database Structure Analyzer")
    print("=" * 80)
    
    # Connect to database
    engine = connect_to_database()
    inspector = inspect(engine)
    
    # Get all tables
    all_tables = get_all_tables(inspector)
    
    if not all_tables:
        print("No tables found in the database.")
        return
    
    # Show database summary first
    show_database_summary(engine, inspector, all_tables)
    
    # Show detailed structure for each table
    print(f"\n\n🔍 DETAILED TABLE ANALYSIS")
    for table_name in sorted(all_tables):
        show_table_structure(inspector, table_name)
    
    # Show relationships between tables
    show_table_relationships(engine, inspector, all_tables)
    
    # Show sample data for each table using SQLAlchemy ORM
    show_sample_data_with_sqlalchemy(engine, all_tables)
    
    print(f"\n{'='*80}")
    print("✅ Database analysis completed successfully!")
    print("📊 This script showed:")
    print("   • All tables and their detailed structure")
    print("   • Column definitions with data types and constraints")
    print("   • Primary keys, foreign keys, unique constraints")
    print("   • Check constraints and indexes")
    print("   • Relationships between tables")
    print("   • Database summary statistics")
    print("   • Sample data from each table")
    print("=" * 80)

if __name__ == "__main__":
    main()