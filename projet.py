#!/usr/bin/env python3
"""
BioShield - CryptoBox, brique 1
César, Substitution, Transposition par colonnes (sans bibliothèque de cryptographie).
Interface : Tkinter (inclus avec Python).   Lancer :  python bioshield.py
"""
import random
import string
import sys
import unicodedata
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

ALPHA = string.ascii_uppercase


# ======================================================================
#  LOGIQUE CRYPTO
# ======================================================================
def clean(text: str) -> str:
    """Majuscules A-Z uniquement : sans espaces, accents ni ponctuation."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return "".join(c for c in text.upper() if c in ALPHA)


# ---------- César : C = (M + k) mod 26 ----------
def caesar_encrypt(msg: str, k: int) -> str:
    return "".join(ALPHA[(ALPHA.index(c) + k) % 26] for c in clean(msg))


def caesar_decrypt(msg: str, k: int) -> str:
    return caesar_encrypt(msg, -k)


# ---------- Détection du texte "qui a du sens" (force brute) ----------
FR_FREQ = dict(zip(ALPHA, [
    7.64, 0.90, 3.26, 3.67, 14.72, 1.07, 0.87, 0.74, 7.53, 0.55, 0.05, 5.46, 2.97,
    7.10, 5.80, 2.52, 1.36, 6.69, 7.95, 7.24, 6.31, 1.84, 0.05, 0.43, 0.13, 0.33]))
FR_WORDS = set("""
DE LA LE LES UN UNE DES DU ET EN AU AUX EST SONT ETE ETRE AVOIR A AI AS ONT AVEC SANS SOUS SUR DANS PAR POUR
CE CET CETTE CES SE SA SON SES MON MA MES TON TA TES NOTRE NOS VOTRE VOS LEUR LEURS JE TU IL ELLE ON NOUS VOUS ILS ELLES
ME TE LUI Y NE PAS PLUS RIEN JAMAIS TOUT TOUS TOUTE TOUTES TRES BIEN MAL MAIS OU DONC OR NI CAR SI QUE QUI QUOI DONT QUAND COMME
COMMENT POURQUOI PUIS ALORS AUSSI ENCORE DEJA TOUJOURS ICI LA LAS BAS HAUT PEU BEAUCOUP ASSEZ TROP MOINS FAIRE FAIT FAIS FONT
DIRE DIT VOIR VU ALLER VA VONT VENIR VIENT POUVOIR PEUT VEUT VOULOIR DOIT DEVOIR SAVOIR SAIT FAUT PRENDRE PREND METTRE MET
DONNER DONNE TROUVER PARLER ARRIVER PASSER RESTER TENIR TIENT CROIRE
BONJOUR BONSOIR SALUT MERCI AMI AMIS AMIE AMIES MESSAGE MESSAGES SECRET SECRETS CLE CLES CODE CODES MOT MOTS TEXTE LETTRE LETTRES
CHIFFRE CHIFFREMENT CRYPTO CRYPTAGE CESAR ORDRE ORDRES ATTAQUE ATTAQUER DEFENSE ENNEMI ENNEMIS ARMEE TROUPES SOLDAT SOLDATS
CHATEAU PONT PORTE PORTES MUR MURS TOUR TOURS VILLE VILLAGE ROUTE CHEMIN FORET RIVIERE MONTAGNE MER OCEAN ILE PLAGE
RENDEZ RENDEZVOUS MIDI MINUIT MATIN SOIR NUIT JOUR JOURS HEURE HEURES DEMAIN HIER AUJOURDHUI SEMAINE MOIS ANNEE LUNDI MARDI MERCREDI
JEUDI VENDREDI SAMEDI DIMANCHE
PREMIER PREMIERE DEUX TROIS QUATRE CINQ SIX SEPT HUIT NEUF DIX VINGT CENT MILLE
GRAND GRANDE PETIT PETITE BON BONNE NOUVEAU NOUVELLE VIEUX VIEILLE AUTRE AUTRES MEME MEMES SEUL SEULE VRAI VRAIE FAUX
HOMME HOMMES FEMME FEMMES ENFANT ENFANTS PERE MERE FRERE SOEUR FILS FILLE ROI REINE CHEF MAITRE MONDE VIE MORT TEMPS CHOSE CHOSES
MAISON MAISONS ECOLE CLASSE COURS EXAMEN TRAVAIL PROJET OUTIL OUTILS GROUPE EQUIPE BINOME DEPOT SUJET REPONSE QUESTION
LIRE ECRIRE TROUVE TROUVEZ LISEZ BRAVO FELICITATIONS VICTOIRE GAGNE REUSSI DECHIFFRE DECHIFFREMENT
ENVOYER ENVOYE ENVOYEZ APPORTER APPORTEZ ATTENDRE ATTENDEZ PARTIR PARTEZ ARRIVEZ VENEZ ALLEZ SUIVRE SUIVEZ CACHER CACHE CACHEZ
OR ARGENT TRESOR CARTE CARTES PLAN PLANS PLACE PLACES LIEU NORD SUD EST OUEST GAUCHE DROITE DEVANT DERRIERE
AVANT APRES PENDANT DEPUIS JUSQUE VERS CHEZ ENTRE CONTRE SELON SAUF
EAU FEU TERRE AIR SOLEIL LUNE ETOILE CIEL
""".split())
BIGRAMS = set("ES LE DE EN RE NT ON ER TE EL AN SE ET LA AI IT ME OU EM IE UR TI EU QU IS NE ND OR NS EC AR UN RA TA LL DA SS TR PA PO CE CO OM US RI IN AL RO MA LI EX UE IL".split())
MAX_WORD = max(len(w) for w in FR_WORDS)


def word_coverage(text: str) -> float:
    """Découpe le texte (sans espaces) en mots français connus : plus c'est haut, mieux c'est."""
    n = len(text)
    best = [0] * (n + 1)
    for i in range(1, n + 1):
        best[i] = best[i - 1]
        for length in range(2, min(MAX_WORD, i) + 1):
            if text[i - length:i] in FR_WORDS:
                weight = length * length if length >= 3 else 2
                best[i] = max(best[i], best[i - length] + weight)
    return best[n] / n


def french_score(text: str) -> float:
    """Score de 'ressemblance au français' : plus il est HAUT, plus le texte est probable."""
    n = len(text)
    if n < 2:
        return -1e9
    chi2 = sum((text.count(l) - p * n / 100) ** 2 / (p * n / 100) for l, p in FR_FREQ.items()) / n
    bigrams = sum(text[i:i + 2] in BIGRAMS for i in range(n - 1)) / (n - 1)
    vowels = sum(text.count(v) for v in "AEIOUY") / n
    return 3 * word_coverage(text) + 6 * bigrams - 0.25 * chi2 - 4 * abs(vowels - 0.45)


def caesar_bruteforce(msg: str):
    """Teste les 25 clés. Retourne (liste [(k, texte)], meilleur (k, texte), top 3 classé)."""
    msg = clean(msg)
    results = [(k, caesar_decrypt(msg, k)) for k in range(1, 26)]
    ranked = sorted(results, key=lambda r: french_score(r[1]), reverse=True)
    return results, ranked[0], ranked[:3]


# ---------- Substitution ----------
def valid_sub_key(key: str) -> bool:
    return len(key) == 26 and set(key) == set(ALPHA)


def random_sub_key() -> str:
    letters = list(ALPHA)
    random.shuffle(letters)
    return "".join(letters)


def sub_encrypt(msg: str, key: str) -> str:
    return "".join(key[ALPHA.index(c)] for c in clean(msg))


def sub_decrypt(msg: str, key: str) -> str:
    return "".join(ALPHA[key.index(c)] for c in clean(msg))


# ---------- Transposition par colonnes ----------
def column_order(keyword: str):
    """Indices des colonnes dans l'ordre alphabétique du mot-clé
    (lettres identiques : ordre d'apparition)."""
    return sorted(range(len(keyword)), key=lambda i: (keyword[i], i))


def trans_encrypt(msg: str, keyword: str) -> str:
    msg, n = clean(msg), len(keyword)
    msg += "X" * (-len(msg) % n)
    rows = [msg[i:i + n] for i in range(0, len(msg), n)]
    return "".join("".join(r[c] for r in rows) for c in column_order(keyword))


def trans_decrypt(msg: str, keyword: str) -> str:
    msg, n = clean(msg), len(keyword)
    if len(msg) % n:
        raise ValueError("La longueur du message doit être un multiple de la longueur du mot-clé.")
    nrows = len(msg) // n
    cols = {c: msg[pos * nrows:(pos + 1) * nrows] for pos, c in enumerate(column_order(keyword))}
    return "".join(cols[c][r] for r in range(nrows) for c in range(n))


# ======================================================================
#  INTERFACE
# ======================================================================
BG = "#0a0e1a"
SURFACE = "#0f1526"
CARD = "#141b30"
INPUT = "#0c1223"
BORDER = "#253052"
FG = "#e8ecf8"
MUTED = "#8793b3"
ACCENT = "#6366f1"
ACCENT_H = "#7b7ef4"
GHOST = "#222b4a"
GHOST_H = "#2d3961"
OK = "#34d399"

UI = "TkDefaultFont"
MONO = "TkFixedFont"


def pick_fonts():
    global UI, MONO
    fams = set(tkfont.families())
    for f in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Inter", "Ubuntu", "Noto Sans", "DejaVu Sans"):
        if f in fams:
            UI = f
            break
    for f in ("Cascadia Mono", "Consolas", "SF Mono", "Menlo", "JetBrains Mono", "DejaVu Sans Mono"):
        if f in fams:
            MONO = f
            break


def copy_text(widget, text, btn=None):
    widget.clipboard_clear()
    widget.clipboard_append(text)
    widget.update()
    if btn is not None:
        btn.flash("Copié ✓")


class Btn(tk.Canvas):
    """Bouton moderne aux coins arrondis avec effet de survol."""

    def __init__(self, parent, text, command, kind="primary", bg=CARD, padx=18, height=36):
        self._font = tkfont.Font(family=UI, size=10, weight="bold")
        self._padx, self._h = padx, height
        self.base_text = self.text = text
        self.command = command
        self.colors = (ACCENT, ACCENT_H) if kind == "primary" else (GHOST, GHOST_H)
        self.current = self.colors[0]
        super().__init__(parent, width=self._font.measure(text) + 2 * padx, height=height,
                         bg=bg, highlightthickness=0, cursor="hand2")
        self._draw()
        self.bind("<Enter>", lambda e: self._paint(self.colors[1]))
        self.bind("<Leave>", lambda e: self._paint(self.colors[0]))
        self.bind("<ButtonRelease-1>", lambda e: self.command() if self.command else None)

    def _draw(self):
        self.delete("all")
        w, h, r = int(self["width"]), self._h, 10
        pts = [r, 0, w - r, 0, w, 0, w, r, w, h - r, w, h, w - r, h, r, h, 0, h, 0, h - r, 0, r, 0, 0]
        self.create_polygon(pts, smooth=True, fill=self.current, outline=self.current)
        self.create_text(w / 2, h / 2, text=self.text, fill="white", font=self._font)

    def _paint(self, color):
        self.current = color
        self._draw()

    def set_text(self, text):
        self.base_text = self.text = text
        self.configure(width=self._font.measure(text) + 2 * self._padx)
        self._draw()

    def flash(self, text, ms=1200):
        self.text = text
        self._draw()
        self.after(ms, self._restore)

    def _restore(self):
        self.text = self.base_text
        self._draw()


def make_readonly(t: tk.Text):
    """Zone de texte sélectionnable/copiable mais non modifiable."""
    def on_key(e):
        if e.state & 0x4 and e.keysym.lower() == "c":
            return None
        if e.keysym in ("Left", "Right", "Up", "Down", "Home", "End", "Prior", "Next"):
            return None
        return "break"

    def select_all(_):
        t.tag_add("sel", "1.0", "end-1c")
        return "break"

    t.bind("<Key>", on_key)
    t.bind("<Control-a>", select_all)
    t.bind("<Control-A>", select_all)
    t.bind("<Button-1>", lambda e: t.focus_set())


def label(parent, text, size=10, bold=False, color=FG, bg=CARD, **kw):
    return tk.Label(parent, text=text, font=(UI, size, "bold" if bold else "normal"),
                    fg=color, bg=bg, **kw)


def entry(parent, var, width=24, mono=True, **kw):
    return tk.Entry(parent, textvariable=var, width=width, font=(MONO if mono else UI, 11),
                    bg=INPUT, fg=FG, insertbackground=FG, relief="flat", highlightthickness=1,
                    highlightbackground=BORDER, highlightcolor=ACCENT, **kw)


def spin(parent, var):
    return tk.Spinbox(parent, from_=0, to=25, width=4, textvariable=var, font=(MONO, 12, "bold"),
                      bg=INPUT, fg=FG, insertbackground=FG, relief="flat", justify="center",
                      buttonbackground=GHOST, highlightthickness=1, highlightbackground=BORDER,
                      highlightcolor=ACCENT, wrap=True)


class TextArea(tk.Frame):
    """Zone de texte avec titre ; en lecture seule elle a un bouton Copier."""

    def __init__(self, parent, title, height=3, readonly=False):
        super().__init__(parent, bg=CARD)
        head = tk.Frame(self, bg=CARD)
        head.pack(fill="x", pady=(0, 5))
        label(head, title, 9, True, MUTED).pack(side="left")
        self.readonly = readonly
        self.text = tk.Text(self, height=height, wrap="char", font=(MONO, 12), bg=INPUT,
                            fg=OK if readonly else FG, insertbackground=FG, relief="flat",
                            padx=10, pady=8, highlightthickness=1, highlightbackground=BORDER,
                            highlightcolor=ACCENT, selectbackground=ACCENT, selectforeground="white")
        self.text.pack(fill="x")
        if readonly:
            make_readonly(self.text)
            self.btn = Btn(head, "Copier", lambda: copy_text(self, self.get(), self.btn),
                           kind="ghost", height=26, padx=12)
            self.btn.pack(side="right")

    def get(self):
        return self.text.get("1.0", "end").strip()

    def set(self, value):
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)


