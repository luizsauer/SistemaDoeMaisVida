import streamlit as st
import os
import random

# Caminho absoluto da pasta atual (utils)
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))

# Sobe um nível (vai para doe+vida/)
BASE_DIR = os.path.dirname(UTILS_DIR)
STATIC_DIR = os.path.join(BASE_DIR, 'static')
IMG_DIR = os.path.join(STATIC_DIR, 'img')

def mostrar_globulos():
    try:
        globulos = ['globulos1-.png', 'globulos2-.png', 'globulos3-.png']
        cols = st.columns(3)  # Cria 4 colunas
        
        # Garante que não repita imagens (repete se tiver menos imagens que colunas)
        if len(globulos) >= 3:
            selecionadas = random.sample(globulos, 3)
        else:
            selecionadas = [random.choice(globulos) for _ in range(3)]
        
        for col, nome_img in zip(cols, selecionadas):
            img_path = os.path.join(IMG_DIR, nome_img)
            if os.path.exists(img_path):
                col.image(img_path, width=80)
            else:
                col.error(f"Imagem não encontrada: {img_path}")
                
    except Exception as e:
        st.error(f"Erro ao carregar glóbulos: {str(e)}")


def add_vertical_space(space):
    for _ in range(space):
        st.write("\n")