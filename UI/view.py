import flet as ft
from UI.alert import AlertManager

'''
    VIEW:
    - Rappresenta l'interfaccia utente
    - Riceve i dati dal MODELLO e li presenta senza modificarli

    Crea i widget grafici e collega gli eventi (click, selezioni) ai metodi del controller.
'''

class View:
    def __init__(self, page: ft.Page):
        # Page: la finestra dell'applicazione Flet, con alcune impostazioni iniziali
        self.page = page
        self.page.title = "Lab08"
        self.page.horizontal_alignment = "center"
        self.page.theme_mode = ft.ThemeMode.DARK

        # Alert: gestore dei messaggi di avviso (es. "Selezionare un Mese!")
        self.alert = AlertManager(page)

        # Controller: viene impostato dopo, con set_controller (vedi main.py)
        self.controller = None

    def show_alert(self, messaggio):
        self.alert.show_alert(messaggio)

    def set_controller(self, controller):
        # La view e il controller si conoscono a vicenda: in main.py prima si crea la view,
        # poi il controller (che riceve la view), infine si passa il controller alla view
        self.controller = controller

    def update(self):
        self.page.update()

    def load_interface(self):
        """ Crea e aggiunge gli elementi di UI alla pagina e la aggiorna. """
        # Va chiamato DOPO set_controller, perché i widget usano i metodi del controller

        # SEZIONE 1: Intestazione
        self.txt_titolo = ft.Text(value="Analisi Prezzi Carburante", size=38, weight=ft.FontWeight.BOLD)

        # SEZIONE 2: Dropdown + Pulsanti ######################################################
        # Dropdown dei mesi: "key" è il valore letto dal controller ("1".."12"), "text" è ciò che vede l'utente
        self.dropdown_mese = ft.Dropdown(
            options=[ft.dropdown.Option(key="1", text="gennaio"),
                     ft.dropdown.Option(key="2", text="febbraio"),
                     ft.dropdown.Option(key="3", text="marzo"),
                     ft.dropdown.Option(key="4", text="aprile"),
                     ft.dropdown.Option(key="5", text="maggio"),
                     ft.dropdown.Option(key="6", text="giugno"),
                     ft.dropdown.Option(key="7", text="luglio"),
                     ft.dropdown.Option(key="8", text="agosto"),
                     ft.dropdown.Option(key="9", text="settembre"),
                     ft.dropdown.Option(key="10", text="ottobre"),
                     ft.dropdown.Option(key="11", text="novembre"),
                     ft.dropdown.Option(key="12", text="dicembre"), ],
            label="Mese",
            width=200,
            hint_text="Selezionare un mese",
            # quando l'utente sceglie un mese viene chiamato controller.leggi_mese(e)
            on_select=self.controller.leggi_mese
        )

        # Pulsante "Prezzo medio" -> controller.get_prezzo_medio(e)
        pulsante_prezzo = ft.Button(
            "Prezzo medio",
            tooltip="Verifica il prezzo medio per distributore, nel mese selezionato",
            on_click=self.controller.get_prezzo_medio
        )

        # Pulsante "Calcola Sequenza" -> controller.calcola_sequenza(e)
        pulsante_calcolo_sequenza = ft.Button(
            "Calcola Sequenza",
            tooltip="Calcola la sequenza ottimale per i rifornimenti",  # Testo di aiuto quando fai hover col mouse
            on_click=self.controller.calcola_sequenza
        )

        # SEZIONE 3: Visualizzazione mediante ListView ########################################
        # Lista scorrevole dove il controller inserisce i risultati (ft.Text)
        self.lista_visualizzazione = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)


        # --- Toggle Tema ---
        self.toggle_cambia_tema = ft.Switch(label="Tema scuro", value=True, on_change=self.cambia_tema)

        # --- Layout della pagina ---
        self.page.add(
            self.toggle_cambia_tema,

            # Sezione 1
            self.txt_titolo,
            ft.Divider(),

            # Sezione 2: Dropdown + Pulsanti, affiancati in una riga centrata
            ft.Row(
                spacing=40,
                controls=[self.dropdown_mese, pulsante_prezzo, pulsante_calcolo_sequenza],
                alignment=ft.MainAxisAlignment.CENTER
            ),

            # Sezione 3: Visualizzazione mediante ListView, dentro un riquadro alto 400 con bordo
            ft.Container(
                content=self.lista_visualizzazione,
                height=400,
                border=ft.Border.all(1, ft.Colors.BLACK),
                padding=5,
            ),
        )

        # Barra di scorrimento della pagina quando serve
        self.page.scroll = "adaptive"
        self.page.update()

    def cambia_tema(self, e):
        """ Cambia tema scuro/chiaro """
        self.page.theme_mode = ft.ThemeMode.DARK if self.toggle_cambia_tema.value else ft.ThemeMode.LIGHT
        self.toggle_cambia_tema.label = "Tema scuro" if self.toggle_cambia_tema.value else "Tema chiaro"
        self.page.update()