def card(parent, title, subtitle=""):
    outer = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    outer.pack(fill="x", padx=6, pady=8)
    inner = tk.Frame(outer, bg=CARD)
    inner.pack(fill="x", padx=20, pady=18)
    label(inner, title, 13, True).pack(anchor="w")
    if subtitle:
        label(inner, subtitle, 9, False, MUTED).pack(anchor="w", pady=(2, 0))
    tk.Frame(inner, bg=CARD, height=10).pack()
    return inner


def row(parent, pady=(12, 0)):
    r = tk.Frame(parent, bg=CARD)
    r.pack(fill="x", pady=pady)
    return r


class ScrollFrame(tk.Frame):
    """Page défilante (molette de souris incluse)."""

    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        bar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=BG)
        self.win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.win, width=e.width))
        self.bind("<Enter>", lambda e: self._bind_wheel())
        self.bind("<Leave>", lambda e: self._unbind_wheel())

    def _bind_wheel(self):
        self.bind_all("<MouseWheel>", self._wheel)
        self.bind_all("<Button-4>", self._wheel)
        self.bind_all("<Button-5>", self._wheel)

    def _unbind_wheel(self):
        for ev in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.unbind_all(ev)

    def _wheel(self, e):
        if isinstance(e.widget, ttk.Treeview):
            return
        if self.inner.winfo_height() <= self.canvas.winfo_height():
            return
        if e.num == 4:
            step = -2
        elif e.num == 5:
            step = 2
        else:
            step = int(-e.delta / 120) * 2 if abs(e.delta) >= 120 else (-2 if e.delta > 0 else 2)
        self.canvas.yview_scroll(step, "units")


