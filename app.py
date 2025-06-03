
import streamlit as st

from utils.helpers import mostrar_globulos
st.set_page_config(
    page_title="Doe+Vida",
    page_icon="💉",
    layout="wide",
)

import pandas as pd
from PIL import Image
import os
import random
import datetime
import base64
import mysql.connector
from database import get_db_connection
from utils.auth import fazer_login, fazer_cadastro, pagina_login
from utils.db_operations import (adicionar_conquista, carregar_hemocentros, 
                                carregar_conquistas, pagina_agendamento, 
                                pagina_conquistas, pagina_hemocentros, 
                                pagina_painel_hemocentro, pagina_quiz,
                                salvar_agendamento, obter_agendamentos_usuario)

#region Configuração de diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
IMG_DIR = os.path.join(STATIC_DIR, 'img')
CSS_DIR = os.path.join(STATIC_DIR, 'css')


def load_css():
    with open(os.path.join(CSS_DIR, 'style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#region Configuração inicial da página
# Carregar CSS
load_css()

#region Função background
def set_bg_hack():
    bg_image = os.path.join(IMG_DIR, 'background.png')
    
    with open(bg_image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    bg_css = f"""
    <style>
    .stApp {{
        background-image: url(data:image/png;base64,{encoded_string});
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

set_bg_hack()

#region Inicializar dados da sessão
def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'agendamentos' not in st.session_state:
        st.session_state.agendamentos = []
    if 'conquistas' not in st.session_state:
        st.session_state.conquistas = []
    if 'pontos' not in st.session_state:
        st.session_state.pontos = 0
    if 'nivel' not in st.session_state:
        st.session_state.nivel = 1

init_session_state()

# Carregar dados
hemocentros = carregar_hemocentros()
conquistas_disponiveis = carregar_conquistas()


#region menu horizontal
def menu_horizontal():
    if st.session_state.user:

        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 3, 1, 1, 1])
        with col1:
            st.image(os.path.join(IMG_DIR, 'logo-.png'), width=200)
        with col2:
            st.markdown(f"<div class='user-info'><h3>Olá, {st.session_state.user['nome'].split()[0]}!</h3></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='level-box'>Nível: {st.session_state.nivel}</div>", unsafe_allow_html=True)
        with col5:
            st.markdown(f"<div class='points-box'>💖 {st.session_state.pontos} pontos</div>", unsafe_allow_html=True)
        with col6:
            # Botão Sair
            # st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Sair", key="btn_sair"):
                st.session_state.user = None
                st.rerun()

        # Menu horizontal
        menu_itens = []

        if st.session_state.user['tipo'] == 'doador':
            menu_itens = [
                ("🏠 Início", "Início"),
                ("📅 Agendar Doação", "Agendar Doação"),
                ("📍 Hemocentros", "Hemocentros"),
                ("🏆 Minhas Conquistas", "Minhas Conquistas"),
                ("❓ Quiz", "Quiz")
            ]
        else:
            menu_itens = [("📊 Painel Hemocentro", "Painel Hemocentro")]

        cols = st.columns(len(menu_itens))
        for col, (label, valor) in zip(cols, menu_itens):
            if col.button(label, use_container_width=True):
                st.session_state.menu_atual = valor

            
#region Página Início
def pagina_inicio():
    st.title("Doe+Vida 💉")
    
    # Mostrar glóbulos aleatórios
    mostrar_globulos()
    
    col1, col2, col3 = st.columns([4, 1, 2])
    with col1:
        st.markdown("""
        <div class="welcome-box">
            <h2>Bem-vindo ao sistema de doação de sangue gamificado!</h2>
            <p>Aqui você pode:</p>
            <ul>
                <li>Encontrar hemocentros próximos</li>
                <li>Agendar suas doações</li>
                <li>Acompanhar seu histórico</li>
                <li>Ganhar pontos e conquistas</li>
                <li>Aprender sobre doação de sangue</li>
            </ul>
            <p class="highlight">Cada doação pode salvar até 4 vidas!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.image(os.path.join(IMG_DIR, 'mao-.png'), width=300)
    
    # Seção de campanhas
    st.subheader("Campanhas Ativas")
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown("""
            <div class="campaign-box">
                <h4>Doação de Inverno</h4>
                <p>Os estoques estão baixos nessa época do ano.</p>
                <p>Ajude a manter os bancos de sangue abastecidos!</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Compartilhar Campanha", key="camp1"):
                adicionar_conquista("Compartilhador")
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="campaign-box urgent">
                <h4>Tipo O- em falta</h4>
                <p>Sangue O- é doador universal e está em falta.</p>
                <p>Se você tem esse tipo sanguíneo, doe agora!</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Compartilhar Campanha", key="camp2"):
                adicionar_conquista("Compartilhador")
    mostrar_globulos()
    
    # Seção de agendamentos recentes
    if st.session_state.agendamentos:
        st.subheader("Seus Agendamentos Recentes")
        for agendamento in st.session_state.agendamentos[-3:]:
            st.markdown(f"""
            <div class="appointment-card">
                <h4>{agendamento['hemocentro_nome']}</h4>
                <p>📅 {agendamento['data_agendamento']} ⏰ {agendamento['horario']}</p>
                <p class="status {agendamento['status'].lower()}">{agendamento['status']}</p>
            </div>
            """, unsafe_allow_html=True)


#region main Roteamento principal
def main():
    if st.session_state.user is None:
        pagina_login()
    else:
        menu_horizontal()
        
        if 'menu_atual' not in st.session_state:
            st.session_state.menu_atual = "Início"
        
        if st.session_state.user['tipo'] == 'doador':
            if st.session_state.menu_atual == "Início":
                pagina_inicio()
            elif st.session_state.menu_atual == "Agendar Doação":
                pagina_agendamento()
            elif st.session_state.menu_atual == "Hemocentros":
                pagina_hemocentros()
            elif st.session_state.menu_atual == "Minhas Conquistas":
                pagina_conquistas()
            elif st.session_state.menu_atual == "Quiz":
                pagina_quiz()
        else:
            pagina_painel_hemocentro()

if __name__ == "__main__":
    main()