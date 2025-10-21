import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import Tuple

# --- Dataclass en beslisfunctie ---
@dataclass
class PatiëntGegevens:
    tumor_grootte_cm: float
    multicentrisch: bool
    eerdere_bestraling_borst: bool
    zwangerschap: bool
    radiotherapie_beschikbaar: bool


def beoordeel_bsc_kandidaat(p: PatiëntGegevens) -> Tuple[str, str]:
    if p.multicentrisch:
        return ("Mastectomie aanbevolen",
                "Er zitten meerdere tumoren in verschillende delen van de borst. "
                "In dat geval is het meestal niet mogelijk om alleen het aangetaste stukje weg te halen. "
                "Daarom wordt vaak gekozen voor het verwijderen van de hele borst (mastectomie).")

    if not p.radiotherapie_beschikbaar:
        return ("Mastectomie aanbevolen",
                "Na een borstsparende operatie is bestraling van de borst altijd nodig om terugkeer van de tumor te voorkomen. "
                "Omdat bestraling in dit geval niet mogelijk of niet beschikbaar is, is het veiliger om de hele borst te verwijderen (mastectomie).")

    if p.zwangerschap and p.radiotherapie_beschikbaar:
        return ("Mastectomie aanbevolen",
                "Tijdens de zwangerschap kan bestraling niet veilig worden uitgevoerd. "
                "Daarom wordt vaak gekozen voor een mastectomie, zodat de behandeling niet hoeft te worden uitgesteld tot na de bevalling.")


    if p.tumor_grootte_cm <= 5.0:
        return ("Borstsparende operatie aanbevolen",
                "De tumor is klein genoeg om alleen het aangetaste deel van de borst weg te halen. "
                "Daarna volgt meestal bestraling van de borst om het risico op terugkeer te verkleinen. "
                "Deze combinatie levert doorgaans hetzelfde resultaat op als een borstverwijdering.")


    if p.tumor_grootte_cm > 5.0:
        return ("Mastectomie aanbevolen",
                "De tumor is relatief groot, waardoor het moeilijk is om de borst mooi te behouden na een operatie. "
                "Daarom wordt meestal gekozen om de hele borst te verwijderen (mastectomie).")

    return ("Overleg met behandelteam aanbevolen",
            "De situatie is complex en niet eenduidig. "
            "Het is verstandig om dit te bespreken met het behandelteam en uw arts en samen te beslissen welke behandeling het beste past.")

# --- Tooltip klasse ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify='left',
            background="#ffffe0",
            relief='solid',
            borderwidth=1,
            wraplength=300,
            font=("Segoe UI", 9)
        )
        label.pack(ipadx=5, ipady=5)

    def hide(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


# --- GUI functie ---
def bereken_aanbeveling():
    try:
        grootte = float(tumor_entry.get())
    except ValueError:
        messagebox.showerror("Fout", "Voer een geldig getal in voor tumorgrootte. Een geldig getal is een positief getal, zo nodig gescheidden door een punt (.)")
        return

    p = PatiëntGegevens(
        tumor_grootte_cm=grootte,
        multicentrisch=multicentrisch_var.get() == "Nee",
        eerdere_bestraling_borst=bestraling_var.get() == "Ja",
        zwangerschap=zwanger_var.get() == "Ja",
        radiotherapie_beschikbaar=radiotherapie_var.get() == "Ja",
    )

    aanbeveling, toelichting = beoordeel_bsc_kandidaat(p)
    resultaat_text.set(f"Aanbeveling: {aanbeveling}\n\nToelichting: {toelichting}")


# --- GUI Setup ---
root = tk.Tk()
root.title("CDSS – Borstsparende Chirurgie of Mastectomie")
root.geometry("700x860")
root.config(bg="#f3f6fa")
root.resizable(False, False)

# Thema voor ttk
style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background="#ffffff")
style.configure("TLabel", background="#ffffff", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=8)
style.map("TButton", background=[("active", "#0078d7")], foreground=[("active", "white")])

# Koptekst
header = tk.Label(
    root,
    text="🩺 Clinical Decision Support – Borstkanker",
    font=("Segoe UI Semibold", 15),
    bg="#0078d7",
    fg="white",
    pady=15
)
header.pack(fill="x")

# Hoofdframe
frm = ttk.Frame(root, padding=30, style="TFrame")
frm.place(relx=0.5, rely=0.53, anchor="center")

# Titel binnen frame
tk.Label(frm, text="Patiëntgegevens", font=("Segoe UI", 13, "bold"), bg="#ffffff").grid(row=0, column=0, columnspan=3, pady=(0, 10))

# Tumorgrootte
ttk.Label(frm, text="Wat is de grootte van de tumor? (in cm):").grid(row=1, column=0, sticky="w", pady=5)
tumor_entry = ttk.Entry(frm, width=10)
tumor_entry.grid(row=1, column=1, sticky="w", pady=5)
tumor_entry.insert(0, "")

