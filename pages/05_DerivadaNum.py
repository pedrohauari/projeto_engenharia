import streamlit as st
import sympy as sp
import math
import string
from sympy.abc import _clash
from scipy.integrate import quad 

# Inicializar a página do streamlit 
st.set_page_config(page_title="Calculadora Numérica Universal", page_icon="⚙️")

st.title("⚙️ Calculadora Numérica de Derivadas")
st.markdown("Cálculo de **Velocidade (1ª)** e **Aceleraçao (2ª)** para qualquer variável.")
st.divider()

def formatar_latex(nome):
    # Simples ajuda para nomes de variáveis gregas no LaTeX
    return f"\\{nome}" if len(nome) > 1 and nome != "exp" else nome

def app():
    # --- CONFIGURAÇÃO DE SÍMBOLOS ---
    latino = list(string.ascii_lowercase + string.ascii_uppercase)
    gregas = ["alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
              "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
              "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"]
    todos_simbolos = latino + gregas + [g.capitalize() for g in gregas]

    st.title("Calculadora de Derivada Numérica e Implícita")

    with st.sidebar:
        st.header("🔧 Configurações")
        col_v = st.columns(2)
        var_indep = col_v[0].selectbox("Independente", todos_simbolos, index=todos_simbolos.index('x'))
        var_dep = col_v[1].selectbox("Dependente", todos_simbolos, index=todos_simbolos.index('y'))
        
        entrada_raw = st.text_input("Equação:", value="y = sin(x)", key="func_raw")
        
        col_pts = st.columns(2)
        v1_val = col_pts[0].number_input(f"Valor de {var_indep}:", value=1.0)
        v2_val = col_pts[1].number_input(f"Valor de {var_dep}:", value=1.0)
        
        st.divider()
        st.markdown("📐 **Trigonometria**")
        unidade = st.radio(
            "Unidade dos valores inseridos:", 
            ("Padrão: Radianos", "Graus"),
            help="Altere para Graus se estiver trabalhando com ângulos trigonométricos."
        )
        
        h = 1e-8 # Passo h preciso para derivada central
        
        st.divider()
        calc_segunda = st.checkbox("Calcular 2ª Derivada?", value=False)

    if unidade == "Graus":
        st.info("💡 **Nota:** Os valores de entrada foram convertidos para radianos para o cálculo.")

    try:
        # --- TRATAMENTO DA EQUAÇÃO ---
        texto = entrada_raw.replace('^', '**')
        if "=" in texto:
            esq, dir = texto.split("=")
            texto_final = f"({dir}) - ({esq})"
        else:
            texto_final = texto

        v1_sym = sp.Symbol(var_indep)
        v2_sym = sp.Symbol(var_dep)
        
        # Uso do clash para evitar conflito com nomes de funções (ex: 'E')
        f_simbolica = sp.sympify(texto_final, locals={**_clash, var_indep: v1_sym, var_dep: v2_sym})
        F = sp.lambdify((v1_sym, v2_sym), f_simbolica, "math")

        # --- LÓGICA DE CONVERSÃO PARA CÁLCULO ---
        if unidade == "Graus":
            v1_calc = math.radians(v1_val)
            v2_calc = math.radians(v2_val)
        else:
            v1_calc = v1_val
            v2_calc = v2_val

        # --- CÁLCULO NUMÉRICO (DIFERENÇA CENTRAL) ---
        f0 = F(v1_calc, v2_calc)
        
        # Parciais de 1ª Ordem
        Fx = (F(v1_calc + h, v2_calc) - F(v1_calc - h, v2_calc)) / (2 * h)
        Fy = (F(v1_calc, v2_calc + h) - F(v1_calc, v2_calc - h)) / (2 * h)

        if Fy == 0:
            st.error("Tangente vertical detectada (Fy = 0). Impossível calcular dy/dx.")
            return

        # 1ª Derivada (Teorema da Função Implícita)
        dy_dx = -Fx / Fy

        # --- EXIBIÇÃO RESULTADOS ---
        l_ind = formatar_latex(var_indep)
        l_dep = formatar_latex(var_dep)
        
        st.subheader("🎯 Resultados Numéricos")
        st.latex(rf"\frac{{d {l_dep}}}{{d {l_ind}}} \approx {dy_dx:.8f}")

        # --- CÁLCULO 2ª ORDEM ---
        if calc_segunda:
            Fxx = (F(v1_calc + h, v2_calc) - 2*f0 + F(v1_calc - h, v2_calc)) / (h**2)
            Fyy = (F(v1_calc, v2_calc + h) - 2*f0 + F(v1_calc, v2_calc - h)) / (h**2)
            Fxy = (F(v1_calc+h, v2_calc+h) - F(v1_calc+h, v2_calc-h) - 
                   F(v1_calc-h, v2_calc+h) + F(v1_calc-h, v2_calc-h)) / (4 * h**2)
            
            d2y_dx2 = -(Fxx * Fy**2 - 2 * Fxy * Fx * Fy + Fyy * Fx**2) / (Fy**3)
            st.latex(rf"\frac{{d^2 {l_dep}}}{{d {l_ind}^2}} \approx {d2y_dx2:.8f}")

        # --- 🛡️ VALIDAÇÃO ANALÍTICA (A PROVA REAL) ---
        st.divider()
        st.subheader("🔍 Validação Analítica (SymPy)")
        
        # Derivadas exatas via SymPy
        df_dx_simb = sp.diff(f_simbolica, v1_sym)
        df_dy_simb = sp.diff(f_simbolica, v2_sym)
        
        # dy/dx = - (dF/dx) / (dF/dy)
        dy_dx_analitica_expr = -df_dx_simb / df_dy_simb
        
        # Substituição dos valores para achar o valor exato
        valor_exato = float(dy_dx_analitica_expr.subs({v1_sym: v1_calc, v2_sym: v2_calc}))
        
        # Cálculo do erro
        erro_relativo = abs((dy_dx - valor_exato) / valor_exato) * 100 if valor_exato != 0 else 0

        c1, c2 = st.columns(2)
        c1.metric("Valor Exato", f"{valor_exato:.8f}")
        c2.metric("Erro Relativo", f"{erro_relativo:.2e} %")

        if erro_relativo < 1e-5:
            st.success("✅ O cálculo numérico confere com a solução analítica!")
        else:
            st.warning("⚠️ Diferença detectada. Isso pode ocorrer em pontos de descontinuidade ou alta curvatura.")

        with st.expander("Ver Detalhes Técnicos"):
            st.write("**Expressão da Derivada Implícita:**")
            st.latex(sp.latex(dy_dx_analitica_expr))
            st.write(f"Passo h utilizado: {h}")

    except Exception as e:
        st.error(f"Erro ao processar a equação: {e}")

if __name__ == "__main__":
    app()