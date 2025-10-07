import os
from datetime import datetime

PASTA_RESULTADOS = os.path.join("extratores", "resultados")
ARQUIVO_LOG = os.path.join(PASTA_RESULTADOS, "log_de_execucao.txt")

def iniciar_log():
    """Cria a pasta de resultados e inicia um novo log com um cabeçalho."""
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mensagem = f"\n{'='*80}\nINÍCIO DA EXECUÇÃO DO PIPELINE EM: {timestamp}\n{'='*80}\n"
    with open(ARQUIVO_LOG, 'a', encoding='utf-8') as f:
        f.write(mensagem)

def logar(mensagem: str):
    """Adiciona uma mensagem com timestamp ao arquivo de log e ao console."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_formatado = f"[{timestamp}] - {mensagem}"
    print(log_formatado)
    with open(ARQUIVO_LOG, 'a', encoding='utf-8') as f:
        f.write(log_formatado + "\n")