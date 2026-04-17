import streamlit as st
import sympy as sp
import string
import math  # <-- Novo import para lidar com trigonometria

st.set_page_config(page_title="Calculadora Numérica Universal", page_icon="⚙️")

st.title("⚙️ Calculadora Numérica de Derivadas")
st.markdown("Cálculo de **Velocidade (1ª)** e **Aceleraçao (2ª)** para qualquer variável.")
st.divider()


def formatar_latex(var):
    gregas = ["alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
              "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
              "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"]
    return rf"\{var}" if var.lower() in gregas else var

def app():
    latino = list(string.ascii_lowercase + string.ascii_uppercase)
    gregas = ["alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
              "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
              "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"]
    todos_simbolos = latino + gregas + [g.capitalize() for g in gregas]

    with st.sidebar:
        st.header("🔧 Configurações")
        col_v = st.columns(2)
        var_indep = col_v[0].selectbox("Independente", todos_simbolos, index=todos_simbolos.index('x'))
        var_dep = col_v[1].selectbox("Dependente", todos_simbolos, index=todos_simbolos.index('y'))
        entrada_raw = st.text_input("Equação:", value="y = sin(x)", key="func_raw")
        col_pts = st.columns(2)
        v1_val = col_pts[0].number_input(f"Valor de {var_indep}:", value=1.0)
        v2_val = col_pts[1].number_input(f"Valor de {var_dep}:", value=1.0)
        
        # --- NOVA FUNCIONALIDADE: SELETOR DE UNIDADE ANGULAR ---
        st.divider()
        st.markdown("📐 **Trigonometria**")
        unidade = st.radio(
            "Unidade dos valores inseridos:", 
            ("Padrão: Radianos", "Graus"),
            help="Altere para Graus se estiver trabalhando com ângulos trigonométricos."
        )
        
        h = 1e-5 # passo h estável
        
        st.divider()
        calc_segunda = st.checkbox("Calcular 2ª Derivada?", value=False)

    # --- MENSAGEM EDUCATIVA SOBRE RADIANOS ---
    if unidade == "Graus":
        st.info("💡 **Nota de Cálculo:** A matemática do cálculo diferencial assume que o ângulo está em radianos. Use Graus apenas se estiver trabalhando com sin, cos, tan, etc")

    try:
        # Tratamento da Equação
        texto = entrada_raw.replace('^', '**')
        if "=" in texto:
            esq, dir = texto.split("=")
            texto_final = f"({dir}) - ({esq})"
        else:
            texto_final = texto

        v1_sym = sp.Symbol(var_indep)
        v2_sym = sp.Symbol(var_dep)
        f_simbolica = sp.sympify(texto_final, locals={var_indep: v1_sym, var_dep: v2_sym})
        F = sp.lambdify((v1_sym, v2_sym), f_simbolica, "math")

        # --- LÓGICA DE CONVERSÃO ---
        # Criamos variáveis de "cálculo" que recebem a conversão se necessário.
        # Convertemos ambas as variáveis (independente e dependente) para manter a universalidade.
        if unidade == "Graus":
            v1_calc = math.radians(v1_val)
            v2_calc = math.radians(v2_val)
        else:
            v1_calc = v1_val
            v2_calc = v2_val

        # --- CÁLCULO DAS DERIVADAS PARCIAIS (usando os valores convertidos) ---
        f0 = F(v1_calc, v2_calc)
        
        # Parciais de 1ª Ordem
        Fx = (F(v1_calc + h, v2_calc) - F(v1_calc - h, v2_calc)) / (2 * h)
        Fy = (F(v1_calc, v2_calc + h) - F(v1_calc, v2_calc - h)) / (2 * h)

        if Fy == 0:
            st.error("Tangente vertical detectada (Fy = 0).")
            return

        # 1ª Derivada (Teorema da Função Implícita)
        dy_dx = -Fx / Fy

        # --- EXIBIÇÃO 1ª ORDEM ---
        l_ind = formatar_latex(var_indep)
        l_dep = formatar_latex(var_dep)
        
        st.subheader("🎯 Resultados")
        st.latex(rf"\frac{{d {l_dep}}}{{d {l_ind}}} \approx {dy_dx:.8f}")

        # --- CÁLCULO 2ª ORDEM (OPCIONAL) ---
        if calc_segunda:
            # Parciais de 2ª Ordem (Diferença Central)
            Fxx = (F(v1_calc + h, v2_calc) - 2*f0 + F(v1_calc - h, v2_calc)) / (h**2)
            Fyy = (F(v1_calc, v2_calc + h) - 2*f0 + F(v1_calc, v2_calc - h)) / (h**2)
            
            # Parcial Mista Fxy
            Fxy = (F(v1_calc+h, v2_calc+h) - F(v1_calc+h, v2_calc-h) - 
                   F(v1_calc-h, v2_calc+h) + F(v1_calc-h, v2_calc-h)) / (4 * h**2)
            
            # Fórmula da 2ª Derivada Implícita
            d2y_dx2 = -(Fxx * Fy**2 - 2 * Fxy * Fx * Fy + Fyy * Fx**2) / (Fy**3)
            
            st.latex(rf"\frac{{d^2 {l_dep}}}{{d {l_ind}^2}} \approx {d2y_dx2:.8f}")
            
            with st.expander("Ver os valores das Derivadas Parciais"):
                st.write(f"Fx: {Fx:.6f} | Fy: {Fy:.6f}")
                st.write(f"Fxx: {Fxx:.6f} | Fyy: {Fyy:.6f} | Fxy: {Fxy:.6f}")

    except Exception as e:
        st.error(f"Erro: {e}")




if __name__ == "__main__":
    app()