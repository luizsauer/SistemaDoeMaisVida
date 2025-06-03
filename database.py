import mysql.connector
from mysql.connector import errorcode
import time
import streamlit as st

def get_db_connection(max_retries=3, retry_delay=2):
    """
    Tenta estabelecer conexão com o banco de dados com retry automático
    """
    for attempt in range(max_retries):
        try:
            conn = mysql.connector.connect(    
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"]
            )
            return conn
        except mysql.connector.Error as err:
            if err.errno == errorcode.CR_CONN_HOST_ERROR:
                print(f"Tentativa {attempt + 1} falhou - Host inacessível")
            elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Erro de acesso - Verifique usuário/senha")
                break  # Não adianta tentar novamente
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Banco de dados não existe")
                break
            else:
                print(f"Erro de conexão: {err}")
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    return None