"""Demonstração de palco do EnergySim. Cálculos preservados em core/demo.py."""
import html
import streamlit as st
from core.demo import QuickDemo
from models.computer import hardware_details
from core.energy import cost_projection


def br(value, digits=1):
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def power_panel(power):
    has_extra = bool(power["waste_w"])
    parts = [
        ("CPU · tarefa" if has_extra else "CPU", "cpu_w", "#b8f16b"),
        ("GPU · tarefa" if has_extra else "GPU", "gpu_w", "#72d4dc"),
        ("Outros componentes", "extras_w", "#aa9aef"),
    ]
    if has_extra:
        parts.append(("Consumo extra", "waste_w", "#ffb879"))
    total = sum(power[key] for _, key, _ in parts)
    stops, legend = [], []
    start = 0
    for label, key, color in parts:
        end = start + 100 * power[key] / total if total else start
        stops.append(f"{color} {start:.3f}% {end:.3f}%")
        legend.append(f'<li><i style="background:{color}"></i>{label}<b>{br(power[key])} W</b></li>')
        start = end
    return (f'<section class="power-panel"><h2>Distribuição da potência</h2>'
            f'<div class="power-body"><div class="power-ring" style="background:conic-gradient({", ".join(stops)})">'
            f'<div><strong>{br(power["total_w"])}</strong><small>watts</small></div></div>'
            f'<ul>{"".join(legend)}</ul></div></section>')


