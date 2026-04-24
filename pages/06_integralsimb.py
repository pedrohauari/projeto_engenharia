import streamlit as st
import sympy as sp
from sympy.abc import _clash
import numpy as np
import scipy as sc
from scipy.integrate import quad
import matplotlib.pyplot as plt


st.set_page_config(page_title="Calculadora de Integrais Simbólicas", layout="wide" , page_icon=":abacus:")
st.title("Calculadora de Integrais Indefinidas")
# Casos Especiais 
funcoes_especiais = {
    sp.erf: "Função de Erro (comum em probabilidade e calor)",
    sp.Si: "Seno Integral (comum em processamento de sinais)",
    sp.Ci: "Cosseno Integral",
    sp.expint: "Integral Exponencial"
}
# Para ajudar o usuário
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

# 1. Inputs - Ajuste na lógica de atribuição
nada = {}
lower_limit = st.number_input("Limite inferior:", value=0.0) # Adicionei .0 para garantir que seja float
expr_lower = sp.Number(lower_limit) # Criamos a versão simbólica para o sp.latex usar depois

upper_limit = st.number_input("Limite superior:", value=1.0)
expr_upper = sp.Number(upper_limit)

# 2. Lógica Principal
if lower_limit is not None and upper_limit is not None:
    try:
        # Processa a função principal
        # Nota: certifique-se que 'meus_simbolos' e '_clash' foram definidos antes no seu código total
        func_def = sp.sympify(raw_input_def, locals={**meus_simbolos, **_clash})
        
        # PREPARA PARA O CALCULO 
        f_lamb = sp.lambdify(sp.symbols('x'), func_def, modules=['numpy'])
        
        # CALCULA 
        resultado, erro = quad(f_lamb, lower_limit, upper_limit)

        # 3. EXIBIÇÃO DA INTEGRAL
        st.write("### Resultado:")
        # Agora o sp.latex funciona porque expr_lower e expr_upper são objetos do SymPy
        st.latex(rf"\int_{{{sp.latex(expr_lower)}}}^{{{sp.latex(expr_upper)}}} {sp.latex(func_def)} \, dx \approx {resultado:.4f}")

        # 4. EXIBIÇÃO DO GRÁFICO (Agora protegido dentro do Try!)
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Visualização da Área Sob a Curva")
            
            # Eixo X com margem de respiro de 1 unidade para os lados
            x_vals = np.linspace(lower_limit - 1, upper_limit + 1, 400)
            
            # Eixo Y otimizado (sem list comprehension lenta)
            y_vals = f_lamb(x_vals)
            
            # Prevenção de erro caso a função seja uma constante (ex: f(x) = 2)
            if np.isscalar(y_vals):
                y_vals = np.full_like(x_vals, y_vals)
                
            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, label=f'f(x) = {func_def}')
            
            # Pinta a área exata da integral
            ax.fill_between(x_vals, y_vals, where=(x_vals >= lower_limit) & (x_vals <= upper_limit), color='lightblue', alpha=0.5)
            
            # Linhas dos eixos (cruz no zero)
            ax.axhline(0, color='black', lw=0.5)
            ax.axvline(0, color='black', lw=0.5)
            
            ax.set_title("Área Sob a Curva")
            ax.legend()
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Erro no cálculo ou no gráfico: {e}")

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