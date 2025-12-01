import itertools
import json

import pandas as pd
import streamlit as st


# 1) Standaard indelingen "ingebakken" in de app
#    Voeg hier zo veel rijen toe als je wilt.
INITIAL_INDELINGEN = [
    {
        "Transport Type": "Blisters (Bak: 400x300)",
        "Artikelnummer": "105 030",
        "Aantal vakken": 24,
        "Indeling (L x B)": "6x4",
        "Vak Afmetingen (L x B x Hoogte)": "52 x 56 x 30",
    },
    {
        "Transport Type": "Blisters (Bak: 400x300)",
        "Artikelnummer": "106 022",
        "Aantal vakken": 16,
        "Indeling (L x B)": "4x4",
        "Vak Afmetingen (L x B x Hoogte)": "76 x 51 x 52",
    },
    {
        "Transport Type": "Blisters (Bak: 400x300)",
        "Artikelnummer": "106 021",
        "Aantal vakken": 8,
        "Indeling (L x B)": "2x4",
        "Vak Afmetingen (L x B x Hoogte)": "163 x 51 x 52",
    },
    # Voeg hier de rest van je indelingen toe in exact dezelfde structuur
]


def get_initial_df() -> pd.DataFrame:
    """Zet de standaardlijst om naar een DataFrame en voeg een Actief kolom toe."""
    df = pd.DataFrame(INITIAL_INDELINGEN)
    if "Actief" not in df.columns:
        df["Actief"] = True
    return df


def parse_dims(dim_str):
    """
    '52 x 56 x 30' -> (52.0, 56.0, 30.0)
    Staat ook tolerant tegenover '52x56x30' of extra spaties.
    """
    if pd.isna(dim_str):
        return None, None, None

    s = str(dim_str).lower().replace(" ", "")
    parts = s.split("x")
    if len(parts) != 3:
        return None, None, None

    try:
        l = float(parts[0])
        b = float(parts[1])
        h = float(parts[2])
        return l, b, h
    except ValueError:
        return None, None, None


def can_fit(item_dims, vak_dims) -> bool:
    """
    Check of item (L,B,H) in een vak past, met draaien toegestaan
    (alle 6 permutaties van L,B,H worden geprobeerd).
    """
    item_L, item_B, item_H = item_dims
    vak_L, vak_B, vak_H = vak_dims

    for perm in set(itertools.permutations((item_L, item_B, item_H))):
        pL, pB, pH = perm
        if pL <= vak_L and pB <= vak_B and pH <= vak_H:
            return True
    return False


def main():
    st.title("Indelingen Tool - beste vakverdeling kiezen")

    st.markdown(
        """
Vul de **lengte, breedte en hoogte** van je product in (bijvoorbeeld in mm).  
De tool zoekt dan de **indeling waar het product in past** en die **de meeste vakken** heeft.
        """
    )

    # 2) Inputs voor het product
    col1, col2, col3 = st.columns(3)
    with col1:
        item_L = st.number_input("Lengte (L)", min_value=0.0, step=1.0)
    with col2:
        item_B = st.number_input("Breedte (B)", min_value=0.0, step=1.0)
    with col3:
        item_H = st.number_input("Hoogte (H)", min_value=0.0, step=1.0)

    # 3) Dataframe in session_state houden zodat edits blijven staan
    if "indelingen_df" not in st.session_state:
        st.session_state["indelingen_df"] = get_initial_df()

    # 4) Editor om indelingen te beheren
    st.subheader("Indelingen beheren")

    with st.expander("Bewerk indelingen (aan/uit zetten, toevoegen, wijzigen)", expanded=False):
        st.write(
            "Je kunt hier rijen aanpassen, nieuwe toevoegen en via **Actief** bepalen of een indeling meegerekend wordt."
        )

        edited_df = st.data_editor(
            st.session_state["indelingen_df"],
            num_rows="dynamic",  # nieuwe rijen kunnen toegevoegd worden
            use_container_width=True,
            column_config={
                "Actief": st.column_config.CheckboxColumn("Actief", default=True),
                "Aantal vakken": st.column_config.NumberColumn(
                    "Aantal vakken", min_value=1, step=1
                ),
            },
            key="indelingen_editor",
        )
        st.session_state["indelingen_df"] = edited_df

        if st.button("Reset naar standaard indelingen"):
            st.session_state["indelingen_df"] = get_initial_df()
            st.experimental_rerun()

    # 5) Berekenen van beste indeling
    if st.button("Bereken beste indeling"):
        if item_L <= 0 or item_B <= 0 or item_H <= 0:
            st.warning("Vul alle drie de afmetingen groter dan 0 in.")
            return

        df = st.session_state["indelingen_df"].copy()

        # Alleen actieve rijen gebruiken
        if "Actief" in df.columns:
            df = df[df["Actief"] == True]

        # Rijen zonder benodigde info eruit
        required_cols = [
            "Vak Afmetingen (L x B x Hoogte)",
            "Aantal vakken",
            "Artikelnummer",
            "Indeling (L x B)",
        ]
        df = df.dropna(subset=[c for c in required_cols if c in df.columns])

        if df.empty:
            st.error("Er zijn geen actieve indelingen met geldige data.")
            return

        # Vak afmetingen parsen
        dims = df["Vak Afmetingen (L x B x Hoogte)"].apply(parse_dims)
        df[["vak_L", "vak_B", "vak_H"]] = pd.DataFrame(dims.tolist(), index=df.index)
        df = df.dropna(subset=["vak_L", "vak_B", "vak_H"])

        if df.empty:
            st.error("Geen indelingen met leesbare vak afmetingen gevonden.")
            return

        item_dims = (item_L, item_B, item_H)

        # Filter alleen indelingen waarin het product in 1 vak past
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

        # Sorteer: meeste vakken eerst, daarna kleinste vakafmetingen als tie-breaker
        passende = passende.sort_values(
            by=["Aantal vakken", "vak_L", "vak_B", "vak_H"],
            ascending=[False, True, True, True],
        )

        beste = passende.iloc[0]

        st.subheader("Beste gevonden indeling")
        st.write(f"**Transport Type:** {beste.get('Transport Type', '')}")
        st.write(f"**Artikelnummer:** {beste.get('Artikelnummer', '')}")
        st.write(f"**Aantal vakken:** {int(beste['Aantal vakken'])}")
        st.write(f"**Indeling (L x B):** {beste.get('Indeling (L x B)', '')}")
        st.write(
            f"**Vak afmetingen (L x B x H):** "
            f"{beste.get('Vak Afmetingen (L x B x Hoogte)', '')}"
        )

        with st.expander("Toon top 10 passende indelingen"):
            kolommen = [
                "Transport Type",
                "Artikelnummer",
                "Aantal vakken",
                "Indeling (L x B)",
                "Vak Afmetingen (L x B x Hoogte)",
                "Actief",
            ]
            kolommen = [c for c in kolommen if c in passende.columns]
            st.dataframe(passende[kolommen].head(10).reset_index(drop=True))


if __name__ == "__main__":
    main()