def render_demo():
    if "quick_demo" not in st.session_state:
        st.session_state.quick_demo = QuickDemo()
    demo = st.session_state.quick_demo
    snap = demo.snapshot()
    power = snap["power"]["total_w"]
    month = cost_projection(power, demo.tariff)["30d"]
    stage = demo.stage
    index = {"normal": 0, "waste": 1, "optimized": 2}[stage]
    st.markdown(
        '<div class="mast"><b><span aria-hidden="true">ϟ</span> EnergySim</b><small>Demonstração guiada</small></div>'
        '<div class="overview"><div class="intro"><h1>Consumo do computador</h1>'
        '<p>Veja como processos em segundo plano afetam a potência, a temperatura e o custo de uso.</p>'
        '<div class="scenario">PC intermediário &nbsp;·&nbsp; Navegador e documentos</div></div>'
        + power_panel(snap["power"]) + '</div>', unsafe_allow_html=True)
    steps = [("Observe", "Como o computador está agora"), ("Identifique", "O que está consumindo a mais"), ("Compare", "O resultado da otimização")]
    segments = []
    for i, (title, desc) in enumerate(steps):
        segments.append(f'<div class="el-step {"active" if i == index else ""}"><span class="el-num">{i+1}</span><div><b>{title}</b><small>{desc}</small></div></div>')
    st.markdown('<div class="el-steps">'+''.join(segments)+'</div>', unsafe_allow_html=True)
    kpis = [
        ("Consumo neste momento", f"{br(power, 1)} W", "Potência elétrica estimada"),
        ("Temperatura", f"{br(snap['temp'], 1)} °C", "Valor estimado pelo modelo"),
        ("Uso do processador", f"{br(snap['cpu_util'], 0)}%", f"Placa gráfica: {br(snap['gpu_util'], 0)}%"),
        ("Custo em 30 dias", f"R$ {br(month['custo'], 2)}", "8 horas por dia, tarifa simulada"),
    ]
    st.markdown('<div class="el-kpis">'+''.join(f'<div class="el-kpi"><div class="el-kpi-label">{html.escape(a)}</div><div class="el-kpi-val">{html.escape(b)}</div><div class="el-kpi-unit">{html.escape(c)}</div></div>' for a,b,c in kpis)+'</div>', unsafe_allow_html=True)

    if stage == "normal":
        story = ("✓", "Tudo dentro do esperado", "O computador está executando tarefas simples. Agora vamos mostrar o que acontece quando processos extras consomem energia sem contribuir para o trabalho.", "")
    elif stage == "waste":
        story = ("!", "Algo está gastando energia sem necessidade", f"Os processos simulados em segundo plano aumentaram o uso total da CPU e da GPU e acrescentaram {br(snap['power']['waste_w'], 0)} W. A carga do navegador e dos documentos continua igual.", "warning")
    else:
        extra_before = demo.before["power"]["waste_w"]
        extra_after = snap["power"]["waste_w"]
        story = (
            "✓",
            "O que foi feito na otimização?",
            f"O simulador aplicou a ação «Verificar processos» e reduziu de {br(extra_before, 0)} W "
            f"para {br(extra_after, 0)} W o consumo extra atribuído a processos desnecessários "
            "em segundo plano. O uso total da CPU e da GPU voltou ao nível da tarefa original, "
            "com menos consumo e geração de calor.",
            "good",
        )
    ico, title, desc, kind = story
    st.markdown(f'<div class="el-story {kind}"><div class="el-story-icon">{ico}</div><div><h3>{html.escape(title)}</h3><p>{html.escape(desc)}</p></div></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 2, 1])
    c1.button("1. Mostrar consumo extra", type="primary" if stage == "normal" else "secondary", disabled=stage != "normal", on_click=demo.inject_waste, use_container_width=True)
    c2.button("2. Simular otimização", type="primary" if stage == "waste" else "secondary", disabled=stage != "waste", on_click=demo.optimize, use_container_width=True)
    def reset():
        st.session_state.quick_demo = QuickDemo(demo.tariff)
    c3.button("Recomeçar", on_click=reset, use_container_width=True)

    result = demo.comparison()
    if result:
        left, right = st.columns([3, 2], gap="medium")
        before_w, after_w = result["before_w"], result["after_w"]
        ratio = after_w / before_w * 100 if before_w else 0
        with left:
            st.markdown(f'''<div class="el-panel"><h3>O que mudou na prática?</h3>
            <div class="el-compare-row"><span>Com consumo desnecessário</span><b>{br(before_w)} W</b></div>
            <div class="el-track"><div class="el-fill el-before" style="width:100%"></div></div>
            <div class="el-compare-row"><span>Após a otimização simulada</span><b>{br(after_w)} W</b></div>
            <div class="el-track"><div class="el-fill el-after" style="width:{ratio:.2f}%"></div></div>
            <div class="el-fine">Temperatura estimada: {br(result['before_temp'])} °C → {br(result['after_temp'])} °C<br>
            Custo em 30 dias: R$ {br(result['before_month']['custo'],2)} → R$ {br(result['after_month']['custo'],2)}</div></div>''', unsafe_allow_html=True)
        with right:
            st.markdown(f'''<div class="el-outcome"><div class="el-t">Redução da potência no cenário</div><div class="el-v">{br(result['reduction_pct'])}%</div>
            <div class="el-line"></div><div class="el-t">Economia projetada em 30 dias</div><div class="el-v small">R$ {br(result['saved_brl'],2)}</div>
            <div class="el-foot">{br(result['saved_kwh'],2)} kWh a menos no mesmo período de uso</div></div>''', unsafe_allow_html=True)
    else:
        normal_min = snap["anomaly"]["esperado_min"]
        normal_max = snap["anomaly"]["esperado_max"]
        st.markdown(f'<div class="el-disclaimer">Faixa de consumo de referência da tarefa: {br(normal_min)} a {br(normal_max)} W. O modelo sinaliza uma anomalia acima de {br(normal_max * 1.15)} W.</div>', unsafe_allow_html=True)

    with st.expander("Premissas da simulação e tarifa"):
        st.markdown(f'<div class="el-disclaimer">Demonstração educativa, sem leitura de sensores nem alteração de processos reais. Projeção: 8 h por dia, durante 30 dias, com tarifa ilustrativa de R$ {br(demo.tariff,2)} por kWh e consumo constante. Cada etapa térmica representa três minutos simulados. Os 90 W adicionais são uma hipótese de teste, não uma medida de aplicativos específicos.</div>', unsafe_allow_html=True)
        st.write("Esta é uma simulação controlada. A intervenção aplica a ação 'verificar processos' do modelo, sem encerrar nenhum programa real. O alerta compara a potência total com uma faixa esperada da tarefa, acrescida de 15% de tolerância. A economia compara a mesma carga útil e as mesmas 240 horas mensais antes e depois.")
        st.write("Atualizações, sincronizações e backups nem sempre são desperdício: o excesso precisa ser confirmado em uma implementação com sensores e processos reais. A temperatura varia ao longo do tempo e não cai imediatamente em hardware físico.")
        tariff = st.number_input("Tarifa utilizada no exemplo (R$/kWh)", min_value=0.10, max_value=3.0, value=demo.tariff, step=0.05, key="demo_tariff")
        if tariff != demo.tariff:
            demo.tariff = tariff
            demo.sim.tarifa_kwh = tariff
            st.rerun()
    with st.expander("Ficha técnica do computador"):
        specs = hardware_details(demo.sim.computer)
        cards = ''.join(
            f'<div class="el-spec"><small>{html.escape(label)}</small><b>{html.escape(value)}</b></div>'
            for label, value in specs
        )
        st.markdown('<div class="el-hardware"><h3>Computador desta simulação</h3><div class="el-specs">' + cards + '</div><p>Configuração de referência. Não é uma detecção do seu computador. Turbo é um limite eventual; consumo, temperatura e clock são estimativas didáticas.</p></div>', unsafe_allow_html=True)
    st.write("O modo completo inclui seleção de computadores e atividades, relatórios, testes de estresse e experimentos.")
    if st.button("Explorar o modo completo"):
        st.session_state.screen = "intro_problema"
        st.rerun()
