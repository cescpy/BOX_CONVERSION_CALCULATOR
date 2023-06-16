# BOX_CONVERSION_CALCULATOR
Calculador de combinaciones de BOX's y CONVERION's a partir del Optionchain.

Calculo de todas las combinaciones en las estrategias:
  - BOX (corto sintético + largo sintético)
  - CONVERSION (largo en acciones + corto sintético)
  - CONVERSION INVERSO (corto de acciones + largo sintético) -- pendiente de revisión

## OJO!! PROYECTO INACABADO!! 
- Pendiente de encontrar data accesible del optionchain de opciones de suficiente calidad.

Con la data de Yfinance y NASDAQ los resultados no tienen la suficiente calidad como para plantearse continuar con las mejoras del código.

Aunque se dan un % alto de resultados correctos, también hay una porción de datos incorrectos (algunos desproporcionados) debido en errores de los datos del Optionchain, por lo que no se puede filtrar automáticamente los que son correctos o incorrectos.

### De momento solo sirve como un "prefiltro".

Si se llega a disponer de data de suficiente calidad se prevé:
- Mejorar, pulir y optimizar los cálculos, limpieza de los datos y funciones.
- Incorporar a la rentabilidad los dividendos a recibir o a pagar en las diferentes combinaciones.
- Posible interface con tkinder para facilitar su uso y muestra de resultados.

## OJO 2!! NO TOMES DECISIONES DE INVERSIÓN EN BASE A ESTE SCRIPT SIN SABER EXACTAMENTE LO QUE HACES Y PODER VALORAR LOS RIESGOS
- En las posiciones de CONVERSION con largos o cortos en acciones ten en cuenta los posibles dividendos.

(Si vas corto en acciones y reparte dividendo lo tienes que pagar y te puede salir más caro que lo que ganabas)
- En las opciones de estilo americano prevé los resultados en caso de asignación anticipada y el capital necesario en ese caso.

(Si entras con una CALL vendida de delta 1, da por sentado que te la van a ejercer. No tiene porqué ser malo, pero puede serlo)

## FUNCIONAMIENTO
- En Play_test_BOX_CONVERSION.py hay ejemplos de uso de la clase.
- En esta versión se puede escojer la data de YFinance o de NASDAQ.

- Se puede escojer entrada a mercado o a precio medio para el cálculo de la compra del Combo (todas las patas/contratos juntas).

## OBSERVACIONES
- Descargar data de optionchain solo dentro del horario de negociación.