# ======================================================================
class CaesarTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        # ---------------- chiffrement ----------------
        c = card(self, "Chiffrement", "C = (M + k) mod 26 — choisissez la clé k")
        self.enc_in = TextArea(c, "MESSAGE CLAIR", 2)
        self.enc_in.pack(fill="x")
        r = row(c)
        label(r, "Clé k").pack(side="left")
        self.enc_k = tk.StringVar(value="3")
        spin(r, self.enc_k).pack(side="left", padx=10)
        Btn(r, "Chiffrer", self.encrypt).pack(side="left")
        self.enc_out = TextArea(c, "MESSAGE CHIFFRÉ", 2, readonly=True)
        self.enc_out.pack(fill="x", pady=(14, 0))

        # ---------------- déchiffrement ----------------
        d = card(self, "Déchiffrement", "Avec la clé connue, ou en testant les 25 clés (force brute)")
        self.dec_in = TextArea(d, "MESSAGE CHIFFRÉ", 2)
        self.dec_in.pack(fill="x")
        self.mode = tk.StringVar(value="key")
        r = row(d)
        for text, val in (("Avec la clé k", "key"), ("Force brute (25 clés)", "brute")):
            tk.Radiobutton(r, text=text, variable=self.mode, value=val, command=self._mode_changed,
                           font=(UI, 10), fg=FG, bg=CARD, selectcolor=INPUT, activebackground=CARD,
                           activeforeground=ACCENT, highlightthickness=0, bd=0,
                           cursor="hand2").pack(side="left", padx=(0, 18))

        # mode clé connue
        self.key_zone = tk.Frame(d, bg=CARD)
        r = row(self.key_zone)
        label(r, "Clé k").pack(side="left")
        self.dec_k = tk.StringVar(value="3")
        spin(r, self.dec_k).pack(side="left", padx=10)
        Btn(r, "Déchiffrer", self.decrypt).pack(side="left")
        self.dec_out = TextArea(self.key_zone, "MESSAGE CLAIR", 2, readonly=True)
        self.dec_out.pack(fill="x", pady=(14, 0))

        # mode force brute
        self.brute_zone = tk.Frame(d, bg=CARD)
        r = row(self.brute_zone)
        Btn(r, "Lancer la force brute", self.brute).pack(side="left")
        self.toggle_btn = Btn(r, "Masquer les résultats", self.toggle, kind="ghost")
        self.toggle_btn.pack(side="left", padx=10)

        self.list_zone = tk.Frame(self.brute_zone, bg=CARD)
        self.list_zone.pack(fill="x", pady=(12, 0))
        wrap = tk.Frame(self.list_zone, bg=CARD)
        wrap.pack(fill="x")
        self.tree = ttk.Treeview(wrap, columns=("k", "txt"), show="headings", height=10,
                                 selectmode="browse")
        self.tree.heading("k", text="CLÉ k")
        self.tree.heading("txt", text="TEXTE OBTENU")
        self.tree.column("k", width=70, anchor="center", stretch=False)
        self.tree.column("txt", width=560)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="x", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.tag_configure("best", foreground=OK)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self.copy_selected())
        self.tree.bind("<Control-c>", lambda e: self.copy_selected())
        self.sel_area = TextArea(self.list_zone, "LIGNE SÉLECTIONNÉE (cliquez sur une ligne du tableau)",
                                 2, readonly=True)
        self.sel_area.pack(fill="x", pady=(12, 0))

        self.best_zone = tk.Frame(self.brute_zone, bg=CARD)
        self.best_title = label(self.best_zone, "", 12, True, OK)
        self.best_title.pack(anchor="w", pady=(4, 8))
        self.best_area = TextArea(self.best_zone, "MESSAGE LISIBLE TROUVÉ", 2, readonly=True)
        self.best_area.pack(fill="x")
        self.others = label(self.best_zone, "", 9, False, MUTED, justify="left", anchor="w")
        self.others.pack(anchor="w", pady=(10, 0))

        self.results, self.best, self.top3, self.hidden = [], None, [], False
        self._mode_changed()

    # ---- helpers ----
    def _mode_changed(self):
        self.key_zone.pack_forget()
        self.brute_zone.pack_forget()
        if self.mode.get() == "key":
            self.key_zone.pack(fill="x")
        else:
            self.brute_zone.pack(fill="x")

    def _k(self, var):
        try:
            return int(var.get()) % 26
        except ValueError:
            messagebox.showerror("Clé invalide", "La clé k doit être un entier entre 0 et 25.")
            return None

    def encrypt(self):
        k = self._k(self.enc_k)
        if k is not None:
            self.enc_out.set(caesar_encrypt(self.enc_in.get(), k))

    def decrypt(self):
        k = self._k(self.dec_k)
        if k is not None:
            self.dec_out.set(caesar_decrypt(self.dec_in.get(), k))

    # ---- force brute ----
    def brute(self):
        msg = clean(self.dec_in.get())
        if not msg:
            messagebox.showinfo("BioShield", "Entrez d'abord un message chiffré.")
            return
        self.results, self.best, self.top3 = caesar_bruteforce(msg)
        self.tree.delete(*self.tree.get_children())
        for k, txt in self.results:
            self.tree.insert("", "end", iid=str(k), values=(k, txt),
                             tags=("best",) if k == self.best[0] else ())
        self.tree.selection_set(str(self.best[0]))
        self.tree.see(str(self.best[0]))
        self.hidden = True       # on affiche d'abord tous les résultats
        self.toggle()

    def _selected(self):
        sel = self.tree.selection()
        return self.tree.item(sel[0], "values") if sel else None

    def _on_select(self, _e=None):
        v = self._selected()
        if v:
            self.sel_area.set(str(v[1]))

    def copy_selected(self):
        v = self._selected()
        if v:
            copy_text(self, str(v[1]))
            self.sel_area.btn.flash("Copié ✓")

    def toggle(self):
        if not self.results:
            return
        self.hidden = not self.hidden
        if self.hidden:
            self.list_zone.pack_forget()
            k, txt = self.best
            self.best_title.config(text=f"✔ Clé la plus probable : k = {k}")
            self.best_area.set(txt)
            others = [f"k = {kk} → {t}" for kk, t in self.top3[1:]]
            self.others.config(text="Autres candidats : " + "   |   ".join(others) if others else "")
            self.best_zone.pack(fill="x", pady=(12, 0))
            self.toggle_btn.set_text("Afficher tous les résultats")
        else:
            self.best_zone.pack_forget()
            self.list_zone.pack(fill="x", pady=(12, 0))
            self.toggle_btn.set_text("Masquer les résultats")


