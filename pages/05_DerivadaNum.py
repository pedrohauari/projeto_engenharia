import streamlit as st
import sympy as sp
import math
import string
from sympy.abc import _clash

def formatar_latex(nome):
    gregas = ["alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
              "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
              "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"]
    if nome.lower() in gregas:
        return f"\\{nome}"
    return nome

def app():
    # --- 1. CONFIGURAÇÃO DE SÍMBOLOS ---
    latino = list(string.ascii_lowercase + string.ascii_uppercase)
    gregas = ["alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
              "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
              "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"]
    todos_simbolos = latino + gregas + [g.capitalize() for g in gregas]

    st.title("Calculadora de Derivadas Definitiva")
    st.markdown("Aceita expressões simples ou equações complexas como `x^3 + y^3 = 6*x*y`.")

    # --- 2. BARRA LATERAL (CONFIGURAÇÃO BASE) ---
    with st.sidebar:
        st.header("🔧 Configurações")
        var_indep_nome = st.selectbox("Variável Independente (Derivar em relação a):", todos_simbolos, index=todos_simbolos.index('x'))
        v1_sym = sp.Symbol(var_indep_nome)
        
        entrada_raw = st.text_input("Equação ou Função:", value="x^3 + y^3 = 6*x*y")
        v1_val = st.number_input(f"Valor de {var_indep_nome}:", value=1.0)
        
        st.divider()
        unidade = st.radio("Unidade Angular:", ("Radianos", "Graus"))
        h = 1e-5 
        calc_segunda = st.checkbox("Calcular 2ª Derivada?", value=False)

    try:
        # --- 3. PARSE E IDENTIFICAÇÃO DE VARIÁVEIS ---
        contexto = {**_clash, "e": sp.E, "pi": sp.pi, "sen": sp.sin, "tg": sp.tan}
        texto_limpo = entrada_raw.replace('^', '**')
        
        if "=" in texto_limpo:
            esq, dir = texto_limpo.split("=")
            f_simbolica = sp.sympify(f"({dir}) - ({esq})", locals=contexto)
            modo_implicito = True
        else:
            f_simbolica = sp.sympify(texto_limpo, locals=contexto)
            modo_implicito = False

        # Detectar todos os símbolos presentes
        todos_na_func = f_simbolica.free_symbols
        # Candidatos a dependente/constantes (tudo que não é a independente nem constantes matemáticas)
        candidatos = [s for s in todos_na_func if str(s) != var_indep_nome and str(s) not in ['e', 'pi', 'E']]

        var_dep_sym = None
        dict_params = {}

        if candidatos:
            st.info("🔍 **Análise de Variáveis**")
            # Se houver mais de um candidato, o usuário escolhe qual é a DEPENDENTE
            if len(candidatos) > 1:
                var_dep_nome = st.selectbox("Qual destas é a variável DEPENDENTE?", [str(c) for c in candidatos])
                var_dep_sym = sp.Symbol(var_dep_nome)
            else:
                var_dep_sym = candidatos[0]
                st.write(f"Variável dependente detectada: **{var_dep_sym}**")

            # Tudo que sobrou vira PARÂMETRO CONSTANTE
            outros_params = [c for c in candidatos if str(c) != str(var_dep_sym)]
            if outros_params:
                with st.expander("Definir Constantes (Parâmetros)"):
                    cols = st.columns(len(outros_params))
                    for i, p in enumerate(outros_params):
                        dict_params[p] = cols[i].number_input(f"Valor de {p}:", value=1.0)

            # Se for implícito, precisamos do valor da dependente para o cálculo numérico
            if modo_implicito:
                v2_val_fixo = st.sidebar.number_input(f"Valor de {var_dep_sym} no ponto:", value=1.0)

        # --- 4. CÁLCULO DAS DERIVADAS ---
        v1_calc = math.radians(v1_val) if unidade == "Graus" else v1_val
        l_ind = formatar_latex(var_indep_nome)
        l_dep = formatar_latex(str(var_dep_sym)) if var_dep_sym else "f"

        if modo_implicito and var_dep_sym:
            # Regra da Função Implícita: dy/dx = -Fx / Fy
            df_dx = sp.diff(f_simbolica, v1_sym)
            df_dy = sp.diff(f_simbolica, var_dep_sym)
            der_simb = -df_dx / df_dy
            
            v2_calc = math.radians(v2_val_fixo) if unidade == "Graus" else v2_val_fixo
            F_num = sp.lambdify((v1_sym, var_dep_sym), f_simbolica.subs(dict_params), "numpy")
            
            # Numérico 1ª Ordem
            Fx_n = (F_num(v1_calc + h, v2_calc) - F_num(v1_calc - h, v2_calc)) / (2 * h)
            Fy_n = (F_num(v1_calc, v2_calc + h) - F_num(v1_calc, v2_calc - h)) / (2 * h)
            res_num = -Fx_n / Fy_n if Fy_n != 0 else float('nan')
            sub_dict = {v1_sym: v1_calc, var_dep_sym: v2_calc, **dict_params}
        else:
            # Derivada simples d/dx
            der_simb = sp.diff(f_simbolica, v1_sym)
            F_num = sp.lambdify(v1_sym, f_simbolica.subs(dict_params), "numpy")
            res_num = (F_num(v1_calc + h) - F_num(v1_calc - h)) / (2 * h)
            sub_dict = {v1_sym: v1_calc, **dict_params}

        # --- 5. EXIBIÇÃO ---
        st.divider()
        st.latex(rf"\text{{Equação: }} {sp.latex(f_simbolica)} = 0")
        
        st.subheader(f"🎯 Primeira Derivada: d{l_dep}/d{l_ind}")
        st.latex(rf"\frac{{d {l_dep}}}{{d {l_ind}}} \approx {res_num:.8f}")
        
        val_exato = float(der_simb.subs(sub_dict))
        c1, c2 = st.columns(2)
        c1.metric("Valor Analítico", f"{val_exato:.8f}")
        c2.metric("Erro Relativo", f"{abs((res_num-val_exato)/val_exato*100):.2e} %" if val_exato != 0 else "0%")

        with st.expander("Ver Fórmula Simbólica"):
            st.latex(sp.latex(der_simb))

        # --- SEGUNDA DERIVADA ---
        if calc_segunda and var_dep_sym:
            if modo_implicito:
                Fxx_s = sp.diff(f_simbolica, v1_sym, 2)
                Fyy_s = sp.diff(f_simbolica, var_dep_sym, 2)
                Fxy_s = sp.diff(f_simbolica, v1_sym, var_dep_sym)
                der2_simb = -(Fxx_s * df_dy**2 - 2 * Fxy_s * df_dx * df_dy + Fyy_s * df_dx**2) / (df_dy**3)
                
                # Numérico 2ª Ordem
                f0 = F_num(v1_calc, v2_calc)
                Fxx_n = (F_num(v1_calc + h, v2_calc) - 2*f0 + F_num(v1_calc - h, v2_calc)) / (h**2)
                Fyy_n = (F_num(v1_calc, v2_calc + h) - 2*f0 + F_num(v1_calc, v2_calc - h)) / (h**2)
                Fxy_n = (F_num(v1_calc+h, v2_calc+h) - F_num(v1_calc+h, v2_calc-h) - F_num(v1_calc-h, v2_calc+h) + F_num(v1_calc-h, v2_calc-h)) / (4 * h**2)
                res2_num = -(Fxx_n * Fy_n**2 - 2 * Fxy_n * Fx_n * Fy_n + Fyy_n * Fx_n**2) / (Fy_n**3)
            else:
                der2_simb = sp.diff(f_simbolica, v1_sym, 2)
                res2_num = (F_num(v1_calc + h) - 2*F_num(v1_calc) + F_num(v1_calc - h)) / (h**2)

            st.subheader(f"🎯 Segunda Derivada: d²{l_dep}/d{l_ind}²")
            st.latex(rf"\frac{{d^2 {l_dep}}}{{d {l_ind}^2}} \approx {res2_num:.8f}")
            val_exato2 = float(der2_simb.subs(sub_dict))
            st.metric("Valor Analítico 2ª", f"{val_exato2:.8f}")
            
            with st.expander("Ver Fórmula Simbólica 2ª Ordem"):
                st.latex(sp.latex(der2_simb))

    except Exception as e:
        st.error(f"Erro: {e}")

if __name__ == "__main__":
    app()