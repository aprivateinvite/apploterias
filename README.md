# App Loterias

Um gerador de apostas otimizado para **Mega-Sena, Lotofácil e Mais Milionária**, construído com Python e Flet. 
Inclui um banco de dados local com resultados, fallback de API e algoritmo de peso para números "quentes" (frequentes).

## Instalação e Execução

### Pré-requisitos
- Python 3.10+ instalado.

### 1. Instalar dependências
No terminal, execute:
```bash
pip install -r requirements.txt
```

### 2. Rodar o App (Desktop)
```bash
flet run -a main.py
```

### 3. Build para Android (APK)
```bash
flet build apk --release
```
> Obs: Certifique-se de que o Flutter SDK está devidamente configurado para realizar builds móveis.

### 4. Build para iOS
```bash
flet build ios
```
> Obs: Requer macOS e XCode.

## Funcionalidades
- **Suporte Offline**: Caso as APIs oficias estejam fora do ar, o aplicativo insere os sorteios "mockados" e continua funcionando baseado no banco local.
- **Exportar Arquivo**: Permite salvar todos os números gerados num arquivo TXT direto na memória do celular.
- **Modo 'Mais Sorteados'**: Utiliza os resultados guardados na base SQLite para aumentar a probabilidade de sorteio dos números que caem com maior frequência.
