import io
import os
import streamlit as st
import pandas as pd
import numpy as np
import datetime
from PIL import Image
import json
import random

from database import get_db_connection
from utils.helpers import mostrar_globulos

# Caminho absoluto da pasta atual (utils)
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))

# Sobe um nível (vai para doe+vida/)
BASE_DIR = os.path.dirname(UTILS_DIR)
STATIC_DIR = os.path.join(BASE_DIR, 'static')
IMG_DIR = os.path.join(STATIC_DIR, 'img')


#region load_data
@st.cache_data
def load_data():
    # Hemocentros fictícios
    hemocentros = pd.DataFrame({
        'Nome': ['Hemocentro Florianópolis', 'Hemocentro Palhoça', 'Hemocentro São José'],
        'Endereço': ['Av. Othon Gama D\'Eça, 756 - Centro', 'Rua João Pereira dos Santos, 100 - Ponte do Imaruim', 'Av. Acioni Souza Filho, 123 - Forquilhas'],
        'Telefone': ['(48) 3333-3333', '(48) 4444-4444', '(48) 5555-5555'],
        'Latitude': [-27.5927, -27.6453, -27.5954],
        'Longitude': [-48.5486, -48.6678, -48.6285],
        'Horário_Funcionamento': ['Seg-Sex: 8h-18h', 'Seg-Sex: 7h-17h', 'Ter-Sab: 8h-19h']
    })
    
    # Conquistas disponíveis
    conquistas = [
        {"nome": "Primeira Doação", "descricao": "Complete sua primeira doação de sangue", "pontos": 50, "icone": "🥇"},
        {"nome": "Doador Frequente", "descricao": "Doar sangue 3 vezes em um ano", "pontos": 150, "icone": "🏆"},
        {"nome": "Herói da Saúde", "descricao": "Doar sangue 5 vezes", "pontos": 300, "icone": "🦸"},
        {"nome": "Compartilhador", "descricao": "Compartilhe uma campanha nas redes sociais", "pontos": 30, "icone": "📢"},
        {"nome": "Quiz Master", "descricao": "Responda corretamente a um quiz sobre doação de sangue", "pontos": 20, "icone": "🧠"}
    ]
    
    return hemocentros, conquistas

hemocentros, conquistas_disponiveis = load_data()


#region agendar_doacao
def agendar_doacao(hemocentro, data, horario):
    agendamento = {
        'hemocentro': hemocentro,
        'data': data,
        'horario': horario,
        'status': 'Agendado'
    }
    st.session_state.agendamentos.append(agendamento)
    
    # Adicionar conquista se for a primeira doação
    if len([a for a in st.session_state.agendamentos if a['status'] == 'Concluído']) == 0:
        adicionar_conquista("Primeira Doação")



#region salvar_agendamento
def salvar_agendamento(usuario_id, hemocentro_id, data, horario):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO agendamentos 
            (usuario_id, hemocentro_id, data_agendamento, horario, status) 
            VALUES (%s, %s, %s, %s, 'Agendado')
            """
            cursor.execute(query, (usuario_id, hemocentro_id, data, horario))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao salvar agendamento: {e}")
            return False
        finally:
            conn.close()
    return False



#regin obter_agendamentos
def obter_agendamentos_usuario(usuario_id, filtro_data=None):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT a.*, h.nome as hemocentro_nome 
            FROM agendamentos a
            JOIN hemocentros h ON a.hemocentro_id = h.id
            WHERE a.usuario_id = %s
            """
            
            params = [usuario_id]
            
            # Adicionar filtro de data se fornecido
            if filtro_data == "passados":
                query += " AND a.data_agendamento < CURDATE()"
            elif filtro_data == "futuros":
                query += " AND a.data_agendamento >= CURDATE()"
            elif filtro_data == "hoje":
                query += " AND a.data_agendamento = CURDATE()"
            elif filtro_data == "semana":
                query += " AND a.data_agendamento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)"
            elif filtro_data == "mes":
                query += " AND a.data_agendamento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)"
            
            query += " ORDER BY a.data_agendamento DESC"
            
            cursor.execute(query, params)
            agendamentos = cursor.fetchall()
            return agendamentos
        except Exception as e:
            print(f"Erro ao obter agendamentos: {e}")
            return []
        finally:
            conn.close()
    return []

def add_vertical_space(space):
    for _ in range(space):
        st.write("\n")

#region Página Agendamento
def pagina_agendamento():
    st.title("Agendar Doação")
    
    hemocentros_db = carregar_hemocentros()  # Carrega do banco
    
    with st.form("agendamento_form"):
        hemocentro_nome = st.selectbox("Hemocentro", [h['nome'] for h in hemocentros_db])
        data = st.date_input("Data", min_value=datetime.date.today())
        horario = st.time_input("Horário", datetime.time(8, 0))
        submit = st.form_submit_button("Agendar")
        
        if submit:
            # Encontra o hemocentro selecionado
            hemocentro = next((h for h in hemocentros_db if h['nome'] == hemocentro_nome), None)
            if hemocentro:
                if salvar_agendamento(st.session_state.user['id'], hemocentro['id'], data, horario):
                    st.success(f"Doação agendada no {hemocentro_nome} para {data.strftime('%d/%m/%Y')} às {horario.strftime('%H:%M')}")
                    st.session_state.agendamentos = obter_agendamentos_usuario(st.session_state.user['id'])
                else:
                    st.error("Erro ao agendar doação")
            else:
                st.error("Hemocentro não encontrado")
    add_vertical_space(5)
    
    col1, col2 = st.columns([2, 1])
    with col2:
        st.image(os.path.join(IMG_DIR, 'gota-.png'), width=100)
    with col1:
        st.subheader("Preparo para Doação")
        st.markdown("""
        - Durma bem na noite anterior
        - Esteja alimentado (evite alimentos gordurosos)
        - Leve documento original com foto
        - Peso mínimo: 50kg
        - Idade entre 16 e 69 anos (menores precisam de autorização)
        """)
    mostrar_globulos()





