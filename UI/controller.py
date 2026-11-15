import flet as ft
from UI.view import View
from model.model import Model

'''
    CONTROLLER:
    - Funziona da intermediario tra MODELLO e VIEW
    - Gestisce la logica del flusso dell'applicazione
'''

class Controller:
    def __init__(self, view: View, model: Model):
        self._model = model
        self._view = view

        # Variabili per memorizzare le selezioni correnti; 0 = nessun mese selezionato
        self.mese_selezionato = 0

    def leggi_mese(self, e):
        # Chiamato quando l'utente sceglie un mese nel Dropdown (on_select).
        # e.control è il Dropdown, e.control.value è la key dell'opzione scelta ("1".."12", stringa)
        self.mese_selezionato = int(e.control.value)

    def get_prezzo_medio(self, e):
        # Chiamato dal pulsante "Prezzo medio"
        if self.mese_selezionato == 0:
            self._view.show_alert("Selezionare un Mese!")
        else:
            # Chiedo al model la lista di tuple (nome, media)
            prezzo_medio = self._model.get_prezzo_medio(self.mese_selezionato)
            # Svuoto la ListView dai risultati precedenti
            self._view.lista_visualizzazione.controls.clear()
            # Aggiungo l'intestazione
            self._view.lista_visualizzazione.controls.append(
                ft.Text(f"Il prezzo medio nel mese selezionato è:")
            )
            # Se ho dati (DB raggiungibile), aggiungo una riga per distributore
            if prezzo_medio is not None:
                for distributore_media in prezzo_medio:
                    self._view.lista_visualizzazione.controls.append(
                        ft.Text(f"{distributore_media[0]}: {distributore_media[1]:.3f} €/litro")
                    )

    def calcola_sequenza(self, e):
        # Chiamato dal pulsante "Calcola Sequenza"
        if self.mese_selezionato == 0:
            self._view.show_alert("Selezionare un Mese!")
        else:
            # Il model restituisce DUE valori: la lista di stringhe "Giorno X: ..." e il costo
            sequenza_ottima, costo = self._model.get_sequenza_ottima(self.mese_selezionato)
            self._view.lista_visualizzazione.controls.clear()
            self._view.lista_visualizzazione.controls.append(ft.Text(f"La sequenza ottima ha costo {costo:.2f}€ ed è:"))
            for stop in sequenza_ottima:
                self._view.lista_visualizzazione.controls.append(ft.Text(stop))
