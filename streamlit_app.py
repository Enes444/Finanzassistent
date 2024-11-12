import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import json
from email_validator import validate_email, EmailNotValidError
import os
import smtplib
from email.mime.text import MIMEText

# -------------------- Geschäftslogik Funktionen -------------------- #

def lade_bankdaten(datei):
    try:
        with open(datei, 'r') as f:
            daten = json.load(f)
        return daten
    except FileNotFoundError:
        st.error(f"Datei {datei} nicht gefunden.")
        return []
    except json.JSONDecodeError:
        st.error(f"Fehler beim Parsen der Datei {datei}.")
        return []

def berechne_monatliche_ausgaben(daten):
    ausgaben = {}
    for transaktion in daten:
        kategorie = transaktion['kategorie']
        betrag = transaktion['betrag']
        if betrag < 0:
            ausgaben[kategorie] = ausgaben.get(kategorie, 0) + abs(betrag)
    return ausgaben

def zeige_ausgaben(ausgaben):
    st.markdown("### 📊 Durchschnittliche monatliche Ausgaben pro Kategorie:")
    df = pd.DataFrame(list(ausgaben.items()), columns=["Kategorie", "Betrag"])

    # Plotly Balkendiagramm mit eindeutigen Schlüssel
    fig = px.bar(df, x="Kategorie", y="Betrag", title="Monatliche Ausgaben", color="Kategorie")
    st.plotly_chart(fig, use_container_width=True, key="ausgaben_balken_unique")  # Eindeutiger Schlüssel

def lade_praeferenzen(datei):
    try:
        with open(datei, 'r') as f:
            daten = json.load(f)
        return daten
    except FileNotFoundError:
        st.error(f"Datei {datei} nicht gefunden.")
        return {}
    except json.JSONDecodeError:
        st.error(f"Fehler beim Parsen der Datei {datei}.")
        return {}

def empfehle_einsparungen(ausgaben, praef):
    st.markdown("### 💡 Empfehlungen zur Einsparung basierend auf deinen Präferenzen:")
    prioritaeten = praef.get("Prioritäten", {})

    for kategorie, betrag in ausgaben.items():
        prioritaet = prioritaeten.get(kategorie, "niedrig")
        if prioritaet == "hoch":
            einsparung = betrag * 0.5  # 50% einsparen
            neue_rate = betrag - einsparung
            st.markdown(f"- **{kategorie}**: Reduziere auf **{neue_rate:.2f} Euro** (50% Einsparung)")
        elif prioritaet == "mittel":
            einsparung = betrag * 0.3  # 30% einsparen
            neue_rate = betrag - einsparung
            st.markdown(f"- **{kategorie}**: Reduziere auf **{neue_rate:.2f} Euro** (30% Einsparung)")
        else:
            einsparung = betrag * 0.1  # 10% einsparen
            neue_rate = betrag - einsparung
            st.markdown(f"- **{kategorie}**: Reduziere auf **{neue_rate:.2f} Euro** (10% Einsparung)")

def lade_fitnessdaten(datei):
    try:
        with open(datei, 'r') as f:
            daten = json.load(f)
        return daten
    except FileNotFoundError:
        st.error(f"Datei {datei} nicht gefunden.")
        return {}
    except json.JSONDecodeError:
        st.error(f"Fehler beim Parsen der Datei {datei}.")
        return {}

def analysiere_fitnessdaten(fitnessdaten):
    schritte = fitnessdaten.get("Schritte_pro_Tag", [])
    durchschnittsschritte = sum(schritte) / len(schritte) if schritte else 0
    aktivitaeten = fitnessdaten.get("Sportaktivitäten", [])
    return durchschnittsschritte, aktivitaeten

def empfehle_fitness_und_sparen(durchschnittsschritte, aktivitaeten):
    st.markdown("### 🏃‍♂️ Empfehlungen basierend auf deinen Fitness-Daten:")
    if durchschnittsschritte < 8000:
        st.warning(f"- Dein durchschnittlicher Schrittzahl ist **{durchschnittsschritte:.0f}**, versuche mehr zu gehen, um Gesundheit und eventuell Kosten zu sparen (z.B. weniger Fahrtkosten).")
    else:
        st.success(f"- Dein durchschnittlicher Schrittzahl ist **{durchschnittsschritte:.0f}**, weiter so!")

    st.write("- **Sportaktivitäten**, die du kostengünstig gestalten kannst:")
    for aktivitaet in aktivitaeten:
        st.write(f"  * {aktivitaet}")

