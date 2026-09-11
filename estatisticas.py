import random
from database import buscar_sorteios

REGRAS = {
    'megasena': {'total_dezenas': 60, 'sorteio': 6, 'min_dezenas': 6, 'max_dezenas': 20, 'trevos': 0},
    'lotofacil': {'total_dezenas': 25, 'sorteio': 15, 'min_dezenas': 15, 'max_dezenas': 20, 'trevos': 0},
    'maismilionaria': {'total_dezenas': 50, 'sorteio': 6, 'min_dezenas': 6, 'max_dezenas': 12, 'trevos': 2, 'total_trevos': 6}
}

def calcular_frequencias(modalidade: str):
    sorteios = buscar_sorteios(modalidade)
    
    frequencia_dezenas = {}
    frequencia_trevos = {}
    
    for s in sorteios:
        for dezena in s['dezenas']:
            d_int = int(dezena)
            frequencia_dezenas[d_int] = frequencia_dezenas.get(d_int, 0) + 1
            
        for trevo in s['trevos']:
            t_int = int(trevo)
            frequencia_trevos[t_int] = frequencia_trevos.get(t_int, 0) + 1
            
    return frequencia_dezenas, frequencia_trevos

def gerar_combinacoes(modalidade: str, quantidade: int, usar_quentes: bool, dezenas_fixas: list = None, tamanho_aposta: int = None):
    regra = REGRAS[modalidade]
    resultados = []
    
    dezenas_fixas = dezenas_fixas or []
    tamanho_aposta = tamanho_aposta or regra['sorteio']
    
    frequencia_dezenas, frequencia_trevos = {}, {}
    if usar_quentes:
        frequencia_dezenas, frequencia_trevos = calcular_frequencias(modalidade)
    
    for _ in range(quantidade):
        combinacao = dezenas_fixas.copy()
        trevos = []
        
        # Gerar dezenas
        populacao_dezenas = [n for n in range(1, regra['total_dezenas'] + 1) if n not in combinacao]
        
        if usar_quentes and frequencia_dezenas:
            pesos = [frequencia_dezenas.get(n, 1) for n in populacao_dezenas]
            while len(combinacao) < tamanho_aposta:
                # random.choices retorna com reposição, precisamos sem reposição
                escolhido = random.choices(populacao_dezenas, weights=pesos, k=1)[0]
                if escolhido not in combinacao:
                    combinacao.append(escolhido)
        else:
            faltam = tamanho_aposta - len(combinacao)
            if faltam > 0:
                combinacao.extend(random.sample(populacao_dezenas, faltam))
            
        combinacao.sort()
        
        # Gerar trevos se for Mais Milionária
        if regra['trevos'] > 0:
            populacao_trevos = list(range(1, regra['total_trevos'] + 1))
            if usar_quentes and frequencia_trevos:
                pesos_trevos = [frequencia_trevos.get(n, 1) for n in populacao_trevos]
                while len(trevos) < regra['trevos']:
                    escolhido = random.choices(populacao_trevos, weights=pesos_trevos, k=1)[0]
                    if escolhido not in trevos:
                        trevos.append(escolhido)
            else:
                trevos = random.sample(populacao_trevos, regra['trevos'])
            trevos.sort()
            
        resultados.append({
            'dezenas': [f"{n:02d}" for n in combinacao],
            'trevos': [f"{n}" for n in trevos] if trevos else []
        })
        
    return resultados
