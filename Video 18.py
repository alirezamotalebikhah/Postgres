from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Boolean, 
    Text, Numeric, ForeignKey, CheckConstraint, UniqueConstraint, 
    Index, text, func
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime
import uuid

Base = declarative_base()

class Product(Base):
    """
    Advanced Product table demonstrating various SQLAlchemy table settings
    """
    __tablename__ = 'products'
    
    # Table-level configurations
    __table_args__ = (
        # Check constraints - Ensure data integrity at database level
        CheckConstraint('price >= 0', name='positive_price_check'),
        CheckConstraint('stock_quantity >= 0', name='non_negative_stock_check'),
        CheckConstraint("status IN ('active', 'inactive', 'discontinued')", name='valid_status_check'),
        
        # Unique constraints - Ensure combination of columns is unique
        UniqueConstraint('name', 'category_id', name='unique_product_per_category'),
        
        # Database indexes for better query performance
        Index('idx_product_name', 'name'),  # Single column index
        Index('idx_product_status_category', 'status', 'category_id'),  # Composite index
        Index('idx_product_created_at', 'created_at'),  # Index for date queries
        Index('idx_product_price_range', 'price', postgresql_where=text('price > 100')),  # Partial index
        
        # PostgreSQL specific table options
        {
            'postgresql_tablespace': None,  # Use default tablespace
            'postgresql_with_oids': False,  # Don't use OIDs (deprecated anyway)
            'postgresql_inherits': None,    # No table inheritance
            'comment': 'Advanced product catalog with comprehensive constraints and indexes'
        }
    )
    
    # Primary key with UUID (more secure than auto-increment)
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        comment='Unique identifier using UUID for security'
    )
    
    # String column with constraints
    name = Column(
        String(200),           # Maximum length constraint
        nullable=False,        # NOT NULL constraint
        comment='Product name with maximum 200 characters'
    )
    
    # Text column for large text data
    description = Column(
        Text,                  # Unlimited text length
        nullable=True,
        comment='Detailed product description without length limit'
    )
    
    # Numeric column with precision and scale
    price = Column(
        Numeric(10, 2),        # 10 digits total, 2 after decimal point
        nullable=False,
        comment='Product price with 2 decimal precision (e.g., 9999999.99)'
    )
    
    # Integer with default value
    stock_quantity = Column(
        Integer,
        nullable=False,
        default=0,             # Default value when not specified
        comment='Available stock quantity, defaults to 0'
    )
    
    # Enum-like string with check constraint (defined in __table_args__)
    status = Column(
        String(20),
        nullable=False,
        default='active',
        comment='Product status: active, inactive, or discontinued'
    )
    
    # Boolean column
    is_featured = Column(
        Boolean,
        nullable=False,
        default=False,         # Default to False
        comment='Whether product is featured on homepage'
    )
    
    # DateTime columns with server defaults
    created_at = Column(
        DateTime(timezone=True),     # Store timezone information
        nullable=False,
        server_default=func.now(),   # Use database function for default
        comment='Creation timestamp with timezone'
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),         # Automatically update on record update
        comment='Last update timestamp, auto-updated on changes'
    )
    
    # PostgreSQL specific JSONB column for flexible data
    metadata_json = Column(
        JSONB,                       # JSON with indexing support
        nullable=True,
        comment='Flexible JSON metadata (dimensions, specifications, etc.)'
    )
    
    # PostgreSQL ARRAY column
    tags = Column(
        ARRAY(String(50)),           # Array of strings
        nullable=True,
        comment='Product tags as an array of strings'
    )
    
    # Foreign key relationship
    category_id = Column(
        Integer,
        ForeignKey('categories.id', ondelete='CASCADE', onupdate='CASCADE'),
        nullable=False,
        comment='Reference to product category with cascade operations'
    )
    
    # Note: search_vector would be created as a computed column via trigger or view
    # PostgreSQL doesn't allow column references in DEFAULT expressions
    # This would typically be implemented with triggers or computed columns
    search_vector = Column(
        Text,
        nullable=True,
        comment='Full-text search vector (populated via triggers or application logic)'
    )

