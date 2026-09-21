# Montaggio

Le istruzioni complete, illustrate e passo-passo sono nel manuale:

**[MANUALE_MONTAGGIO_V4.2.pdf](MANUALE_MONTAGGIO_V4.2.pdf)** (18 pagine)

Contiene:

- **Capitolo 0** - architettura, elenco completo dei pezzi da stampare con
  volumi e orientamenti, viteria, elettronica, attrezzi, scelta del materiale
  del tappo, adattamento al proprio tubo
- **Parte A** - meccanica, dai pezzi stampati al gruppo motore-ingranaggi
- **Parte B** - elettronica, alimentazione, sensori, firmware, prova a banco
- **Parte C** - taratura, chiusura, braccio, tappo, montaggio sul telescopio,
  configurazione Ekos
- **Appendici** - comandi seriali, coppia e posizione di park, diagnostica,
  limiti verificati, come rigenerare i pezzi, note per chi viene dalla V4.1

Il manuale si rigenera dai sorgenti:

```
python docs/genera_figure_manuale.py
python docs/genera_manuale_pdf.py
```

Il testo sta in `docs/contenuto_manuale.py`, l'impaginazione in
`docs/genera_manuale_pdf.py`, le figure sono prodotte dal modello parametrico.
