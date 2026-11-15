from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        # Lista dei distributori (oggetti Distributore), caricata subito all'avvio
        self._distributori = None
        self.load_distributori()

        # Stato della ricorsione: migliore sequenza trovata e il suo costo.
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1   # -1 significa "nessuna soluzione ancora trovata"

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        # Chiamo il metodo statico del DAO -> [Distributore A, Distributore B] (oppure None)
        self._distributori = DistributoreDAO.get_distributori()

    # PREZZO MEDIO MENSILE (con l'ORM, senza scrivere nuovo SQL)
    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        # Se il DB non era raggiungibile all'avvio non ho distributori: restituisco None
        # (il controller gestisce già il caso "prezzo_medio is None")
        if self._distributori is None:
            return None

        risultato = []
        for distributore in self._distributori:
            # uso la RELAZIONE dell'ORM per ottenere tutti i suoi oggetti Prezzo
            prezzi = distributore.get_prezzi()
            # se il caricamento fallisce salto questo distributore
            if prezzi is None:
                continue

            # Tengo solo i prezzi (float) dei giorni del mese scelto.
            # p.data è un datetime.date, quindi p.data.month è il numero del mese
            prezzi_mese = [p.prezzo_litro for p in prezzi if p.data.month == mese]
            # Il datetime ci crea un oggetto data con dentro gli attributi year, month, day già organizzati
            if len(prezzi_mese) > 0:
                media = sum(prezzi_mese) / len(prezzi_mese)
                risultato.append((distributore.nome, media))

        return risultato

    # SEQUENZA OTTIMA (ricorsione)
    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        # Azzero lo stato: ogni pressione del pulsante è un calcolo nuovo
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        # Avvio la ricorsione: sequenza vuota, si parte dal giorno 1: nessun distributore precedente (None), costo iniziale 0
        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduco gli ID in nomi: dizionario {1: "Distributore A", 2: "Distributore B"}
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        # enumerate(..., start=1) numera i giorni da 1: ["Giorno 1: Distributore A", ...]
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]

        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        # Significato dei parametri:
        # - sequenza_parziale: id dei distributori scelti fin qui (es. [1, 1, 2])
        # - giorno: il giorno che devo decidere ora (livello della ricorsione, da 1 a 7)
        # - ultimo_distributore: id scelto il giorno prima (None al giorno 1)
        # - costo_corrente: costo accumulato dalle scelte fatte fin qui
        # - prezzi_settimana: {id_distributore: [7 prezzi]}

        # La ricorsione esplora tutte le 2^7 = 128 sequenze di distributori disponibili e tiene la più economica
        # -1 è un valore sentinella che indica che non abbiamo ancora salvato nessuna sequenza
        # Avrei potuto anche impostare costo ottimo a 10000 ma per evitare casini uso il -1

        # Condizione terminale: ho scelto un distributore per tutti i 7 giorni
        if giorno > 7:
            # Se è la prima soluzione completa (-1) o è più economica della migliore, la salvo
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                # salvo una COPIA: sequenza_parziale verrà poi eventualmente modificata dal backtracking (pop)
                self.__sequenza_ottima = list(sequenza_parziale)
            return

        # Provo, per il giorno corrente, ciascun distributore (le chiavi del dizionario: 1 e 2)
        for id_distributore in prezzi_settimana:
            # Calcolo il costo parziale se scelgo questo distributore oggi
            costo_giorno = prezzi_settimana[id_distributore][giorno - 1] * 100
            if ultimo_distributore is not None and id_distributore != ultimo_distributore:
                costo_giorno += 5
            nuovo_costo = costo_corrente + costo_giorno

            # Filtro: proseguo solo se posso ancora battere la soluzione migliore.
            # I costi sono tutti positivi: se ho già raggiunto il costo ottimo, continuare non serve
            if self.__costo_ottimo == -1 or nuovo_costo < self.__costo_ottimo:
                sequenza_parziale.append(id_distributore)
                # passo al giorno successivo (livello + 1)
                self.__ricorsione(sequenza_parziale, giorno + 1, id_distributore, nuovo_costo, prezzi_settimana)

                # Backtracking: annullo la scelta per provare l'altro distributore (tento tutte le strade possibili)
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
            # Relazione ORM: tutti i prezzi del distributore
            prezzi = distributore.get_prezzi()
            if prezzi is None:
                continue

            # Filtro: giorni da 1 a 7 DEL MESE SCELTO
            prezzi_prima_settimana = [p.prezzo_litro for p in prezzi if p.data.day <= 7 and p.data.month == mese]
            # Aggiungo una chiave al dizionario (senza sovrascrivere quelle già presenti)
            risultato[distributore.id] = prezzi_prima_settimana
        return risultato