#region carregar_hemocentros
def carregar_hemocentros():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM hemocentros")
            hemocentros = cursor.fetchall()
            return hemocentros
        except Exception as e:
            print(f"Erro ao carregar hemocentros: {e}")
            return []
        finally:
            conn.close()
    return []

#region Página Hemocentros
def pagina_hemocentros():
    st.title("Hemocentros Próximos")
    
    hemocentros_db = carregar_hemocentros()
    
    # Prepara dados para o mapa
    df = pd.DataFrame(hemocentros_db)
    df = df.rename(columns={
        'latitude': 'lat',
        'longitude': 'lon'
    })
    
    # Converter colunas numéricas para float
    if 'lat' in df.columns and 'lon' in df.columns:
        df['lat'] = df['lat'].astype(float)
        df['lon'] = df['lon'].astype(float)
        st.map(df)
    else:
        st.error("Dados de localização não encontrados")
    
    # Lista de hemocentros
    for hemocentro in hemocentros_db:
        with st.expander(f"{hemocentro['nome']} - {hemocentro['endereco']}"):
            st.write(f"**Telefone:** {hemocentro['telefone']}")
            st.write(f"**Horário de Funcionamento:** {hemocentro['horario_funcionamento']}")
    mostrar_globulos()

#region Página Painel Hemocentro
def pagina_painel_hemocentro():
    st.title("🏥 Painel do Hemocentro")
    
    # Verificação mais robusta do tipo de usuário
    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("Você precisa fazer login para acessar esta página.")
        return
    
    # Verifica se o usuário é um hemocentro
    if st.session_state.user['tipo'].lower() != 'hemocentro':
        st.warning("Acesso restrito a hemocentros cadastrados.")
        return
    
    # Carregar dados do hemocentro associado ao usuário
    hemocentro = carregar_dados_hemocentro(st.session_state.user['id'])
    
    if not hemocentro:
        st.error("""
        Hemocentro não encontrado. 
        Por favor, verifique se seu usuário está corretamente associado a um hemocentro.
        """)
        return
    
    st.subheader(f"Bem-vindo, {hemocentro['nome']}")
    
    # Abas para organização
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Agendamentos", "💉 Estoque de Sangue", "📢 Campanhas", "📊 Estatísticas"])
    
    with tab1:  # Aba de Agendamentos
        st.subheader("Próximos Agendamentos")
        agendamentos = obter_agendamentos_hemocentro(hemocentro)
        
        if agendamentos:
            # Formatar dados para exibição
            df = pd.DataFrame(agendamentos)
            
            # Converter colunas de data/hora
            df['data_agendamento'] = pd.to_datetime(df['data_agendamento']).dt.strftime('%d/%m/%Y')
            df['horario'] = pd.to_datetime(df['horario'], format='%H:%M:%S').dt.strftime('%H:%M')
            
            # Selecionar e renomear colunas
            df = df[['nome_usuario', 'tipo_sanguineo', 'data_agendamento', 'horario', 'status']]
            df = df.rename(columns={
                'nome_usuario': 'Doador',
                'tipo_sanguineo': 'Tipo Sanguíneo',
                'data_agendamento': 'Data',
                'horario': 'Horário',
                'status': 'Status'
            })
            
            # Adicionar filtros
            col1, col2 = st.columns(2)
            with col1:
                filtro_status = st.selectbox(
                    "Filtrar por status",
                    ["Todos"] + list(df['Status'].unique())
                )
            
            with col2:
                filtro_data = st.selectbox(
                    "Filtrar por data",
                    ["Próximos 7 dias", "Próximos 30 dias", "Todos"]
                )
            
            # Aplicar filtros
            if filtro_status != "Todos":
                df = df[df['Status'] == filtro_status]
            
            if filtro_data == "Próximos 7 dias":
                hoje = datetime.date.today()
                df = df[pd.to_datetime(df['Data']) <= (hoje + datetime.timedelta(days=7))]
            elif filtro_data == "Próximos 30 dias":
                hoje = datetime.date.today()
                df = df[pd.to_datetime(df['Data']) <= (hoje + datetime.timedelta(days=30))]
            
            # Estilizar a tabela
            st.dataframe(
                df.style.applymap(
                    lambda x: 'color: green' if x == 'Confirmado' else 
                    ('color: orange' if x == 'Agendado' else 'color: red'),
                    subset=['Status']
                ),
                use_container_width=True,
                height=min(400, 35 * (len(df) + 1)))
            
            # Opções de ação
            st.markdown("**Ações:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🖨️ Exportar para Excel"):
                    exportar_para_excel(df, f"agendamentos_{hemocentro['nome']}.xlsx")
            with col2:
                if st.button("🔄 Atualizar Agendamentos"):
                    st.rerun()
        else:
            st.info("Nenhum agendamento encontrado para este hemocentro.")
    
    with tab2:  # Aba de Estoque de Sangue
        st.subheader("Estoque de Sangue")
        
        # Carregar estoque do banco de dados
        estoque = carregar_estoque_hemocentro(hemocentro)
        
        if not estoque:
            # Se não houver estoque cadastrado, criar um fictício
            tipos_sanguineos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
            estoque = {tipo: random.randint(0, 100) for tipo in tipos_sanguineos}
        
        # Organizar em 4 colunas
        cols = st.columns(4)
        
        for i, (tipo, quantidade) in enumerate(estoque.items()):
            with cols[i % 4]:
                # Definir cor com base na quantidade
                if quantidade < 10:
                    cor = "#FF5252"  # Vermelho - estoque crítico
                elif quantidade < 30:
                    cor = "#FFD740"  # Amarelo - estoque baixo
                else:
                    cor = "#69F0AE"  # Verde - estoque bom
                
                # Mostrar card para cada tipo sanguíneo
                st.markdown(f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 15px; background-color: {cor};">
                    <h3 style="margin: 0;">{tipo}</h3>
                    <p style="font-size: 24px; font-weight: bold; margin: 5px 0;">{quantidade}</p>
                    <p style="margin: 0;">bolsas</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Formulário para atualizar estoque
        with st.expander("Atualizar Estoque"):
            with st.form("estoque_form"):
                st.write("Informe as novas quantidades:")
                
                cols = st.columns(4)
                novo_estoque = {}
                
                for i, tipo in enumerate(estoque.keys()):
                    with cols[i % 4]:
                        novo_estoque[tipo] = st.number_input(
                            f"{tipo}", 
                            min_value=0, 
                            max_value=200, 
                            value=estoque[tipo],
                            key=f"estoque_{tipo}"
                        )
                
                if st.form_submit_button("Salvar Estoque"):
                    if salvar_estoque(hemocentro, novo_estoque):
                        st.success("Estoque atualizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao atualizar estoque.")
    
    with tab3:  # Aba de Campanhas
        st.subheader("Enviar Campanha")
        
        with st.form("campanha_form"):
            titulo = st.text_input("Título da Campanha*", max_chars=100)
            
            col1, col2 = st.columns(2)
            with col1:
                urgencia = st.selectbox(
                    "Nível de Urgência*", 
                    ["Normal", "Urgente", "Emergência"], 
                    help="Define a prioridade da campanha"
                )
            with col2:
                validade = st.date_input(
                    "Validade da Campanha*", 
                    min_value=datetime.date.today(),
                    help="Até quando a campanha deve ser exibida"
                )
            
            mensagem = st.text_area("Mensagem*", height=150)
            imagem = st.file_uploader("Imagem (opcional)", type=["jpg", "png", "jpeg"])
            
            st.markdown("**Campos obrigatórios***")
            
            if st.form_submit_button("📢 Publicar Campanha"):
                if not titulo or not mensagem:
                    st.error("Preencha todos os campos obrigatórios")
                else:
                    # Salvar a campanha no banco de dados
                    if salvar_campanha(hemocentro, titulo, mensagem, urgencia, validade, imagem):
                        st.success("Campanha publicada com sucesso!")
                        # Opcional: enviar notificação para usuários
                        enviar_notificacao_campanha(hemocentro, titulo)
                    else:
                        st.error("Erro ao publicar campanha")
        
        # Listar campanhas ativas
        st.subheader("Campanhas Ativas")
        campanhas = obter_campanhas_hemocentro(hemocentro)
        
        if campanhas:
            for campanha in campanhas:
                with st.expander(f"{campanha['titulo']} - {campanha['data_publicacao'].strftime('%d/%m/%Y')}"):
                    st.markdown(f"**Urgência:** {campanha['urgencia']}")
                    st.markdown(f"**Validade:** {campanha['validade'].strftime('%d/%m/%Y')}")
                    st.markdown("**Mensagem:**")
                    st.write(campanha['mensagem'])
                    
                    if campanha['imagem']:
                        st.image(campanha['imagem'], width=300)
                    
                    if st.button(f"Encerrar Campanha {campanha['id']}"):
                        if encerrar_campanha(campanha['id']):
                            st.success("Campanha encerrada")
                            st.rerun()
        else:
            st.info("Nenhuma campanha ativa no momento.")
    
    with tab4:  # Aba de Estatísticas
        st.subheader("Estatísticas do Hemocentro")
        
        # Carregar estatísticas
        estatisticas = carregar_estatisticas_hemocentro(hemocentro)
        
        if estatisticas:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Doações este mês", estatisticas['doacoes_mes'])
                st.metric("Agendamentos futuros", estatisticas['agendamentos_futuros'])
            
            with col2:
                st.metric("Taxa de comparecimento", f"{estatisticas['taxa_comparecimento']}%")
                st.metric("Doadores frequentes", estatisticas['doadores_frequentes'])
            
            with col3:
                st.metric("Estoque médio", f"{estatisticas['estoque_medio']}%")
                st.metric("Campanhas ativas", estatisticas['campanhas_ativas'])
            
            # Gráficos
            st.subheader("Histórico de Doações (últimos 6 meses)")
            if estatisticas.get('historico_doacoes'):
                df_historico = pd.DataFrame(estatisticas['historico_doacoes'])
                st.bar_chart(df_historico.set_index('mes'))
            
            st.subheader("Tipos Sanguíneos Mais Demandados")
            if estatisticas.get('tipos_mais_demandados'):
                df_tipos = pd.DataFrame(estatisticas['tipos_mais_demandados'])
                st.bar_chart(df_tipos.set_index('tipo_sanguineo'))
        else:
            st.info("Nenhuma estatística disponível ainda.")
    
    mostrar_globulos()

#region carregar_dados_hemocentro
def carregar_dados_hemocentro(usuario_id):
    """Carrega os dados do hemocentro do banco de dados"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                    SELECT h.* FROM hemocentros h
                    JOIN hemocentro_usuario hu ON h.id = hu.hemocentro_id
                    WHERE hu.usuario_id = %s
                    """
            cursor.execute(query, (usuario_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao carregar hemocentro: {e}")
            return None
        finally:
            conn.close()
    return None

#region obter_agendamentos_hemocentro
def obter_agendamentos_hemocentro(hemocentro_id):
    """Obtém os agendamentos do hemocentro com informações do usuário"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT a.*, u.nome as nome_usuario, u.tipo_sanguineo 
            FROM agendamentos a
            JOIN usuarios u ON a.usuario_id = u.id
            WHERE a.hemocentro_id = %s
            ORDER BY a.data_agendamento, a.horario
            """
            cursor.execute(query, (hemocentro_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter agendamentos: {e}")
            return []
        finally:
            conn.close()
    return []

#region carregar_estoque_hemocentro
def carregar_estoque_hemocentro(hemocentro_id):
    """Carrega o estoque de sangue do hemocentro"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM estoque_sangue WHERE hemocentro_id = %s", (hemocentro_id,))
            estoque = cursor.fetchone()
            
            if estoque:
                # Converter para dicionário de tipos sanguíneos
                return {
                    'A+': estoque['a_positivo'],
                    'A-': estoque['a_negativo'],
                    'B+': estoque['b_positivo'],
                    'B-': estoque['b_negativo'],
                    'AB+': estoque['ab_positivo'],
                    'AB-': estoque['ab_negativo'],
                    'O+': estoque['o_positivo'],
                    'O-': estoque['o_negativo']
                }
            return None
        except Exception as e:
            print(f"Erro ao carregar estoque: {e}")
            return None
        finally:
            conn.close()
    return None

#region salvar_estoque
def salvar_estoque(hemocentro_id, estoque):
    """Salva o estoque de sangue no banco de dados"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Verificar se já existe registro
            cursor.execute("SELECT id FROM estoque_sangue WHERE hemocentro_id = %s", (hemocentro_id,))
            existe = cursor.fetchone()
            
            if existe:
                # Atualizar
                query = """
                UPDATE estoque_sangue SET
                    a_positivo = %s,
                    a_negativo = %s,
                    b_positivo = %s,
                    b_negativo = %s,
                    ab_positivo = %s,
                    ab_negativo = %s,
                    o_positivo = %s,
                    o_negativo = %s,
                    data_atualizacao = NOW()
                WHERE hemocentro_id = %s
                """
                params = (
                    estoque['A+'], estoque['A-'], estoque['B+'], estoque['B-'],
                    estoque['AB+'], estoque['AB-'], estoque['O+'], estoque['O-'],
                    hemocentro_id
                )
            else:
                # Inserir novo
                query = """
                INSERT INTO estoque_sangue (
                    hemocentro_id, a_positivo, a_negativo, b_positivo, b_negativo,
                    ab_positivo, ab_negativo, o_positivo, o_negativo, data_atualizacao
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """
                params = (
                    hemocentro_id, estoque['A+'], estoque['A-'], estoque['B+'], estoque['B-'],
                    estoque['AB+'], estoque['AB-'], estoque['O+'], estoque['O-']
                )
            
            cursor.execute(query, params)
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao salvar estoque: {e}")
            return False
        finally:
            conn.close()
    return False

#region salvar_campanha
def salvar_campanha(hemocentro_id, titulo, mensagem, urgencia, validade, imagem=None):
    """Salva uma nova campanha no banco de dados"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Converter imagem para bytes se existir
            imagem_bytes = None
            if imagem:
                imagem_bytes = imagem.read()
            
            query = """
            INSERT INTO campanhas (
                hemocentro_id, titulo, mensagem, urgencia, validade, imagem, data_publicacao
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (hemocentro_id, titulo, mensagem, urgencia, validade, imagem_bytes))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao salvar campanha: {e}")
            return False
        finally:
            conn.close()
    return False

#region obter_campanhas_ativas
def obter_campanhas_ativas(filtro_data=None):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT c.*, h.nome as hemocentro_nome 
            FROM campanhas c
            JOIN hemocentros h ON c.hemocentro_id = h.id
            WHERE c.ativa = TRUE AND c.data_fim >= CURDATE()
            """
            
            # Adicionar filtro de data se fornecido
            if filtro_data == "semana":
                query += " AND c.data_inicio <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)"
            elif filtro_data == "mes":
                query += " AND c.data_inicio <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)"
            elif filtro_data == "urgentes":
                query += " AND c.urgencia = 'Alta'"
            
            query += " ORDER BY c.urgencia DESC, c.data_inicio"
            
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter campanhas: {e}")
            return []
        finally:
            conn.close()
    return []

#region obter_campanhas
def obter_campanhas_hemocentro(hemocentro_id):
    """Obtém as campanhas ativas do hemocentro"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT id, titulo, mensagem, urgencia, validade, data_publicacao, imagem
            FROM campanhas
            WHERE hemocentro_id = %s AND validade >= CURDATE()
            ORDER BY urgencia DESC, data_publicacao DESC
            """
            cursor.execute(query, (hemocentro_id,))
            
            campanhas = []
            for campanha in cursor.fetchall():
                # Converter imagem bytes para objeto de imagem se existir
                if campanha['imagem']:
                    campanha['imagem'] = Image.open(io.BytesIO(campanha['imagem']))
                campanhas.append(campanha)
            
            return campanhas
        except Exception as e:
            print(f"Erro ao obter campanhas: {e}")
            return []
        finally:
            conn.close()
    return []

#region encerrar_campanha
def encerrar_campanha(campanha_id):
    """Encerra uma campanha antes da data de validade"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE campanhas SET validade = CURDATE() WHERE id = %s",
                (campanha_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao encerrar campanha: {e}")
            return False
        finally:
            conn.close()
    return False


#region carregar_estatisticas_hemocentro
def carregar_estatisticas_hemocentro(hemocentro_id):
    """Carrega estatísticas do hemocentro"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Estatísticas básicas
            estatisticas = {}
            
            # Doações este mês
            cursor.execute("""
                SELECT COUNT(*) as total FROM doacoes
                WHERE hemocentro_id = %s AND MONTH(data_doacao) = MONTH(CURDATE())
            """, (hemocentro_id,))
            estatisticas['doacoes_mes'] = cursor.fetchone()['total']
            
            # Agendamentos futuros
            cursor.execute("""
                SELECT COUNT(*) as total FROM agendamentos
                WHERE hemocentro_id = %s AND data_agendamento >= CURDATE()
            """, (hemocentro_id,))
            estatisticas['agendamentos_futuros'] = cursor.fetchone()['total']
            
            # Taxa de comparecimento (últimos 30 dias)
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN status = 'Concluído' THEN 1 END) as concluidos,
                    COUNT(*) as total
                FROM agendamentos
                WHERE hemocentro_id = %s AND data_agendamento BETWEEN DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND CURDATE()
            """, (hemocentro_id,))
            result = cursor.fetchone()
            estatisticas['taxa_comparecimento'] = round((result['concluidos'] / result['total']) * 100, 1) if result['total'] > 0 else 0
            
            # Doadores frequentes (3+ doações no último ano)
            cursor.execute("""
                SELECT COUNT(*) as total FROM (
                    SELECT usuario_id FROM doacoes
                    WHERE hemocentro_id = %s AND data_doacao >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                    GROUP BY usuario_id HAVING COUNT(*) >= 3
                ) as freq
            """, (hemocentro_id,))
            estatisticas['doadores_frequentes'] = cursor.fetchone()['total']
            
            # Estoque médio (% do ideal)
            cursor.execute("""
                SELECT AVG((a_positivo + a_negativo + b_positivo + b_negativo + ab_positivo + ab_negativo + o_positivo + o_negativo) / 8) as media
                FROM estoque_sangue
                WHERE hemocentro_id = %s
            """, (hemocentro_id,))
            estatisticas['estoque_medio'] = round(cursor.fetchone()['media'] or 0, 1)
            
            # Campanhas ativas
            cursor.execute("""
                SELECT COUNT(*) as total FROM campanhas
                WHERE hemocentro_id = %s AND validade >= CURDATE()
            """, (hemocentro_id,))
            estatisticas['campanhas_ativas'] = cursor.fetchone()['total']
            
            # Histórico de doações (últimos 6 meses)
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(data_doacao, '%Y-%m') as mes,
                    COUNT(*) as total
                FROM doacoes
                WHERE hemocentro_id = %s AND data_doacao >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                GROUP BY DATE_FORMAT(data_doacao, '%Y-%m')
                ORDER BY mes
            """, (hemocentro_id,))
            estatisticas['historico_doacoes'] = cursor.fetchall()
            
            # Tipos sanguíneos mais demandados
            cursor.execute("""
                SELECT 
                    tipo_sanguineo,
                    COUNT(*) as total
                FROM doacoes d
                JOIN usuarios u ON d.usuario_id = u.id
                WHERE d.hemocentro_id = %s AND d.data_doacao >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
                GROUP BY tipo_sanguineo
                ORDER BY total DESC
                LIMIT 4
            """, (hemocentro_id,))
            estatisticas['tipos_mais_demandados'] = cursor.fetchall()
            
            return estatisticas
        except Exception as e:
            print(f"Erro ao carregar estatísticas: {e}")
            return None
        finally:
            conn.close()
    return None

#region exportar_para_excel
def exportar_para_excel(df, filename):
    """Exporta um DataFrame para Excel"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Agendamentos')
        writer.save()
    st.download_button(
        label="⬇️ Baixar Excel",
        data=output.getvalue(),
        file_name=filename,
        mime="application/vnd.ms-excel"
    )

#region enviar_notificacao_campanha
def enviar_notificacao_campanha(hemocentro_id, titulo_campanha):
    """Envia notificação aos usuários sobre nova campanha"""
    # Implementação opcional - poderia enviar emails ou notificações no app
    pass


#region adicionar_conquista
def adicionar_conquista(nome_conquista):
    conquista = next((c for c in conquistas_disponiveis if c['nome'] == nome_conquista), None)
    if conquista and not any(c['nome'] == nome_conquista for c in st.session_state.conquistas):
        st.session_state.conquistas.append(conquista)
        st.session_state.pontos += conquista['pontos']
        
        # Simples sistema de níveis (100 pontos por nível)
        st.session_state.nivel = st.session_state.pontos // 100 + 1
        
        st.success(f"Conquista desbloqueada: {conquista['nome']}! +{conquista['pontos']} pontos")
        return True
    return False

#region carregar_conquistas
def carregar_conquistas():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM conquistas")
            conquistas = cursor.fetchall()
            return conquistas
        except Exception as e:
            print(f"Erro ao carregar conquistas: {e}")
            return []
        finally:
            conn.close()
    return []

#region carregar_conquistas_usuario
def carregar_conquistas_usuario(usuario_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT c.* FROM conquistas c
                JOIN usuario_conquistas uc ON c.id = uc.conquista_id
                WHERE uc.usuario_id = %s
            """, (usuario_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao carregar conquistas do usuário: {e}")
            return []
        finally:
            conn.close()
    return []


#region Página Conquistas
def pagina_conquistas():
    st.title("Minhas Conquistas")
    
    if st.session_state.conquistas:
        cols = st.columns(3)
        for i, conquista in enumerate(st.session_state.conquistas):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="border: 1px solid #ccc; border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 10px;">
                    <div style="font-size: 2em;">{conquista['icone']}</div>
                    <h3>{conquista['nome']}</h3>
                    <p>{conquista['descricao']}</p>
                    <p><strong>{conquista['pontos']} pontos</strong></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Você ainda não desbloqueou conquistas. Agende sua primeira doação para começar!")
    
    st.subheader("Conquistas Disponíveis")
    cols = st.columns(3)
    for i, conquista in enumerate(conquistas_disponiveis):
        if conquista['nome'] not in [c['nome'] for c in st.session_state.conquistas]:
            with cols[i % 3]:
                st.markdown(f"""
                <div style="border: 1px solid #ccc; border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 10px; opacity: 0.6;">
                    <div style="font-size: 2em;">🔒</div>
                    <h3>{conquista['nome']}</h3>
                    <p>{conquista['descricao']}</p>
                    <p><strong>{conquista['pontos']} pontos</strong></p>
                </div>
                """, unsafe_allow_html=True)
    mostrar_globulos()
    
#region Página Quiz
def pagina_quiz():
    col1, col2 = st.columns([2, 1])
    with col2:
        add_vertical_space(10)
        st.image(os.path.join(IMG_DIR, 'coracao-.png'), width=150)
    with col1:
        st.title("Quiz sobre Doação de Sangue")
        
        todas_perguntas = [
                {
                    "pergunta": "Qual o intervalo mínimo entre doações de sangue para homens?",
                    "opcoes": ["1 mês", "2 meses", "3 meses", "6 meses"],
                    "resposta": 1,
                    "dica": "O intervalo é maior para homens do que para mulheres."
                },
                {
                    "pergunta": "Qual o intervalo mínimo entre doações de sangue para mulheres?",
                    "opcoes": ["1 mês", "2 meses", "3 meses", "4 meses"],
                    "resposta": 2,
                    "dica": "O intervalo é menor que para homens."
                },
                {
                    "pergunta": "Qual dessas condições impede temporariamente a doação de sangue?",
                    "opcoes": ["Gripe", "Diabetes controlada", "Pressão alta controlada", "Colesterol alto"],
                    "resposta": 0,
                    "dica": "Condições agudas impedem temporariamente."
                },
                {
                    "pergunta": "Quantas vidas uma única doação de sangue pode salvar?",
                    "opcoes": ["1", "2", "3", "4"],
                    "resposta": 3,
                    "dica": "O sangue pode ser separado em componentes."
                },
                {
                    "pergunta": "Qual o volume de sangue normalmente coletado em uma doação?",
                    "opcoes": ["250 ml", "450 ml", "650 ml", "850 ml"],
                    "resposta": 1,
                    "dica": "É menos de meio litro."
                },
                {
                    "pergunta": "Quanto tempo leva em média uma doação de sangue?",
                    "opcoes": ["5-10 minutos", "15-20 minutos", "30-40 minutos", "1 hora"],
                    "resposta": 1,
                    "dica": "Incluindo a triagem e o lanche após."
                },
                {
                    "pergunta": "Qual a idade mínima para doar sangue no Brasil?",
                    "opcoes": ["16 anos", "18 anos", "21 anos", "25 anos"],
                    "resposta": 0,
                    "dica": "Menores precisam de autorização."
                },
                {
                    "pergunta": "Qual o peso mínimo exigido para doar sangue?",
                    "opcoes": ["45 kg", "50 kg", "55 kg", "60 kg"],
                    "resposta": 1,
                    "dica": "É um pouco abaixo do peso médio."
                },
                {
                    "pergunta": "Qual desses alimentos deve ser evitado antes de doar sangue?",
                    "opcoes": ["Maçã", "Pão integral", "Feijoada", "Banana"],
                    "resposta": 2,
                    "dica": "Alimentos gordurosos interferem nos testes."
                },
                {
                    "pergunta": "Quanto tempo após um parto a mulher pode doar sangue?",
                    "opcoes": ["1 mês", "3 meses", "6 meses", "9 meses"],
                    "resposta": 2,
                    "dica": "Incluindo parto natural e cesárea."
                },
                {
                    "pergunta": "Qual desses tipos sanguíneos é considerado doador universal?",
                    "opcoes": ["A+", "B-", "AB+", "O-"],
                    "resposta": 3,
                    "dica": "Pode ser doado para qualquer tipo."
                },
                {
                    "pergunta": "Qual desses tipos sanguíneos é considerado receptor universal?",
                    "opcoes": ["A+", "B-", "AB+", "O-"],
                    "resposta": 2,
                    "dica": "Pode receber de qualquer tipo."
                },
                {
                    "pergunta": "Quantas vezes por ano um homem pode doar sangue?",
                    "opcoes": ["2 vezes", "4 vezes", "6 vezes", "8 vezes"],
                    "resposta": 1,
                    "dica": "Considerando o intervalo mínimo."
                },
                {
                    "pergunta": "Quantas vezes por ano uma mulher pode doar sangue?",
                    "opcoes": ["2 vezes", "3 vezes", "4 vezes", "5 vezes"],
                    "resposta": 1,
                    "dica": "Considerando o intervalo mínimo."
                },
                {
                    "pergunta": "Qual dessas vacinas impede temporariamente a doação?",
                    "opcoes": ["COVID-19", "Febre amarela", "Gripe", "Hepatite B"],
                    "resposta": 1,
                    "dica": "Vacinas com vírus vivos atenuados."
                },
                {
                    "pergunta": "Quanto tempo após fazer tatuagem pode-se doar sangue?",
                    "opcoes": ["1 mês", "6 meses", "1 ano", "Não impede"],
                    "resposta": 0,
                    "dica": "Desde que feita em local regulamentado."
                },
                {
                    "pergunta": "Qual a validade de uma bolsa de sangue?",
                    "opcoes": ["7 dias", "30 dias", "42 dias", "90 dias"],
                    "resposta": 2,
                    "dica": "Depende do tipo de conservante usado."
                },
                {
                    "pergunta": "Qual o componente sanguíneo mais demandado?",
                    "opcoes": ["Hemácias", "Plaquetas", "Plasma", "Crioprecipitado"],
                    "resposta": 0,
                    "dica": "Usado em anemias e cirurgias."
                },
                {
                    "pergunta": "Qual o tempo de validade das plaquetas?",
                    "opcoes": ["5 dias", "10 dias", "21 dias", "30 dias"],
                    "resposta": 0,
                    "dica": "Precisam ser armazenadas em agitação."
                },
                {
                    "pergunta": "Qual a porcentagem aproximada da população brasileira que doa sangue?",
                    "opcoes": ["1%", "2%", "5%", "10%"],
                    "resposta": 1,
                    "dica": "Ainda abaixo do recomendado pela OMS."
                },
                {
                    "pergunta": "Qual desses medicamentos impede a doação?",
                    "opcoes": ["Aspirina", "Paracetamol", "Anticoncepcional", "Antibiótico"],
                    "resposta": 3,
                    "dica": "Medicamentos para infecções ativas."
                },
                {
                    "pergunta": "Quanto tempo após extração dentária pode-se doar sangue?",
                    "opcoes": ["24 horas", "3 dias", "7 dias", "15 dias"],
                    "resposta": 2,
                    "dica": "Procedimentos odontológicos simples."
                },
                {
                    "pergunta": "Qual dessas situações impede permanentemente a doação?",
                    "opcoes": ["Hepatite B", "Hepatite C", "HIV", "Todas as anteriores"],
                    "resposta": 3,
                    "dica": "Doenças transmissíveis pelo sangue."
                },
                {
                    "pergunta": "Qual o percentual de sangue que pode ser doado sem prejudicar o doador?",
                    "opcoes": ["5%", "10%", "15%", "20%"],
                    "resposta": 2,
                    "dica": "Em torno de 450ml para adultos."
                },
                {
                    "pergunta": "Quanto tempo o corpo leva para repor o sangue doado?",
                    "opcoes": ["24 horas", "3 dias", "1 semana", "1 mês"],
                    "resposta": 3,
                    "dica": "O plasma em 24h, as hemácias demoram mais."
                },
                {
                    "pergunta": "Qual desses é um requisito para doar sangue?",
                    "opcoes": ["Estar em jejum", "Ter dormido bem", "Não ter comido gordura", "Todas as anteriores"],
                    "resposta": 2,
                    "dica": "Jejum não é necessário, apenas evitar gordura."
                },
                {
                    "pergunta": "Qual a temperatura de armazenamento das hemácias?",
                    "opcoes": ["-20°C", "2-6°C", "20-24°C", "37°C"],
                    "resposta": 1,
                    "dica": "Em refrigeradores específicos."
                },
                {
                    "pergunta": "Qual o principal objetivo da triagem antes da doação?",
                    "opcoes": ["Proteger o receptor", "Proteger o doador", "Ambos", "Nenhum"],
                    "resposta": 2,
                    "dica": "Segurança de quem doa e quem recebe."
                },
                {
                    "pergunta": "Qual o principal motivo para a falta de doadores?",
                    "opcoes": ["Medo de agulhas", "Falta de informação", "Falta de tempo", "Todas as anteriores"],
                    "resposta": 3,
                    "dica": "Diversas barreiras psicológicas e logísticas."
                },
                {
                    "pergunta": "Qual o melhor horário para doar sangue?",
                    "opcoes": ["Manhã", "Tarde", "Noite", "Qualquer horário"],
                    "resposta": 3,
                    "dica": "Desde que siga as recomendações pré-doação."
                }
            ]
        # Selecionar 5 perguntas aleatórias
        if 'perguntas_quiz' not in st.session_state:
            st.session_state.perguntas_quiz = random.sample(todas_perguntas, 5)
            st.session_state.quiz_respostas = {}
            st.session_state.quiz_finalizado = False
            st.session_state.mostrar_dica = [False] * 5
        
        perguntas = st.session_state.perguntas_quiz
        
        for i, pergunta in enumerate(perguntas):
            st.subheader(f"Pergunta {i+1}: {pergunta['pergunta']}")
            
            if st.button(f"Dica {i+1}", key=f"dica_{i}"):
                st.session_state.mostrar_dica[i] = not st.session_state.mostrar_dica[i]
            
            if st.session_state.mostrar_dica[i]:
                st.info(f"Dica: {pergunta['dica']}")
            
            if i not in st.session_state.quiz_respostas:
                resposta = st.radio(
                    f"Opções para pergunta {i+1}", 
                    pergunta['opcoes'], 
                    key=f"quiz_{i}",
                    index=None
                )
                
                if resposta is not None:
                    st.session_state.quiz_respostas[i] = pergunta['opcoes'].index(resposta)
            else:
                resposta_idx = st.session_state.quiz_respostas[i]
                correta = pergunta['resposta'] == resposta_idx
                cor = "#4CAF50" if correta else "#F44336"
                emoji = "✅" if correta else "❌"
                
                st.markdown(f"""
                <div style="border: 1px solid {cor}; border-radius: 5px; padding: 10px; margin-bottom: 10px;">
                    <p>Sua resposta: <strong>{pergunta['opcoes'][resposta_idx]}</strong> {emoji}</p>
                    <p>Resposta correta: <strong>{pergunta['opcoes'][pergunta['resposta']]}</strong></p>
                </div>
                """, unsafe_allow_html=True)
        
        # Verificar se todas as perguntas foram respondidas
        todas_respondidas = len(st.session_state.quiz_respostas) == len(perguntas)
        
        if not todas_respondidas:
            st.warning("Responda todas as perguntas para ver seu resultado!")
        else:
            if not st.session_state.quiz_finalizado:
                acertos = sum(1 for i in range(len(perguntas)) 
                            if st.session_state.quiz_respostas[i] == perguntas[i]['resposta'])
                
                # Calcular pontuação
                pontos_ganhos = acertos * 20  # 20 pontos por acerto
                st.session_state.pontos += pontos_ganhos
                
                # Atualizar nível
                st.session_state.nivel = st.session_state.pontos // 100 + 1
                
                # Mostrar resultado
                if acertos == len(perguntas):
                    st.balloons()
                    st.success(f"🎉 Perfeito! Você acertou todas as {len(perguntas)} perguntas e ganhou {pontos_ganhos} pontos!")
                    adicionar_conquista("Quiz Master")
                elif acertos >= len(perguntas) / 2:
                    st.success(f"👍 Bom trabalho! Você acertou {acertos} de {len(perguntas)} perguntas e ganhou {pontos_ganhos} pontos!")
                else:
                    st.warning(f"📚 Estude mais! Você acertou {acertos} de {len(perguntas)} perguntas. Ganhou {pontos_ganhos} pontos.")
                
                st.session_state.quiz_finalizado = True
        
        if st.session_state.quiz_finalizado:
            if st.button("🔁 Refazer Quiz"):
                st.session_state.perguntas_quiz = random.sample(todas_perguntas, 5)
                st.session_state.quiz_respostas = {}
                st.session_state.quiz_finalizado = False
                st.session_state.mostrar_dica = [False] * 5
                st.rerun()
    
    mostrar_globulos()