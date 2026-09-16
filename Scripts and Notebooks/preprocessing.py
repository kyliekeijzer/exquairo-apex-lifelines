# preprocessing.py
# Doel: één centrale plek die de dataset inlaadt en opschoont voor BEIDE modellen.

import pandas as pd


def load_and_preprocess(path="data/raw/diabetes.csv"):
    """
    Laadt de data en doet de gedeelde opschoonstappen.
    Geeft terug: X (features) en y (target).

    Gebruik (in je eigen notebook):
        from preprocessing import load_and_preprocess
        from sklearn.model_selection import train_test_split

        X, y = load_and_preprocess()

        # ieder doet zelf de split — spreek één random_state af (bv. 42) zodat
        # alle modellen op dezelfde splitsing draaien en eerlijk vergelijkbaar zijn
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
    """

    # 1. Data inladen
    #    lees het csv-bestand in een dataframe

    # 2. GEDEELDE opschoonstappen (voor iedereen gelijk)
    #    - behandel missende waarden (bv. invullen met de mediaan of verwijderen)
    #    - (indien nodig) zet 0-en die eigenlijk "ontbrekend" betekenen eerst om
    #      naar echte missende waarden vóór je ze invult
    #    - zet categorische kolommen om naar numeriek (encoding), indien aanwezig

    # 3. Features (X) en target (y) scheiden
    #    y = de doelkolom (pas de naam aan naar jullie dataset, bv. "Outcome")
    #    X = alle overige kolommen

    # 4. Geef de schone data terug
    #    return X, y