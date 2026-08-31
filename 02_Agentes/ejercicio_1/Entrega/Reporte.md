# ¿Qué agentes lograron salir con el oro en tu mapa y cuáles no?
El agente de reflejo simple no pudo obtener el oro ya que había una brisa que tenía que atravesar para poder encontrar el oro.
El agente basado en modelos tampoco pudo obtener el oro por las mismas razones.
El agente basado en metas se acercaba al oro pero como detectaba brisas alrededor terminó gastando sus movimientos rotando a unos espacios de distancia del oro.
El agente basado en utilidades logró obtener el oro de forma exitosa, fue el único que logró salir con el oro.
Lo interesante fue que el agente de aprendizaje, con 1500 episodios, obtuvo una media de puntaje de -22.9, y concluyó que la mejor acción es simplemente salir sin hacer nada, obtuviendo un puntaje de -1. Por lo tanto, se buscaría cambiar los puntajes o el comportamiento para poder encontrar todos los caminos posibles y encontrar el oro.

# ¿Por qué el agente de reflejo simple falla (o tiene suerte) en tu diseño?
Porque como detectaba la brisa o el olor simplemente rotaba, por lo que nunca se acercó al oro.

# ¿Cómo cambia el resultado del agente basado en modelo si acercas o alejas un pit de la casilla inicial?
El agente basado en modelo cuando esta lejos el pit de la casilla inicial parece que si puede tener posibilidades de salir con el oro, pero se quedo dando vueltas hasta que se agotaron sus movimientos. Por otro lado, cuando se le acerco un pit a la casilla inicial el agente solo estaba rotando en el inicio hasta agotar sus movimientos, no avanzó a ningun lado.