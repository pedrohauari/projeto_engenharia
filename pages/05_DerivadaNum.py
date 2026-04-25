import streamlit as st
import sympy as sp
import math
from utils.math_utils import formatar_latex, calcular_seguro, analisar_expressao, extrair_simbolos_da_string

def app():
    st.title("🚀 Calculadora de Derivadas Numéricas")

    with st.sidebar:
        st.header("Configuração")
        # 1. Primeiro o usuário digita a função
        entrada_raw = st.text_input("Digite sua Equação:", value="x^2 + y^2 = 25")
        
        # 2. O programa detecta os símbolos em tempo real
        simbolos_detectados = extrair_simbolos_da_string(entrada_raw)
        
        # 3. O Selectbox agora só mostra o que existe na função!
        var_indep_nome = st.selectbox(
            "Derivar em relação a:", 
            options=simbolos_detectados,
            index=0 if simbolos_detectados else 0
        )
        
        v1_val = st.number_input(f"Valor de {var_indep_nome}:", value=3.0)
        unidade = st.radio("Unidade:", ("Radianos", "Graus"))
        h = 1e-5

    try:
        # --- PROCESSAMENTO ---
        f_simbolica, modo_implicito, parametros = analisar_expressao(entrada_raw, var_indep_nome)
        v1_sym = sp.Symbol(var_indep_nome)
        
        dict_params = {}
        var_dep_sym = None

        if parametros:
            st.info("📝 Parâmetros e Variáveis extras")
            if modo_implicito:
                # No modo implícito, se houver outra letra, ela é a dependente
                var_dep_sym = parametros[0]
                v2_val_fixo = st.number_input(f"Valor de {var_dep_sym} no ponto:", value=4.0)
                # Outras letras além da dependente viram constantes
                outros = parametros[1:]
            else:
                outros = parametros

            if outros:
                cols = st.columns(len(outros))
                for i, p in enumerate(outros):
                    dict_params[p] = cols[i].number_input(f"Constante {p}:", value=1.0)

        # --- CÁLCULO ---
        f_num_preparada = f_simbolica.subs(dict_params)
        v1_calc = math.radians(v1_val) if unidade == "Graus" else v1_val

        if modo_implicito and var_dep_sym:
            # Derivada Implícita: dy/dx = -Fx / Fy
            df_dx_s = sp.diff(f_simbolica, v1_sym)
            df_dy_s = sp.diff(f_simbolica, var_dep_sym)
            der_simb = -df_dx_s / df_dy_s
            
            F_num = sp.lambdify((v1_sym, var_dep_sym), f_num_preparada, modules=['numpy', 'math'])
            v2_calc = v2_val_fixo # Aqui você pode adicionar lógica de graus se necessário
            
            Fx_n = (calcular_seguro(F_num, v1_calc + h, v2_calc) - calcular_seguro(F_num, v1_calc - h, v2_calc)) / (2 * h)
            Fy_n = (calcular_seguro(F_num, v1_calc, v2_calc + h) - calcular_seguro(F_num, v1_calc, v2_calc - h)) / (2 * h)
            res_num = -Fx_n / Fy_n if Fy_n != 0 else float('nan')
        else:
            der_simb = sp.diff(f_simbolica, v1_sym)
            F_num = sp.lambdify(v1_sym, f_num_preparada, modules=['numpy', 'math'])
            res_num = (calcular_seguro(F_num, v1_calc + h) - calcular_seguro(F_num, v1_calc - h)) / (2 * h)

        # --- OUTPUT ---
        st.divider()
        if modo_implicito:
            st.latex(rf"F({formatar_latex(var_indep_nome)}, {formatar_latex(var_dep_sym)}) = {sp.latex(f_simbolica)} = 0")
        else:
            st.latex(rf"f({formatar_latex(var_indep_nome)}) = {sp.latex(f_simbolica)}")
            
        st.subheader("📊 Resultados")
        c1, c2 = st.columns(2)
        c1.metric(f"Derivada d/d{var_indep_nome}", f"{res_num:.6f}")
        
        with st.expander("Ver Expressão Simbólica"):
            st.latex(sp.latex(der_simb))

    except Exception as e:
        st.error(f"Aguardando expressão válida... ({e})")

if __name__ == "__main__":
    app()