# -*- coding: utf-8 -*-
"""EnergySim — Simulador de Consumo Energético de Computadores
Projeto de Hackathon de Engenharia da Computação.

Rode com: streamlit run app.py
"""

from pathlib import Path

import streamlit as st
import pandas as pd

from models.computer import hardware_details, Computer, COMPUTER_PRESETS
from models.activities import ACTIVITIES, get_task
from core.simulator import StressTest
from core import report as report_mod
from core import stress as stress_mod
from core import experiments as exp_mod
from ui.demo import render_comparison, render_demo
from ui.lab import render_line, render_scatter, render_table

st.set_page_config(page_title="EnergySim", page_icon="⚡", layout="wide")

stylesheet = Path(__file__).with_name("ui") / "theme.css"
st.markdown(f"<style>{stylesheet.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

SCREENS = [
    "intro_problema",
    "novidade", "afetados", "impactos", "solucoes",
    "intro_objetivo", "intro_voltagem",
    "intro_quartzo", "intro_geometria",
    "demo", "comparativo",
    "teste_estresse_intro", "teste_estresse_execucao",
    "teste_estresse_resultado", "teste_estresse_explicacao",
    "laboratorio",
    "conclusao",
]

# ---------------------------------------------------------------- estado ----
if st.session_state.get("screen") not in SCREENS:
    st.session_state.screen = SCREENS[0]
if "stress_test" not in st.session_state:
    st.session_state.stress_test = None
if "stress_test_report" not in st.session_state:
    st.session_state.stress_test_report = None


def goto(screen_key):
    st.session_state.screen = screen_key
    st.rerun()


def nav_buttons(prev_key=None, next_key=None, next_label="Continuar →", prev_label="← Voltar"):
    actions = [(prev_key, prev_label, "secondary"), (next_key, next_label, "primary")]
    available = [action for action in actions if action[0]]
    for col, (target, label, kind) in zip(st.columns(len(available)), available):
        if col.button(label, type=kind, width="stretch"):
            goto(target)

# ========================================================== TELA: PROBLEMA ==
def screen_intro_problema():
    st.title("Qual é o problema?")
    st.markdown("""
Todo computador **consome energia elétrica** — mas essa quantidade não é fixa.
Ela muda de acordo com:

- a **carga da CPU** (processamento);
- a **carga da GPU** (gráficos);
- a **tarefa realizada** (navegar é diferente de renderizar um vídeo);
- o **tempo de utilização**;
- as **configurações de desempenho** escolhidas.

Computadores mais potentes **podem consumir muito mais energia** quando
usados em cargas elevadas — e a maioria das pessoas nunca vê esse consumo
acontecer em tempo real.
    """)
    st.info("Este simulador torna esse processo **visível**.")
    nav_buttons(next_key="novidade")


# ========================================================== TELA: OBJETIVO ==
def screen_intro_objetivo():
    st.title("Objetivo do simulador")
    st.markdown("""
Este simulador representa, **de forma simplificada**, o que acontece na
prática dentro de um computador:

> **CPU + GPU + outros componentes → consumo → calor → temperatura → energia → custo**

Ele não pretende reproduzir perfeitamente um computador real — os valores são
**estimativas plausíveis para fins educacionais**, construídas a partir de
perfis de hardware modernos.
    """)
    nav_buttons(prev_key="solucoes", next_key="intro_voltagem")


# ========================================================== TELA: VOLTAGEM ==
def screen_intro_voltagem():
    st.title("Um pouco de eletricidade")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
- **Tensão (V):** "força" que empurra a corrente elétrica.
- **Corrente (A):** quantidade de carga elétrica que flui por segundo.
- **Potência (W):** V × A — energia usada *por instante*.
- **Energia (kWh):** potência **ao longo do tempo** — o que a concessionária cobra.
        """)
    with col2:
        st.markdown("""
O computador **não usa direto** os 127/220 V da tomada:

**Tomada → Fonte → Placa-mãe / VRM → CPU / GPU**

O **VRM** regula a tensão que chega ao processador. Quando a carga aumenta,
o VRM eleva ligeiramente a tensão para sustentar o clock — e isso **aumenta a
potência consumida e o calor gerado**.
        """)
    st.caption("Simplificado de propósito — o objetivo é intuição, não uma aula de eletrônica.")
    nav_buttons(prev_key="intro_objetivo", next_key="intro_quartzo")


# ========================================================== TELA: QUARTZO ==
def screen_intro_quartzo():
    st.title("O papel do quartzo")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
Cristais de **quartzo** são usados em **osciladores de frequência/clock**,
ajudando o computador a ter uma **referência de tempo estável**.

> O quartzo pode ser usado para ajudar a manter uma frequência de referência
> estável nos circuitos eletrônicos. Essa referência funciona como um
> "relógio" para organizar o funcionamento dos componentes.

**Analogia:** imagine uma banda tocando música. O clock funciona como o
ritmo que ajuda todos os instrumentos a permanecerem sincronizados.
        """)
    with col2:
        st.info(
            "**O que o quartzo NÃO faz:** ele não retira calor da CPU e não "
            "é responsável por resfriar o computador. Sua função é fornecer "
            "uma referência de frequência estável — quem cuida do calor é o "
            "sistema de refrigeração (ventoinhas, dissipadores, water cooler) "
            "e a geometria dos componentes, como você verá na próxima tela."
        )
        st.warning(
            "A temperatura pode, sim, influenciar circuitos eletrônicos "
            "(incluindo os que dependem de uma referência de frequência). Por "
            "isso, mais adiante, o simulador mostra uma pequena variação de "
            "clock em altas temperaturas — deixamos claro que isso é uma "
            "**simplificação educativa**, não um efeito direto do quartzo."
        )
    nav_buttons(prev_key="intro_voltagem", next_key="intro_geometria")


