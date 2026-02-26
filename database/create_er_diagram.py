import sqlite3
import os

def create_er_diagram():
    conn = sqlite3.connect('shoe_store.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    er_content = "@startuml\n\n"
    er_content += "!define Table(name,desc) class name as \"desc\" << (T,#FFAAAA) >>\n\n"
    
    for table in tables:
        table_name = table[0]
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fks = cursor.fetchall()
        
        er_content += f"Table({table_name}, \"{table_name}\") {{\n"
        
        pk_columns = []
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            is_pk = col[5] == 1
            
            if is_pk:
                pk_columns.append(col_name)
                er_content += f"  # {col_name} : {col_type}\n"
            else:
                is_fk = False
                for fk in fks:
                    if fk[3] == col_name:
                        is_fk = True
                        er_content += f"  + {col_name} : {col_type}\n"
                        break
                
                if not is_fk:
                    er_content += f"  {col_name} : {col_type}\n"
        
        er_content += "}\n\n"
    
    for table in tables:
        table_name = table[0]
        
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fks = cursor.fetchall()
        
        for fk in fks:
            from_col = fk[3]
            to_table = fk[2]
            to_col = fk[4]
            
            er_content += f"{table_name}o--||{to_table}\n"
    
    er_content += "\n@enduml"
    
    with open('database/er_diagram.puml', 'w', encoding='utf-8') as f:
        f.write(er_content)
    
    print("ER-диаграмма создана в формате PlantUML")
    print("Для создания PDF используйте PlantUML онлайн или локально")

if __name__ == "__main__":
    create_er_diagram()
