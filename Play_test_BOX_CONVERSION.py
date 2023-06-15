####################################################################################
###########                     INICI PROGRAMA                         #############
####################################################################################
from BOX_CONVERSION_CALCULATOR import OptionChain


# Crear una instancia de OptionChain
# Es passa el ticker per la funcio (si cal modificar el multipliocador per defete de 100)
# cleantype[0] si 0 elimina les files amb zeros. Si 1 subsitueix per 0,01
# cleantype[1] i cleantype[2] límits % strike maxim i minim a mantenir
# source = 'NSDQ' , 'YF' o 'CBOE'

OBJ = OptionChain('PBR', multiplier = 100.00, cleantype = [1,1.6,0.7])
OBJ.dividends
### PER A STOCKS 'NORMALS' ESTRATEGIA LONG ACCIONS - SHORT OPCIONS
## ESTA PENDENT DE VEURE COM ES PODRIEN INCLOURE ELS DIVIDENDS PREVISTOS PER EL CALCUL DE LA RENTABILITAT
MSFT_NSDQ = OptionChain('MSFT', multiplier = 100.00, cleantype = [1, 1.5, 0.5], source = 'NSDQ')
MSFT_NSDQ_Lstock_Soption = MSFT_NSDQ.strategy_Lstock_Soption(order = 'mkt').sort_values(by='Strategy_anual_pct', ascending=False)

GOOG_NSDQ = OptionChain('GOOG', multiplier = 100.00, cleantype = [1, 1.5, 0.5], source = 'NSDQ')
GOOG_NSDQ_Lstock_Soption = GOOG_NSDQ.strategy_Lstock_Soption(order = 'mkt').sort_values(by='Strategy_anual_pct', ascending=False)


MSFT_YF = OptionChain('MSFT', multiplier = 100.00, cleantype = [1, 1.5, 0.5], source = 'YF')
MSFT_YF_Lstock_Soption = MSFT_YF.strategy_Lstock_Soption(order = 'mkt').sort_values(by='Strategy_anual_pct', ascending=False)

MSFT_YF.ticker.dividends

GOOG_YF = OptionChain('GOOG', multiplier = 100.00, cleantype = [1, 1.5, 0.5], source = 'YF')
GOOG_YF_Lstock_Soption = GOOG_YF.strategy_Lstock_Soption(order = 'mkt').sort_values(by='Strategy_anual_pct', ascending=False)


TSLA = OptionChain('TSLA', multiplier = 100.00, cleantype = [1, 1.5, 0.5], source = 'YF')
TSLA_Lstock_Soption = TSLA.strategy_Lstock_Soption(order = 'mkt').sort_values(by='Strategy_anual_pct', ascending=False)


### NSDQ NO FUNCIONA AL SER UN ETF (MIRAR EL REQUEST) // Tampoc funciona NSDQ pels indexs (tipo SPX)
# SPY_NSDQ = OptionChain('SPY', multiplier = 100.00, cleantype = [1,1.6,0.7], source = 'NSDQ')
SPY_YF = OptionChain('SPY', multiplier = 100.00, cleantype = [1, 1.6, 0.5], source = 'YF')
SPY_YF_Lstock_Soption = SPY_YF.strategy_Lstock_Soption(order = 'mkt').sort_values(by='Strategy_anual_pct', ascending=False)


### PER A INDEX ESTRATEGIA BOX
SPX_YF = OptionChain('^SPX', multiplier = 100.00, cleantype = [1, 1.1, 0.9], source = 'YF')
SPX_YF_Loption_Soption = SPX_YF.strategy_Loption_Soption(order = 'mkt').sort_values(by='Strategy_anual_pct', ascending=False)

# Filtro
SPX_YF_Loption_Soption_filter = SPX_YF_Loption_Soption[(SPX_YF_Loption_Soption['Strike_Long'] == 3900) & (SPX_YF_Loption_Soption['Strike_Short'] > 4300)]
SPX_YF_Loption_Soption_filter = SPX_YF_Loption_Soption[(SPX_YF_Loption_Soption['Strike_Long'].between(3900, 4100)) & (SPX_YF_Loption_Soption['Strike_Short'].between(4100, 4300))]

