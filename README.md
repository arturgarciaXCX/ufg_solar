# ufg_solar
Repositório do Projeto de Finalização de Curso do curso de Engenharia de Computação na Universidade Federal de Goiás

## Visão Geral da Arquitetura

O projeto é dividido em camadas lógicas, cada uma contida em seu próprio diretório:
- **`credenciais`**: Gerencia o acesso seguro a bancos de dados e APIs.
- **`bancos`** e **`apis`**: Camadas de baixo nível responsáveis pela comunicação com as fontes de dados (internas e externas).
- **`extratores`**: Camada de orquestração e lógica de negócio, que utiliza os outros componentes para executar o pipeline completo.

---

### 📁 `credenciais/`
Esta pasta centraliza todas as informações sensíveis e a lógica para carregá-las, garantindo que o código-fonte permaneça livre de senhas ou chaves de API.

- **📄 `credenciais_apis.xlsx`** e **📄 `credenciais_bancos.xlsx`**: Planilhas Excel que armazenam as credenciais de acesso para as APIs externas (Solis, WEG, Solarman) e para os bancos de dados (Supabase, SideUFG), respectivamente. **Esses arquivos nunca devem ser enviados para o GitHub e devem estar no seu arquivo `.gitignore`**.
- **📄 `gerenciador_credenciais.py`**: Módulo responsável por ler as planilhas `.xlsx` e carregar as credenciais de forma segura em dicionários Python. Esses dicionários são importados e utilizados pelos módulos das pastas `bancos` e `apis`.

### 📁 `bancos/`
Contém os "clientes" de banco de dados. Cada módulo aqui é um especialista em se comunicar com um banco de dados específico.

- **📄 `funcs_supabase.py`**: Centraliza toda a comunicação com o banco de dados Supabase. Ele gerencia uma conexão de cliente única e eficiente e fornece funções genéricas para realizar consultas (`consultar_supabase`) e buscar valores específicos (`obter_valor_maximo_coluna`).
- **📄 `funcs_sideufg.py`**: Responsável por toda a comunicação com o banco de dados PostgreSQL (SideUFG), fornecendo uma função genérica para executar consultas SQL.

### 📁 `apis/`
Similar à pasta `bancos`, esta contém os clientes para as APIs externas. Cada módulo encapsula a complexidade de autenticação e chamada de endpoints de uma plataforma.

- **📄 `funcs_solis.py`**: Contém toda a lógica para interagir com a API da Solis, incluindo a complexa geração de cabeçalhos de autenticação e a iteração diária para busca de dados históricos.
- **📄 `funcs_weg.py`**: Responsável por se comunicar com a API da WEG, ajustando os parâmetros de data/hora para o fuso horário correto (UTC-3) e realizando a busca de dados dia a dia.
- **📄 `funcs_solarman.py`**: Gerencia a comunicação com a API da Solarman, incluindo o processo de obtenção e atualização de tokens de acesso e a busca de dados históricos por dia.

### 📁 `extratores/`
O coração do projeto, onde a orquestração acontece. Este diretório contém os pipelines de alto nível e seus componentes.

#### 📁 `extratores/parametros/`
Módulos responsáveis por gerar dinamicamente os parâmetros necessários para cada execução.

- **📄 `parametros_inversores.py`**: Consulta o banco Supabase para obter a lista de inversores de cada plataforma. Ele gera uma estrutura de dados que contém tanto o número de série original do inversor (`sn_original`) quanto o identificador formatado para a API (`id_formatado`).
- **📄 `parametros_datas.py`**: Calcula o intervalo de tempo correto para cada extração. Para cada inversor, ele busca a data da última leitura no Supabase para definir a `data_inicio` e usa a data/hora atual para a `data_fim`. Também contém a lógica para ajustar o fuso horário da Solis.

#### 📁 `extratores/tratamento/`
Módulos responsáveis por transformar os dados brutos extraídos em formatos padronizados, prontos para serem carregados no banco de dados.

- **📄 `tratamento_solis.py`**, **📄 `tratamento_weg.py`**, **📄 `tratamento_solarman.py`**: Cada um desses arquivos contém uma função que recebe um DataFrame de dados brutos de sua respectiva plataforma e retorna dois DataFrames:
    1.  **Completo**: Contém todos os dados originais, com colunas renomeadas e um ID único, pronto para uma tabela de log detalhada.
    2.  **Resumido**: Contém apenas as colunas essenciais (`data_hora`, `inversor_sn`, `potencia_kw`, etc.), padronizadas para serem inseridas na tabela principal `leitura`.

#### Arquivos Principais

- **📄 `extrator_sideufg.py`**, **📄 `extrator_solis.py`**, **📄 `extrator_weg.py`**, **📄 `extrator_solarman.py`**: São os scripts de pipeline individuais para cada fonte de dados. O fluxo de cada um é:
    1.  Chamar os módulos de `parametros` para obter a lista de inversores e os intervalos de data.
    2.  Chamar o módulo `apis` ou `bancos` correspondente para extrair os dados brutos.
    3.  Chamar o módulo `tratamento` correspondente para processar os dados.
    4.  Salvar os dois DataFrames resultantes em arquivos CSV na pasta `resultados`.

- **📄 `teste_extratores.py`**: O script mestre do projeto. Ele serve como ponto de entrada para executar todo o processo de ETL em sequência. Ele importa e chama a função principal de cada um dos scripts extratores, orquestrando a extração completa de todas as fontes.

#### 📁 `extratores/resultados/`
Esta pasta é criada automaticamente pelo `teste_extratores.py` e é para onde todos os arquivos CSV de resultado são salvos. Ela serve como um "armazém temporário" dos dados tratados, validando que todo o processo de extração e tratamento funcionou corretamente antes da futura implementação do carregamento para o banco.
