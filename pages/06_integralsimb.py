import streamlit as st
import sympy as sp
from sympy.abc import _clash
import numpy as np
import scipy as sc
from scipy.integrate import quad
import matplotlib.pyplot as plt

st.set_page_config(page_title="Calculadora de Integrais Simbólicas", layout="wide" , page_icon=":abacus:")
st.title("Calculadora de Integrais Indefinidas")
funcoes_especiais = {
    sp.erf: "Função de Erro (comum em probabilidade e calor)",
    sp.Si: "Seno Integral (comum em processamento de sinais)",
    sp.Ci: "Cosseno Integral",
    sp.expint: "Integral Exponencial"
}
meus_simbolos = {"e": sp.E, "pi": sp.pi, "ln": sp.log,}
raw_input = st.text_input("Digite a função a ser integrada (use 'x' como variável):", value="cos(x)", key="func_indef") 

try:
    func = sp.sympify(raw_input, locals={**meus_simbolos, **_clash})
    x = sp.symbols('x')
    integral = sp.integrate(func, x)
# Se a integral nao tiver solucao analitica, mostrar um aviso
    if isinstance(integral, sp.Integral):
        st.warning("⚠️ **Aviso:** Não foi encontrada uma solução analítica simples.")
        st.markdown("Tente Integrar numericamente usando a aba de integrais definidas") 
        # Mostra a forma simbólica sem a constante +C
        st.latex(f"\\int {sp.latex(func)} \\, dx = {sp.latex(integral)}")
    else:
        # Funcoes especiais 
        for f, desc in funcoes_especiais.items():
            if integral.has(f):
                st.info(f"⚡ A integral envolve a função especial `{f.__name__}`: {desc}")
        st.write(f"Integral de `{func}` em relação a x é:")
        st.latex(f"\\int {sp.latex(func)} \\, dx = {sp.latex(integral)} + C")
except (sp.SympifyError, ValueError) as e:
        st.error(f"Erro ao processar a função: {e}")

st.divider()
st.title("Calculadora de Integrais Definidas")
st.caption("Aqui você pode calcular integrais definidas usando integração numérica para funções que não possuem uma solução analítica simples.")
raw_input_def = st.text_input(f"Digite a função a ser integrada (use 'x' como variável):", value=raw_input, key="func_def")
lower_limit = st.text_input("Digite o limite inferior de integração:", value="0")
upper_limit = st.text_input("Digite o limite superior de integração:", value="1")
try:
    func_def = sp.sympify(raw_input_def, locals={**meus_simbolos, **_clash})
    lower = float(sp.sympify(lower_limit, locals={**meus_simbolos, **_clash}))
    upper = float(sp.sympify(upper_limit, locals={**meus_simbolos, **_clash}))
    resultado, erro = quad(lambda x: sp.lambdify(sp.symbols('x'), func_def)(x), lower, upper)
    st.write(f"Integral definida de `{func_def}` de `{lower}` a `{upper}` é aproximadamente:")
    st.latex(f"\\int_{{{lower}}}^{{{upper}}} {sp.latex(func_def)} \\, dx \\approx {resultado:.4f}")

except (sp.SympifyError, ValueError) as e:
    st.error(f"Erro ao processar a função ou os limites: {e}")


col1, col2 = st.columns(2)

# Quero adicionar um gráfico mostrando a área sob a curva da função integrada entre os limites definidos
with col1:
    st.subheader("Visualização da Área Sob a Curva")
    x_vals = np.linspace(lower - 1, upper + 1, 400)
    y_vals = [sp.lambdify(sp.symbols('x'), func_def)(x) for x in x_vals]
    fig, ax = plt.subplots()
    ax.plot(x_vals, y_vals, label=f'f(x) = {func_def}')
    ax.fill_between(x_vals, y_vals, where=(x_vals >= lower) & (x_vals <= upper), color='lightblue', alpha=0.5)
    ax.axhline(0, color='black', lw=0.5)
    ax.axvline(0, color='black', lw=0.5)
    ax.set_title("Área Sob a Curva")
    ax.legend()
    st.pyplot(fig)

st.divider()

with st.expander("Exemplos de Funções para Integrar"):
    st.markdown("""
    - `sin(x)`
    - `cos(x)`
    - `exp(x)`
    - `x**2`
    - `1/x`
    - `tan(x)`
    - `log(x)`
    """)
st.divider()
# Guia de sintaxe para a entrada de funções
st.subheader("Guia de Sintaxe para Entrada de Funções")
st.markdown("Multiplicação: use `*` (ex: `2*x` ou `x*sin(x)`)\n\n" \
"Potenciação: use `**` ou `^` (ex: `x**2` ou x^2)\n\n" \
"Logaritmo Natural: `log(x)` ou `ln(x)` \n\n" \
"Trigonometria: `sin(x)`, `cos(x)`, `tan(x)`, `cot(x)`, `csc(x)`, `sec(x)` \n\n" \
"Constantes: `e` para a base do logaritmo natural, `pi` para π\n\n" \
"Exemplo de entrada: `2*sin(x) + 3*x**2`")