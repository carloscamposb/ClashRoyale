
import streamlit as st
from pymongo import MongoClient
import pandas as pd
import random
from datetime import datetime
import pytz
import requests

# Configurar conexão MongoDB
client = MongoClient('mongodb+srv://CARLOS:AneHWQWQQyYvBvBl@cluster0.wjfbqla.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['clash_royale']
collection = db['jogadores']
resultados = db['resultados']

# Função para obter jogadores
def obter_jogadores():
    return list(collection.find({}))

# Função para obter batalhas
def obter_batalhas():
    return list(resultados.find({}))

# Função para calcular combos vencedores
def calcular_combos_vitoriosos(timestamp_inicio, timestamp_fim):
    timestamp_inicio = datetime.strptime(timestamp_inicio, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
    timestamp_fim = datetime.strptime(timestamp_fim, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)

    batalhas = resultados.find({
        'data_hora_batalha.inicio': {'$gte': timestamp_inicio},
        'data_hora_batalha.fim': {'$lte': timestamp_fim}
    })

    combos_vitorias = {}
    total_combos = {}

    for batalha in batalhas:
        jogador1 = collection.find_one({'nome': batalha['jogador1']})
        jogador2 = collection.find_one({'nome': batalha['jogador2']})

        if batalha['vitoria_jogador1']:
            vencedor = jogador1
        else:
            vencedor = jogador2

        deck_vencedor = tuple(sorted(c['name'] for c in vencedor['deck']))

        if deck_vencedor in combos_vitorias:
            combos_vitorias[deck_vencedor] += 1
        else:
            combos_vitorias[deck_vencedor] = 1

        if deck_vencedor in total_combos:
            total_combos[deck_vencedor] += 1
        else:
            total_combos[deck_vencedor] = 1

    combos_vitoriosos = []
    for combo in combos_vitorias:
        vitorias = combos_vitorias[combo]
        total = total_combos[combo]
        if total > 0 and (vitorias / total) * 100 > 50:
            combos_vitoriosos.append((combo, (vitorias / total) * 100))

    combos_vitoriosos.sort(key=lambda x: x[1], reverse=True)
    return combos_vitoriosos

# Interface Streamlit
st.title('Simulação de Batalhas Clash Royale')

# Exibir jogadores
st.header('Jogadores')
jogadores = obter_jogadores()
jogadores_df = pd.DataFrame(jogadores)
st.write(jogadores_df)

# Exibir resultados de batalhas
st.header('Batalhas')
batalhas = obter_batalhas()
batalhas_df = pd.DataFrame(batalhas)
st.write(batalhas_df)

# Calcular e exibir combos vencedores
st.header('Combos Vencedores')
inicio = st.text_input('Início (YYYY-MM-DD HH:MM:SS)', '2024-09-30 16:00:00')
fim = st.text_input('Fim (YYYY-MM-DD HH:MM:SS)', '2024-09-30 16:33:56')

if st.button('Calcular Combos Vencedores'):
    combos = calcular_combos_vitoriosos(inicio, fim)
    st.write(pd.DataFrame(combos, columns=['Combo', 'Porcentagem de Vitórias']))
