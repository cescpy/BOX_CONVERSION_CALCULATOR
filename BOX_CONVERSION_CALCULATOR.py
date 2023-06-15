# -*- coding: utf-8 -*-
'''
version 0.1
ANALITZADOR DE OPTION CHAIN.

PER BUSCAR LES MILLORS COMBINACIONS DE BOX's i CONVERSIONS PER RETORN ANUALITZAT

'''

import pandas as pd
import yfinance as yf

import datetime

import numpy as np
from itertools import product

from enum import Enum

cleantype_arg = Enum('cleantype', {'delzeros': 0, 'subszeros': 1})

# ticker = yf.Ticker('SPY')
# optchains = ticker.option_chain('2023-06-01')

# dir(ticker)


class OptionChain():
    '''
    CREA UN OBJETO QUE CONTIENE LA OPTION CHAIN DEL TICKER Y OTROS DATOS
    ticker_symbol = Ticker
    multiplier = Multiplicador del contrato de opciones
    cleantype = Tipo de limpieza
    source = Fuente de datos
    '''
    def __init__(self, ticker_symbol, multiplier = 100.00, cleantype = [1,2,0.5], source = 'YF'):
        
        # Multiplicador del contracte d'opcions
        self.multiplier = multiplier
        # Parametre per la neteja de les chains
        self.cleantype = cleantype        
        
        # Objecte ticker de yf amb la informacio del ticker
        self.ticker = yf.Ticker(ticker_symbol)
        # Preu del ticker en temps real (dades de les opcions retrassades 15 minuts)
        self.price_yf = self.ticker.history_metadata['regularMarketPrice']
        # Ultims dividends
        # self.dividends = self.ticker.dividends
        self.dividends = yf.Ticker(ticker_symbol).dividends
        # Llista amb els venciments
        self.expiries = list(self.ticker.options)[:]

        # DataFrame per totes les chains concatenades
        self.totalchain = pd.DataFrame()
              
        # Diccionari amb les cadenes d'opcions de tots els venciments
        if source == 'YF':
            self.chains = self.__get_chains_dict_YF()
        if source == 'NSDQ':
            self.chains = self.__get_chains_dict_NSDQ()

        # Calcul del preu aproximat del ticker del mateix moment de les dades obtingudes de les opcions
        self.price = self.__get_price()

        ## Si s'activa aixo es creen el df de resultats directament al instanciar l'objecte i es guarden dins l'objecte
        # Estrategia Long accions + Short opcions (Futur sintetic)
        # self.Lstock_Soption = self.strategy_Lstock_Soption()
        # # Estrategia Long opcions (Futur sintetic) + Short accions
        # self.Loption_Sstock = self.strategy_Loption_Sstock()
        # # Estrategia Long opcions (Futur sintetic) + Short opcions (Futur sintetic)
        # self.Loption_Soption = self.strategy_Loption_Soption()        

        # Final (per assegurar de deixar la cadena d'opcions només amb les columnes originals de la chain)
        # self._restoreChains()
        print('Objeto creado')


    def __cleanchains(self, call, put, cleantype):

        if cleantype[0] == 0:
            # (REVISAR) Elimino les files que tenen BID i ASK == 0 
            call = call.replace(0, None).dropna(axis=0)
            put = put.replace(0, None).dropna(axis=0)
        
        if cleantype[0] == 1:
            # (REVISAR) Els strikes que no tenen preu hi poso 0,01
            call = call.replace(0, 0.01) #.dropna(axis=0)
            put = put.replace(0, 0.01)   #.dropna(axis=0)
            
        if cleantype[1] in cleantype: 
            # (REVISAR) Elimino els strikes de +XX% del preu actual del subjacent
            uplim = self.price_yf * cleantype[1]
            call = call.drop(call[call['Strike'] > uplim].index)
            put = put.drop(put[put['Strike'] > uplim].index)
        
        if cleantype[2] in cleantype: 
            # (REVISAR) Elimino els strikes de -XX% del preu actual del subjacent
            dowlim = self.price_yf * cleantype[2]       
            call = call.drop(call[call['Strike'] < dowlim].index)
            put = put.drop(put[put['Strike'] < dowlim].index) 
            
        # if cleantype[3] == 1:
        #     # (REVISAR) intento corregir errors de dades molt erronies
        #     # Si un strike té un preu superior a l'anterior en la CALL es podria el preu mig entre els dos strikes.

        return call, put
    
    
    def __get_chains_dict_YF(self):
        '''
        Descarrega i ajusta els Dataframes de les cadenes amb les columnes que s'utilitzen
        S'obté un diccionari de dataframes. Cada dataframe es un OptionChain de cada venciment
        '''
        clean= self.cleantype
        #Això només es informatiu
        if clean[0] == 0:
            print('Borrado de strikes con BID/ASK con 0s')
        
        if clean[0] == 1:
            print('Reemplazo de 0s por 0.01')
            
        if clean[1] in clean: 
            uplim = self.price_yf * clean[1]
            print(f'Limite strike superior {clean[1]} = {uplim}')
        
        if clean[2] in clean: 
            dowlim = self.price_yf * clean[2]       
            print(f'Limite strike inferior {clean[2]} = {dowlim}')

        
        chains_dict = {}
        for expiry in self.expiries:
            # Descarrega de les Call i Puts per venciment
            chain0 = self.ticker.option_chain(expiry)
            # Extrec i em quedo nomes amb les 3 columnes que interesen
            call = pd.DataFrame({'Strike': chain0[0].strike, 'Bid_C': chain0[0].bid, 'Ask_C': chain0[0].ask})
            put = pd.DataFrame({'Strike': chain0[1].strike, 'Bid_P': chain0[1].bid, 'Ask_P': chain0[1].ask})

            ## NETEJA
            call, put = self.__cleanchains(call= call, put = put, cleantype = clean)
            
            # Fusiono els dos dataframes de CALL i PUT en un sol.
            # Es mantenen les files que coincideixen en el strike
            chain = pd.merge(call, put, on='Strike', how='inner')
            
            # Afegeixo el preu mitj BID/ASK
            chain['Mid_C'] = (chain['Bid_C'] + chain['Ask_C']) / 2
            chain['Mid_P'] = (chain['Bid_P'] + chain['Ask_P']) / 2
            # Afegeixo columnes identificadores
            chain[['Vencimiento', 'Ticker']] = expiry, self.ticker.ticker
            
            # Columna 'Vemcimiento' a format datetime
            chain['Vencimiento'] = pd.to_datetime(chain['Vencimiento'])
            # Calculo columna de dies per a venciment
            chain['Daystoexpiry'] = (chain['Vencimiento'] - pd.Timestamp.today()).dt.days
            chain['Daystoexpiry'] = chain['Daystoexpiry'] + 2
            
            # Reordeno les columnes
            chain = chain.reindex(columns=['Ticker', 'Vencimiento', 'Daystoexpiry', 'Bid_C', 'Mid_C', 'Ask_C', 'Strike', 'Bid_P', 'Mid_P', 'Ask_P'])
            
            # Afegeixo el venciment al diccionari
            chains_dict[expiry] = chain
           
            
        # Elimino del diccionari els df que no tinguin files (ja que si n'hi ha dona error en la combinatoria vectoritzada del Lo_So)
        keys_to_delete = []
        for key, df in chains_dict.items():
            if len(df) == 0:
                keys_to_delete.append(key)      
        # Eliminar las claves del diccionario
        for key in keys_to_delete:
            del chains_dict[key]      
        # Ho elimino tambe de la llista de venciments (si no em dona error la funcio _restoreChains())
        # Tot i que esta modificat ja per no dependre de la llista de venciments
        self.expiries = [x for x in self.expiries if x not in keys_to_delete]

        print('Cadena de opciones descargada y procesada')
        print(f'Vencimientos vacios borrados: {keys_to_delete}')
        
        return chains_dict


    def __get_chains_dict_NSDQ(self):
        '''
        Descarrega i ajusta els Dataframes de les cadenes amb les columnes que s'utilitzen
        S'obté un diccionari de dataframes. Cada dataframe es un OptionChain de cada venciment
        '''
        import requests 

        headers = { 
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36', 
        } 
         
        params = { 
            "assetclass":"stocks", 
            "limit":"99999", 
            "fromdate":"all", 
            "excode":"oprac", 
            "callput":"callput", 
            "money":"all", 
            "type":"all" 
        } 
         
        response = requests.get(f'https://api.nasdaq.com/api/quote/{self.ticker.ticker}/option-chain', params=params, headers=headers).json() 
        options_chain = pd.DataFrame(response['data']['table']['rows']) 
        options_chain = options_chain[['expirygroup', 'c_Bid', 'c_Ask', 'strike', 'p_Bid', 'p_Ask']]
        
        #Neteja y ordre
        # Renombrar las columnas
        options_chain = options_chain.rename(columns={'expirygroup': 'Vencimiento' ,'c_Bid': 'Bid_C', 'c_Ask': 'Ask_C', 'strike': 'Strike','p_Bid': 'Bid_P', 'p_Ask': 'Ask_P'})
        # Rellenar los valores vacíos con el último valor anterior
        options_chain['Vencimiento']= pd.to_datetime(options_chain['Vencimiento'])
        options_chain['Vencimiento'].fillna(method='ffill', inplace=True)
        # Eliminar files separadores amb 'None'
        options_chain = options_chain.dropna(axis = 0)
        # Treure '--'
        options_chain.replace('--', '0', inplace=True)
        # Passar números a 'float'
        options_chain[['Bid_C', 'Ask_C', 'Strike', 'Bid_P', 'Ask_P']] = options_chain[['Bid_C', 'Ask_C', 'Strike', 'Bid_P', 'Ask_P']].astype(float)
        
        # Columna Ticker
        options_chain['Ticker'] = self.ticker.ticker
        # Afegeixo el preu mitj BID/ASK
        options_chain['Mid_C'] = (options_chain['Bid_C'] + options_chain['Ask_C']) / 2
        options_chain['Mid_P'] = (options_chain['Bid_P'] + options_chain['Ask_P']) / 2
        # Calculo columna de dies per a venciment
        options_chain['Daystoexpiry'] = (options_chain['Vencimiento'] - pd.Timestamp.today()).dt.days
        options_chain['Daystoexpiry'] = options_chain['Daystoexpiry'] + 2
        
        # Reordeno les columnes
        options_chain = options_chain.reindex(columns=['Ticker', 'Vencimiento', 'Daystoexpiry', 'Bid_C', 'Mid_C', 'Ask_C', 'Strike', 'Bid_P', 'Mid_P', 'Ask_P'])

        # Eliminar els venciments vençuts
        options_chain = options_chain[options_chain['Daystoexpiry'] >= 0].copy()
        
        # Poso en un dict els df dels diferents venciments
        chains_dict = {}
        expiries = list(set(options_chain['Vencimiento']))
        for expiry in expiries:
             # Afegeixo els venciment al diccionari
             expiry_str = expiry.strftime('%Y-%m-%d')
             chains_dict[expiry_str] = options_chain[options_chain['Vencimiento']== expiry]

        # Elimino del diccionari els df que no tinguin files (ja que si n'hi ha dona error en la combinatoria vectoritzada del Lo_So)
        keys_to_delete = []
        for key, df in chains_dict.items():
            if len(df) == 0:
                keys_to_delete.append(key)      
        # Eliminar las claves del diccionario
        for key in keys_to_delete:
            del chains_dict[key]      
        # Elimino tambe de la llista de venciments (si no em dona error la funcio _restoreChains()
        # Tot i que esta modificat ja per no dependre de la llista de venciments
        self.expiries = [x for x in self.expiries if x not in keys_to_delete]

        print('Cadena de opciones descargada y procesada')
        print(f'Vencimientos vacios borrados: {keys_to_delete}')
        
        return chains_dict


    def __restoreChains(self):
        '''
        Retorna les chains a l'estat inicial. Deixa les columnes "basiques"
        '''
        for i in self.chains.keys():         
            self.chains[i] = self.chains[i][['Ticker', 'Vencimiento', 'Daystoexpiry', 'Bid_C', 'Mid_C', 'Ask_C', 'Strike', 'Bid_P', 'Mid_P', 'Ask_P']].copy()
        
        print('chains restauradas')
            
    def __get_price(self):
        ''' 
        Preu del subjacent en el moment de la foto de les dades de les opcions
        ( = preu CALL - preu PUT + strike ATM)
        Obtenim un preu bastant fiable del subjacent en el moment de descarregar les dades de les opcions
        Les dades de les opcions tenen 15 min de retard i el preu descarregat amb les dades es temps real.
        '''
        dftemp = self.chains[self.expiries[0]].copy()
        dftemp['C-P'] = dftemp['Mid_C']-dftemp['Mid_P']
        dftemp = dftemp[dftemp['C-P'] >= 0]
        ticker_price = dftemp.iloc[-1,-1] + dftemp.iloc[-1,6]

        print(f'Precio del subyacente calculado {ticker_price}') 
        print(f'Precio del subyacente descargado {self.price_yf}')
        return ticker_price
        

    def __short_Future_Synth(self, order = 'mid'):
        '''
        Inclou a les OptionChains columnes amb la prima i preu de cada futur sintetic Short en cada strike
        Es pot triar si treballar amb preu de mercat ('mkt') o preu mig ('mid')
        '''
        
        for i in self.chains.keys():
            if order == 'mkt':
                self.chains[i]['Short_Premium'] = (self.chains[i]['Ask_P'] - self.chains[i]['Bid_C']) * self.multiplier
                self.chains[i]['Short_Breack'] = self.chains[i]['Strike'] - (self.chains[i]['Short_Premium'] / self.multiplier)

            elif order == 'mid': 
                self.chains[i]['Short_Premium'] = (self.chains[i]['Mid_P'] - self.chains[i]['Mid_C']) * self.multiplier
                self.chains[i]['Short_Breack'] = self.chains[i]['Strike'] - (self.chains[i]['Short_Premium'] / self.multiplier)
            
            else: 
                print('Error en el argumento "orden"')
                break
        print('Futuros Synth Cortos calculados')


    def __long_Future_Synth(self, order = 'mid'):
        '''
        Inclou a les OptionChains columnes amb la prima i preu de cada futur sintetic Long en cada strike
        Es pot triar si treballar amb preu de mercat ('mkt') o preu mig ('mid')
        '''
       
        for i in self.chains.keys():
            if order == 'mkt':
                self.chains[i]['Long_Premium'] = (self.chains[i]['Ask_C'] - self.chains[i]['Bid_P']) * self.multiplier
                self.chains[i]['Long_Breack'] = self.chains[i]['Strike'] + (self.chains[i]['Long_Premium'] / self.multiplier)

            elif order == 'mid': 
                self.chains[i]['Long_Premium'] = (self.chains[i]['Mid_C'] - self.chains[i]['Mid_P']) * self.multiplier
                self.chains[i]['Long_Breack'] = self.chains[i]['Strike'] + (self.chains[i]['Long_Premium'] / self.multiplier)
                
            else: 
                print('Error en el argumento "order"')
                break
        print('Futuros Synth Largos calculados')
        

    def __total_chain(self, chains_dict):
        '''
        Creo un dataframe amb tots els venciments concatenats amb les columnes que tinguin les chains
        '''
        
        totalchain = pd.DataFrame(columns = chains_dict[self.expiries[0]].columns)
        for i in chains_dict.keys():
            totalchain = pd.concat([totalchain, chains_dict[i]])            
        
        # FER REINDEX??
        print('totalchain creada')      
        return totalchain


    def strategy_Lstock_Soption(self, order = 'mkt'):
        '''
        ESTRATEGIA CONVERSION: LONG ACCIONS + SHORT SINTETIC OPCIONS
        '''
        self.__short_Future_Synth(order = order)
        
        # Resultats Long accions - Short opcions (CONVERSION)
        for i in self.chains.keys():
            self.chains[i]['Long_Stock'] = self.price
            self.chains[i]['Strategy_Profit'] = (self.chains[i]['Short_Breack'] - self.price) * self.multiplier
            self.chains[i]['Strategy_Capital'] = self.chains[i]['Short_Premium'] + (self.price * self.multiplier)
            self.chains[i]['Strategy_pct'] = (self.chains[i]['Strategy_Profit'] * self.multiplier) / self.chains[i]['Strategy_Capital']
            self.chains[i]['Strategy_anual_pct'] = (365 / self.chains[i]['Daystoexpiry'] * self.chains[i]['Strategy_pct']  ) 
        
        Ls_So = self.chains.copy()
        
        # Creo el dataframe de totes les combinacions
        Lstock_Soption = self.__total_chain(chains_dict = Ls_So)
        Lstock_Soption = Lstock_Soption.drop(['Bid_C', 'Mid_C', 'Ask_C','Bid_P', 'Mid_P', 'Ask_P' ], axis=1)       

        self.__restoreChains()
        print('strategy_Lstock_Soption creada') 
        return Lstock_Soption

        
    def strategy_Loption_Sstock(self, order = 'mkt'):
        '''
        ESTRATEGIA CONVERSION: SHORT ACCIONS + LONG SINTETIC OPCIONS
        (REVISAR EL TEMA DEL PCT JA QUE SERIEN OPERACIONS A CREDIT)
        '''
        self.__long_Future_Synth(order = order)
        
        # Resultats Long accions - Short opcions (CONVERSION)
        for i in self.chains.keys():
            self.chains[i]['Short_Stock'] = -1 * self.price
            self.chains[i]['Strategy_Profit'] = (self.price - self.chains[i]['Long_Breack']) * self.multiplier
            self.chains[i]['Strategy_Capital'] = self.chains[i]['Long_Premium'] - (self.price * self.multiplier)
            self.chains[i]['Strategy_pct'] = -1 *(self.chains[i]['Strategy_Profit'] * self.multiplier) / self.chains[i]['Strategy_Capital']
            self.chains[i]['Strategy_anual_pct'] = (365 / self.chains[i]['Daystoexpiry'] * self.chains[i]['Strategy_pct']  ) 
       
        Lo_Ss = self.chains.copy()
        
        # Creo el dataframe de totes les combinacions
        Loption_Sstock = self.__total_chain(chains_dict = Lo_Ss)
        Loption_Sstock = Loption_Sstock.drop(['Bid_C', 'Mid_C', 'Ask_C','Bid_P', 'Mid_P', 'Ask_P' ], axis=1) 
        
        self.__restoreChains()
        print('strategy_Loption_Sstock creada') 
        return Loption_Sstock


    def strategy_Loption_Soption(self, order = 'mkt'):
        '''
        ESTRATEGIA BOX SINTETIC OPCIONS
        '''
        self.__long_Future_Synth(order = order)
        self.__short_Future_Synth(order = order)
        
        # Crear totes les combinacions de BOX's de cada venciment
        Lo_So = self.chains.copy()
      
        # Bucle for para iterar los df de cada vencimiento en el diccionario
        for c, df in Lo_So.items():
            LoSodf = df[['Ticker', 'Vencimiento', 'Daystoexpiry', 'Strike', 'Long_Premium', 'Long_Breack', 'Short_Premium', 'Short_Breack']].copy()
            LoSodf['Strike_Long'] = LoSodf['Strike']
            LoSodf['Strike_Short'] = LoSodf['Strike']
            LoSodf.drop(['Strike'], axis=1, inplace=True)
        
            # Obtener todas las combinaciones de filas utilizando operaciones vectorizadas
            indices = np.arange(len(LoSodf))
            row_indices = np.array(list(product(indices, indices)))
            row_long = LoSodf[['Ticker', 'Vencimiento', 'Daystoexpiry','Strike_Long', 'Long_Premium', 'Long_Breack']].iloc[row_indices[:, 0]].reset_index(drop=True)
            row_short = LoSodf[['Strike_Short', 'Short_Premium', 'Short_Breack']].iloc[row_indices[:, 1]].reset_index(drop=True)
        
            # Concatenar las filas para obtener el dataframe de combinaciones
            combined_df = pd.concat([row_long, row_short], axis=1)
        
            # Sustituir el df original por el df con las combinaciones en cada clave del diccionario
            Lo_So[c] = combined_df    
                     
        # Resultats Long opcions - Short opcions (BOX)
        for i in self.chains.keys():
            Lo_So[i]['Strategy_Profit'] = (Lo_So[i]['Short_Breack']  - Lo_So[i]['Long_Breack']) * self.multiplier
            Lo_So[i]['Strategy_Capital'] = Lo_So[i]['Long_Premium'] + Lo_So[i]['Short_Premium']
            Lo_So[i]['Strategy_pct'] = (Lo_So[i]['Strategy_Profit'] * self.multiplier) / Lo_So[i]['Strategy_Capital']
            Lo_So[i]['Strategy_anual_pct'] = (365 / Lo_So[i]['Daystoexpiry'] * Lo_So[i]['Strategy_pct']) 
            
        # Creo el dataframe de totes les combinacions    
        Loption_Soption = self.__total_chain(chains_dict = Lo_So)
        
        self.__restoreChains()
        print('strategy_Loption_Soption creada') 
        return Loption_Soption
        



####################################################################################
###########                     INICI PROGRAMA                         #############
####################################################################################

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