# ======================================================================
class SubstitutionTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        c = card(self, "Chiffrement", "La clé est un alphabet de 26 lettres, généré aléatoirement")
        self.enc_in = TextArea(c, "MESSAGE CLAIR", 2)
        self.enc_in.pack(fill="x")
        r = row(c)
        label(r, "Clé").pack(side="left")
        self.enc_key = tk.StringVar()
        entry(r, self.enc_key, 30, state="readonly", readonlybackground=INPUT).pack(side="left", padx=10, ipady=4)
        Btn(r, "🎲 Générer", self.generate, kind="ghost").pack(side="left")
        self.copy_key_btn = Btn(r, "Copier la clé", lambda: copy_text(self, self.enc_key.get(), self.copy_key_btn),
                                kind="ghost")
        self.copy_key_btn.pack(side="left", padx=8)
        Btn(r, "Chiffrer", self.encrypt).pack(side="left")
        self.enc_out = TextArea(c, "MESSAGE CHIFFRÉ", 2, readonly=True)
        self.enc_out.pack(fill="x", pady=(14, 0))

        d = card(self, "Déchiffrement", "Saisissez la clé de 26 lettres")
        self.dec_in = TextArea(d, "MESSAGE CHIFFRÉ", 2)
        self.dec_in.pack(fill="x")
        r = row(d)
        label(r, "Clé").pack(side="left")
        self.dec_key = tk.StringVar()
        entry(r, self.dec_key, 30).pack(side="left", padx=10, ipady=4)
        Btn(r, "Déchiffrer", self.decrypt).pack(side="left")
        self.dec_out = TextArea(d, "MESSAGE CLAIR", 2, readonly=True)
        self.dec_out.pack(fill="x", pady=(14, 0))

    def generate(self):
        self.enc_key.set(random_sub_key())

    def encrypt(self):
        if not self.enc_key.get():
            self.generate()
        self.enc_out.set(sub_encrypt(self.enc_in.get(), self.enc_key.get()))

    def decrypt(self):
        key = clean(self.dec_key.get())
        if not valid_sub_key(key):
            messagebox.showerror("Clé invalide",
                                 "La clé doit contenir exactement 26 lettres, toutes différentes (A-Z).")
            return
        self.dec_out.set(sub_decrypt(self.dec_in.get(), key))


