import csv
import sys
from datetime import datetime

def escape_sql_string(value):
    """Escape single quotes in string values for SQL"""
    if value is None or value == '':
        return 'NULL'
    # Replace single quotes with escaped single quotes
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"

def convert_value(value, column_name):
    """Convert CSV value to appropriate SQL format"""
    if value is None or value == '' or value.strip() == '':
        return 'NULL'
    
    value = value.strip()
    
    # Handle string fields FIRST
    if column_name in ['Div', 'HomeTeam', 'AwayTeam', 'FTR', 'HTR', 'Time']:
        return escape_sql_string(value)
    
    # Handle numeric fields
    if column_name in ['FTHG', 'FTAG', 'HTHG', 'HTAG', 'HS', 'AS', 'HST', 'AST', 
                       'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR']:
        try:
            return str(int(value))
        except ValueError:
            return 'NULL'
    
    # Handle date field
    if column_name == 'Date':
        try:
            # Parse date in format DD/MM/YYYY
            date_obj = datetime.strptime(value, '%d/%m/%Y')
            return f"'{date_obj.strftime('%Y-%m-%d')}'"
        except ValueError:
            return 'NULL'
    
    # Handle float fields (odds and statistics)
    if any(x in column_name for x in ['>2.5', '<2.5', 'HH', 'HA', 'CH', 'CD', 'CA', 'AHH', 'AHA']):
        try:
            if value == '':
                return 'NULL'
            return str(float(value))
        except ValueError:
            return 'NULL'
    
    # Handle remaining odds columns (B365H, B365D, B365A, etc.) - more specific check
    if any(x in column_name for x in ['365', 'BFD', 'BMGM', 'BV', 'BW', 'CL', 'LB', 'PS', 'Max', 'Avg', 'BFE']):
        try:
            if value == '':
                return 'NULL'
            return str(float(value))
        except ValueError:
            return 'NULL'
    
    # Default: treat as string
    return escape_sql_string(value)

def csv_to_insert_queries(csv_file_path, table_name='matches', batch_size=100):
    """
    Convert CSV file to INSERT SQL queries
    
    Args:
        csv_file_path: Path to the CSV file
        table_name: Name of the table to insert into
        batch_size: Number of rows per INSERT statement
    """
    
    insert_statements = []
    row_buffer = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            original_columns = csv_reader.fieldnames
            
            if not original_columns:
                print("Error: CSV file is empty or invalid", file=sys.stderr)
                return []
            
            # Clean column names for SQL (remove BOM and whitespace)
            clean_columns = [col.strip().replace('\ufeff', '') for col in original_columns]
            
            # Create mapping from original to clean column names
            col_mapping = dict(zip(original_columns, clean_columns))
            
            # Start first INSERT statement
            columns_str = ', '.join([f'`{col}`' for col in clean_columns])
            insert_prefix = f"INSERT INTO `{table_name}` ({columns_str}) VALUES\n"
            
            for row_num, row in enumerate(csv_reader, 1):
                # Convert each value
                values = []
                for orig_col in original_columns:
                    clean_col = col_mapping[orig_col]
                    raw_value = row.get(orig_col, '')
                    value = convert_value(raw_value, clean_col)
                    values.append(value)
                
                # Create value tuple
                row_str = f"({', '.join(values)})"
                row_buffer.append(row_str)
                
                # When buffer reaches batch_size or it's the last row, create INSERT statement
                if len(row_buffer) >= batch_size or row_num % 1000 == 0:
                    insert_stmt = insert_prefix + ',\n'.join(row_buffer) + ';\n'
                    insert_statements.append(insert_stmt)
                    row_buffer = []
                    insert_prefix = f"INSERT INTO `{table_name}` ({columns_str}) VALUES\n"
            
            # Handle remaining rows
            if row_buffer:
                insert_stmt = insert_prefix + ',\n'.join(row_buffer) + ';\n'
                insert_statements.append(insert_stmt)
        
        return insert_statements
    
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error reading CSV file: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return []

def generate_create_table(csv_file_path, table_name='matches'):
    """Generate CREATE TABLE statement based on CSV headers"""
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            original_columns = csv_reader.fieldnames
            
            if not original_columns:
                return None
            
            # Clean column names (remove BOM and whitespace)
            clean_columns = [col.strip().replace('\ufeff', '') for col in original_columns]
            
            # Create mapping
            col_mapping = dict(zip(original_columns, clean_columns))
            
            # Infer column types from first row
            first_row = next(csv_reader)
            
            column_defs = []
            for orig_col in original_columns:
                col_clean = col_mapping[orig_col]
                value = first_row.get(orig_col, '')
                col_type = 'VARCHAR(255)'
                
                # Determine column type
                if col_clean in ['FTHG', 'FTAG', 'HTHG', 'HTAG', 'HS', 'AS', 'HST', 'AST', 
                               'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR']:
                    col_type = 'INT'
                elif col_clean in ['Date']:
                    col_type = 'DATE'
                elif col_clean in ['Time']:
                    col_type = 'VARCHAR(10)'
                elif col_clean in ['FTR', 'HTR', 'Div', 'HomeTeam', 'AwayTeam']:
                    col_type = 'VARCHAR(100)'
                elif any(x in col_clean for x in ['H', 'D', 'A', '>2.5', '<2.5', 'HH', 'HA', 'CH', 'CD', 'CA']):
                    col_type = 'DECIMAL(5,2)'
                else:
                    col_type = 'VARCHAR(100)'
                
                column_defs.append(f"  `{col_clean}` {col_type}")
            
            create_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (\n"
            create_sql += "  id INT AUTO_INCREMENT PRIMARY KEY,\n"
            create_sql += ",\n".join(column_defs)
            create_sql += "\n);"
            
            return create_sql
    
    except Exception as e:
        print(f"Error generating CREATE TABLE: {e}", file=sys.stderr)
        return None


def main():
    # Configuration
    csv_file = r'C:\Users\Chris\Downloads\N1.csv'
    output_file = r'C:\Users\Chris\Documents\GitHub\python-shit\random-small-projects\test\insert_queries.sql'
    table_name = 'matches'
    
    print(f"Converting {csv_file} to INSERT queries...")
    
    # Generate CREATE TABLE statement
    create_table_stmt = generate_create_table(csv_file, table_name)
    
    # Generate INSERT statements
    insert_statements = csv_to_insert_queries(csv_file, table_name, batch_size=500)
    
    if not insert_statements:
        print("No INSERT statements were generated.")
        return
    
    # Write to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- Generated SQL Script\n")
            f.write(f"-- Table: {table_name}\n")
            f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write CREATE TABLE
            if create_table_stmt:
                f.write("-- ==================== CREATE TABLE ====================\n")
                f.write(create_table_stmt)
                f.write("\n\n")
            
            # Write INSERT statements
            f.write("-- ==================== INSERT DATA ====================\n")
            for stmt in insert_statements:
                f.write(stmt)
                f.write("\n")
        
        total_rows = sum(stmt.count('\n') - 2 for stmt in insert_statements)  # Approximate
        print(f"✓ Successfully created CREATE TABLE statement")
        print(f"✓ Successfully created {len(insert_statements)} INSERT statement(s)")
        print(f"✓ Output written to: {output_file}")
        
    except Exception as e:
        print(f"Error writing to output file: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