# ======================================================== TELA: GEOMETRIA ==
def screen_intro_geometria():
    st.title("Por que o formato dos componentes importa?")
    st.markdown("""
A **geometria** de um dissipador de calor influencia diretamente sua
capacidade de resfriar um componente: quanto **maior a área de contato com o
ar**, mais calor ele consegue transferir para fora.
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Componente de entrada")
        st.code(
            "┌──────────────┐\n"
            "│      CPU     │\n"
            "└──────────────┘\n"
            "     █████\n"
            "     █████",
            language=None,
        )
        st.caption("Dissipador pequeno, poucas aletas → pouca área para liberar calor.")
    with col2:
        st.markdown("#### Componente High-End")
        st.code(
            "│ │ │ │ │ │ │\n"
            "│ │ │ │ │ │ │\n"
            "█████████████\n"
            "     CPU",
            language=None,
        )
        st.caption("Dissipador com várias aletas → mais área de contato com o ar.")

    st.success(
        "As aletas aumentam a área disponível para transferir calor para o ar. "
        "Isso pode ajudar o componente a trabalhar em temperaturas menores."
    )

    st.markdown("#### Fluxo de ar")
    st.markdown(
        "**AR FRIO → COMPONENTE → AR QUENTE.** Uma boa circulação de ar ajuda a "
        "retirar o calor acumulado dentro do computador."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.caption("PC de Entrada: fluxo de ar mais simples")
        st.text("❄️ →  [CPU]  → 🔥")
    with c2:
        st.caption("PC High-End: fluxo de ar melhor, VRM mais robusta")
        st.text("❄️❄️❄️ →  [CPU]  → 🔥🔥🔥")

    st.caption(
        "No simulador, essa diferença de geometria e fluxo de ar já está "
        "representada pelos parâmetros de refrigeração de cada PC (o quão "
        "rápido ele esfria e qual a temperatura máxima que costuma atingir)."
    )
    nav_buttons(prev_key="intro_quartzo", next_key="demo", next_label="Abrir demonstração rápida →")


def screen_demo():
    demo = render_demo()
    next_screen = "comparativo" if demo.stage == "optimized" else None
    nav_buttons(prev_key="intro_geometria", next_key=next_screen, next_label="Ver comparativo →")


def screen_comparativo():
    demo = st.session_state.get("quick_demo")
    if demo is None or not render_comparison(demo):
        st.info("Conclua a otimização na demonstração para ver a comparação.")
        nav_buttons(prev_key="demo")
        return
    nav_buttons(prev_key="demo", next_key="teste_estresse_intro", next_label="Ir para o teste de estresse →")


# ====================================================== TELAS EXPLICATIVAS ==
def screen_novidade():
    st.title("Esse problema é novo?")
    st.markdown("""
**Não.** Eficiência energética em computação já é um problema conhecido nas
áreas de computação, eletrônica e infraestrutura. Já existem:

- gerenciamento de energia (power management);
- modos de economia de energia;
- monitoramento de hardware (sensores, telemetria);
- controle dinâmico de frequência e tensão (DVFS);
- gerenciamento térmico ativo.

O diferencial deste projeto é apresentar essas relações de forma **simples,
visual e interativa** — mostrando não só o consumo, mas **por que ele
acontece, qual o impacto e o que pode ser feito**.
    """)
    nav_buttons(prev_key="intro_problema", next_key="afetados")


def screen_afetados():
    st.title("Quem é afetado por esse problema?")
    cols = st.columns(5)
    dados = [
        ("Usuários domésticos", "Aumento na conta de energia pelo uso prolongado."),
        ("Gamers", "CPU e GPU em carga elevada por várias horas seguidas."),
        ("Estudantes/profissionais", "Computador ligado por muitas horas de trabalho/estudo."),
        ("Empresas", "Muitos computadores ligados diariamente — pequenas economias somam muito."),
        ("Data centers", "Grandes volumes de equipamentos e altíssima demanda energética."),
    ]
    for col, (titulo, texto) in zip(cols, dados):
        with col:
            with st.container(border=True):
                st.markdown(f"**{titulo}**")
                st.caption(texto)
    nav_buttons(prev_key="novidade", next_key="impactos")


def screen_impactos():
    st.title("O que esse problema causa?")
    cols = st.columns(4)
    dados = [
        ("Financeiro", "Maior consumo → maior custo de eletricidade."),
        ("Térmico", "Mais calor precisa ser dissipado — desgaste e ruído."),
        ("Desperdício", "Usar mais potência do que a tarefa exige."),
        ("Ambiental", "Consumo elétrico está ligado aos impactos da geração de energia."),
    ]
    for col, (titulo, texto) in zip(cols, dados):
        with col:
            with st.container(border=True):
                st.markdown(f"**{titulo}**")
                st.caption(texto)
    nav_buttons(prev_key="afetados", next_key="solucoes")


def screen_solucoes():
    st.title("O que podemos fazer?")
    st.markdown("""
1. **Monitorar o consumo** — W, kWh, temperatura, uso de CPU/GPU em tempo real.
2. **Modos de energia** — Economia / Equilibrado / Desempenho, conforme a necessidade.
3. **Escolher hardware adequado** — nem sempre o mais potente é o necessário.
4. **Gerenciar a GPU** — reduzir uso desnecessário em cargas leves.
5. **Gerenciar processos** — identificar aplicações consumindo recursos à toa.
6. **Melhorar a refrigeração** — reduz picos de temperatura.
7. **Detectar consumo anormal** — comparar consumo esperado × consumo real, como
   você verá na demonstração.
    """)
    nav_buttons(prev_key="impactos", next_key="intro_objetivo")


# ============================================== TESTE DE ESTRESSE / LONGA DURAÇÃO
def screen_teste_estresse_intro():
    st.title("Teste de Estresse: PC de Entrada x PC High-End")
    st.markdown("""
Um pico rápido de carga é diferente de **manter o computador trabalhando
intensamente por muito tempo**. Quanto maior o tempo sob estresse, maior a
chance de:

- aumento da temperatura;
- redução de desempenho (throttling);
- quedas de FPS;
- travamentos;
- redução da estabilidade;
- necessidade de resfriamento.

Agora vamos rodar a **mesma tarefa pesada, ao mesmo tempo**, em um **PC de
Entrada** e em um **PC High-End**, para ver essa diferença acontecer.
    """)

    st.subheader("Configurações dos computadores")
    for card, profile in zip(st.columns(2), ("entrada", "premium")):
        with card, st.container(border=True):
            computer = Computer(profile)
            st.markdown(f"### {computer.nome}")
            for label, value in hardware_details(computer):
                st.write(f"**{label}** · {value}")
            st.caption(f"Fluxo de ar {computer.fluxo_ar} · Potência máxima estimada de {computer.max_power_w():.0f} W")

    tarefas_pesadas = list(ACTIVITIES["pesado"]["tarefas"].keys())
    tarefa = st.selectbox("Tarefa do teste de estresse", options=tarefas_pesadas)

    if st.button("Iniciar teste de estresse →", type="primary"):
        ranges = get_task("pesado", tarefa)
        st.session_state.stress_test = StressTest(
            "entrada", "premium", ranges["cpu"], ranges["gpu"]
        )
        st.session_state.stress_test_report = None
        goto("teste_estresse_execucao")

    nav_buttons(prev_key="comparativo")


def screen_teste_estresse_execucao():
    test: StressTest = st.session_state.stress_test
    if test is None:
        st.warning("Inicie o teste de estresse primeiro.")
        nav_buttons(prev_key="teste_estresse_intro")
        return

    st.title("📊 Teste de Estresse em andamento")
    st.caption(
        "O desempenho indica quanto cada PC mantém da própria capacidade. "
        f"O teste usa a mesma referência térmica de {test.THERMAL_REFERENCE_C:.0f} °C para os dois perfis. "
        "Os FPS são estimativas didáticas e partem de valores de referência diferentes."
    )
    snap = test.snapshot()
    a, b = snap["a"], snap["b"]

    ALVO_S = 600  # "longa duração" de referência para a barra de progresso
    tempo_frac = min(1.0, a["t"] / ALVO_S)
    st.markdown("##### ⏱️ Tempo de teste")
    st.progress(tempo_frac, text=f"{a['t']:.0f}s / {ALVO_S}s (referência de longa duração)")

    col1, col2 = st.columns(2)
    for col, snap_pc, tier_label in ((col1, a, "PC DE ENTRADA"), (col2, b, "PC HIGH-END")):
        with col:
            st.markdown(f"### {tier_label}")
            badge = stress_mod.temp_badge(snap_pc["temp"], snap_pc["temp_max_ref"])
            st.metric("Temperatura", f"{snap_pc['temp']:.1f} °C", delta=f"{badge['emoji']} {badge['label']}", delta_color="off")
            st.progress(min(1.0, snap_pc["temp"] / snap_pc["temp_max_ref"]), text="Temperatura")
            st.metric("Desempenho", f"{snap_pc['performance_pct']:.0f} %")
            st.progress(snap_pc["performance_pct"] / 100, text="Desempenho")
            st.metric("FPS (educativo)", f"{snap_pc['fps']:.0f}",
                      delta=f"Referência inicial: {snap_pc['fps_base']:.0f}", delta_color="off")
            st.metric("Tempo sob estresse", stress_mod.fmt_mmss(snap_pc["stress_s"]))
            st.metric("Travamentos", snap_pc["lockups"])
            st.caption(f"Reinícios simulados · {snap_pc['restarts']}")
            estab_parcial = stress_mod.estabilidade_rating(
                snap_pc["lockups"], snap_pc["restarts"], snap_pc["performance_pct"]
            )
            st.write(f"**Estabilidade parcial:** {estab_parcial}")

            track = test.track_a if tier_label == "PC DE ENTRADA" else test.track_b
            if track.last_event:
                if "TELA AZUL" in track.last_event or "INSTÁVEL" in track.last_event:
                    st.error(track.last_event)
                else:
                    st.warning(track.last_event)

    if len(test.track_a.history) > 1:
        st.divider()
        st.caption("Temperatura ao longo do tempo")
        df_cmp = pd.DataFrame({
            "t": [h["t"] for h in test.track_a.history],
            "PC de Entrada": [h["temp"] for h in test.track_a.history],
            "PC High-End": [h["temp"] for h in test.track_b.history],
        }).set_index("t")
        st.line_chart(df_cmp)

    st.divider()
    t1, t2, t3 = st.columns(3)
    if t1.button("⏱️ Avançar 10s"):
        test.advance(10, passo=2)
        st.rerun()
    if t2.button("⏱️ Avançar 60s"):
        test.advance(60, passo=2)
        st.rerun()
    if t3.button("⏱️ Avançar 2 min (uso prolongado)"):
        test.advance(120, passo=5)
        st.rerun()

    st.divider()
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("← Reiniciar teste"):
            st.session_state.stress_test = None
            goto("teste_estresse_intro")
    with c2:
        if st.button("🏁 Finalizar teste e ver resultado →", type="primary"):
            st.session_state.stress_test_report = {
                "entrada": report_mod.build_stress_test_report(test.track_a),
                "high_end": report_mod.build_stress_test_report(test.track_b),
            }
            goto("teste_estresse_resultado")


def screen_teste_estresse_resultado():
    rep = st.session_state.stress_test_report
    if rep is None:
        st.warning("Finalize o teste de estresse primeiro.")
        nav_buttons(prev_key="teste_estresse_execucao")
        return

    st.title("🏁 Resultado do Teste de Estresse")
    ra, rb = rep["entrada"], rep["high_end"]

    df = pd.DataFrame({
        "": ["Temp. máxima (°C)", "Desempenho médio (%)", "FPS médio", "Travamentos", "Reinicializações", "Estabilidade"],
        "PC de Entrada": [ra["temp_max"], ra["performance_medio"], ra["fps_medio"], ra["travamentos"], ra["reinicializacoes"], ra["estabilidade"]],
        "PC High-End": [rb["temp_max"], rb["performance_medio"], rb["fps_medio"], rb["travamentos"], rb["reinicializacoes"], rb["estabilidade"]],
    }).set_index("")
    st.table(df)

    st.caption(
        "Todos os valores acima foram **calculados pela simulação** durante o "
        "teste que você acabou de rodar — nada foi fixado no código."
    )
    nav_buttons(prev_key="teste_estresse_execucao", next_key="teste_estresse_explicacao", next_label="Por que existiu essa diferença? →")


def screen_teste_estresse_explicacao():
    st.title("🔎 Por que existiu essa diferença?")
    st.markdown("""
A diferença de comportamento entre o PC de Entrada e o PC High-End sob carga
prolongada acontece por um conjunto de fatores combinados:

- **Melhor dissipação de calor** — dissipadores com mais aletas e maior área de contato com o ar.
- **Melhor circulação de ar** — fluxo de ar mais forte remove o calor acumulado mais rápido.
- **Geometria dos dissipadores** — mais área de superfície transfere mais calor por segundo.
- **Componentes mais preparados para cargas prolongadas** — CPU/GPU e VRM com maior margem térmica.
- **Menor perda de energia e menor aquecimento** relativo à potência entregue.
- **Maior estabilidade** — menos throttling, menos travamentos, menos reinicializações.
    """)
    st.info(
        "O cooler box foi representado com menor capacidade de dissipação. "
        "À medida que a temperatura sobe, a proteção térmica reduz a potência dos chips "
        "e o desempenho. Travamentos e reinícios só aparecem após exposição prolongada "
        "acima do limiar de instabilidade do modelo. "
        "O percentual de desempenho é calculado em relação à capacidade de cada PC."
    )
    st.info(
        "🔷 **Sobre o quartzo:** ele tem outra função — ajudar em referências de "
        "frequência e sincronização dos circuitos. Ele **não é responsável pela "
        "dissipação de calor** nem pela diferença de estabilidade observada acima."
    )
    st.warning(
        "⚠️ Os valores utilizados nesta simulação são **simplificados e "
        "hipotéticos**, para demonstrar conceitos de Física e Computação. Não "
        "representam testes reais de placas-mãe ou componentes específicos."
    )
    nav_buttons(prev_key="teste_estresse_resultado", next_key="laboratorio", next_label="Laboratório de experimentos →")


# ============================================== LABORATÓRIO DE EXPERIMENTOS
# Todos os números vêm de core/experiments.py, que roda o mesmo motor da
# simulação principal com carga controlada (semente fixa → reproduzível).
def _lab_topo(exp_id: int):
    meta = exp_mod.EXPERIMENTOS[exp_id]
    st.markdown(f"### Experimento {exp_id} — {meta['titulo']}")
    st.caption(exp_mod.GRUPO_ROTULO[meta["grupo"]])
    st.markdown(f"**Pergunta experimental:** {meta['pergunta']}")
    with st.expander("Objetivo, procedimento e o que observar"):
        st.markdown(f"**Objetivo:** {meta['objetivo']}")
        st.markdown("**Procedimento:**")
        st.markdown("\n".join(f"{i}. {p}" for i, p in enumerate(meta["procedimento"], 1)))
        st.markdown(f"**O que observar:** {meta['observar']}")


def _lab_fim(exp_id: int, df: pd.DataFrame, conclusao: str):
    st.success(f"**Conclusão gerada pela simulação:** {conclusao}")
    st.download_button(
        "Baixar tabela (CSV)", df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"experimento_{exp_id}.csv", mime="text/csv", key=f"lab_dl_{exp_id}",
    )


def _lab_exp1(tier):
    _lab_topo(1)
    r = exp_mod.exp1_normal_vs_elevado(tier)
    lo, hi = r["faixa_esperada"]
    st.caption(f"Faixa de consumo esperada para a carga normal: {lo:.0f}–{hi:.0f} W (limite de alerta = 115% do máximo esperado).")
    st.caption("Temperatura (°C) ao longo do tempo")
    render_line(r["temp_tempo"], "Temperatura (°C)")
    render_table(r["tabela"])
    _lab_fim(1, r["tabela"], r["conclusao"])


def _lab_exp2(tier):
    _lab_topo(2)
    r = exp_mod.exp2_carga_progressiva(tier)
    g1, g2 = st.columns(2)
    with g1:
        st.caption("Carga (%) × Potência (W)")
        render_line(r["carga_potencia"])
    with g2:
        st.caption("Carga (%) × Temperatura estabilizada (°C)")
        render_line(r["carga_temp"])
    render_table(r["tabela"])
    _lab_fim(2, r["tabela"], r["conclusao"])


def _lab_exp3(tier):
    _lab_topo(3)
    r = exp_mod.exp3_potencia_x_temperatura(tier)
    st.caption("Potência (W) × Temperatura de equilíbrio (°C)")
    render_scatter(r["tabela"])
    with st.expander("Ver tabela de dados"):
        render_table(r["tabela"])
    _lab_fim(3, r["tabela"], r["conclusao"])


def _lab_exp4(tier):
    _lab_topo(4)
    carga = st.slider("Carga do sistema (%)", 50, 100, 80, step=5, key="lab_exp4_carga")
    r = exp_mod.exp4_refrigeracao(tier, carga=carga)
    st.caption(f"Temperatura (°C) ao longo do tempo — limite térmico do componente: {exp_mod.LIMITE_TERMICO_LAB_C:.0f} °C")
    render_line(r["temp_tempo"], "Temperatura (°C)")
    render_table(r["tabela"])
    _lab_fim(4, r["tabela"], r["conclusao"])


def _lab_exp5(tier):
    _lab_topo(5)
    carga = st.slider("Carga do sistema (%)", 20, 100, 80, step=5, key="lab_exp5_carga")
    r = exp_mod.exp5_tempo_x_temperatura(tier, carga=carga)
    st.caption("Temperatura ao longo do tempo")
    render_line(r["temp_tempo"])
    render_table(r["tabela"])
    _lab_fim(5, r["tabela"], r["conclusao"])


def _lab_exp6(tier):
    _lab_topo(6)
    r = exp_mod.exp6_sobrecarga(tier)
    st.caption(f"A sobrecarga começa em t = {r['t_sobrecarga_s']} s.")
    g1, g2 = st.columns(2)
    with g1:
        st.caption("Temperatura (°C)")
        render_line(r["series"][["Temperatura (°C)"]])
    with g2:
        st.caption("Desempenho entregue (%)")
        render_line(r["series"][["Desempenho (%)"]])
    render_table(r["tabela"])
    _lab_fim(6, r["tabela"], r["conclusao"])


def _lab_exp7(tier):
    _lab_topo(7)
    r = exp_mod.exp7_variacao_brusca(tier)
    g1, g2, g3 = st.columns(3)
    with g1:
        st.caption("Carga (%)")
        render_line(r["series"][["Carga (%)"]])
    with g2:
        st.caption("Potência (W) — resposta elétrica")
        render_line(r["series"][["Potência (W)"]])
    with g3:
        st.caption("Temperatura (°C) — resposta térmica")
        render_line(r["series"][["Temperatura (°C)"]])
    render_table(r["tabela"])
    _lab_fim(7, r["tabela"], r["conclusao"])


def _lab_exp8(tier):
    _lab_topo(8)
    r = exp_mod.exp8_comparativo(tier)
    render_table(r["tabela"])
    st.caption(f"Limite térmico do componente usado na classificação: {r['limite_c']:.0f} °C.")
    _lab_fim(8, r["tabela"], r["conclusao"])


LAB_RENDERERS = {1: _lab_exp1, 2: _lab_exp2, 3: _lab_exp3, 4: _lab_exp4,
                 5: _lab_exp5, 6: _lab_exp6, 7: _lab_exp7, 8: _lab_exp8}


def screen_laboratorio():
    st.title("🔬 Laboratório de Experimentos")
    st.markdown(
        "Até aqui você **usou** o simulador. Agora vamos **medir**: em cada experimento uma variável é alterada, "
        "os parâmetros são registrados e a conclusão vem dos dados — todos os valores são calculados pela "
        "simulação (com semente fixa, então o resultado é reproduzível)."
    )
    st.markdown("##### A grande pergunta do projeto")
    st.info(
        "Como o aumento ou a irregularidade do consumo de energia de um sistema computacional influencia "
        "seu comportamento elétrico e térmico?"
    )
    st.markdown("""
1. O consumo aumenta?
2. A potência aumenta?
3. O calor gerado aumenta?
4. A temperatura aumenta?
5. A refrigeração consegue controlar esse aumento?
    """)

    c1, c2 = st.columns([1, 2])
    with c1:
        tier = st.selectbox(
            "Computador usado nos experimentos", options=list(COMPUTER_PRESETS.keys()), index=1,
            format_func=lambda k: COMPUTER_PRESETS[k]["nome"], key="lab_pc",
        )
    with c2:
        enxuto = st.checkbox(
            "Mostrar só os recomendados", key="lab_enxuto"
        )

    ids = [i for i, m in exp_mod.EXPERIMENTOS.items()
           if not enxuto or m["grupo"] in ("essencial", "opcional")]
    experiment = st.selectbox(
        "Experimento", ids, format_func=lambda i: exp_mod.EXPERIMENTOS[i]["aba"],
        key="lab_experimento",
    )
    LAB_RENDERERS[experiment](tier)
    st.caption(
        "⚠️ Modelo educativo simplificado: a temperatura de equilíbrio é proporcional à potência por construção "
        "(aproximação de 1ª ordem) e a corrente da CPU é estimada como I = P / V. Em hardware real essas relações "
        "não são perfeitamente lineares."
    )
    nav_buttons(prev_key="teste_estresse_explicacao", next_key="conclusao")


def screen_conclusao():
    st.title("Tecnologia também é eficiência")
    st.markdown("""
1. **Problema** — O consumo energético costuma passar despercebido.
2. **Monitoramento** — Acompanhe CPU, GPU, temperatura e potência.
3. **Análise** — Compare o consumo esperado com o observado.
4. **Detecção** — Identifique possíveis desperdícios.
5. **Recomendação** — Escolha uma ação para otimizar o uso.
6. **Resultado** — Compare consumo, temperatura e custo após a intervenção.
    """)
    st.success(
        "Não basta saber que um computador consome energia — é preciso entender "
        "**por que**, qual o **impacto**, e como a **tecnologia** pode ajudar a "
        "identificar e reduzir desperdícios."
    )
    if st.button("Recomeçar roteiro"):
        st.session_state.pop("quick_demo", None)
        st.session_state.pop("demo_tariff", None)
        st.session_state.stress_test = None
        st.session_state.stress_test_report = None
        goto("intro_problema")
    nav_buttons(prev_key="laboratorio")


# ================================================================= ROTEADOR
SCREEN_FUNCS = {
    "demo": screen_demo,
    "comparativo": screen_comparativo,
    "intro_problema": screen_intro_problema,
    "intro_objetivo": screen_intro_objetivo,
    "intro_voltagem": screen_intro_voltagem,
    "intro_quartzo": screen_intro_quartzo,
    "intro_geometria": screen_intro_geometria,
    "novidade": screen_novidade,
    "afetados": screen_afetados,
    "impactos": screen_impactos,
    "solucoes": screen_solucoes,
    "teste_estresse_intro": screen_teste_estresse_intro,
    "teste_estresse_execucao": screen_teste_estresse_execucao,
    "teste_estresse_resultado": screen_teste_estresse_resultado,
    "teste_estresse_explicacao": screen_teste_estresse_explicacao,
    "laboratorio": screen_laboratorio,
    "conclusao": screen_conclusao,
}

screen = st.session_state.screen
step = SCREENS.index(screen) + 1
total = len(SCREENS)
st.markdown(
    '<div class="mast full-mode"><b><span aria-hidden="true">ϟ</span> EnergySim</b>'
    f'<small>Etapa {step} de {total}</small></div>',
    unsafe_allow_html=True,
)
st.progress(step / total)
SCREEN_FUNCS[screen]()