# ======================================================================
class TranspositionTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)
        c = card(self, "Chiffrement", "Écriture en lignes sous le mot-clé, lecture par colonnes (ordre alphabétique)")
        self.enc_in = TextArea(c, "MESSAGE CLAIR", 2)
        self.enc_in.pack(fill="x")
        r = row(c)
        label(r, "Mot-clé").pack(side="left")
        self.enc_key = tk.StringVar()
        entry(r, self.enc_key, 22).pack(side="left", padx=10, ipady=4)
        Btn(r, "Chiffrer", self.encrypt).pack(side="left")
        self.enc_out = TextArea(c, "MESSAGE CHIFFRÉ", 2, readonly=True)
        self.enc_out.pack(fill="x", pady=(14, 0))
        label(c, "GRILLE UTILISÉE", 9, True, MUTED).pack(anchor="w", pady=(14, 4))
        self.grid_view = tk.Label(c, text="—", font=(MONO, 11), bg=INPUT, fg=MUTED, justify="left",
                                  anchor="w", padx=12, pady=10)
        self.grid_view.pack(fill="x")

        d = card(self, "Déchiffrement", "Saisissez le mot-clé")
        self.dec_in = TextArea(d, "MESSAGE CHIFFRÉ", 2)
        self.dec_in.pack(fill="x")
        r = row(d)
        label(r, "Mot-clé").pack(side="left")
        self.dec_key = tk.StringVar()
        entry(r, self.dec_key, 22).pack(side="left", padx=10, ipady=4)
        Btn(r, "Déchiffrer", self.decrypt).pack(side="left")
        self.dec_out = TextArea(d, "MESSAGE CLAIR", 2, readonly=True)
        self.dec_out.pack(fill="x", pady=(14, 0))

    def _keyword(self, var):
        kw = clean(var.get())
        if not kw:
            messagebox.showerror("Mot-clé invalide", "Entrez un mot-clé (lettres A-Z).")
            return None
        return kw

    def encrypt(self):
        kw = self._keyword(self.enc_key)
        if not kw:
            return
        msg = clean(self.enc_in.get())
        self.enc_out.set(trans_encrypt(msg, kw))
        n = len(kw)
        padded = msg + "X" * (-len(msg) % n)
        nums = [0] * n
        for pos, c in enumerate(column_order(kw)):
            nums[c] = pos + 1
        fmt = lambda items: " ".join(f"{x:^3}" for x in items)
        lines = [fmt(kw), fmt(nums), "─" * (4 * n - 1)]
        lines += [fmt(padded[i:i + n]) for i in range(0, len(padded), n)]
        self.grid_view.config(text="\n".join(lines), fg=FG)

    def decrypt(self):
        kw = self._keyword(self.dec_key)
        if not kw:
            return
        try:
            self.dec_out.set(trans_decrypt(self.dec_in.get(), kw))
        except ValueError as e:
            messagebox.showerror("Message invalide", str(e))


