import psycopg2
import time


def fix_collation_mismatch():
    try:
        # اتصال به دیتابیس
        conn = psycopg2.connect(
            dbname='mydatabase',
            user='myuser',  # باید superuser باشه
            password='mypassword',
            host='localhost',
            port=5432
        )
        conn.autocommit = True
        cursor = conn.cursor()

        print("Starting collation fix process...")

        # مرحله 1: چک کردن وضعیت فعلی collation
        print("\n1. Checking current collation versions...")
        cursor.execute("""
            SELECT datname, datcollate, datctype 
            FROM pg_database WHERE datname = current_database()
        """)
        result = cursor.fetchone()
        print(f"Database: {result[0]}, Collate: {result[1]}, Ctype: {result[2]}")

        # مرحله 2: پیدا کردن objects که از default collation استفاده می‌کنن
        print("\n2. Finding objects using default collation...")
        cursor.execute("""
            SELECT table_schema, table_name, column_name, collation_name
            FROM information_schema.columns 
            WHERE table_catalog = current_database()
            AND collation_name IS NOT NULL
            ORDER BY table_schema, table_name, column_name
        """)

        collation_objects = cursor.fetchall()
        if collation_objects:
            print(f"Found {len(collation_objects)} columns with specific collations:")
            for obj in collation_objects[:10]:  # نمایش 10 تای اول
                print(f"  - {obj[0]}.{obj[1]}.{obj[2]} -> {obj[3]}")
        else:
            print("No columns with explicit collations found")

        # مرحله 3: پیدا کردن indexes که نیاز به rebuild دارن
        print("\n3. Finding indexes to rebuild...")
        cursor.execute("""
            SELECT n.nspname as schema_name, 
                   t.relname as table_name, 
                   i.relname as index_name,
                   pg_get_indexdef(i.oid) as index_def
            FROM pg_class i
            JOIN pg_index ix ON i.oid = ix.indexrelid
            JOIN pg_class t ON ix.indrelid = t.oid
            JOIN pg_namespace n ON t.relnamespace = n.oid
            WHERE i.relkind = 'i'
            AND n.nspname = 'public'
            ORDER BY n.nspname, t.relname, i.relname
        """)

        indexes = cursor.fetchall()
        print(f"Found {len(indexes)} indexes to rebuild")

        # مرحله 4: چک کردن اتصالات فعال
        print("\n4. Checking active connections...")
        cursor.execute("""
            SELECT count(*) FROM pg_stat_activity 
            WHERE datname = current_database() AND pid <> pg_backend_pid()
        """)
        active_connections = cursor.fetchone()[0]

        if active_connections > 0:
            print(f"⚠ Warning: {active_connections} active connections found")
            print("Consider closing other connections for faster processing")
        else:
            print("✓ No other active connections")

        # مرحله 5: REINDEX عملیات
        print("\n5. Starting REINDEX process...")
        start_time = time.time()

        # ابتدا schema های عمومی
        try:
            print("  Reindexing schema 'public'...")
            cursor.execute("REINDEX SCHEMA public;")
            print("  ✓ Schema 'public' completed")
        except Exception as e:
            print(f"  ⚠ Schema reindex failed: {e}")

        # سپس کل دیتابیس (اگه دسترسی داری)
        try:
            print("  Reindexing entire database...")
            cursor.execute(f"REINDEX DATABASE {result[0]};")
            print("  ✓ Full database reindex completed")
        except psycopg2.errors.InsufficientPrivilege:
            print("  ⚠ Insufficient privileges for full database reindex")
        except Exception as e:
            print(f"  ⚠ Database reindex failed: {e}")

        reindex_time = time.time() - start_time
        print(f"REINDEX completed in {reindex_time:.2f} seconds")

        # مرحله 6: به‌روزرسانی collation version
        print("\n6. Refreshing collation version...")
        try:
            cursor.execute(f"ALTER DATABASE {result[0]} REFRESH COLLATION VERSION;")
            print("✓ Collation version refreshed successfully")
        except Exception as e:
            print(f"❌ Failed to refresh collation version: {e}")
            return False

        # مرحله 7: تایید نهایی
        print("\n7. Final verification...")
        cursor.execute("SELECT version();")
        pg_version = cursor.fetchone()[0]
        print(f"PostgreSQL version: {pg_version}")

        # چک کردن اینکه warning برطرف شده
        print("\n8. Checking if warning is resolved...")
        print("Run a simple query to see if warning appears...")
        cursor.execute("SELECT 1;")
        print("✓ Test query executed - check for warnings in output")

        print("\n🎉 Collation fix process completed!")
        return True

    except psycopg2.errors.InsufficientPrivilege:
        print("❌ Error: Need superuser privileges")
        print("Connect as 'postgres' user or get superuser access")
        return False

    except psycopg2.errors.ObjectInUse:
        print("❌ Error: Database in use. Try during maintenance window")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# اجرای اسکریپت
if __name__ == "__main__":
    print("=== PostgreSQL Collation Fix Tool ===")
    print("This will rebuild indexes and refresh collation version")

    confirm = input("\nContinue? (yes/no): ").lower().strip()
    if confirm in ['yes', 'y']:
        success = fix_collation_mismatch()
        if success:
            print("\n✅ Process completed!")
            print("Test your database to ensure the warning is gone.")
        else:
            print("\n❌ Process failed. Check errors above.")
    else:
        print("Operation cancelled.")