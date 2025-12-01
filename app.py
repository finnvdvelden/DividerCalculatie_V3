import itertools
from pathlib import Path

import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "Indelingen Tool.xlsx"


@st.cache_data
def load_data():
    # Excel inlezen
    df = pd.read_excel(DATA_PATH)

    # Rijen met '---' of lege vak-afmetingen eruit filteren
    df = df.copy()
    df["Vak Afmetingen (L x B x Hoogte)"] = df["Vak Afmetingen (L x B x Hoogte)"].astype(str)
    df = df[~df["Vak Afmetingen (L x B x Hoogte)"].str.contains("---", na=False)]

    # Aantal vakken naar numeriek
    df["Aantal vakken"] = pd.to_numeric(df["Aantal vakken"], errors="coerce")

    # Vak-afmetingen splitten naar L, B, H
    def parse_dims(s):
        # Voorbeelden: "52 x 56 x 30" of "52x56x30"
        s = s.lower().replace(" ", "")
        parts = s.split("x")
        if len(parts) != 3:
            return None, None, None
        try:
            return float(parts[0]), float(parts[1]), float(parts[2])
        except ValueError:
            return None, None, None

    df[["vak_L", "vak_B", "vak_H"]] = df["Vak Afmetingen (L x B x Hoogte)"].apply(
        lambda x: pd.Series(parse_dims(x))
    )

    # Ongeldige rijen droppen
    df = df.dropna(subset=["vak_L", "vak_B", "vak_H", "Aantal vakken"])

    return df


def can_fit(item_dims, vak_dims):
    """
    Checkt of het item (L,W,H) in een vak past,
    waarbij je het item mag draaien (alle 6 permutaties).
    """
    item_L, item_B, item_H = item_dims
    vak_L, vak_B, vak_H = vak_dims

    for perm in set(itertools.permutations((item_L, item_B, item_H))):
        pL, pB, pH = perm
        if pL <= vak_L and pB <= vak_B and pH <= vak_H:
            return True
    return False


def main():
    st.title("Indelingen Tool – beste vakverdeling kiezen")

    st.markdown(
        """
Vul de **lengte, breedte en hoogte** in van het product (in mm).
De tool kiest de **beste indeling** uit de lijst:

- Het product moet in één vak passen (met draaien toegestaan).
- Van alle passende indelingen wordt degene met de **meeste vakken** gekozen.
        """
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        item_L = st.number_input("Lengte (mm)", min_value=0.0, step=1.0)
    with col2:
        item_B = st.number_input("Breedte (mm)", min_value=0.0, step=1.0)
    with col3:
        item_H = st.number_input("Hoogte (mm)", min_value=0.0, step=1.0)

    df = load_data()

    if st.button("Bereken beste indeling"):
        if item_L <= 0 or item_B <= 0 or item_H <= 0:
            st.warning("Vul alle afmetingen groter dan 0 in.")
            return

        item_dims = (item_L, item_B, item_H)

        # Filter alle indelingen waar het item in 1 vak past
        mask = df.apply(
            lambda row: can_fit(
                item_dims, (row["vak_L"], row["vak_B"], row["vak_H"])
            ),
            axis=1,
        )
        passende = df[mask].copy()

        if passende.empty:
            st.error("Er is geen indeling gevonden waarin dit product past.")
            return

        # Beste: meeste vakken, daarna kleinste vak (optionele tie-breaker)
        passende = passende.sort_values(
            by=["Aantal vakken", "vak_L", "vak_B", "vak_H"],
            ascending=[False, True, True, True],
        )
        beste = passende.iloc[0]

        st.subheader("Beste gevonden indeling")
        st.write(
            f"**Transport Type:** {beste['Transport Type']}\n\n"
            f"**Artikelnummer:** {beste['Artikelnummer']}\n\n"
            f"**Aantal vakken:** {int(beste['Aantal vakken'])}\n\n"
            f"**Indeling (L x B):** {beste['Indeling (L x B)']}\n\n"
            f"**Vak afmetingen (L x B x H):** {beste['Vak Afmetingen (L x B x Hoogte)']}"
        )

        with st.expander("Toon top 10 passende indelingen"):
            kolommen = [
                "Transport Type",
                "Artikelnummer",
                "Aantal vakken",
                "Indeling (L x B)",
                "Vak Afmetingen (L x B x Hoogte)",
            ]
            st.dataframe(passende[kolommen].head(10).reset_index(drop=True))


if __name__ == "__main__":
    main()