# ======================================================================
class BioShield(tk.Tk):
    def __init__(self):
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass
        super().__init__()
        pick_fonts()
        self.title("BioShield")
        self.geometry("1000x820")
        self.minsize(880, 640)
        self.configure(bg=BG)
        self._style()
        self.welcome = self._build_welcome()
        self.main = self._build_main()
        self.welcome.pack(fill="both", expand=True)

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview", background=INPUT, fieldbackground=INPUT, foreground=FG,
                    rowheight=30, font=(MONO, 11), borderwidth=0, relief="flat")
        s.configure("Treeview.Heading", background=GHOST, foreground=MUTED, font=(UI, 9, "bold"),
                    relief="flat", padding=(8, 7))
        s.map("Treeview.Heading", background=[("active", GHOST_H)])
        s.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "white")])
        s.configure("Vertical.TScrollbar", background=GHOST, troughcolor=SURFACE, bordercolor=SURFACE,
                    arrowcolor=MUTED, lightcolor=GHOST, darkcolor=GHOST, relief="flat")
        s.map("Vertical.TScrollbar", background=[("active", GHOST_H)])

    # ---------- accueil ----------
    def _build_welcome(self):
        f = tk.Frame(self, bg=BG)
        box = tk.Frame(f, bg=BG)
        box.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(box, text="🛡", font=("Segoe UI Emoji", 70), bg=BG, fg=ACCENT).pack()
        tk.Label(box, text="BioShield", font=(UI, 38, "bold"), bg=BG, fg=FG).pack(pady=(4, 0))
        tk.Label(box, text="Bienvenue — CryptoBox · brique 1", font=(UI, 14), bg=BG, fg=MUTED).pack(pady=(2, 22))
        chips = tk.Frame(box, bg=BG)
        chips.pack(pady=(0, 30))
        for t in ("César", "Substitution", "Transposition"):
            tk.Label(chips, text=t, font=(UI, 10, "bold"), bg=GHOST, fg=FG, padx=14, pady=6).pack(side="left", padx=5)
        Btn(box, "Continuer  →", self._go_main, bg=BG, padx=40, height=46).pack()
        tk.Label(box, text="Chiffrez, déchiffrez et cassez des messages classiques.",
                 font=(UI, 10), bg=BG, fg=MUTED).pack(pady=(28, 0))
        return f

    def _go_main(self):
        self.welcome.pack_forget()
        self.main.pack(fill="both", expand=True)

    # ---------- principal ----------
    def _build_main(self):
        f = tk.Frame(self, bg=BG)
        head = tk.Frame(f, bg=BG)
        head.pack(fill="x", padx=26, pady=(18, 0))
        tk.Label(head, text="🛡 BioShield", font=(UI, 18, "bold"), bg=BG, fg=FG).pack(side="left")
        tk.Label(head, text="A–Z uniquement · espaces et accents retirés automatiquement",
                 font=(UI, 9), bg=BG, fg=MUTED).pack(side="right")

        bar = tk.Frame(f, bg=BG)
        bar.pack(fill="x", padx=26, pady=(14, 0))
        tk.Frame(f, bg=BORDER, height=1).pack(fill="x", padx=26)
        body = tk.Frame(f, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=(6, 14))

        self.pages, self.tab_btns = {}, {}
        for name, cls in (("1 · César", CaesarTab), ("2 · Substitution", SubstitutionTab),
                          ("3 · Transposition", TranspositionTab)):
            sf = ScrollFrame(body)
            cls(sf.inner).pack(fill="x")
            self.pages[name] = sf
            holder = tk.Frame(bar, bg=BG, cursor="hand2")
            holder.pack(side="left", padx=(0, 22))
            lab = tk.Label(holder, text=name, font=(UI, 11, "bold"), bg=BG, fg=MUTED, cursor="hand2")
            lab.pack(pady=(0, 6))
            underline = tk.Frame(holder, bg=BG, height=3)
            underline.pack(fill="x")
            for w in (holder, lab):
                w.bind("<Button-1>", lambda e, n=name: self.show_tab(n))
            self.tab_btns[name] = (lab, underline)
        self.show_tab("1 · César")
        return f

    def show_tab(self, name):
        for n, page in self.pages.items():
            page.pack_forget()
            lab, line = self.tab_btns[n]
            lab.config(fg=MUTED)
            line.config(bg=BG)
        self.pages[name].pack(fill="both", expand=True)
        lab, line = self.tab_btns[name]
        lab.config(fg=FG)
        line.config(bg=ACCENT)


if __name__ == "__main__":
    BioShield().mainloop()