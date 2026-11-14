from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        if self._distributori is None:
            return None

        risultato = []
        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            if prezzi is None:
                continue

            prezzi_mese = [p.prezzo_litro for p in prezzi if p.data.month == mese]
            # Il datetime ci crea un oggetto data con dentro gli attributi year, month, day già organizzati
            if len(prezzi_mese) > 0:
                media = sum(prezzi_mese) / len(prezzi_mese)
                risultato.append((distributore.nome, media))

        return risultato

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        # Condizione terminale: ho scelto un distributore per tutti i 7 giorni
        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return

        for id_distributore in prezzi_settimana:
            # Calcolo il costo parziale se scelgo questo distributore oggi
            costo_giorno = prezzi_settimana[id_distributore][giorno - 1] * 100
            if ultimo_distributore is not None and id_distributore != ultimo_distributore:
                costo_giorno += 5  # costo fisso di spostamento
            nuovo_costo = costo_corrente + costo_giorno

            # Filtro: proseguo solo se posso ancora battere la soluzione migliore
            if self.__costo_ottimo == -1 or nuovo_costo < self.__costo_ottimo:
                sequenza_parziale.append(id_distributore)
                self.__ricorsione(sequenza_parziale, giorno + 1, id_distributore, nuovo_costo, prezzi_settimana)

                # Backtracking
                sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        if self._distributori is None:
            return None

        risultato = {}
        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            if prezzi is None:
                continue

            prezzi_prima_settimana = [p.prezzo_litro for p in prezzi if p.data.day <= 7 and p.data.month == mese]
            risultato[distributore.id] = prezzi_prima_settimana
        return risultato
