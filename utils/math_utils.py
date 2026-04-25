import sympy as sp
import numpy as np
import math
from sympy.abc import _clash

def formatar_latex(nome):
    gregas = ["alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
              "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
              "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"]
    nome_low = nome.lower()
    return f"\\{nome_low}" if nome_low in gregas else nome

def calcular_seguro(func, *args):
    """Evita quebras por números complexos ou divisões por zero."""
    try:
        res = func(*args)
        if np.iscomplexobj(res):
            return float(np.real(res))
        return float(res)
    except:
        return float('nan')

def analisar_expressao(entrada_raw, var_indep_nome):
    """
    Identifica se a função é implícita ou explícita e quais são os parâmetros (A, w, etc).
    """
    contexto = {**_clash, "e": sp.E, "E": sp.E, "pi": sp.pi, "sen": sp.sin, "tg": sp.tan, "ln": sp.log, "cossec": sp.csc, "cotg": sp.cot}
    texto_limpo = entrada_raw.replace('^', '**')
    
    if "=" in texto_limpo:
        esq, dir = texto_limpo.split("=")
        f_simbolica = sp.sympify(f"({dir}) - ({esq})", locals=contexto)
        modo_implicito = True
    else:
        f_simbolica = sp.sympify(texto_limpo, locals=contexto)
        modo_implicito = False

    simbolos_livres = f_simbolica.free_symbols
    # Captura letras que não são a variável principal nem constantes matemáticas
    parametros = [s for s in simbolos_livres if str(s) != var_indep_nome and str(s) not in ['e', 'pi', 'E']]
    
    return f_simbolica, modo_implicito, parametros