# Functie om vragen toe te voegen
def add_question(row, text, toelichting):
    ttk.Label(frm, text=text).grid(row=row, column=0, sticky="w", pady=5)
    var = tk.StringVar(value="")  # <-- start leeg
    dropdown = ttk.Combobox(frm, textvariable=var, values=["Ja", "Nee"], state="readonly", width=8)
    dropdown.grid(row=row, column=1, sticky="w", pady=5)
    info_label = tk.Label(frm, text="🛈", fg="#0078d7", bg="#ffffff", cursor="question_arrow", font=("Segoe UI", 11, "bold"))
    info_label.grid(row=row, column=2, sticky="w", padx=5)
    ToolTip(info_label, toelichting)
    return var

# Vragen
multicentrisch_var = add_question(2, "Bevind de tumor zich in 1 gebied?",
                                  "Als alle tumorcellen bij elkaar in één deel van de borst zitten, is een borstsparende operatie vaak goed mogelijk. Wanneer er echter meerdere tumoren in verschillende delen van de borst zitten, wordt het moeilijk om alles veilig te verwijderen zonder de borst ernstig te veranderen. In dat geval adviseren artsen meestal om de hele borst te verwijderen (mastectomie).")
bestraling_var = add_question(3, "Heeft u eerder bestraling gehad aan uw borst?",
                              "Wanneer een patiënt eerder radiotherapie heeft gehad, is herhaling vaak niet veilig.")
zwanger_var = add_question(4, "Bent u zwanger?",
                           "Tijdens zwangerschap is radiotherapie meestal niet mogelijk, wat invloed heeft op de keuze.")
radiotherapie_var = add_question(6, "Bent u bereid en in staat om radiotherapie te ondergaan?",
                                 "Na BSC is radiotherapie noodzakelijk; als dit niet mogelijk is, wordt vaak mastectomie gekozen.")


def bereken_aanbeveling():
    # Controleer tumorgrootte
    grootte_str = tumor_entry.get().strip()
    if not grootte_str:
        messagebox.showerror("Fout", "Voer de tumorgrootte in.")
        return

    try:
        grootte = float(grootte_str)
    except ValueError:
        messagebox.showerror("Fout", "Voer een geldig getal in voor tumorgrootte.")
        return

    # Controleer of alle dropdowns ingevuld zijn
    if "" in [multicentrisch_var.get(), bestraling_var.get(), zwanger_var.get(), radiotherapie_var.get()]:
        messagebox.showerror("Fout", "Beantwoord alle vragen voordat u het advies berekent.")
        return

    # Maak patiëntgegevens
    p = PatiëntGegevens(
        tumor_grootte_cm=grootte,
        multicentrisch=multicentrisch_var.get() == "Nee",
        eerdere_bestraling_borst=bestraling_var.get() == "Ja",
        zwangerschap=zwanger_var.get() == "Ja",
        radiotherapie_beschikbaar=radiotherapie_var.get() == "Ja",
    )

    # Bereken advies
    aanbeveling, toelichting = beoordeel_bsc_kandidaat(p)
    resultaat_text.set(f"Aanbeveling: {aanbeveling}\n\nToelichting: {toelichting}")


# Berekenknop
calculate_btn = ttk.Button(frm, text="🔍 Bereken aanbeveling", command=bereken_aanbeveling)
calculate_btn.grid(row=8, column=0, columnspan=3, pady=25)

# Resultaatvak
result_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
result_frame.pack(fill="x", padx=40, pady=10)

tk.Label(result_frame, text="BSC vs. Mastectomie", bg="#ffffff", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(5, 0))

# Starttekst met uitleg
introductie_tekst = (
    "Dit Clinical Decision Support System (CDSS) helpt bij de keuze tussen "
    "borstsparende chirurgie (BSC) en mastectomie voor patiënten met borstkanker.\n\n"
    "💠 Borstsparende chirurgie (BSC) betekent dat de tumor verwijderd wordt, maar de borst grotendeels behouden blijft. "
    "Na de operatie is bijna altijd radiotherapie nodig.\n\n"
    "💠 Mastectomie is het volledig verwijderen van de borst. Dit kan nodig zijn bij grotere tumoren, meerdere tumoren, "
    "of wanneer radiotherapie niet mogelijk is.\n\n"
    "Na het invullen van de patiëntgegevens en het klikken op 'Bereken aanbeveling' verschijnt hieronder een advies gebaseerd op klinische criteria."
)

resultaat_text = tk.StringVar(value=introductie_tekst)
tk.Label(result_frame, textvariable=resultaat_text, wraplength=520, justify="left", bg="#ffffff",
         font=("Segoe UI", 10)).pack(padx=10, pady=10, anchor="w")

# --- Resetfunctie ---
def reset_gui():
    tumor_entry.delete(0, tk.END)
    tumor_entry.insert(0, "")
    multicentrisch_var.set("")
    bestraling_var.set("")
    zwanger_var.set("")
    radiotherapie_var.set("")
    resultaat_text.set(introductie_tekst)

# --- Resetknop ---
reset_btn = ttk.Button(frm, text="♻ Reset formulier", command=reset_gui)
reset_btn.grid(row=9, column=0, columnspan=3, pady=10)

root.mainloop()

