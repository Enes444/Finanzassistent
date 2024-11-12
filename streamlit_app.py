import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import json
import getpass
import smtplib
from email.mime.text import MIMEText
from email_validator import validate_email, EmailNotValidError

# Importiere deine bestehenden Funktionen aus main.py
from main import (
    lade_bankdaten,
    berechne_monatliche_ausgaben,
    zeige_ausgaben,
    lade_praeferenzen,
    empfehle_einsparungen,
    lade_fitnessdaten,
    analysiere_fitnessdaten,
    empfehle_fitness_und_sparen,
    erstelle_monatsbericht,
    sende_email,
    berechne_monatliche_sparrate
)

def main():
    st.set_page_config(page_title="Persönlicher Finanzassistent", layout="wide")
    st.title("📈 Persönlicher Finanzassistent")

    st.sidebar.header("Einstellungen")

    # Sparziel und Zeitraum
    sparziel = st.sidebar.number_input("Wie viel Geld möchtest du sparen? (in Euro):", min_value=0.0, step=100.0, value=1200.0)
    zeitraum = st.sidebar.number_input("In wie vielen Monaten möchtest du dein Ziel erreichen?", min_value=1, step=1, value=12)

    if sparziel <= 0 or zeitraum <= 0:
        st.error("Bitte gib positive Werte für Sparziel und Zeitraum ein.")
        return

    monatliche_rate = berechne_monatliche_sparrate(sparziel, zeitraum)
    st.sidebar.markdown(f"**Monatliche Sparrate:** {monatliche_rate:.2f} Euro")

    # Laden der Daten
    daten = lade_bankdaten('bankdaten.json')
    praef = lade_praeferenzen('praeferenzen.json')
    fitnessdaten = lade_fitnessdaten('fitnessdaten.json')

    # Berechnung und Anzeige der Ausgaben
    if daten:
        ausgaben = berechne_monatliche_ausgaben(daten)
        zeige_ausgaben(ausgaben)

        if praef:
            empfehle_einsparungen(ausgaben, praef)
    else:
        st.warning("Keine Bankdaten gefunden.")

    # Analyse der Fitnessdaten
    if fitnessdaten:
        durchschnittsschritte, aktivitaeten = analysiere_fitnessdaten(fitnessdaten)
        empfehle_fitness_und_sparen(durchschnittsschritte, aktivitaeten)
    else:
        st.warning("Keine Fitnessdaten gefunden.")

    # Monatsbericht generieren
    if daten and praef and fitnessdaten:
        if st.button("Monatsbericht erstellen"):
            bericht = erstelle_monatsbericht(sparziel, zeitraum, monatliche_rate, ausgaben, praef, durchschnittsschritte, aktivitaeten)
            st.text_area("📄 Monatsbericht:", value=bericht, height=300)

            # Optional: E-Mail senden
            sende_email_option = st.checkbox("Monatsbericht per E-Mail senden")
            if sende_email_option:
                empfaenger = st.text_input("E-Mail-Adresse des Empfängers:")
                absender = st.text_input("Deine E-Mail-Adresse:")
                smtp_server = st.text_input("SMTP-Server (z.B. smtp.gmail.com):")
                smtp_port = st.number_input("SMTP-Port (z.B. 587):", min_value=1, step=1, value=587)
                smtp_user = absender
                smtp_pass = st.text_input("E-Mail-Passwort eingeben:", type="password")

                if st.button("Bericht senden"):
                    # Validierung der E-Mail-Adressen
                    try:
                        valid = validate_email(empfaenger)
                        empfaenger = valid.email
                        valid = validate_email(absender)
                        absender = valid.email
                    except EmailNotValidError as e:
                        st.error(str(e))
                        return

                    if not all([empfaenger, absender, smtp_server, smtp_port, smtp_user, smtp_pass]):
                        st.error("Bitte fülle alle Felder aus.")
                        return

                    ergebnis = sende_email(empfaenger, "Monatsbericht Finanzassistent", bericht, absender, smtp_server, smtp_port, smtp_user, smtp_pass)
                    if "gesendet" in ergebnis.lower():
                        st.success(ergebnis)
                    else:
                        st.error(ergebnis)

    # Visualisierungen
    st.header("📊 Visualisierungen")

    # Ausgabenvisualisierung
    if daten:
        st.subheader("Monatliche Ausgaben")
        ausgaben_df = pd.DataFrame(list(ausgaben.items()), columns=["Kategorie", "Betrag"])
        fig = px.bar(ausgaben_df, x="Kategorie", y="Betrag", title="Monatliche Ausgaben", color="Kategorie")
        st.plotly_chart(fig, use_container_width=True)

    # Fitnessdatenvisualisierung
    if fitnessdaten:
        st.subheader("Fitness-Daten")
        schritte = fitnessdaten.get("Schritte_pro_Tag", [])
        tags = [f"Tag {i+1}" for i in range(len(schritte))]
        schritte_df = pd.DataFrame({
            "Tag": tags,
            "Schritte": schritte
        })
        fig_steps = px.line(schritte_df, x="Tag", y="Schritte", title="Schritte pro Tag", markers=True)
        st.plotly_chart(fig_steps, use_container_width=True)

        # Sportaktivitäten anzeigen
        st.subheader("Sportaktivitäten")
        st.write(", ".join(aktivitaeten))

if __name__ == "__main__":
    main()