def erstelle_monatsbericht(sparziel, zeitraum, monatliche_rate, ausgaben, praef, durchschnittsschritte, aktivitaeten):
    bericht = f"""
**Monatsbericht**
=================

**Sparziel:** {sparziel} Euro  
**Zeitraum:** {zeitraum} Monate  
**Monatliche Sparrate:** {monatliche_rate:.2f} Euro  

---

**Ausgaben pro Kategorie:**
"""
    for kategorie, betrag in ausgaben.items():
        bericht += f"- **{kategorie}**: {betrag:.2f} Euro\n"

    bericht += "\n**Empfehlungen zur Einsparung basierend auf deinen Präferenzen:**\n"
    prioritaeten = praef.get("Prioritäten", {})
    for kategorie, betrag in ausgaben.items():
        prioritaet = prioritaeten.get(kategorie, "niedrig")
        if prioritaet == "hoch":
            einsparung = betrag * 0.5
            neue_rate = betrag - einsparung
            bericht += f"- **{kategorie}**: Reduziere auf **{neue_rate:.2f} Euro** (50% Einsparung)\n"
        elif prioritaet == "mittel":
            einsparung = betrag * 0.3
            neue_rate = betrag - einsparung
            bericht += f"- **{kategorie}**: Reduziere auf **{neue_rate:.2f} Euro** (30% Einsparung)\n"
        else:
            einsparung = betrag * 0.1
            neue_rate = betrag - einsparung
            bericht += f"- **{kategorie}**: Reduziere auf **{neue_rate:.2f} Euro** (10% Einsparung)\n"

    bericht += "\n**Empfehlungen basierend auf deinen Fitness-Daten:**\n"
    if durchschnittsschritte < 8000:
        bericht += f"- Dein durchschnittlicher Schrittzahl ist **{durchschnittsschritte:.0f}**, versuche mehr zu gehen, um Gesundheit und eventuell Kosten zu sparen.\n"
    else:
        bericht += f"- Dein durchschnittlicher Schrittzahl ist **{durchschnittsschritte:.0f}**, weiter so!\n"

    bericht += "- **Sportaktivitäten**, die du kostengünstig gestalten kannst:\n"
    for aktivitaet in aktivitaeten:
        bericht += f"  * {aktivitaet}\n"

    return bericht

def sende_email(empfaenger, betreff, inhalt, absender, smtp_server, smtp_port, smtp_user, smtp_pass):
    msg = MIMEText(inhalt)
    msg['Subject'] = betreff
    msg['From'] = absender
    msg['To'] = empfaenger

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return "Bericht wurde per E-Mail gesendet."
    except Exception as e:
        return f"Fehler beim Senden der E-Mail: {e}"

def berechne_monatliche_sparrate(sparziel, zeitraum):
    try:
        monatliche_rate = sparziel / zeitraum
        return monatliche_rate
    except ZeroDivisionError:
        return "Der Zeitraum darf nicht null sein."

# -------------------- Streamlit Benutzeroberfläche -------------------- #

