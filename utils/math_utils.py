import sympy as sp
import numpy as np
import math
from sympy.abc import _clash

def extrair_simbolos_da_string(entrada_raw, texto):
    """Retorna uma lista de strings com todas as letras detectadas na entrada."""
    try:
        texto_limpo = texto.replace('^', '**').split('=')[0] # Pega apenas um lado para evitar confusão
        contexto = {**_clash, "sen": sp.sin, "tg": sp.tan, 'e': sp.E}
        expr = sp.sympify(texto.replace('^', '**'), locals=contexto)
        # Retorna lista de nomes de variáveis, ignorando constantes matemáticas
        return sorted([str(s) for s in expr.free_symbols if str(s) not in ['e', 'pi', 'E']])
    except:
        return ["x"] # Fallback caso a expressão esteja incompleta

def formatar_latex(nome):
    gregas = ["alpha", "beta", "gamma", "delta", "epsilon", "omega", "psi", "chi", 
              "phi", "eta", "zeta", "theta", "iota", "kappa", "lambda", "nu", 
              "mu", "omicron", "xi", "pi", "rho", "sigma", "tau", "upsilon"]
    n = str(nome).lower()
    return f"\\{n}" if n in gregas else str(nome)

def calcular_seguro(func, *args):
    try:
        res = func(*args)
        if np.iscomplexobj(res): return float(np.real(res))
        return float(res)
    except:
        return float('nan')

def analisar_expressao(entrada_raw, var_indep_nome):
    contexto = {**_clash, "e": sp.E, "pi": sp.pi, "sen": sp.sin, "tg": sp.tan}
    texto_limpo = entrada_raw.replace('^', '**')
    
    if "=" in texto_limpo:
        esq, dir = texto_limpo.split("=")
        # Invertido para (esq) - (dir) para ficar mais natural visualmente
        f_simbolica = sp.sympify(f"({esq}) - ({dir})", locals=contexto)
        modo_implicito = True
    else:
        f_simbolica = sp.sympify(texto_limpo, locals=contexto)
        modo_implicito = False

    simbolos_livres = f_simbolica.free_symbols
    parametros = [s for s in simbolos_livres if str(s) != var_indep_nome and str(s) not in ['e', 'pi', 'E']]
    
    return f_simbolica, modo_implicito, parametros