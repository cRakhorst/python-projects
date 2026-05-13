import csv
import sys
from datetime import datetime

def escape_sql_string(value):
    """Escape single quotes in string values for SQL"""
    if value is None or value == '':
        return 'NULL'
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
            date_obj = datetime.strptime(value, '%d/%m/%Y')
            return f"'{date_obj.strftime('%Y-%m-%d')}'"
        except ValueError:
            return 'NULL'
    
    # Default: treat as string
    return escape_sql_string(value)

def csv_to_database(csv_file_path, output_sql_path):
    """
    Convert CSV to minimal SQL with only essential match columns
    """
    
    # Columns we want to keep
    keep_columns = ['Div', 'Date', 'Time', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 
                    'HTHG', 'HTAG', 'HTR', 'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 
                    'HY', 'AY', 'HR', 'AR']
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            original_columns = csv_reader.fieldnames
            
            if not original_columns:
                print("Error: CSV file is empty", file=sys.stderr)
                return
            
            # Filter to only keep desired columns
            filtered_columns = [col for col in original_columns if col.strip().replace('\ufeff', '') in keep_columns]
            
            with open(output_sql_path, 'w', encoding='utf-8') as sqlfile:
                # Write header
                sqlfile.write("-- ==================== MINIMAL MATCH DATA ====================\n")
                sqlfile.write("-- Generated from N1.csv\n")
                sqlfile.write(f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Create table
                sqlfile.write("CREATE TABLE IF NOT EXISTS `matches_minimal` (\n")
                sqlfile.write("  id INT AUTO_INCREMENT PRIMARY KEY,\n")
                
                column_defs = []
                for col in filtered_columns:
                    col_clean = col.strip().replace('\ufeff', '')
                    if col_clean in ['FTHG', 'FTAG', 'HTHG', 'HTAG', 'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR']:
                        col_type = 'INT'
                    elif col_clean == 'Date':
                        col_type = 'DATE'
                    elif col_clean == 'Time':
                        col_type = 'VARCHAR(10)'
                    elif col_clean in ['FTR', 'HTR']:
                        col_type = 'VARCHAR(5)'
                    else:
                        col_type = 'VARCHAR(100)'
                    
                    column_defs.append(f"  `{col_clean}` {col_type}")
                
                sqlfile.write(",\n".join(column_defs))
                sqlfile.write("\n);\n\n")
                
                # Read and write data as INSERT
                sqlfile.write("-- ==================== INSERT DATA ====================\n")
                columns_str = ', '.join([f'`{col.strip().replace(chr(65279), "")}`' for col in filtered_columns])
                
                rows = []
                for row in csv_reader:
                    values = []
                    for col in filtered_columns:
                        col_clean = col.strip().replace('\ufeff', '')
                        raw_value = row.get(col, '')
                        value = convert_value(raw_value, col_clean)
                        values.append(value)
                    
                    row_str = f"({', '.join(values)})"
                    rows.append(row_str)
                
                # Write all rows in one INSERT statement
                if rows:
                    sqlfile.write(f"INSERT INTO `matches_minimal` ({columns_str}) VALUES\n")
                    sqlfile.write(",\n".join(rows))
                    sqlfile.write(";\n")
        
        print(f"✓ Successfully created minimal SQL file")
        print(f"✓ Columns kept: {len(filtered_columns)} out of {len(original_columns)}")
        print(f"✓ Output written to: {output_sql_path}")
        
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    csv_path = r'C:\Users\Chris\Downloads\N1.csv'
    sql_path = r'C:\Users\Chris\Documents\GitHub\python-shit\random-small-projects\test\matches_minimal.sql'
    csv_to_database(csv_path, sql_path)
