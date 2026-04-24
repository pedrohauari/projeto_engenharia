import streamlit as st
import sympy as sp
import math
import string
from sympy.abc import _clash

def formatar_latex(nome):
    return f"\\{nome}" if len(nome) > 1 and nome != "exp" else nome

def app():
    latino = list(string.ascii_lowercase + string.ascii_uppercase)
    gregas = ["alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
              "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
              "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"]
    todos_simbolos = latino + gregas + [g.capitalize() for g in gregas]

    st.title("Calculadora de Derivadas Implícitas (1ª e 2ª Ordem)")

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
            ("Padrão: Radianos", "Graus")
        )
        
        # Para 2ª derivada, h muito pequeno (1e-8) pode gerar ruído numérico. 
        # 1e-5 é o ideal para equilibrar truncamento e arredondamento.
        h = 1e-5 
        
        st.divider()
        calc_segunda = st.checkbox("Calcular 2ª Derivada?", value=False)

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
        f_simbolica = sp.sympify(texto_final, locals={**_clash, var_indep: v1_sym, var_dep: v2_sym})
        F = sp.lambdify((v1_sym, v2_sym), f_simbolica, "math")

        if unidade == "Graus":
            v1_calc = math.radians(v1_val)
            v2_calc = math.radians(v2_val)
        else:
            v1_calc = v1_val
            v2_calc = v2_val

        # --- CÁLCULO NUMÉRICO 1ª ORDEM ---
        f0 = F(v1_calc, v2_calc)
        Fx = (F(v1_calc + h, v2_calc) - F(v1_calc - h, v2_calc)) / (2 * h)
        Fy = (F(v1_calc, v2_calc + h) - F(v1_calc, v2_calc - h)) / (2 * h)

        if Fy == 0:
            st.error("Erro: Fy = 0 (Tangente Vertical).")
            return

        dy_dx = -Fx / Fy

        # --- EXIBIÇÃO 1ª ORDEM ---
        l_ind = formatar_latex(var_indep)
        l_dep = formatar_latex(var_dep)
        
        st.subheader("🎯 Resultados da 1ª Derivada")
        st.latex(rf"\frac{{d {l_dep}}}{{d {l_ind}}} \approx {dy_dx:.8f}")

        # Validação Analítica 1ª Ordem
        df_dx_s = sp.diff(f_simbolica, v1_sym)
        df_dy_s = sp.diff(f_simbolica, v2_sym)
        dy_dx_analitica_expr = -df_dx_s / df_dy_s
        val_exato_1 = float(dy_dx_analitica_expr.subs({v1_sym: v1_calc, v2_sym: v2_calc}))
        erro_1 = abs((dy_dx - val_exato_1) / val_exato_1 * 100) if val_exato_1 != 0 else 0

        c1, c2 = st.columns(2)
        c1.metric("Valor Exato (SymPy)", f"{val_exato_1:.8f}")
        c2.metric("Erro Relativo", f"{erro_1:.2e} %")

        # --- CÁLCULO NUMÉRICO E VALIDAÇÃO DA 2ª ORDEM ---
        if calc_segunda:
            st.divider()
            st.subheader("🎯 Resultados da 2ª Derivada")

            # Numérico
            Fxx = (F(v1_calc + h, v2_calc) - 2*f0 + F(v1_calc - h, v2_calc)) / (h**2)
            Fyy = (F(v1_calc, v2_calc + h) - 2*f0 + F(v1_calc, v2_calc - h)) / (h**2)
            Fxy = (F(v1_calc+h, v2_calc+h) - F(v1_calc+h, v2_calc-h) - 
                   F(v1_calc-h, v2_calc+h) + F(v1_calc-h, v2_calc-h)) / (4 * h**2)
            
            d2y_dx2 = -(Fxx * Fy**2 - 2 * Fxy * Fx * Fy + Fyy * Fx**2) / (Fy**3)
            st.latex(rf"\frac{{d^2 {l_dep}}}{{d {l_ind}^2}} \approx {d2y_dx2:.8f}")

            # Analítico (Prova Real)
            # Calculamos as parciais de segunda ordem simbolicamente
            Fxx_s = sp.diff(f_simbolica, v1_sym, 2)
            Fyy_s = sp.diff(f_simbolica, v2_sym, 2)
            Fxy_s = sp.diff(f_simbolica, v1_sym, v2_sym)
            
            # Montamos a fórmula da segunda derivada implícita
            d2y_dx2_analitica_expr = -(Fxx_s * df_dy_s**2 - 2 * Fxy_s * df_dx_s * df_dy_s + Fyy_s * df_dx_s**2) / (df_dy_s**3)
            
            val_exato_2 = float(d2y_dx2_analitica_expr.subs({v1_sym: v1_calc, v2_sym: v2_calc}))
            erro_2 = abs((d2y_dx2 - val_exato_2) / val_exato_2 * 100) if val_exato_2 != 0 else 0

            c3, c4 = st.columns(2)
            c3.metric("Valor Exato (SymPy)", f"{val_exato_2:.8f}")
            c4.metric("Erro Relativo", f"{erro_2:.2e} %")

            with st.expander("🔍 Detalhes Técnicos da 2ª Derivada"):
                st.write("**Fórmula Simbólica:**")
                st.latex(sp.latex(d2y_dx2_analitica_expr))
                st.write(f"**Passo h:** {h}")
                st.info("Nota: O erro em 2ª ordem costuma ser maior que em 1ª devido ao acúmulo de arredondamentos.")

    except Exception as e:
        st.error(f"Erro no processamento: {e}")

if __name__ == "__main__":
    app()