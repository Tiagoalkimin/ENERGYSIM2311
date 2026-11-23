# EnergySim

Demonstração de desperdício de energia em computadores para apresentação de aproximadamente dois minutos. Abre diretamente no painel, sem cadastro ou configuração prévia.

## Executar

Use Python 3.12, a versão validada para o projeto. Abra o terminal na pasta que contém `app.py`.

```bash
python -m venv .venv
```

No Windows:

```powershell
.venv\Scripts\activate
```

No macOS ou Linux:

```bash
source .venv/bin/activate
```

Instale e execute:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Abra http://localhost:8501. O tema é carregado da pasta .streamlit, por isso execute na pasta do projeto. A interface não requer serviços externos, sensores ou conta. Faça a instalação das dependências antes do evento.

## Publicar no Streamlit Community Cloud

Se você recebeu o projeto em ZIP, extraia a pasta `EnergySim` e rode `git init -b main` nela para criar o repositório local.

1. No GitHub Desktop, adicione a pasta que contém `app.py` em **File → Add local repository**. Faça o primeiro commit se a pasta veio do ZIP. Com a branch `main` selecionada, use **Publish repository**.
2. Em [Streamlit Community Cloud](https://share.streamlit.io/), conecte sua conta do GitHub e selecione **Create app**. Escolha seu repositório e preencha **Branch** com `main` e **Main file path** com `app.py`.
3. Em **Advanced settings**, escolha **Python 3.12**. O Community Cloud instala as dependências de `requirements.txt` e carrega o tema de `.streamlit/config.toml`. O app usa dados simulados e dispensa configuração de segredos.
4. Clique em **Deploy** e abra o endereço `streamlit.app` gerado.

## Demonstração

1. Observe os quatro indicadores de um PC intermediário executando navegador e documentos.
2. Clique em **1. Mostrar consumo extra**. O consumo extra de processos em segundo plano aparece imediatamente e dispara o alerta.
3. Clique em **2. Simular otimização**. A mesma tela compara potência, temperatura, percentual de redução, energia e custo mensal.
4. Use **Recomeçar** para uma nova apresentação. A tarifa configurada é mantida.

Os dois cliques não impõem duração mínima. O roteiro em docs/ROTEIRO_HACKATHON.md distribui a explicação em 120 segundos, dentro da faixa solicitada de 90 a 150 segundos. A duração ao vivo depende do apresentador.

## Valores e limites

Todos os indicadores são simulados. Nenhum processo real é encerrado e nenhum consumo real de hardware é medido. A utilização útil de CPU e GPU permanece fixa, isolando a parcela de 90 W adicionada pelo modelo. Essa parcela é um recurso didático, não uma estimativa de consumo de um programa específico.

A faixa esperada usa as faixas originais da tarefa e a margem de detecção de 15%. O cálculo de potência e a resposta térmica de primeira ordem reutilizam o motor original. Cada cenário avança 180 segundos simulados sem espera real. A temperatura exibida após a intervenção representa o final desse intervalo, não resfriamento instantâneo. O cenário escolhido permanece abaixo dos limiares de instabilidade e não apresenta falhas físicas.

O custo mensal considera potência constante por 8 horas diárias, durante 30 dias, com tarifa ilustrativa padrão de R$ 0,90/kWh. Altere a tarifa em **Premissas da simulação e tarifa**.

Fórmulas:

```text
energia mensal = potência em W / 1000 × 8 × 30
custo mensal = energia mensal × tarifa
redução percentual = (potência antes - potência depois) / potência antes × 100
economia mensal = custo antes - custo depois
```

No cenário padrão: 162,4 W antes, 72,4 W depois, redução de 55,4%, economia de 21,60 kWh e R$ 19,44 por mês. Esses números são calculados pelo modelo. A economia usa cenários com a mesma duração mensal, não o histórico acumulado durante os cliques.

## Recursos preservados

O botão **Explorar o modo completo** abre 19 etapas com três perfis de computador, atividades, recomendações, relatórios, teste de estresse e oito experimentos. O botão **Voltar à demonstração rápida** fica no fim de cada etapa.

Os cálculos e o comportamento legado não foram reescritos. As simulações antigas de instabilidade continuam apenas no modo educativo completo, com seus avisos originais. O novo comparativo usa um cálculo próprio e explícito entre dois estados da mesma tarefa. Não depende do percentual histórico do relatório legado.

## Estrutura alterada

* app.py: registro da demonstração como tela inicial e retorno pelo menu.
* ui/demo.py: painel com quatro indicadores e comparação visual.
* core/demo.py: fluxo controlado que reutiliza Simulator, inject_waste e apply_decision.
* .streamlit/config.toml: tema claro do app.
* tests/: testes de fluxo, cálculos, persistência, tarifa e compatibilidade.
* docs/: análise inicial, roteiro de apresentação e documentação original.

## Verificação

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem a detecção de consumo extra, a otimização, a tarifa, o reinício, a navegação e o funcionamento básico do simulador, do relatório e do teste de estresse.

## Interface para apresentação em hackathon

A demonstração inicial apresenta indicadores resumidos e uma comparação visual de antes e depois. O código dos cálculos fica em `core/demo.py`.

O roteiro sugerido para apresentar o projeto à banca está em `docs/ROTEIRO_HACKATHON.md`.
