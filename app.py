import itertools
import pandas as pd
import streamlit as st


# 1) Standaard indelingen "ingebakken" in de app
#    Hier zet je de vak-indelingen. Dit vervangt de Excel.
INITIAL_INDELINGEN = [
    {"Transport Type": "Blisters (Bak: 400x300)", "Artikelnummer": "105 030", "Aantal vakken": 24, "Indeling (L x B)": "6x4", "Vak Afmetingen (L x B x Hoogte)": "52 x 56 x 30"},
    {"Transport Type": "Blisters (Bak: 400x300)", "Artikelnummer": "106 022", "Aantal vakken": 16, "Indeling (L x B)": "4x4", "Vak Afmetingen (L x B x Hoogte)": "76 x 51 x 52"},
    {"Transport Type": "Blisters (Bak: 400x300)", "Artikelnummer": "106 021", "Aantal vakken": 8,  "Indeling (L x B)": "2x4", "Vak Afmetingen (L x B x Hoogte)": "163 x 51 x 52"},
    {"Transport Type": "Blisters (Bak: 400x300)", "Artikelnummer": "106 024", "Aantal vakken": 12, "Indeling (L x B)": "3x4", "Vak Afmetingen (L x B x Hoogte)": "105 x 51 x 52"},

    {"Transport Type": "Foam Inlays (Bak: 400x300)", "Artikelnummer": "106 020", "Aantal vakken": 6,  "Indeling (L x B)": "3x2", "Vak Afmetingen (L x B x Hoogte)": "105 x 113 x 52"},
    {"Transport Type": "Foam Inlays (Bak: 400x300)", "Artikelnummer": "106 023", "Aantal vakken": 4,  "Indeling (L x B)": "2x2", "Vak Afmetingen (L x B x Hoogte)": "113 x 63 x 52"},
    {"Transport Type": "Foam Inlays (Bak: 400x300)", "Artikelnummer": "106 026", "Aantal vakken": 32, "Indeling (L x B)": "4x8", "Vak Afmetingen (L x B x Hoogte)": "76 x 20 x 52"},
    {"Transport Type": "Foam Inlays (Bak: 400x300)", "Artikelnummer": "106 025", "Aantal vakken": 8,  "Indeling (L x B)": "4x2", "Vak Afmetingen (L x B x Hoogte)": "76 x 113 x 52"},

    {"Transport Type": "Foam Inlays (Bak: 400x300)", "Artikelnummer": "107 025", "Aantal vakken": 8,  "Indeling (L x B)": "4x2", "Vak Afmetingen (L x B x Hoogte)": "76 x 113 x 95"},
    {"Transport Type": "Foam Inlays (Bak: 400x300)", "Artikelnummer": "107 024", "Aantal vakken": 12, "Indeling (L x B)": "3x4", "Vak Afmetingen (L x B x Hoogte)": "105 x 51 x 95"},
    {"Transport Type": "Foam Inlays (Bak: 400x300)", "Artikelnummer": "107 023", "Aantal vakken": 4,  "Indeling (L x B)": "2x2", "Vak Afmetingen (L x B x Hoogte)": "113 x 63 x 95"},
    {"Transport Type": "Foam Inlays (Bak: 400x300)", "Artikelnummer": "107 022", "Aantal vakken": 16, "Indeling (L x B)": "4x4", "Vak Afmetingen (L x B x Hoogte)": "76 x 51 x 95"},
    {"Transport Type": "Foam Inlays (Bak: 400x300)", "Artikelnummer": "107 021", "Aantal vakken": 8,  "Indeling (L x B)": "2x4", "Vak Afmetingen (L x B x Hoogte)": "163 x 51 x 95"},
    {"Transport Type": "Foam Inlays (Bak: 400x300)", "Artikelnummer": "107 020", "Aantal vakken": 6,  "Indeling (L x B)": "3x2", "Vak Afmetingen (L x B x Hoogte)": "105 x 113 x 95"},
    {"Transport Type": "Foam Inlays (Bak: 400x300)", "Artikelnummer": "107 026", "Aantal vakken": 32, "Indeling (L x B)": "4x8", "Vak Afmetingen (L x B x Hoogte)": "76 x 20 x 95"},

    {"Transport Type": "Pallets (Halve Europallet)", "Artikelnummer": "108 029", "Aantal vakken": 4,  "Indeling (L x B)": "4x1", "Vak Afmetingen (L x B x Hoogte)": "120 x 730 x 190"},
    {"Transport Type": "Pallets (Europallet)",       "Artikelnummer": "108 029", "Aantal vakken": 7,  "Indeling (L x B)": "1x7", "Vak Afmetingen (L x B x Hoogte)": "120 x 730 x 190"},

    {"Transport Type": "Pallets (Halve Europallet)", "Artikelnummer": "108 027", "Aantal vakken": 12, "Indeling (L x B)": "3x4", "Vak Afmetingen (L x B x Hoogte)": "155 x 155 x 190"},
    {"Transport Type": "Pallets (Europallet)",       "Artikelnummer": "108 027", "Aantal vakken": 24, "Indeling (L x B)": "4x6", "Vak Afmetingen (L x B x Hoogte)": "155 x 155 x 190"},

    {"Transport Type": "Pallets (Halve Europallet)", "Artikelnummer": "108 026", "Aantal vakken": 6,  "Indeling (L x B)": "3x2", "Vak Afmetingen (L x B x Hoogte)": "155 x 360 x 190"},
    {"Transport Type": "Pallets (Europallet)",       "Artikelnummer": "108 026", "Aantal vakken": 12, "Indeling (L x B)": "2x6", "Vak Afmetingen (L x B x Hoogte)": "155 x 360 x 190"},

    {"Transport Type": "Pallets (Halve Europallet)", "Artikelnummer": "108 025", "Aantal vakken": 8,  "Indeling (L x B)": "2x4", "Vak Afmetingen (L x B x Hoogte)": "255 x 155 x 190"},
    {"Transport Type": "Pallets (Europallet)",       "Artikelnummer": "108 025", "Aantal vakken": 16, "Indeling (L x B)": "4x4", "Vak Afmetingen (L x B x Hoogte)": "255 x 155 x 190"},

    {"Transport Type": "Pallets (Halve Europallet)", "Artikelnummer": "108 024", "Aantal vakken": 4,  "Indeling (L x B)": "2x2", "Vak Afmetingen (L x B x Hoogte)": "255 x 360 x 190"},
    {"Transport Type": "Pallets (Europallet)",       "Artikelnummer": "108 024", "Aantal vakken": 8,  "Indeling (L x B)": "2x4", "Vak Afmetingen (L x B x Hoogte)": "255 x 360 x 190"},

    {"Transport Type": "Pallets (Halve Europallet)", "Artikelnummer": "108 023", "Aantal vakken": 2,  "Indeling (L x B)": "2x1", "Vak Afmetingen (L x B x Hoogte)": "255 x 730 x 190"},
    {"Transport Type": "Pallets (Europallet)",       "Artikelnummer": "108 023", "Aantal vakken": 4,  "Indeling (L x B)": "1x4", "Vak Afmetingen (L x B x Hoogte)": "255 x 730 x 190"},

    {"Transport Type": "Pallets (Halve Europallet)", "Artikelnummer": "108 022", "Aantal vakken": 4,  "Indeling (L x B)": "1x4", "Vak Afmetingen (L x B x Hoogte)": "525 x 155 x 190"},
    {"Transport Type": "Pallets (Europallet)",       "Artikelnummer": "108 022", "Aantal vakken": 8,  "Indeling (L x B)": "4x2", "Vak Afmetingen (L x B x Hoogte)": "525 x 155 x 190"},

    {"Transport Type": "Pallets (Halve Europallet)", "Artikelnummer": "108 021", "Aantal vakken": 2,  "Indeling (L x B)": "1x2", "Vak Afmetingen (L x B x Hoogte)": "525 x 360 x 190"},
    {"Transport Type": "Pallets (Europallet)",       "Artikelnummer": "108 021", "Aantal vakken": 4,  "Indeling (L x B)": "2x2", "Vak Afmetingen (L x B x Hoogte)": "525 x 360 x 190"},

    {"Transport Type": "Pallets (Halve Europallet)", "Artikelnummer": "108 020", "Aantal vakken": 1,  "Indeling (L x B)": "1x1", "Vak Afmetingen (L x B x Hoogte)": "525 x 730 x 190"},
    {"Transport Type": "Pallets (Europallet)",       "Artikelnummer": "108 020", "Aantal vakken": 2,  "Indeling (L x B)": "1x2", "Vak Afmetingen (L x B x Hoogte)": "525 x 730 x 190"},

    {"Transport Type": "Pallets (Halve Europallet)", "Artikelnummer": "108 031", "Aantal vakken": 16, "Indeling (L x B)": "4x4", "Vak Afmetingen (L x B x Hoogte)": "120 x 155 x 190"},
    {"Transport Type": "Pallets (Europallet)",       "Artikelnummer": "108 031", "Aantal vakken": 28, "Indeling (L x B)": "4x7", "Vak Afmetingen (L x B x Hoogte)": "120 x 155 x 190"},

    {"Transport Type": "Pallets (Halve Europallet)", "Artikelnummer": "108 030", "Aantal vakken": 8,  "Indeling (L x B)": "4x2", "Vak Afmetingen (L x B x Hoogte)": "120 x 360 x 190"},
    {"Transport Type": "Pallets (Europallet)",       "Artikelnummer": "108 030", "Aantal vakken": 14, "Indeling (L x B)": "2x7", "Vak Afmetingen (L x B x Hoogte)": "120 x 360 x 190"},
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
    Werkt ook bij '52x56x30' of extra spaties.
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
    Check of item (L,B,H) in een vak past, met draaien toegestaan.
    We proberen alle permutaties van (L,B,H).
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
De tool zoekt de **indeling waar het product in past** en die **de meeste vakken** heeft.
        """
    )

    # 1. Productafmetingen invoeren
    col1, col2, col3 = st.columns(3)
    with col1:
        item_L = st.number_input("Lengte (L)", min_value=0.0, step=1.0)
    with col2:
        item_B = st.number_input("Breedte (B)", min_value=0.0, step=1.0)
    with col3:
        item_H = st.number_input("Hoogte (H)", min_value=0.0, step=1.0)

    # 2. Dataframe in session_state houden
    if "indelingen_df" not in st.session_state:
        st.session_state["indelingen_df"] = get_initial_df()

    # 3. Editor om indelingen te beheren
    st.subheader("Indelingen beheren")

    with st.expander("Bewerk indelingen (aan/uit zetten, toevoegen, wijzigen)", expanded=False):
        st.write(
            "Je kunt hier rijen aanpassen, nieuwe toevoegen en via **Actief** bepalen of een indeling meegerekend wordt."
        )

        edited_df = st.data_editor(
            st.session_state["indelingen_df"],
            num_rows="dynamic",  # nieuwe rijen toegestaan
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

    # 4. Berekenen van beste indeling
    if st.button("Bereken beste indeling"):
        if item_L <= 0 or item_B <= 0 or item_H <= 0:
            st.warning("Vul alle drie de afmetingen groter dan 0 in.")
            return

        df = st.session_state["indelingen_df"].copy()

        # Alleen actieve rijen
        if "Actief" in df.columns:
            df = df[df["Actief"] == True]

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

        # Vak afmetingen parsen naar getallen
        dims = df["Vak Afmetingen (L x B x Hoogte)"].apply(parse_dims)
        df[["vak_L", "vak_B", "vak_H"]] = pd.DataFrame(dims.tolist(), index=df.index)
        df = df.dropna(subset=["vak_L", "vak_B", "vak_H"])

        if df.empty:
            st.error("Geen indelingen met leesbare vak afmetingen gevonden.")
            return

        item_dims = (item_L, item_B, item_H)

        # Filter op indelingen waar het item in 1 vak past
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

        # Sorteer: meeste vakken eerst, dan kleinste vak om te breken bij gelijkspel
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
