import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from math import atan2, sqrt, pi

# Configuração da página
st.set_page_config(page_title="Gerador de Polígonos Complexos", layout="wide")

st.title("🎨 Gerador de Polígonos Regulares no Plano Complexo")
st.markdown("""
Este app resolve equações do tipo $z^n = w$, onde $w = a + bi$. 
As raízes formam um polígono regular inscrito em uma circunferência.
""")

# --- Sidebar para Inputs ---
st.sidebar.header("Parâmetros da Equação")
a = st.sidebar.number_input("Parte Real (a)", value=1.0, step=1.0)
b = st.sidebar.number_input("Parte Imaginária (b)", value=0.0, step=1.0)
n = st.sidebar.number_input("Ordem da Raiz (n)", min_value=2, max_value=100, value=3)

# --- Processamento Matemático ---

# 1. Cálculo do Módulo e Argumento
r = sqrt(a**2 + b**2)   # Módulo do numero complexo
theta = atan2(b, a) # Argumento, Resolve automaticamente os casos de a=0 e quadrantes com atan2

# 2. Representação em LaTeX usando SymPy
z_sym, w_sym = sp.symbols('z w')
forma_algebrica = a + b*sp.I
# Criando a representação polar simbólica para o LaTeX
r_sym = sp.simplify(sp.sqrt(a**2 + b**2))
# Simplificar o ângulo para frações de pi se possível
theta_sym = sp.Rational(sp.atan2(b, a)) 

st.subheader("1. Representação da Equação")
col1, col2 = st.columns(2)

with col1:
    st.write("**Forma Algébrica:**")
    st.latex(f"z^{{{n}}} = {sp.latex(forma_algebrica)}")

with col2:
    st.write("**Forma Polar (w):**")
    # Mostrando r * (cos(theta) + i*sin(theta))
    st.latex(f"w = {r:.4f} \cdot (\cos({theta:.4f}) + i \cdot \sin({theta:.4f}))")

# 3. Cálculo das Raízes (De Moivre)
raizes = []
raio_raiz = r**(1/n)

for k in range(n):
    angulo_k = (theta + 2 * k * pi) / n
    real_k = raio_raiz * np.cos(angulo_k)
    imag_k = raio_raiz * np.sin(angulo_k)
    raizes.append((real_k, imag_k))

# --- Visualização com Matplotlib ---
st.subheader(f"2. Geometria das {n} Raízes")

fig, ax = plt.subplots(figsize=(8, 8))

# Extrair coordenadas X e Y
x_coords = [p[0] for p in raizes]
y_coords = [p[1] for p in raizes]

# Adicionar a primeira raiz ao final para fechar o polígono
x_plot = x_coords + [x_coords[0]]
y_plot = y_coords + [y_coords[0]]

# Desenhar o círculo circunscrito
circulo = plt.Circle((0, 0), raio_raiz, color='gray', fill=False, linestyle='--', alpha=0.5)
ax.add_artist(circulo)

# Plotar os vértices (Pontos Vermelhos)
ax.scatter(x_coords, y_coords, color='red', s=50, zorder=5, label='Raízes (Vértices)')

# Desenhar as arestas do polígono
ax.plot(x_plot, y_plot, color='blue', linewidth=2, alpha=0.8, label=f'Polígono (n={n})')

# Configurações do gráfico
limite = raio_raiz * 1.3
ax.set_xlim(-limite, limite)
ax.set_ylim(-limite, limite)
ax.axhline(0, color='black', linewidth=1)
ax.axvline(0, color='black', linewidth=1)
ax.set_aspect('equal') # Importante para o polígono não ficar deformado
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_xlabel("Eixo Real (Re)")
ax.set_ylabel("Eixo Imaginário (Im)")
ax.legend()

st.pyplot(fig)

# --- Lista das Raízes ---
with st.expander("Ver valores numéricos das raízes"):
    for i, (re, im) in enumerate(raizes):
        st.write(f"Raiz {i}: {re:.4f} + {im:.4f}j")