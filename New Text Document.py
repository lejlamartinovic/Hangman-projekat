import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import random
from datetime import datetime

def ucitaj_rijeci(ime_fajla):
    kategorije = {}
    with open(ime_fajla, 'r', encoding='utf-8') as f:
        for linija in f:
            if ':' in linija:
                kat, rijeci_str = linija.strip().split(':')
                rijeci = [r.strip() for r in rijeci_str.split(',')]
                kategorije[kat.strip()] = rijeci
    return kategorije

def odaberi_rijec(kategorije, kategorija=None):
    if kategorija and kategorija in kategorije:
        rijeci = kategorije[kategorija]
    else:
        sve_rijeci = sum(kategorije.values(), [])
        return random.choice(sve_rijeci), "random"
    return random.choice(kategorije[kategorija]), kategorija

def zapisi_rezultat(igrac, mod, niz):
    with open("rezultati.txt", "a", encoding="utf-8") as f:
        datum = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"{datum} | igrac: {igrac} | mod: {mod} | niz: {niz}\n")

def procitaj_najveci_rekord(mod):
    try:
        max_niz = 0
        with open("rezultati.txt", "r", encoding="utf-8") as f:
            for linija in f:
                if f"mod: {mod}" in linija:
                    deo = linija.strip().split('|')
                    for d in deo:
                        d = d.strip()
                        if d.startswith("niz:"):
                            vrednost = int(d.split(':')[1].strip())
                            if vrednost > max_niz:
                                max_niz = vrednost
        return max_niz
    except FileNotFoundError:
        return 0

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Vješalica - Meni")
        self.root.geometry("400x350")
        self.kategorije = ucitaj_rijeci("rijeci.txt")

        frame = ttk.Frame(root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Izaberi kategoriju:", font=("Helvetica", 14)).pack(pady=(0, 10))

        self.kat_var = tk.StringVar()
        self.kat_combobox = ttk.Combobox(frame, textvariable=self.kat_var, state="readonly", width=30)
        self.kat_combobox['values'] = list(self.kategorije.keys()) + ["Sve kategorije"]
        self.kat_combobox.current(0)
        self.kat_combobox.pack(pady=(0, 20))

        ttk.Label(frame, text="Unesi ime igrača (opcionalno):", font=("Helvetica", 12)).pack(pady=(0, 5))
        self.igrac_var = tk.StringVar()
        igrac_entry = ttk.Entry(frame, textvariable=self.igrac_var, width=30)
        igrac_entry.pack(pady=(0, 20))
        self.igrac_var.set("anonimno")

        self.start_btn = ttk.Button(frame, text="🎮 Počni igru", command=self.pokreni_igru)
        self.start_btn.pack(pady=10)


    def pokreni_igru(self):
        izbor = self.kat_var.get()
        if izbor == "Sve kategorije":
            izbor = None
        self.root.destroy()
        root = tk.Tk()
        app = VjesalicaGUI(root, self.kategorije, izbor, self.igrac_var.get())
        root.mainloop()

class VjesalicaGUI:
    def __init__(self, master, kategorije, izabrana_kategorija, igrac):
        self.master = master
        self.kategorije = kategorije
        self.kategorija = izabrana_kategorija
        self.igrac = igrac
        self.niz_pogodaka = 0
        self.pogresna_slova = set()
        self.master.title("Vješalica - Igra")
        self.resetuj_igru()

    def resetuj_igru(self):
        self.slova_pogodjena = []
        self.broj_pokusaja = 6
        self.pogresna_slova.clear()
        self.trenutna_rijec, self.mod = odaberi_rijec(self.kategorije, self.kategorija)
        self.najveci_rekord = procitaj_najveci_rekord(self.mod)
        self.azuriraj_gui()

    def azuriraj_gui(self):
        self.master.geometry("400x500")
        for widget in self.master.winfo_children():
            widget.destroy()

        kat_tekst = f"Kategorija: {self.mod}" if self.mod != "random" else "Kategorija: (random)"
        tk.Label(self.master, text=kat_tekst, font=("Helvetica", 14)).pack(pady=10)

        prikaz = " ".join([slovo if slovo in self.slova_pogodjena else "_" for slovo in self.trenutna_rijec])
        tk.Label(self.master, text=prikaz, font=("Helvetica", 20)).pack(pady=10)

        self.canvas = tk.Canvas(self.master, width=200, height=200)
        self.canvas.pack()
        self.crtaj_vjesala()

        self.entry = tk.Entry(self.master)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.provjeri_slovo)
        self.entry.focus_set()

        self.status_label = tk.Label(self.master, text=f"Preostalo pokušaja: {self.broj_pokusaja}")
        self.status_label.pack()

        self.skor_label = tk.Label(self.master, text=f"Trenutni niz pogodaka: {self.niz_pogodaka}")
        self.skor_label.pack()

        self.rekord_label = tk.Label(self.master, text=f"Najveći rekord za ovaj mod: {self.najveci_rekord}")
        self.rekord_label.pack(pady=5)

        if self.pogresna_slova:
            pogresna_tekst = ", ".join(sorted(self.pogresna_slova))
        else:
            pogresna_tekst = "Nema pogrešnih slova."
        self.pogresna_label = tk.Label(self.master, text=f"Pogrešna slova: {pogresna_tekst}")
        self.pogresna_label.pack(pady=5)

    def crtaj_vjesala(self):
        c = self.canvas
        c.delete("all")
        konopac_boje = "#333"
        figura_boje = "#cc0000"
        debljina = 3

        c.create_line(50, 180, 150, 180, width=debljina)  
        c.create_line(100, 180, 100, 20, width=debljina)  
        c.create_line(100, 20, 150, 20, width=debljina)   
        c.create_line(150, 20, 150, 40, width=debljina, fill=konopac_boje)  

        if self.broj_pokusaja <= 5:
            c.create_oval(140, 40, 160, 60, width=debljina, outline=figura_boje)
        if self.broj_pokusaja <= 4:
            c.create_line(150, 60, 150, 100, width=debljina, fill=figura_boje)
        if self.broj_pokusaja <= 3:
            c.create_line(150, 70, 130, 90, width=debljina, fill=figura_boje)
        if self.broj_pokusaja <= 2:
            c.create_line(150, 70, 170, 90, width=debljina, fill=figura_boje)
        if self.broj_pokusaja <= 1:
            c.create_line(150, 100, 130, 130, width=debljina, fill=figura_boje)
        if self.broj_pokusaja <= 0:
            c.create_line(150, 100, 170, 130, width=debljina, fill=figura_boje)

    def provjeri_slovo(self, event):
        unos = self.entry.get().lower().strip()
        self.entry.delete(0, tk.END)
        if not unos or len(unos) != 1 or not unos.isalpha():
            messagebox.showwarning("Greška", "Unesi jedno slovo!")
            return
        if unos in self.slova_pogodjena or unos in self.pogresna_slova:
            return

        if unos in self.trenutna_rijec:
            self.slova_pogodjena.append(unos)
        else:
            self.pogresna_slova.add(unos)
            self.broj_pokusaja -= 1

        if self.broj_pokusaja == 0:
            self.azuriraj_gui()
            messagebox.showinfo("Izgubio si", f"Riječ je bila: {self.trenutna_rijec}")
            zapisi_rezultat(self.igrac, self.mod, self.niz_pogodaka)
            self.niz_pogodaka = 0
            self.pitanje_ponovo()
        elif all(slovo in self.slova_pogodjena for slovo in self.trenutna_rijec):
            self.niz_pogodaka += 1
            messagebox.showinfo("Bravo!", f"Tačno! Riječ je: {self.trenutna_rijec}")
            self.resetuj_igru()
        else:
            self.azuriraj_gui()

    def pitanje_ponovo(self):
        if messagebox.askyesno("Nova igra", "Želiš li da igraš ponovo?"):
            self.resetuj_igru()
        else:
            self.master.destroy()
            main()  
def main():
    root = tk.Tk()
    MainMenu(root)
    root.mainloop()

if __name__ == "__main__":
    main()
