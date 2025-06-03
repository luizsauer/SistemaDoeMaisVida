import datetime
import mysql
import streamlit as st
from database import get_db_connection
from utils.db_operations import carregar_conquistas_usuario, obter_agendamentos_usuario
import os
import hashlib
import re

# Caminho absoluto da pasta atual (utils)
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))

# Sobe um nível (vai para doe+vida/)
BASE_DIR = os.path.dirname(UTILS_DIR)
STATIC_DIR = os.path.join(BASE_DIR, 'static')
IMG_DIR = os.path.join(STATIC_DIR, 'img')

def add_vertical_space(space):
    for _ in range(space):
        st.write("\n")
        
def hash_password(password):
    """Cria um hash SHA-256 da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Valida o formato do email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Valida a força da senha"""
    if len(password) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"
    return True, ""

#region pagina login
def pagina_login():
    col1, col2, col3 = st.columns([4, 6, 1])
    with col1:
        logo_path = os.path.join(IMG_DIR, 'logo-.png')  # ajuste o nome conforme necessário
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)
        else:
            st.warning(f"Imagem não encontrada: {logo_path}")
    with col2:
        st.title("Bem-vindo ao Doe+Vida 💉")
        
        st.markdown("""
        **Doe+Vida** é uma plataforma gamificada para incentivar a doação de sangue,
        """)
        st.markdown("""
        conectando doadores a hemocentros de forma fácil e motivadora.
        """)
        
    add_vertical_space(5)
    
    col1, col2, col3 = st.columns([4, 6, 4])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Cadastro"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("E-mail")
                senha = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar")
                
                if submit:
                    if fazer_login(email, senha):
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas")
        
        with tab2:
            with st.form("cadastro_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Informações Básicas")
                    nome = st.text_input("Nome Completo*")
                    email = st.text_input("E-mail*")
                    senha = st.text_input("Senha*", type="password")
                    confirm_senha = st.text_input("Confirmar Senha*", type="password")
                    tipo = st.radio("Tipo de Conta*", ["Doador", "Hemocentro"])
                with col2:
                
                    st.write("Adicionais (Doadores)")
                    tipo_sanguineo = st.selectbox("Tipo Sanguíneo", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    data_nascimento = st.date_input("Data de Nascimento", min_value=datetime.date(1900, 1, 1))
                    cpf = st.text_input("CPF")
                    telefone = st.text_input("Telefone")
                    endereco = st.text_input("Endereço")
                    
                col1, col2 = st.columns([2.1, 3])
                with col2:
                    submit = st.form_submit_button("Cadastrar")
                    if submit:
                        if senha != confirm_senha:
                            st.error("As senhas não coincidem")
                        else:
                            if fazer_cadastro(
                                nome, email, senha, tipo.lower(),
                                tipo_sanguineo if tipo_sanguineo else None,
                                data_nascimento,
                                cpf if cpf else None,
                                telefone if telefone else None,
                                endereco if endereco else None
                            ):
                                st.success("Cadastro realizado com sucesso! Faça login para continuar.")
                    
#region Fazer Cadastro
def fazer_cadastro(nome, email, senha, tipo, tipo_sanguineo=None, data_nascimento=None, cpf=None, telefone=None, endereco=None):
    # Validações
    if not all([nome, email, senha, tipo]):
        st.error("Por favor, preencha todos os campos obrigatórios")
        return False

    if not validate_email(email):
        st.error("Por favor, insira um e-mail válido")
        return False

    is_valid_pwd, pwd_msg = validate_password(senha)
    if not is_valid_pwd:
        st.error(pwd_msg)
        return False

    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            st.error("Erro ao conectar ao banco de dados. Tente novamente mais tarde.")
            return False

        cursor = conn.cursor(dictionary=True)
        
        # Verifica se o email já existe
        cursor.execute("SELECT email FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            st.error("Este e-mail já está cadastrado")
            return False
        
        # Hash da senha
        hashed_password = hash_password(senha)
        
        # Inserção completa
        insert_query = """
        INSERT INTO usuarios 
        (nome, email, senha, tipo, tipo_sanguineo, data_nascimento, cpf, telefone, endereco, data_cadastro) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(insert_query, (
            nome, email, hashed_password, tipo.lower(), 
            tipo_sanguineo, data_nascimento, cpf, telefone, endereco
        ))
        conn.commit()
        
        # Obter o ID do usuário recém-criado
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        user_id = cursor.fetchone()['id']
        
        st.session_state.user = {
            'id': user_id,
            'nome': nome,
            'email': email,
            'tipo': tipo.lower()
        }
        return True
        
    except mysql.connector.Error as err:
        st.error(f"Erro no banco de dados: {err.msg}")
        return False
    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()           

#region Fazer Login
def fazer_login(email, senha):
    """Autentica um usuário"""
    if not email or not senha:
        st.error("Por favor, informe e-mail e senha")
        return False

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Busca usuário pelo email
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                # Verifica a senha (comparando hashes)
                hashed_input = hash_password(senha)
                if hashed_input == user['senha']:
                    st.session_state.user = {
                        'id': user['id'],
                        'nome': user['nome'],
                        'email': user['email'],
                        'tipo': user['tipo'].lower(),
                        'pontos': user['pontos'],
                        'nivel': user['nivel']
                    }
                    
                    # Carrega dados específicos do tipo de usuário
                    if user['tipo'].lower() == 'hemocentro':
                        st.session_state.hemocentro_id = user['id']
                        
                    st.session_state.agendamentos = obter_agendamentos_usuario(user['id'])
                    st.session_state.conquistas = carregar_conquistas_usuario(user['id'])
                    st.session_state.pontos = user['pontos']
                    st.session_state.nivel = user['nivel']
                    return True
                else:
                    st.error("Senha incorreta")
                    return False
            else:
                st.error("E-mail não cadastrado")
                return False
                
        except Exception as e:
            st.error(f"Erro ao fazer login: {str(e)}")
            return False
        finally:
            conn.close()
    else:
        st.error("Erro ao conectar ao banco de dados")
        return False

