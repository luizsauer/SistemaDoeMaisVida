import mysql.connector

DB_CONFIG = {
    'host': '193.203.175.194',
    'port': 3306,
    'database': 'u267182948_doeMais',  # Certifique-se que é exatamente este nome
    'user': 'u267182948_doeMaisVida',
    'password': 'doeMa1sVida,',
    'connect_timeout': 10
}

def test_final_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Teste 1: Verificar se pode acessar o banco
        cursor.execute("SELECT DATABASE()")
        print(f"✅ Conectado ao banco: {cursor.fetchone()[0]}")
        
        # Teste 2: Verificar tabelas
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"Tabelas disponíveis: {', '.join(tables)}")
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Erro: {err}")
        if err.errno == 1044:  # ER_DBACCESS_DENIED_ERROR
            print("\n🔴 ATENÇÃO: O usuário não tem acesso ao banco especificado")
            print("Verifique:")
            print(f"- O nome do banco está exatamente como nas permissões? (Atual: {DB_CONFIG['database']})")
            print("- As permissões foram concedidas para o host correto (%)")
        return False

if __name__ == "__main__":
    print("=== Teste Final de Conexão ===")
    if test_final_connection():
        print("\n🎉 Conexão funcionando corretamente!")
    else:
        print("\n⚠️  Execute como administrador no MySQL:")
        print(f"GRANT ALL ON {DB_CONFIG['database']}.* TO '{DB_CONFIG['user']}'@'%';")
        print("FLUSH PRIVILEGES;")