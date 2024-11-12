def berechne_monatliche_sparrate(sparziel, zeitraum):
    try:
        monatliche_rate = sparziel / zeitraum
        return monatliche_rate
    except ZeroDivisionError:
        return "Der Zeitraum darf nicht null sein."

def main():
    print("Willkommen beim persönlichen Finanzassistenten!")
    try:
        sparziel = float(input("Wie viel Geld möchtest du sparen? (in Euro): "))
        zeitraum = int(input("In wie vielen Monaten möchtest du dein Ziel erreichen? "))

        if sparziel < 0 or zeitraum <= 0:
            print("Bitte gib positive Werte ein.")
            return

        monatliche_rate = berechne_monatliche_sparrate(sparziel, zeitraum)
        print(f"Du musst {monatliche_rate:.2f} Euro pro Monat sparen, um dein Ziel in {zeitraum} Monaten zu erreichen.")
    except ValueError:
        print("Bitte gib gültige Zahlen ein.")

if __name__ == "__main__":
    main()
