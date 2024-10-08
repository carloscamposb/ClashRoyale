# Importa as bibliotecas necessárias
import random # Para gerar números aleatórios
import streamlit as st 
import time
from pymongo import MongoClient
import requests
from datetime import datetime
import pytz # Para manipulação de fusos horários

# Conecta ao banco de dados MongoDB
client = MongoClient('mongodb+srv://CARLOS:b6ZjQBJPZr4yHPAl@cluster0.wjfbqla.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['clash_royale']
collection = db['jogadores']
resultados = db['resultados']

# Função para obter as cartas do jogo através da API
def obter_cartas():
    URL_CARDS = 'https://api.clashroyale.com/v1/cards'
    headers = {
        'Content-type': 'application/json',
        'Authorization':'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImU3YzVlYTA0LWE2NjktNGIxOS1iY2I5LTY4NjBmYjRmODI4YSIsImlhdCI6MTcyNzcxMjMyOSwic3ViIjoiZGV2ZWxvcGVyLzZlYzQzMTcxLWZlMDctY2Q4Ni02N2IxLTk0NDBmZmZhZGZhOCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxODcuMTQuNTkuMTY1Il0sInR5cGUiOiJjbGllbnQifV19.bYk7nAeIVu8TLDK7L60qiqP6HCGh0p5w3wIwvLm1PWvDLUu0kSao2UCigsod20TEQN0iFXqW6fP3J51H5c1jxg'
    }

    # Faz a requisição GET para obter as cartas
    response = requests.get(URL_CARDS, headers=headers)
    if response.status_code == 200:
        return response.json()['items']
    else:
        print(f"Erro ao obter cartas: {response.status_code}")
        return []

# Função para criar um jogador com um nome e um deck de cartas
def criar_jogador(nome, cartas):
    deck = random.sample(cartas, 8) # Seleciona aleatoriamente 8 cartas para o deck
    jogador = {
        'nome': nome,
        'deck': deck,
        'trofeus': 0
    }
    collection.insert_one(jogador)
    print(f'Jogador {nome} inserido com sucesso!')

# Função para adicionar múltiplos jogadores com nomes pré-definidos
def adicionar_jogadores(cartas):
    nomes = ['Jogador1', 'Jogador2', 'Jogador3', 'Jogador4', 'Jogador5', 'Jogador6']
    for nome in nomes:
        criar_jogador(nome, cartas)

# Função para obter todos os jogadores cadastrados
def obter_jogadores():
    return list(collection.find({}))  # Retorna a lista de jogadores

# Função para simular uma batalha entre dois jogadores
def simular_batalha(jogador1, jogador2):
    tempo_inicio = datetime.now(pytz.utc)  # Marca o tempo de início da batalha
    
     # Define dois intervalos de tempo aleatório para espera
    intervalo1 = (1, 1.59)  
    intervalo2 = (2, 2.59)  
    escolha_intervalo = random.choice([intervalo1, intervalo2])  # Escolhe um intervalo aleatoriamente
    tempo_espera = random.uniform(*escolha_intervalo) * 60  # Calcula o tempo de espera em segundos
    time.sleep(tempo_espera) # Pausa a execução por esse tempo

# Gera um número aleatório de torres derrubadas para cada jogador
    torres_jogador1 = random.randint(0, 2)
    torres_jogador2 = random.randint(0, 2)

# Determina o vencedor da batalha
    if torres_jogador1 > torres_jogador2:
        vitoria_jogador1 = True
    elif torres_jogador1 < torres_jogador2:
        vitoria_jogador1 = False
    else:  
        vitoria_jogador1 = random.choice([True, False])
        
        if vitoria_jogador1:
            torres_jogador1 = min(torres_jogador1 + 1, 3)
        else:
            torres_jogador2 = min(torres_jogador2 + 1, 3)

    tempo_fim = datetime.now(pytz.utc)
    tempo_batalha = (tempo_fim - tempo_inicio).total_seconds() 

    return vitoria_jogador1, tempo_batalha, torres_jogador1, torres_jogador2, tempo_inicio, tempo_fim

# Função para atualizar os troféus de um jogador após uma batalha
def atualizar_trofeus(nome_jogador, ganhou):
    jogador = collection.find_one({'nome': nome_jogador})
    if jogador:
        if ganhou:
            trofeus = jogador.get('trofeus', 0) + 30
        else:
            trofeus = max(jogador.get('trofeus', 0) - 10, 0)
        collection.update_one({'nome': nome_jogador}, {'$set': {'trofeus': trofeus}})
        print(f'Troféus atualizados para {nome_jogador}: {trofeus}')

# Função para registrar o resultado da batalha no banco de dados
def atualizar_resultado(nome_jogador1, nome_jogador2, vitoria_jogador1, tempo_batalha, torres_jogador1, torres_jogador2, tempo_inicio, tempo_fim):
    resultado = {
        'jogador1': nome_jogador1,
        'jogador2': nome_jogador2,
        'vitoria_jogador1': vitoria_jogador1,
        'tempo_batalha': round(tempo_batalha, 2),
        'torres_jogador1': torres_jogador1,
        'torres_jogador2': torres_jogador2,
        'data_hora_batalha': {
            'inicio': tempo_inicio.strftime('%Y-%m-%d %H:%M:%S'),
            'fim': tempo_fim.strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    resultados.insert_one(resultado)
    print(f'Batalha entre {nome_jogador1} e {nome_jogador2} registrada com sucesso!')

# Função para colocar jogadores para duelarem entre si
def colocar_para_duelar():
    jogadores = obter_jogadores()
    if len(jogadores) < 2:
        print('Não há jogadores suficientes para duelar.')
        return

    # Loop para fazer duelos entre todos os jogadores
    for i in range(len(jogadores)):
        for j in range(i + 1, len(jogadores)):
            jogador1 = jogadores[i]
            jogador2 = jogadores[j]
            nome_jogador1 = jogador1['nome']
            nome_jogador2 = jogador2['nome']
            vitoria_jogador1, tempo_batalha, torres_jogador1, torres_jogador2, tempo_inicio, tempo_fim = simular_batalha(jogador1, jogador2)
    
     # Atualiza resultados e troféus com base na vitória
            if vitoria_jogador1:
                atualizar_resultado(nome_jogador1, nome_jogador2, True, tempo_batalha, torres_jogador1, torres_jogador2, tempo_inicio, tempo_fim)
                atualizar_trofeus(nome_jogador1, True)
                atualizar_trofeus(nome_jogador2, False)
            else:
                atualizar_resultado(nome_jogador1, nome_jogador2, False, tempo_batalha, torres_jogador1, torres_jogador2, tempo_inicio, tempo_fim)
                atualizar_trofeus(nome_jogador1, False)
                atualizar_trofeus(nome_jogador2, True)

# Função para exibir a interface do usuário
def exibir_resultados():
    resultados_registrados = resultados.find({})
    for resultado in resultados_registrados:
        vencedor = resultado['jogador1'] if resultado['vitoria_jogador1'] else resultado['jogador2']
        trofeus_vencedor = collection.find_one({'nome': vencedor}).get('trofeus', 0)
        trofeus_perdedor = collection.find_one({'nome': resultado['jogador2'] if resultado['vitoria_jogador1'] else resultado['jogador1']}).get('trofeus', 0)
        print(f"Batalha entre {resultado['jogador1']} e {resultado['jogador2']}:")
        print(f"  Vencedor: {vencedor} (Troféus: {trofeus_vencedor})")
        print(f"  Perdedor: {resultado['jogador2'] if resultado['vitoria_jogador1'] else resultado['jogador1']} (Troféus: {trofeus_perdedor})")
        print(f"  Tempo da Batalha: {resultado['tempo_batalha']} segundos")
        print(f"  Início da Batalha: {resultado['data_hora_batalha']['inicio']}")
        print(f"  Fim da Batalha: {resultado['data_hora_batalha']['fim']}\n")

# Execução

# cartas = obter_cartas() 
# adicionar_jogadores(cartas) 
# colocar_para_duelar() 
exibir_resultados()



# =============================== CONSULTAS ===============================================================================


 #consulta de porcentagem de vitórias e derrotas utilizando x carta ocorridas em um intervalo de timestamps

def calcular_porcentagem_vitorias_derrotas(carta, timestamp_inicio, timestamp_fim):
    # Converter as strings de timestamp para objetos datetime, ajustando o fuso horário para UTC
    timestamp_inicio = datetime.strptime(timestamp_inicio, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
    timestamp_fim = datetime.strptime(timestamp_fim, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)

 # Buscar batalhas no banco de dados que ocorram dentro do intervalo de tempo fornecido
    batalhas = resultados.find({
        'data_hora_batalha.inicio': {'$gte': timestamp_inicio.strftime('%Y-%m-%d %H:%M:%S')},
        'data_hora_batalha.fim': {'$lte': timestamp_fim.strftime('%Y-%m-%d %H:%M:%S')}
    })

 # Inicializa as variáveis
    total_batalhas_com_carta = 0
    vitorias_com_carta = 0
    derrotas_com_carta = 0

# Iterar sobre as batalhas encontradas
    for batalha in batalhas:
        # Buscar os jogadores envolvidos na batalha   
        jogador1 = collection.find_one({'nome': batalha['jogador1']})
        jogador2 = collection.find_one({'nome': batalha['jogador2']})

        # Verificar se a carta está no deck de algum dos jogadores
        jogador1_tem_carta = any(c['name'] == carta for c in jogador1['deck'])
        jogador2_tem_carta = any(c['name'] == carta for c in jogador2['deck'])
        # Se pelo menos um jogador tiver a carta, contabilizar a batalha
        if jogador1_tem_carta or jogador2_tem_carta:
            total_batalhas_com_carta += 1
        # Verificar quem venceu a batalha e atualizar contadores de vitórias e derrotas
            if jogador1_tem_carta and batalha['vitoria_jogador1']:
                vitorias_com_carta += 1
            elif jogador2_tem_carta and not batalha['vitoria_jogador1']:
                vitorias_com_carta += 1
            else:
                derrotas_com_carta += 1
    # Se não houver batalhas com a carta, informar ao usuário
    if total_batalhas_com_carta == 0:
        print(f'Nenhuma batalha encontrada com a carta "{carta}" no intervalo fornecido.')
        return
    # Calcular as porcentagens de vitórias e derrotas
    porcentagem_vitorias = (vitorias_com_carta / total_batalhas_com_carta) * 100
    porcentagem_derrotas = (derrotas_com_carta / total_batalhas_com_carta) * 100

    print(f'Porcentagem de vitórias usando a carta "{carta}": {porcentagem_vitorias:.2f}%')
    print(f'Porcentagem de derrotas usando a carta "{carta}": {porcentagem_derrotas:.2f}%')
    print(f'Total de batalhas com a carta "{carta}": {total_batalhas_com_carta}')   
#Uso:
# calcular_porcentagem_vitorias_derrotas('Zap', '2024-09-30 16:06:22', '2024-09-30 16:14:32')


# consulta 2: Liste os decks completos que produziram mais porcentagem de vitorias (x%) ocorrida em um intervalo de timestamps 
def calcular_decks_com_mais_de_70_porcento_vitorias(timestamp_inicio, timestamp_fim):
    timestamp_inicio = datetime.strptime(timestamp_inicio, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
    timestamp_fim = datetime.strptime(timestamp_fim, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)

    batalhas = resultados.find({
        'data_hora_batalha.inicio': {'$gte': timestamp_inicio.strftime('%Y-%m-%d %H:%M:%S')},
        'data_hora_batalha.fim': {'$lte': timestamp_fim.strftime('%Y-%m-%d %H:%M:%S')}
    })

    # Dicionários para armazenar vitórias, derrotas e a associação entre decks e jogadores
    deck_vitorias = {}
    deck_derrotas = {}
    deck_jogador_associado = {}

    for batalha in batalhas:
         # Recupera os jogadores associados à batalha
        jogador1 = collection.find_one({'nome': batalha['jogador1']})
        jogador2 = collection.find_one({'nome': batalha['jogador2']})
         
         # Cria tuplas ordenadas representando os decks dos jogadores
        deck_jogador1 = tuple(sorted([c['name'] for c in jogador1['deck']]))
        deck_jogador2 = tuple(sorted([c['name'] for c in jogador2['deck']]))
        
        # Inicializa contadores para vitórias e derrotas se o deck ainda não foi registrado
        if deck_jogador1 not in deck_vitorias:
            deck_vitorias[deck_jogador1] = 0
            deck_derrotas[deck_jogador1] = 0
            deck_jogador_associado[deck_jogador1] = jogador1['nome']
        if deck_jogador2 not in deck_vitorias:
            deck_vitorias[deck_jogador2] = 0
            deck_derrotas[deck_jogador2] = 0
            deck_jogador_associado[deck_jogador2] = jogador2['nome']

        # Atualiza o número de vitórias e derrotas com base no resultado da batalha
        if batalha['vitoria_jogador1']:
            deck_vitorias[deck_jogador1] += 1
            deck_derrotas[deck_jogador2] += 1
        else:
            deck_vitorias[deck_jogador2] += 1
            deck_derrotas[deck_jogador1] += 1
    
    # Lista para armazenar decks que possuem mais de 70% de vitórias
    decks_com_mais_de_70_porcento_vitorias = []

    for deck, vitorias in deck_vitorias.items():
        total_batalhas = vitorias + deck_derrotas[deck]
        if total_batalhas > 0:
            porcentagem_vitorias = (vitorias / total_batalhas) * 100
            if porcentagem_vitorias > 70:
                decks_com_mais_de_70_porcento_vitorias.append({
                    'deck': deck,
                    'porcentagem_vitorias': porcentagem_vitorias,
                    'jogador': deck_jogador_associado[deck]
                })
    # Imprime os resultados ou uma mensagem caso não haja decks com mais de 70% de vitórias
    if decks_com_mais_de_70_porcento_vitorias:
        for deck_info in decks_com_mais_de_70_porcento_vitorias:
            print(f"Deck: {deck_info['deck']}")
            print(f"Porcentagem de vitórias: {deck_info['porcentagem_vitorias']:.2f}%")
            print(f"Pertence ao jogador: {deck_info['jogador']}")
            print('-' * 40)
    else:
        print('Nenhum deck com mais de 70% de vitórias encontrado no intervalo fornecido.')

# Uso:
# calcular_decks_com_mais_de_70_porcento_vitorias('2024-09-30 16:06:22', '2024-09-30 16:33:56')

#consulta 3: Liste os decks completos que produziram mais porcentagem de vitorias (x%) ocorrida em um intervalo de timestamps 
def calcular_derrotas_com_combo(timestamp_inicio, timestamp_fim):
    timestamp_inicio = datetime.strptime(timestamp_inicio, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
    timestamp_fim = datetime.strptime(timestamp_fim, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)

    batalhas = resultados.find({
        'data_hora_batalha.inicio': {'$gte': timestamp_inicio.strftime('%Y-%m-%d %H:%M:%S')},
        'data_hora_batalha.fim': {'$lte': timestamp_fim.strftime('%Y-%m-%d %H:%M:%S')}
    })

 # Define o conjunto de cartas do combo a ser analisado
    combo_cartas = {"Musketeer", "Royal Ghost", "Electro Spirit"}
    derrotas_combo = 0

    for batalha in batalhas:
        jogador1 = collection.find_one({'nome': batalha['jogador1']})
        jogador2 = collection.find_one({'nome': batalha['jogador2']})

        deck_jogador1 = {c['name'] for c in jogador1['deck']}
        deck_jogador2 = {c['name'] for c in jogador2['deck']}
        
        #Verifica se o combo de cartas está no deck do jogador 1 e se ele perdeu a batalha
        if combo_cartas.issubset(deck_jogador1):
            if not batalha['vitoria_jogador1']:
                derrotas_combo += 1
        
        # Verifica se o combo de cartas está no deck do jogador 2 e se ele ganhou a batalha
        if combo_cartas.issubset(deck_jogador2):
            if batalha['vitoria_jogador1']:
                derrotas_combo += 1  # Conta como derrota se jogador 2 usou o combo e jogador 1 ganhou
    # Imprime a quantidade total de derrotas quando o combo foi utilizado
    print(f"Quantidade de derrotas utilizando o combo 'Musketeer', 'Royal Ghost', 'Electro Spirit': {derrotas_combo}")

# Uso:
# calcular_derrotas_com_combo('2024-09-30 16:06:22', '2024-09-30 16:33:56')

#consulta 4: Calcule a quantidade de vitorias envolvendo a carta "Electro Giant"  nos casos que o vencedor possui 20% menos trofeus que o perdedor, a partida durou menos de 2 minutos e o perdedor derrubou ao menos duas torres do adversario
def calcular_vitorias_com_condicoes(timestamp_inicio, timestamp_fim):
    timestamp_inicio = datetime.strptime(timestamp_inicio, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
    timestamp_fim = datetime.strptime(timestamp_fim, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)

    batalhas = resultados.find({
        'data_hora_batalha.inicio': {'$gte': timestamp_inicio.strftime('%Y-%m-%d %H:%M:%S')},
        'data_hora_batalha.fim': {'$lte': timestamp_fim.strftime('%Y-%m-%d %H:%M:%S')}
    })

    vitorias_condicionais = 0
    carta_especifica = "Electro Giant"  # Define a carta específica a ser verificada

    for batalha in batalhas:
        jogador1 = collection.find_one({'nome': batalha['jogador1']})
        jogador2 = collection.find_one({'nome': batalha['jogador2']})

        # Calcular duração da batalha
        inicio_batalha = datetime.strptime(batalha['data_hora_batalha']['inicio'], '%Y-%m-%d %H:%M:%S')
        fim_batalha = datetime.strptime(batalha['data_hora_batalha']['fim'], '%Y-%m-%d %H:%M:%S')
        duracao_batalha = fim_batalha - inicio_batalha  # Duração em segundos

        # Obtém a quantidade de troféus dos jogadores
        trofeus_jogador1 = jogador1['trofeus']
        trofeus_jogador2 = jogador2['trofeus']

        # Determina quem é o vencedor e o perdedor da batalha
        if batalha['vitoria_jogador1']:
            vencedor = jogador1
            perdedor = jogador2
            vencedor_torres = batalha['torres_jogador1']
            perdedor_torres = batalha['torres_jogador2']
        else:
            vencedor = jogador2
            perdedor = jogador1
            vencedor_torres = batalha['torres_jogador2']
            perdedor_torres = batalha['torres_jogador1']

        # Verificar se o vencedor tem 20% menos troféus que o perdedor
        if vencedor['trofeus'] < perdedor['trofeus'] * 0.8:
            # Verificar se a batalha durou menos de 2 minutos
            if duracao_batalha.total_seconds() < 120:
                # Verificar se o perdedor derrubou pelo menos duas torres
                if perdedor_torres >= 2:
                    # Verificar se o vencedor usou a carta "Electro Giant"
                    deck_vencedor = {c['name'] for c in vencedor['deck']}
                    if carta_especifica in deck_vencedor:
                        vitorias_condicionais += 1

    print(f"Quantidade de vitórias com 'Electro Giant' nas condições especificadas: {vitorias_condicionais}")

# Uso:
# calcular_vitorias_com_condicoes('2024-09-30 16:06:22', '2024-09-30 16:33:56')

#consulta 5:Liste o combo de cartas que produziram mais de 50% de vitorias ocorridas em um intervalo de timestamps.
def calcular_combos_vitoriosos(timestamp_inicio, timestamp_fim):
    timestamp_inicio = datetime.strptime(timestamp_inicio, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
    timestamp_fim = datetime.strptime(timestamp_fim, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)

    # Buscar todas as batalhas no intervalo de tempo especificado
    batalhas = resultados.find({
        'data_hora_batalha.inicio': {'$gte': timestamp_inicio.strftime('%Y-%m-%d %H:%M:%S')},
        'data_hora_batalha.fim': {'$lte': timestamp_fim.strftime('%Y-%m-%d %H:%M:%S')}
    })

    # Dicionário para contar vitórias por combo de cartas
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

        # Contabilizar vitórias
        if deck_vencedor in combos_vitorias:
            combos_vitorias[deck_vencedor] += 1
        else:
            combos_vitorias[deck_vencedor] = 1

        # Contabilizar total de jogos
        if deck_vencedor in total_combos:
            total_combos[deck_vencedor] += 1
        else:
            total_combos[deck_vencedor] = 1

    # Lista de combos com mais de 50% de vitórias
    combos_vitoriosos = []

    for combo in combos_vitorias:
        vitorias = combos_vitorias[combo]
        total = total_combos[combo]
        if total > 0:
            porcentagem_vitorias = (vitorias / total) * 100
            if porcentagem_vitorias > 50:
                combos_vitoriosos.append((combo, porcentagem_vitorias))

    # Ordenar os combos pela porcentagem de vitórias
    combos_vitoriosos.sort(key=lambda x: x[1], reverse=True)

    # Exibir os combos vitoriosos
    for combo, porcentagem in combos_vitoriosos:
        print(f"Combo: {combo} -> {porcentagem:.2f}% de vitórias")

# Uso:
# calcular_combos_vitoriosos('2024-09-30 16:00:00', '2024-09-30 16:33:56')




# =============================== INTERFACE ===============================================================================
st.title("Análise de Batalhas")

# Seção para calcular porcentagem de vitórias/derrotas de uma carta
st.header("Porcentagem de Vitórias/Derrota de uma Carta")
carta = st.text_input("Nome da Carta")
timestamp_inicio = st.text_input("Data e Hora de Início (YYYY-MM-DD HH:MM:SS)")
timestamp_fim = st.text_input("Data e Hora de Fim (YYYY-MM-DD HH:MM:SS)")
if st.button("Calcular"):
    calcular_porcentagem_vitorias_derrotas('Zap', '2024-09-30 16:00:00', '2024-09-30 16:33:56')

# Seção para calcular decks com mais de 70% de vitórias
st.header("Decks com Mais de 70% de Vitórias")
if st.button("Listar Decks"):
    calcular_decks_com_mais_de_70_porcento_vitorias('2024-09-30 16:00:00', '2024-09-30 16:33:56')

# Seção para calcular derrotas com combo específico
st.header("Derrotas com Combo de Cartas")
if st.button("Calcular Derrotas"):
    calcular_derrotas_com_combo('2024-09-30 16:00:00', '2024-09-30 16:33:56')

# Seção para calcular vitórias com condições específicas
st.header("Vitórias com Condições Específicas")
if st.button("Calcular Vitórias"):
    calcular_vitorias_com_condicoes('2024-09-30 16:00:00', '2024-09-30 16:33:56')

# Seção para calcular combos vitoriosos
st.header("Combos Vitoriosos")
if st.button("Listar Combos Vitoriosos"):
    calcular_combos_vitoriosos('2024-09-30 16:00:00', '2024-09-30 16:33:56')