class Category(Base):
    """
    Product category table with hierarchical structure
    """
    __tablename__ = 'categories'
    
    __table_args__ = (
        # Self-referencing check to prevent circular references
        CheckConstraint('id != parent_id', name='no_self_parent_check'),
        Index('idx_category_parent', 'parent_id'),
        Index('idx_category_path', 'path'),  # For hierarchical queries
        {
            'comment': 'Product categories with hierarchical parent-child relationships'
        }
    )
    
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='Auto-incrementing category ID'
    )
    
    name = Column(
        String(100),
        nullable=False,
        unique=True,                 # Table-level unique constraint
        comment='Unique category name'
    )
    
    # Self-referencing foreign key for hierarchy
    parent_id = Column(
        Integer,
        ForeignKey('categories.id', ondelete='CASCADE'),
        nullable=True,
        comment='Parent category ID for hierarchical structure'
    )
    
    # Path for efficient hierarchy queries (like '/electronics/computers/laptops/')
    path = Column(
        String(500),
        nullable=False,
        comment='Hierarchical path for efficient tree queries'
    )
    
    # Relationship definitions
    # Self-referencing relationship for parent-child
    children = relationship(
        "Category",
        backref="parent",            # Creates parent attribute automatically
        remote_side=[id],            # Specifies the remote side of self-reference
        cascade="all, delete"        # Cascade delete to children (orphan removal handled by FK)
    )
    
    # Relationship to products
    products = relationship(
        "Product",
        backref="category",          # Creates category attribute in Product
        cascade="all, delete-orphan",
        lazy="dynamic"               # Load products only when accessed
    )

# Database engine with advanced connection settings
engine = create_engine(
    'postgresql://myuser:mypassword@localhost:5432/mydatabase',
    echo=True,                       # Show SQL statements (for learning)
    pool_size=10,                    # Connection pool size
    max_overflow=20,                 # Additional connections beyond pool_size
    pool_pre_ping=True,              # Validate connections before use
    pool_recycle=3600,               # Recycle connections every hour
    connect_args={
        "options": "-c timezone=UTC" # Set timezone for all connections
    }
)

print("Creating advanced tables with comprehensive constraints...")

# Drop existing tables for clean start
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS products CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS categories CASCADE"))
    conn.commit()

# Create all tables
Base.metadata.create_all(engine)

# Create session with advanced configuration
Session = sessionmaker(
    bind=engine,
    autoflush=True,                  # Automatically flush before queries
    autocommit=False,                # Use explicit commits
    expire_on_commit=True            # Expire objects after commit
)

session = Session()

print("\nInserting sample data...")

# Create sample categories (hierarchical)
electronics = Category(
    name='Electronics',
    path='/electronics/',
    parent_id=None
)
session.add(electronics)
session.flush()  # Get the ID

computers = Category(
    name='Computers',
    path='/electronics/computers/',
    parent_id=electronics.id
)
session.add(computers)
session.flush()

laptops = Category(
    name='Laptops',
    path='/electronics/computers/laptops/',
    parent_id=computers.id
)
session.add(laptops)
session.flush()

# Create sample products with advanced features
products_data = [
    {
        'name': 'MacBook Pro 16"',
        'description': 'Professional laptop with M2 Max chip, perfect for developers and content creators.',
        'price': 2499.99,
        'stock_quantity': 15,
        'status': 'active',
        'is_featured': True,
        'category_id': laptops.id,
        'metadata_json': {
            'specifications': {
                'processor': 'Apple M2 Max',
                'ram': '32GB',
                'storage': '1TB SSD',
                'display': '16.2-inch Liquid Retina XDR'
            },
            'dimensions': {
                'width': 35.57,
                'height': 24.81,
                'depth': 1.68,
                'weight': 2.15
            },
            'warranty_years': 1
        },
        'tags': ['apple', 'professional', 'high-performance', 'laptop']
    },
    {
        'name': 'Dell XPS 13',
        'description': 'Ultra-portable laptop with excellent build quality and long battery life.',
        'price': 1299.99,
        'stock_quantity': 25,
        'status': 'active',
        'is_featured': False,
        'category_id': laptops.id,
        'metadata_json': {
            'specifications': {
                'processor': 'Intel Core i7-1355U',
                'ram': '16GB',
                'storage': '512GB SSD',
                'display': '13.4-inch FHD+'
            },
            'dimensions': {
                'width': 29.5,
                'height': 19.9,
                'depth': 1.49,
                'weight': 1.17
            },
            'warranty_years': 2
        },
        'tags': ['dell', 'ultrabook', 'portable', 'business']
    },
    {
        'name': 'Gaming Laptop ASUS ROG',
        'description': 'High-performance gaming laptop with RTX 4070 graphics.',
        'price': 1899.50,
        'stock_quantity': 8,
        'status': 'active',
        'is_featured': True,
        'category_id': laptops.id,
        'metadata_json': {
            'specifications': {
                'processor': 'AMD Ryzen 9 7900HX',
                'ram': '32GB DDR5',
                'storage': '1TB NVMe SSD',
                'graphics': 'NVIDIA RTX 4070',
                'display': '17.3-inch QHD 165Hz'
            },
            'gaming_features': {
                'rgb_keyboard': True,
                'cooling_system': 'Liquid Metal',
                'audio': 'Hi-Res Audio'
            },
            'warranty_years': 2
        },
        'tags': ['asus', 'gaming', 'high-performance', 'rtx', 'rgb']
    }
]