def main():
    st.set_page_config(page_title="📈 Persönlicher Finanzassistent", layout="wide")
    st.title("📈 Persönlicher Finanzassistent")

    st.sidebar.header("🛠️ Einstellungen")

    # Sparziel und Zeitraum Eingabe
    sparziel = st.sidebar.number_input(
        "💰 Wie viel Geld möchtest du sparen? (in Euro):",
        min_value=0.0,
        step=100.0,
        value=1200.0
    )
    zeitraum = st.sidebar.number_input(
        "📅 In wie vielen Monaten möchtest du dein Ziel erreichen?",
        min_value=1,
        step=1,
        value=12
    )

    if sparziel <= 0 or zeitraum <= 0:
        st.sidebar.error("Bitte gib positive Werte für Sparziel und Zeitraum ein.")
        st.stop()

    monatliche_rate = berechne_monatliche_sparrate(sparziel, zeitraum)
    st.sidebar.markdown(f"**Monatliche Sparrate:** {monatliche_rate:.2f} Euro")

    # Laden der Daten
    with st.spinner("Daten werden geladen..."):
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

    # Visualisierungen
    st.header("📊 Visualisierungen")
    col1, col2 = st.columns(2)

    # Ausgabenvisualisierung
    if daten:
        with col1:
            st.subheader("Monatliche Ausgaben")
            ausgaben_df = pd.DataFrame(list(ausgaben.items()), columns=["Kategorie", "Betrag"])
            fig = px.bar(
                ausgaben_df,
                x="Kategorie",
                y="Betrag",
                title="Monatliche Ausgaben",
                color="Kategorie",
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True, key="ausgaben_balken_unique_1")  # Eindeutiger Schlüssel

    # Fitnessdatenvisualisierung
    if fitnessdaten:
        with col2:
            st.subheader("Schritte pro Tag")
            schritte = fitnessdaten.get("Schritte_pro_Tag", [])
            tags = [f"Tag {i+1}" for i in range(len(schritte))]
            schritte_df = pd.DataFrame({
                "Tag": tags,
                "Schritte": schritte
            })
            fig_steps = px.line(
                schritte_df,
                x="Tag",
                y="Schritte",
                title="Schritte pro Tag",
                markers=True,
                template="plotly_dark"
            )
            st.plotly_chart(fig_steps, use_container_width=True, key="schritte_linienchart_unique_2")  # Eindeutiger Schlüssel

    # Sportaktivitäten anzeigen
    if fitnessdaten:
        st.subheader("🧘‍♂️ Sportaktivitäten")
        st.write(", ".join(aktivitaeten))

    # Monatsbericht erstellen und anzeigen
    st.header("📄 Monatsbericht")
    if daten and praef and fitnessdaten:
        if st.button("Monatsbericht erstellen"):
            bericht = erstelle_monatsbericht(
                sparziel,
                zeitraum,
                monatliche_rate,
                ausgaben,
                praef,
                durchschnittsschritte,
                aktivitaeten
            )
            st.text_area("📄 Monatsbericht:", value=bericht, height=300)

            # Optional: E-Mail senden
            sende_email_option = st.checkbox("📧 Monatsbericht per E-Mail senden")
            if sende_email_option:
                empfaenger = st.text_input("📨 E-Mail-Adresse des Empfängers:")
                absender = st.text_input("✉️ Deine E-Mail-Adresse:")
                smtp_server = st.text_input("🔐 SMTP-Server (z.B. smtp.gmail.com):")
                smtp_port = st.number_input("🔢 SMTP-Port (z.B. 587):", min_value=1, step=1, value=587)
                smtp_user = absender
                smtp_pass = st.text_input("🔑 E-Mail-Passwort eingeben:", type="password")

                if st.button("📤 Bericht senden"):
                    # Validierung der E-Mail-Adressen
                    try:
                        valid = validate_email(empfaenger)
                        empfaenger = valid.email
                        valid = validate_email(absender)
                        absender = valid.email
                    except EmailNotValidError as e:
                        st.error(str(e))
                        st.stop()

                    # Überprüfen, ob alle Felder ausgefüllt sind
                    if not all([empfaenger, absender, smtp_server, smtp_port, smtp_user, smtp_pass]):
                        st.error("Bitte fülle alle Felder aus.")
                        st.stop()

                    # E-Mail senden
                    ergebnis = sende_email(
                        empfaenger,
                        "Monatsbericht Finanzassistent",
                        bericht,
                        absender,
                        smtp_server,
                        smtp_port,
                        smtp_user,
                        smtp_pass
                    )
                    if "gesendet" in ergebnis.lower():
                        st.success(ergebnis)
                    else:
                        st.error(ergebnis)
    else:
        st.warning("Stelle sicher, dass alle Datenquellen vorhanden sind.")

if __name__ == "__main__":
    main()
