import aiohttp
import asyncio
from database import inserir_sorteio

MOCK_DATA = {
    'megasena': [
        {'concurso': 2500, 'data': '01/01/2023', 'dezenas': ['01', '10', '20', '30', '40', '50']},
        {'concurso': 2501, 'data': '04/01/2023', 'dezenas': ['05', '15', '25', '35', '45', '55']},
        {'concurso': 2502, 'data': '08/01/2023', 'dezenas': ['02', '12', '22', '32', '42', '52']}
    ],
    'lotofacil': [
        {'concurso': 2500, 'data': '01/01/2023', 'dezenas': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15']},
        {'concurso': 2501, 'data': '02/01/2023', 'dezenas': ['02', '04', '06', '08', '10', '12', '14', '16', '18', '20', '21', '22', '23', '24', '25']},
        {'concurso': 2502, 'data': '03/01/2023', 'dezenas': ['01', '03', '05', '07', '09', '11', '13', '15', '17', '19', '21', '22', '23', '24', '25']}
    ],
    'maismilionaria': [
        {'concurso': 100, 'data': '01/01/2023', 'dezenas': ['01', '10', '20', '30', '40', '50'], 'trevos': ['1', '2']},
        {'concurso': 101, 'data': '08/01/2023', 'dezenas': ['05', '15', '25', '35', '45', '49'], 'trevos': ['3', '4']},
        {'concurso': 102, 'data': '15/01/2023', 'dezenas': ['02', '12', '22', '32', '42', '48'], 'trevos': ['5', '6']}
    ]
}

async def fetch_loteriascaixa_api(session, modalidade):
    url = f"https://loteriascaixa-api.herokuapp.com/api/{modalidade}/latest"
    # Pegando só o último para testar a comunicação e pegar resultados recentes. 
    # Opcional: pegar a lista toda de concursos e baixar. Para evitar timeout, pegamos apenas os últimos resultados.
    # Note: herokuapp API pode estar fora do ar.
    async with session.get(url, timeout=10) as response:
        response.raise_for_status()
        return await response.json()

async def fetch_guidi_api(session, modalidade):
    url = f"https://loteria.guidi.dev.br/api/v1/resultados/{modalidade}"
    async with session.get(url, timeout=10) as response:
        response.raise_for_status()
        # O Guidi API pode retornar uma lista ou o mais recente, precisa testar. 
        # Assumiremos um dict com 'numero', 'data', 'dezenas'.
        return await response.json()

async def atualizar_dados(modalidade: str) -> bool:
    """
    Tenta baixar dados da API. Retorna True se conseguiu baixar, False se falhou e usou mock.
    """
    try:
        async with aiohttp.ClientSession() as session:
            try:
                # Tenta API Primária
                dados = await fetch_loteriascaixa_api(session, modalidade)
                # Formatar os dados para salvar
                # Assumindo que a herokuapp retorna: {'concurso': 123, 'data': '...', 'dezenas': ['01',...], 'trevos': [...]}
                concurso = int(dados.get('concurso', 0))
                data = dados.get('data', '')
                dezenas = dados.get('dezenas', [])
                trevos = dados.get('trevos', [])
                if concurso:
                    inserir_sorteio(concurso, modalidade, data, dezenas, trevos)
                return True
                
            except Exception as e:
                print(f"Erro na API 1: {e}")
                try:
                    # Tenta API Secundária
                    dados = await fetch_guidi_api(session, modalidade)
                    concurso = int(dados.get('numero', 0))
                    data = dados.get('data', '')
                    dezenas = dados.get('dezenas', [])
                    trevos = dados.get('trevos', [])
                    if concurso:
                        inserir_sorteio(concurso, modalidade, data, dezenas, trevos)
                    return True
                except Exception as e2:
                    print(f"Erro na API 2: {e2}")
                    raise e2 # Vai pro block de except geral

    except Exception as general_e:
        print(f"Ambas APIs falharam para {modalidade}: {general_e}")
        # Falhou, usa Mock
        for item in MOCK_DATA.get(modalidade, []):
            inserir_sorteio(item['concurso'], modalidade, item['data'], item['dezenas'], item.get('trevos'))
        return False
