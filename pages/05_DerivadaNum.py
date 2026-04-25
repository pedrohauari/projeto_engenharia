import streamlit as st
import sympy as sp
import math
# Importando o motor que criamos
from utils.math_utils import formatar_latex, calcular_seguro, analisar_expressao

def app():
    st.title("🚀 Calculadora de Derivadas Modular")
    
    # --- INPUTS ---
    with st.sidebar:
        st.header("Configuração")
        var_indep_nome = st.selectbox("Variável Independente:", ["x", "t", "y", "z", "theta"], index=1)
        entrada_raw = st.text_input("Equação:", value="A + cos(omega * t + phi)")
        v1_val = st.number_input(f"Valor de {var_indep_nome}:", value=1.0)
        h = 1e-5
        unidade = st.radio("Unidade:", ("Radianos", "Graus"))

    try:
        # 1. Chama o motor para entender a equação
        f_simbolica, modo_implicito, parametros = analisar_expressao(entrada_raw, var_indep_nome)
        
        # 2. Se houver parâmetros (A, omega...), cria campos para eles
        dict_params = {}
        var_dep_sym = None
        
        if parametros:
            st.info("🔍 Parâmetros Detectados")
            if modo_implicito:
                # Se for implícito (com =), o primeiro parâmetro costuma ser a dependente (y)
                var_dep_sym = parametros[0]
                outros = parametros[1:]
                v2_val_fixo = st.number_input(f"Valor de {var_dep_sym} no ponto:", value=1.0)
            else:
                outros = parametros

            if outros:
                cols = st.columns(len(outros))
                for i, p in enumerate(outros):
                    dict_params[p] = cols[i].number_input(f"{p}:", value=1.0)

        # 3. Preparação Matemática
        v1_sym = sp.Symbol(var_indep_nome)
        f_num_preparada = f_simbolica.subs(dict_params)
        v1_calc = math.radians(v1_val) if unidade == "Graus" else v1_val

        # 4. Cálculo da Derivada (Lógica que estava no motor)
        if modo_implicito and var_dep_sym:
            # Caso Implícito: dy/dx = -Fx / Fy
            df_dx_s = sp.diff(f_simbolica, v1_sym)
            df_dy_s = sp.diff(f_simbolica, var_dep_sym)
            der_simb = -df_dx_s / df_dy_s
            
            F_num = sp.lambdify((v1_sym, var_dep_sym), f_num_preparada, modules=['numpy', 'math'])
            v2_calc = v2_val_fixo # simplificado
            
            Fx_n = (calcular_seguro(F_num, v1_calc + h, v2_calc) - calcular_seguro(F_num, v1_calc - h, v2_calc)) / (2 * h)
            Fy_n = (calcular_seguro(F_num, v1_calc, v2_calc + h) - calcular_seguro(F_num, v1_calc, v2_calc - h)) / (2 * h)
            res_num = -Fx_n / Fy_n if Fy_n != 0 else float('nan')
        else:
            # Caso Explícito
            der_simb = sp.diff(f_simbolica, v1_sym)
            F_num = sp.lambdify(v1_sym, f_num_preparada, modules=['numpy', 'math'])
            res_num = (calcular_seguro(F_num, v1_calc + h) - calcular_seguro(F_num, v1_calc - h)) / (2 * h)

        # --- EXIBIÇÃO ---
        st.divider()
        st.latex(rf"f({formatar_latex(var_indep_nome)}) = {sp.latex(f_simbolica)}")
        st.metric("Resultado Numérico", f"{res_num:.6f}")
        with st.expander("Ver Derivada Simbólica"):
            st.latex(sp.latex(der_simb))

    except Exception as e:
        st.error(f"Erro ao processar: {e}")

if __name__ == "__main__":
    app()