SPX_YF_Loption_Soption_filter = SPX_YF_Loption_Soption[(SPX_YF_Loption_Soption['Strike_Long'].isin([3900, 4000, 4100])) & (SPX_YF_Loption_Soption['Strike_Short'].isin([4100, 4200, 4300]))]

SPX_YF_Loption_Soption_filter = SPX_YF_Loption_Soption[(SPX_YF_Loption_Soption['Strategy_anual_pct'].between(3, 8))]


'''
FILTRES
'''
# Loption_Soption_filter = Loption_Soption[Loption_Soption['Vencimiento'] == '2023-08-31']
# Loption_Soption_filter = Loption_Soption_filter[Loption_Soption_filter['Strike_Long'] == 3900]
# Loption_Soption_filter = Loption_Soption_filter[Loption_Soption_filter['Strike_Short'] > 4300]



'''
ESTRATEGIA CONVERSION: LONG ACCIONS + SHORT SINTETIC OPCIONS
'''
# # Estrategia Long accions + Short opcions (Futur sintetic)
# Lstock_Soption = OBJ.strategy_Lstock_Soption().sort_values(by='Strategy_anual_pct', ascending=False)


'''
ESTRATEGIA CONVERSION: SHORT ACCIONS + LONG SINTETIC OPCIONS
(REVISAR EL TEMA DEL PCT JA QUE SERIEN OPERACIONS A CREDIT)
'''
# # Estrategia Long opcions (Futur sintetic) + Short accions
# Loption_Sstock = OBJ.strategy_Loption_Sstock().sort_values(by='Strategy_anual_pct', ascending=False)

'''
ESTRATEGIA BOX SINTETIC OPCIONS
'''
# # Estrategia Long opcions (Futur sintetic) + Short opcions (Futur sintetic)
# Loption_Soption = OBJ.strategy_Loption_Soption().sort_values(by='Strategy_anual_pct', ascending=False)  

# OBJ.ticker.ticker
# OBJ.chains['2023-06-16']
# OBJ.chains
# OBJ.expiries[0:5]
# OBJ.price
# OBJ.price_yf



# Acciones sin dividendo: 
ticker_list = ['META', 'GOOG', 'GOOGL', 'TSLA', 'AMZN']
ticker_list = ['AMC', 'GME']
objects_dict = {}
results_dict = {}
for ticker in ticker_list:
    YF = OptionChain(ticker, multiplier = 100.00, cleantype = [1, 1.3, 0.7], source = 'YF')
    YF_Lstock_Soption = YF.strategy_Lstock_Soption(order = 'mid').sort_values(by='Strategy_anual_pct', ascending=False)
    objects_dict[ticker] = YF
    results_dict[ticker] = YF_Lstock_Soption
    YF_Loption_Sstock = YF.strategy_Loption_Sstock(order = 'mid').sort_values(by='Strategy_anual_pct', ascending=False)
    results_dict[f'{ticker}_inv'] = YF_Loption_Sstock





# Acciones con dividendo: 
ticker_list = ['SPY', 'MSFT', 'AAPL', 'JNJ']

objects_dict = {}
results_dict = {}
for ticker in ticker_list:
    YF = OptionChain(ticker, multiplier = 100.00, cleantype = [1, 1.3, 0.7], source = 'YF')
    YF_Lstock_Soption = YF.strategy_Lstock_Soption(order = 'mkt').sort_values(by='Strategy_anual_pct', ascending=False)
    objects_dict[ticker] = YF
    results_dict[ticker] = YF_Lstock_Soption

# Acciones con MEGAdividendo: 
ticker_list = ['PXD', 'DVN', 'NWL', 'LNC', 'PBR', 'CTRA', 'MO', 'KEY']

NSDQ = OptionChain('KEY', multiplier = 100.00, cleantype = [1, 1.5, 0.5], source = 'NSDQ')
NSDQ_Lstock_Soption = NSDQ.strategy_Lstock_Soption(order = 'mkt').sort_values(by='Strategy_anual_pct', ascending=False)
NSDQ.dividends

YF = OptionChain('PXD', multiplier = 100.00, cleantype = [1, 1.5, 0.5], source = 'YF')
YF_Lstock_Soption = YF.strategy_Lstock_Soption(order = 'mkt').sort_values(by='Strategy_anual_pct', ascending=False)