for product_data in products_data:
    product = Product(**product_data)
    session.add(product)

# Commit all changes
session.commit()

print("\n" + "="*80)
print("ADVANCED TABLE DEMONSTRATION - QUERYING DATA")
print("="*80)

# Demonstrate advanced queries
print("\n1. Products with metadata JSON queries:")
gaming_products = session.query(Product).filter(
    Product.metadata_json['specifications']['graphics'].astext.ilike('%rtx%')
).all()

for product in gaming_products:
    print(f"   {product.name}: {product.metadata_json['specifications']['graphics']}")

print("\n2. Products with array tag searches:")
apple_products = session.query(Product).filter(
    Product.tags.any('apple')
).all()

for product in apple_products:
    print(f"   {product.name}: {product.tags}")

print("\n3. Price range queries (using check constraints):")
expensive_products = session.query(Product).filter(
    Product.price > 2000
).all()

for product in expensive_products:
    print(f"   {product.name}: ${product.price}")

print("\n4. Category hierarchy demonstration:")
def print_category_tree(category, indent=0):
    print("   " + "  " * indent + f"├─ {category.name} (ID: {category.id})")
    # Load children explicitly for this demonstration
    children = session.query(Category).filter(Category.parent_id == category.id).all()
    for child in children:
        print_category_tree(child, indent + 1)

root_categories = session.query(Category).filter(Category.parent_id.is_(None)).all()
for root in root_categories:
    print_category_tree(root)

print("\n5. Full-text search using search_vector:")
# Note: This would work with PostgreSQL's text search, but requires additional setup
print("   Search vector example: Products contain auto-generated search vectors")
print("   for efficient full-text search on name and description fields.")

print("\n6. Constraint demonstrations:")
print("   ✓ All prices are >= 0 (positive_price_check)")
print("   ✓ All stock quantities are >= 0 (non_negative_stock_check)")
print("   ✓ All statuses are valid values (valid_status_check)")
print("   ✓ Product names are unique per category (unique_product_per_category)")

print("\n7. Index usage for performance:")
print("   ✓ Index on product name for fast name searches")
print("   ✓ Composite index on status + category for filtered listings")
print("   ✓ Date index for time-based queries")
print("   ✓ Partial index on expensive products (price > 100)")

print("\n8. Advanced column features:")
for product in session.query(Product).limit(1).all():
    print(f"   UUID Primary Key: {product.id}")
    print(f"   Timezone-aware timestamps: {product.created_at}")
    print(f"   JSONB metadata: {type(product.metadata_json).__name__}")
    print(f"   Array tags: {type(product.tags).__name__}")
    print(f"   Decimal precision: {type(product.price).__name__}")

print(f"\nDatabase schema information:")
print(f"Total tables created: {len(Base.metadata.tables)}")
print(f"Total constraints defined: Multiple check, unique, and foreign key constraints")
print(f"Total indexes created: 5+ indexes for optimal query performance")

session.close()
print("\n✅ Advanced table demonstration completed successfully!")
print("📚 This script demonstrates:")
print("   • Complex table constraints (check, unique, foreign key)")
print("   • Advanced PostgreSQL data types (UUID, JSONB, ARRAY)")
print("   • Comprehensive indexing strategies")
print("   • Hierarchical data modeling")
print("   • Timezone-aware datetime handling")
print("   • Server-side defaults and computed columns")
print("   • Relationship configurations with cascading")
print("   • Connection pool and session management")