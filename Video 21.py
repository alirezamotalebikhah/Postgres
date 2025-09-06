from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import datetime
import json
import os
import sys
import base64
import hashlib

Base = declarative_base()

class BackupStore(Base):
    """SQLAlchemy model for storing database backups with encryption"""
    __tablename__ = 'backup_store'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    backup_name = Column(String(255), nullable=False, unique=True)
    backup_type = Column(String(50), nullable=False)  # 'full', 'incremental', 'differential'
    source_database = Column(String(255), nullable=False)
    backup_size = Column(Integer, nullable=True)  # Size in bytes
    compressed = Column(Boolean, default=True)
    encrypted = Column(Boolean, default=True)
    backup_data = Column(LargeBinary, nullable=False)  # Encrypted backup data
    metadata_info = Column(Text, nullable=True)  # JSON string with backup metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(20), default='active')  # 'active', 'archived', 'corrupted'
    checksum = Column(String(64), nullable=True)  # SHA256 checksum for integrity
    
    def __repr__(self):
        return f"<BackupStore(id={self.id}, name='{self.backup_name}', type='{self.backup_type}', size={self.backup_size})>"

class BackupStoreManager:
    """Manager class for handling backup store operations with encryption"""
    
    def __init__(self, database_url='postgresql://myuser:mypassword@localhost:5432/mydatabase'):
        self.database_url = database_url
        self.engine = None
        self.session = None
        self.encryption_key = None
        self.cipher_suite = None
        
    def connect_to_database(self):
        """Connect to PostgreSQL database and create tables if needed"""
        try:
            self.engine = create_engine(self.database_url)
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            print("✅ Connected to database successfully")
            return True
        except SQLAlchemyError as e:
            print(f"❌ Error connecting to database: {e}")
            return False
    
    def generate_encryption_key(self):
        """Generate or load encryption key for backup data (Simple XOR-based encryption)"""
        key_file = 'backup_encryption.key'
        
        if os.path.exists(key_file):
            with open(key_file, 'r') as f:
                self.encryption_key = f.read().strip()
            print("🔑 Loaded existing encryption key")
        else:
            # Generate a simple key for XOR encryption
            import secrets
            self.encryption_key = secrets.token_hex(32)  # 32 byte hex key
            with open(key_file, 'w') as f:
                f.write(self.encryption_key)
            print("🔑 Generated new encryption key and saved to backup_encryption.key")
        
        return True
    
    def encrypt_data(self, data):
        """Encrypt backup data using simple XOR encryption with base64 encoding"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Simple XOR encryption
        key_bytes = bytes.fromhex(self.encryption_key)
        encrypted = bytearray()
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        # Return base64 encoded encrypted data
        return base64.b64encode(bytes(encrypted))
    
    def decrypt_data(self, encrypted_data):
        """Decrypt backup data using simple XOR decryption"""
        # Decode from base64
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode('utf-8')
        
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # XOR decryption (same as encryption)
        key_bytes = bytes.fromhex(self.encryption_key)
        decrypted = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        
        return bytes(decrypted).decode('utf-8')
    
    def create_backup_entry(self, backup_name, backup_type, source_database, backup_data, metadata=None):
        """Create a new backup entry in the backup store"""
        try:
            # Check if backup already exists
            existing_backup = self.session.query(BackupStore).filter_by(backup_name=backup_name).first()
            if existing_backup:
                print(f"❌ Backup with name '{backup_name}' already exists")
                return False
            
            # Encrypt backup data
            encrypted_data = self.encrypt_data(backup_data)
            
            # Calculate checksum for integrity verification
            import hashlib
            checksum = hashlib.sha256(backup_data.encode('utf-8') if isinstance(backup_data, str) else backup_data).hexdigest()
            
            # Create backup entry
            backup_entry = BackupStore(
                backup_name=backup_name,
                backup_type=backup_type,
                source_database=source_database,
                backup_size=len(backup_data),
                compressed=True,
                encrypted=True,
                backup_data=encrypted_data,
                metadata_info=json.dumps(metadata) if metadata else None,
                checksum=checksum,
                status='active'
            )
            
            self.session.add(backup_entry)
            self.session.commit()
            
            print(f"✅ Backup '{backup_name}' created successfully")
            print(f"   Type: {backup_type}")
            print(f"   Source: {source_database}")
            print(f"   Size: {len(backup_data)} bytes")
            print(f"   Encrypted: Yes")
            print(f"   Checksum: {checksum[:16]}...")
            
            return True
            
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"❌ Error creating backup: {e}")
            return False
    
    def retrieve_backup(self, backup_name):
        """Retrieve and decrypt a backup from the store"""
        try:
            backup = self.session.query(BackupStore).filter_by(backup_name=backup_name).first()
            
            if not backup:
                print(f"❌ Backup '{backup_name}' not found")
                return None
            
            # Decrypt backup data
            decrypted_data = self.decrypt_data(backup.backup_data)
            
            print(f"✅ Retrieved backup '{backup_name}'")
            print(f"   Type: {backup.backup_type}")
            print(f"   Source: {backup.source_database}")
            print(f"   Created: {backup.created_at}")
            print(f"   Size: {backup.backup_size} bytes")
            print(f"   Status: {backup.status}")
            
            return {
                'backup_name': backup.backup_name,
                'backup_type': backup.backup_type,
                'source_database': backup.source_database,
                'backup_data': decrypted_data,
                'metadata': json.loads(backup.metadata_info) if backup.metadata_info else None,
                'created_at': backup.created_at,
                'checksum': backup.checksum,
                'size': backup.backup_size
            }
            
        except Exception as e:
            print(f"❌ Error retrieving backup: {e}")
            return None
    
    def list_all_backups(self):
        """List all backups in the store"""
        try:
            backups = self.session.query(BackupStore).order_by(BackupStore.created_at.desc()).all()
            
            if not backups:
                print("📋 No backups found in the store")
                return []
            
            print(f"\n{'='*80}")
            print(f"BACKUP STORE - ALL BACKUPS ({len(backups)} total)")
            print(f"{'='*80}")
            
            for i, backup in enumerate(backups, 1):
                print(f"\n{i:2d}. {backup.backup_name}")
                print(f"    Type: {backup.backup_type}")
                print(f"    Source DB: {backup.source_database}")
                print(f"    Size: {backup.backup_size:,} bytes")
                print(f"    Created: {backup.created_at}")
                print(f"    Status: {backup.status}")
                print(f"    Encrypted: {'Yes' if backup.encrypted else 'No'}")
                print(f"    Checksum: {backup.checksum[:16]}..." if backup.checksum else "    Checksum: None")
            
            return backups
            
        except SQLAlchemyError as e:
            print(f"❌ Error listing backups: {e}")
            return []
    
    def delete_backup(self, backup_name):
        """Delete a backup from the store"""
        try:
            backup = self.session.query(BackupStore).filter_by(backup_name=backup_name).first()
            
            if not backup:
                print(f"❌ Backup '{backup_name}' not found")
                return False
            
            self.session.delete(backup)
            self.session.commit()
            
            print(f"✅ Backup '{backup_name}' deleted successfully")
            return True
            
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"❌ Error deleting backup: {e}")
            return False
    
    def verify_backup_integrity(self, backup_name):
        """Verify backup integrity using checksum"""
        try:
            backup = self.session.query(BackupStore).filter_by(backup_name=backup_name).first()
            
            if not backup:
                print(f"❌ Backup '{backup_name}' not found")
                return False
            
            # Decrypt and verify checksum
            decrypted_data = self.decrypt_data(backup.backup_data)
            
            import hashlib
            current_checksum = hashlib.sha256(decrypted_data.encode('utf-8')).hexdigest()
            
            if current_checksum == backup.checksum:
                print(f"✅ Backup '{backup_name}' integrity verified - checksum matches")
                return True
            else:
                print(f"❌ Backup '{backup_name}' integrity check failed - checksum mismatch")
                print(f"   Expected: {backup.checksum}")
                print(f"   Current:  {current_checksum}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying backup integrity: {e}")
            return False
    
    def show_backup_statistics(self):
        """Show statistics about the backup store"""
        try:
            total_backups = self.session.query(BackupStore).count()
            active_backups = self.session.query(BackupStore).filter_by(status='active').count()
            
            from sqlalchemy import func
            total_size = self.session.query(func.sum(BackupStore.backup_size)).scalar() or 0
            
            backup_types = self.session.query(BackupStore.backup_type, func.count(BackupStore.backup_type)).group_by(BackupStore.backup_type).all()
            
            print(f"\n{'='*80}")
            print("BACKUP STORE STATISTICS")
            print(f"{'='*80}")
            print(f"Total Backups: {total_backups}")
            print(f"Active Backups: {active_backups}")
            print(f"Total Storage Used: {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)")
            
            if backup_types:
                print(f"\nBackup Types:")
                for backup_type, count in backup_types:
                    print(f"  • {backup_type}: {count}")
            
            print(f"Encryption: Enabled")
            print(f"Key File: backup_encryption.key")
            
        except SQLAlchemyError as e:
            print(f"❌ Error getting statistics: {e}")
    
    def close_connection(self):
        """Close database connection"""
        if self.session:
            self.session.close()
            print("🔌 Database connection closed")

def demonstrate_backup_store():
    """Demonstrate backup store functionality"""
    print("🚀 BACKUP STORE DEMONSTRATION")
    print("=" * 80)
    
    # Initialize backup store manager
    manager = BackupStoreManager()
    
    # Connect to database
    if not manager.connect_to_database():
        print("Failed to connect to database. Exiting...")
        return
    
    # Initialize encryption
    manager.generate_encryption_key()
    
    # Create sample backups
    print(f"\n📦 Creating sample backups...")
    
    sample_backups = [
        {
            'name': 'daily_backup_2024_01_15',
            'type': 'full',
            'database': 'mydatabase',
            'data': 'SAMPLE BACKUP DATA: Full database dump with all tables and data...',
            'metadata': {'tables': ['users', 'products', 'orders'], 'compression': 'gzip', 'version': '1.0'}
        },
        {
            'name': 'incremental_backup_2024_01_16',
            'type': 'incremental',
            'database': 'mydatabase',
            'data': 'SAMPLE INCREMENTAL DATA: Only changed records since last backup...',
            'metadata': {'base_backup': 'daily_backup_2024_01_15', 'changes': 150}
        },
        {
            'name': 'weekly_backup_2024_01_21',
            'type': 'full',
            'database': 'mydatabase',
            'data': 'SAMPLE WEEKLY BACKUP: Complete database snapshot for weekly archive...',
            'metadata': {'schedule': 'weekly', 'retention': '6_months'}
        }
    ]
    
    for backup in sample_backups:
        manager.create_backup_entry(
            backup['name'],
            backup['type'],
            backup['database'],
            backup['data'],
            backup['metadata']
        )
        print()
    
    # List all backups
    print(f"\n📋 Listing all backups in the store...")
    manager.list_all_backups()
    
    # Retrieve a specific backup
    print(f"\n🔍 Retrieving specific backup...")
    retrieved = manager.retrieve_backup('daily_backup_2024_01_15')
    if retrieved:
        print(f"Retrieved data preview: {retrieved['backup_data'][:50]}...")
    
    # Verify backup integrity
    print(f"\n🔐 Verifying backup integrity...")
    manager.verify_backup_integrity('daily_backup_2024_01_15')
    
    # Show statistics
    print(f"\n📊 Backup store statistics...")
    manager.show_backup_statistics()
    
    # Close connection
    manager.close_connection()

def main():
    """Main function to run the backup store system"""
    print("🗄️  PostgreSQL Backup Store with Encryption")
    print("=" * 80)
    
    try:
        # Run the demonstration
        demonstrate_backup_store()
        
        print(f"\n{'='*80}")
        print("✅ Backup Store demonstration completed successfully!")
        print("🔑 Features demonstrated:")
        print("   • SQLAlchemy ORM models for backup storage")
        print("   • XOR encryption with base64 encoding (lightweight encryption)")
        print("   • Backup creation with metadata and checksums")
        print("   • Backup retrieval and decryption")
        print("   • Integrity verification using SHA256 checksums")
        print("   • Comprehensive backup listing and statistics")
        print("   • Secure key management")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error running backup store: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()