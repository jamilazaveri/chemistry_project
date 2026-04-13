import streamlit as st
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import AllChem
from rdkit.Chem import Descriptors
from rdkit.Chem import Lipinski
import py3Dmol
from stmol import showmol

# --- 1. SET UP THE PAGE ---
st.set_page_config(
    page_title="Stereochemical Analyzer", 
    page_icon="🖋️",
    layout="centered"
)

# --- 2. CUSTOM CSS STYLING (DARK ACADEMIA & CHALKBOARD BACKGROUND) ---
import base64
import os

def set_bg():
    # Try looking for bg.jpg or bg.png or bg.jpeg
    bg_file = None
    for ext in ['jpg', 'png', 'jpeg']:
        if os.path.exists(f"bg.{ext}"):
            bg_file = f"bg.{ext}"
            break
            
    if bg_file:
        with open(bg_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        ext = bg_file.split('.')[-1]
        
        st.markdown(f"""
        <style>
            .stApp {{
                background-image: url(data:image/{ext};base64,{encoded_string});
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            /* Safely target the main application box */
            [data-testid="block-container"],
            [data-testid="stAppViewBlockContainer"], 
            .main .block-container,
            .appview-container section > div:first-of-type {{
                background-color: rgba(15, 12, 11, 0.80) !important;
                border-radius: 20px;
                padding: 50px !important;
                border: 1px solid #cfab7a88;
                box-shadow: 0px 0px 50px rgba(0,0,0,0.95);
                margin-top: 30px;
                margin-bottom: 30px;
            }}
            /* Ensure text pops aggressively no matter what */
            p, h1, h2, h3, h4, span, label, div {{
                text-shadow: 0px 2px 4px rgba(0,0,0,0.9);
            }}
        </style>
        """, unsafe_allow_html=True)
    else:
        # Fallback dark background
        st.markdown("""
        <style>
            .stApp {{
                background-color: #12100e;
                background-image: radial-gradient(circle at center, #1b1714 0%, #0a0807 100%);
            }}
        </style>
        """, unsafe_allow_html=True)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap');
    
    .stApp {
        color: #d4c8b2;
        font-family: 'EB Garamond', serif;
        font-size: 18px;
    }
    
    h1, h2, h3 {
        font-family: 'Cinzel', serif !important;
        color: #cfab7a !important;
        letter-spacing: 1.5px;
    }
    
    h1 {
        border-bottom: 1px solid #cfab7a33;
        padding-bottom: 10px;
        margin-bottom: 25px;
        text-align: center;
    }

    /* Elegant Student Card */
    .student-card {
        background: rgba(20, 17, 15, 0.95);
        border: 1px solid #cfab7a66;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8);
        color: #d4c8b2;
        margin-bottom: 30px;
    }
    .student-card h2 {
        margin-top: 0;
        text-align: center;
        border-bottom: none;
        font-size: 1.5em;
    }
    .student-details {
        font-size: 1.1em;
        line-height: 1.8;
        text-align: center;
    }
    .highlight-span {
        color: #e5c99f;
        font-style: italic;
    }
    
    /* Elegant Button */
    .stButton>button {
        background: rgba(20, 17, 15, 0.8);
        color: #cfab7a;
        font-family: 'Cinzel', serif;
        font-size: 1.1em;
        border: 1px solid #cfab7a;
        border-radius: 0px;
        padding: 10px 20px;
        transition: all 0.4s ease;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .stButton>button:hover {
        background: #cfab7a;
        color: #12100e;
        border-color: #cfab7a;
        box-shadow: 0 0 15px rgba(207, 171, 122, 0.4);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        border-radius: 0px;
        border: 1px solid #5a4b3c;
        background-color: #1a1714;
        padding: 12px;
        color: #e5c99f;
        font-family: 'EB Garamond', serif;
    }
    .stTextInput>div>div>input:focus {
        border-color: #cfab7a;
        box-shadow: 0 0 8px rgba(207, 171, 122, 0.3);
    }
    
    /* Table styles */
    tbody tr:nth-child(odd) {
        background-color: #181512;
    }
    tbody tr:nth-child(even) {
        background-color: #1e1a17;
    }
    tbody tr:hover {
        background-color: #2a241f;
    }
    th {
        background-color: #1b1714 !important;
        color: #cfab7a !important;
        font-family: 'Cinzel', serif;
        text-transform: uppercase;
        border-bottom: 2px solid #5a4b3c !important;
    }
    td {
        color: #d4c8b2;
        font-family: 'EB Garamond', serif;
    }
    
    /* Minimalist Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        border-bottom: 1px solid #5a4b3c;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 0px;
        padding: 10px 20px;
        background-color: transparent;
        border: none;
        color: #8c7b64;
        font-family: 'Cinzel', serif;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #cfab7a !important;
        border-bottom: 2px solid #cfab7a;
    }
    
    /* SVG ancient parchment styling */
    .svg-container {
        border: 2px solid #8c7b64;
        padding: 10px;
        background: radial-gradient(circle, #f3e9d2 0%, #d8c29e 100%); 
        border-radius: 8px;
        box-shadow: inset 0 0 30px rgba(90, 75, 60, 0.5), 0 5px 20px rgba(0,0,0,1.0);
    }
    
    /* Disable balloons or sparkles */
    
</style>
""", unsafe_allow_html=True)

# Load the background if it exists
set_bg()

# --- 3. STUDENT DETAILS BOX ---
st.markdown("""
<div class="student-card">
    <h2>Academic Project Portfolio</h2>
    <div class="student-details">
        <strong>Scholar:</strong> <span class="highlight-span">Jamila Mustaali Zaveri</span><br>
        <strong>Registration Number:</strong> <span class="highlight-span">RA2511026050033</span><br>
        <strong>Division:</strong> <span class="highlight-span">AIML-A</span> &nbsp;|&nbsp; <strong>Term:</strong> <span class="highlight-span">I / II</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4. APP HEADER & INPUT ---
st.title("Stereochemical Analyzer")
st.markdown("<p style='text-align: center; color: #8c7b64; font-size: 1.1em; margin-bottom: 30px;'>An analytical instrument to deduce structural chirality and R/S configurations via the PubChem archive.</p>", unsafe_allow_html=True)

# Selection for input type
search_type = st.radio("Query Paradigm Selection", ["Query by Chemical Nomenclature (PubChem)", "Query by SMILES String"])

# Examples
example_mols = {
    "Sitagliptin": "FC(F)(F)C1=CC(N2C(=O)C[C@H](N)CC2=O)=NN1CC1=C(F)C=C(F)C=C1F",
    "Oseltamivir": "CCOC(=O)[C@H]1[C@H](O)[C@@H](OC)[C@H](N)[C@H](OC(C)=O)C1",
    "Aspirin": "CC(=O)Oc1ccccc1C(=O)O",
    "Ibuprofen": "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
    "Penicillin G": "CC1([C@@H](N2[C@H](S1)[C@@H](C2=O)NC(=O)Cc3ccccc3)C(=O)O)C"
}
selected_example = st.selectbox("Bibliographic Examples (Quick Select)", ["Custom Query"] + list(example_mols.keys()))

default_val = ""
if selected_example != "Custom Query":
    if search_type == "Query by Chemical Nomenclature (PubChem)":
        default_val = selected_example
    else:
        default_val = example_mols[selected_example]

if search_type == "Query by Chemical Nomenclature (PubChem)":
    query_input = st.text_input("Enter Standard IUPAC or Common Name:", value=default_val or "Aspirin")
else:
    query_input = st.text_input("Enter SMILES Notation:", value=default_val or "FC(F)(F)C1=CC(N2C(=O)C[C@H](N)CC2=O)=NN1CC1=C(F)C=C(F)C=C1F")

analyze_btn = st.button("Commence Analysis", use_container_width=True)

# --- 5. INITIALIZE SESSION STATE ---
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# --- 6. MAIN LOGIC TRIGGER ---
if analyze_btn:
    if not query_input.strip():
        st.error("Please provide a valid query.")
    else:
        with st.spinner("Consulting archives and synthesizing structural models..."):
            
            smiles_string = query_input.strip()
            compound_name = "Custom Molecule"
            
            # PubChem Search API integration
            if search_type == "Query by Chemical Nomenclature (PubChem)":
                try:
                    compounds = pcp.get_compounds(query_input.strip(), 'name')
                    if compounds:
                        smiles_string = compounds[0].isomeric_smiles
                        compound_name = compounds[0].iupac_name or query_input.strip()
                        
                        # Fetch Layman Description
                        try:
                            import requests
                            cid = compounds[0].cid
                            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON?heading=Description"
                            resp = requests.get(url).json()
                            description = resp['Record']['Section'][0]['Information'][0]['Value']['StringWithMarkup'][0]['String']
                        except:
                            description = "Informality on this specific compound is restricted within the primary archives, though its structural properties remain analytically valid."
                    else:
                        st.error("Compound not found within the PubChem archive.")
                        smiles_string = None
                except Exception as e:
                    st.error("Failure accessing the PubChem Archive.")
                    smiles_string = None
            else:
                description = "Custom SMILES structures are synthesized manually; clinical biographies are only available for recognized nomenclature queries."

            if smiles_string:
                mol = Chem.MolFromSmiles(smiles_string)
                if mol:
                    # Deep Analysis
                    mol_with_h = Chem.AddHs(mol)
                    Chem.AssignStereochemistry(mol_with_h, force=True, cleanIt=True)
                    chiral_centers = Chem.FindMolChiralCenters(mol_with_h, includeUnassigned=True)
                    num_chiral = len(chiral_centers)
                    
                    R_count = S_count = unknown = 0
                    results_data = []
                    chiral_indices_h = []
                    for idx, config in chiral_centers:
                        atom = mol_with_h.GetAtomWithIdx(idx)
                        chiral_indices_h.append(idx)
                        if config == 'R': R_count += 1
                        elif config == 'S': S_count += 1
                        else: unknown += 1
                        results_data.append({"Atom Index": idx, "Symbol": atom.GetSymbol(), "Configuration": config})
                    
                    achiral_sp3 = 0
                    for atom in mol_with_h.GetAtoms():
                        if atom.GetAtomicNum() == 6 and atom.GetHybridization() == Chem.HybridizationType.SP3:
                            if atom.GetIdx() not in chiral_indices_h: achiral_sp3 += 1

                    # Descriptors
                    mol_wt = Descriptors.MolWt(mol)
                    exact_mass = Descriptors.ExactMolWt(mol)
                    formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
                    logp = Descriptors.MolLogP(mol)
                    tpsa = Descriptors.TPSA(mol)
                    hbd = Lipinski.NumHDonors(mol)
                    hba = Lipinski.NumHAcceptors(mol)
                    rot_bonds = Lipinski.NumRotatableBonds(mol)
                    
                    # Advanced Science Properties
                    formal_charge = Chem.GetFormalCharge(mol)
                    # For a neutral drug molecule, multiplicity is usually 1 (singlet)
                    # calculated as 2S + 1 where S is the total spin
                    multiplicity = 1 
                    molar_refractivity = Descriptors.MolMR(mol)
                    lip_viol = sum([mol_wt > 500, logp > 5, hbd > 5, hba > 10])

                    # Store in Session State
                    st.session_state.analysis_results = {
                        "smiles": smiles_string,
                        "name": compound_name,
                        "description": description,
                        "num_chiral": num_chiral,
                        "R": R_count, "S": S_count, "U": unknown,
                        "achiral_sp3": achiral_sp3,
                        "results_data": results_data,
                        "mol_wt": mol_wt, "exact_mass": exact_mass, "formula": formula,
                        "logp": logp, "tpsa": tpsa, "hbd": hbd, "hba": hba, "rot": rot_bonds,
                        "formal_charge": formal_charge,
                        "multiplicity": multiplicity,
                        "molar_refractivity": molar_refractivity,
                        "lip_viol": lip_viol
                    }
                    st.success("✅ Analysis Synthesized.")

# --- 7. DISPLAY RESULTS (Persistent) ---
if st.session_state.analysis_results:
    res = st.session_state.analysis_results
    
    st.markdown("<br>", unsafe_allow_html=True)
    tab_bio, tab1, tab_desc, tab2, tab3 = st.tabs(["Molecular Biography", "Analytical Parameters", "Molecular Descriptors", "2D Highlighting", "3D Projection"])
    
    with tab_bio:
        st.markdown(f"### Historical & Clinical Summary")
        st.write(res['description'])
        st.markdown("---")
        st.info("⚡ *Biography data is fetched dynamically from clinical archives via PubChem REST API.*")

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Results")
            st.markdown(f"**Total Chiral Centers:** {res['num_chiral']}")
            st.markdown(f"**R Configuration:** {res['R']}")
            st.markdown(f"**S Configuration:** {res['S']}")
            st.markdown(f"**Unassigned:** {res['U']}")
            st.markdown(f"**Achiral (sp3) Carbons:** {res['achiral_sp3']}")
        with c2:
            st.markdown("### Chiral Centers Details")
            if res['results_data']: st.table(res['results_data'])
            else: st.write("No structural chirality recognized.")

    with tab_desc:
        st.markdown("### Molecular Descriptive Data")
        st.markdown(f"**Formula:** `{res['formula']}` &nbsp;|&nbsp; **Exact Mass:** `{res['exact_mass']:.4f} Da`")
        col1, col2, col3 = st.columns(3)
        col1.metric("Molecular Weight", f"{res['mol_wt']:.2f} Da")
        col2.metric("LogP", f"{res['logp']:.2f}")
        col3.metric("TPSA", f"{res['tpsa']:.2f} Å²")

        col4, col5, col6 = st.columns(3)
        col4.metric("H-Bond Donors", res['hbd'])
        col5.metric("H-Bond Acceptors", res['hba'])
        col6.metric("Rotatable Bonds", res['rot'])

        col7, col8, col9 = st.columns(3)
        col7.metric("Formal Charge", res['formal_charge'])
        col8.metric("Spin Multiplicity", res['multiplicity'])
        col9.metric("Molar Refractivity", f"{res['molar_refractivity']:.2f}")
        
        st.markdown("---")
        st.markdown("### Lipinski's Rule of Five")
        if res['lip_viol'] == 0: st.success("✅ Adheres to Rule of Five.")
        else: st.warning(f"⚠️ {res['lip_viol']} Violations.")

    with tab2:
        mol = Chem.MolFromSmiles(res['smiles'])
        Chem.AssignStereochemistry(mol, force=True, cleanIt=True)
        chiral_centers_orig = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
        highlight_atoms = [idx for idx, _ in chiral_centers_orig]
        drawer = rdMolDraw2D.MolDraw2DSVG(600, 450)
        opts = drawer.drawOptions()
        opts.clearBackground = False
        # Use a simpler highlight color setting if available
        try:
            opts.highlightColour = rdMolDraw2D.DrawColour(0.65, 0.15, 0.15)
        except:
            pass
        drawer.DrawMolecule(mol, highlightAtoms=highlight_atoms)
        drawer.FinishDrawing()
        st.markdown(f'<div class="svg-container" style="text-align: center;">{drawer.GetDrawingText()}</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("### Interactive 3D Model")
        model_style = st.selectbox("Orbital Representation", ["Stick", "Sphere", "Line", "Cross"], index=0)
        
        # Prepare Molecule
        source_mol = Chem.MolFromSmiles(res['smiles'])
        if source_mol:
            mol_h = Chem.AddHs(source_mol)
            # Try 3D Embedding with multiple attempts
            with st.spinner("Calculating 3D Atomic Coordinates..."):
                params = AllChem.ETKDGv3()
                params.randomSeed = 42
                status = AllChem.EmbedMolecule(mol_h, params)
                if status == -1:
                    # Fallback attempt
                    status = AllChem.EmbedMolecule(mol_h, randomSeed=42)
            
            if status != -1:
                AllChem.MMFFOptimizeMolecule(mol_h)
                mb = Chem.MolToMolBlock(mol_h)
                
                view = py3Dmol.view(width=700, height=500)
                view.addModel(mb, 'sdf')
                
                styles = {"Stick": {'stick': {}}, "Sphere": {'sphere': {}}, "Line": {'line': {}}, "Cross": {'cross': {}}}
                view.setStyle(styles.get(model_style))
                
                # Stark background for the viewer to ensure it's seen
                view.setBackgroundColor('#1a1714')
                
                if st.checkbox("Enable 360° Structural Rotation", key="rotate_3d"):
                    view.spin(True)
                else:
                    view.spin(False)
                
                view.zoomTo()
                showmol(view, height=500, width=700)
            else:
                st.warning("⚠️ Critical: The structural complexity of this molecule prevents stable 3D coordinate synthesis.")
        else:
            st.error("Failed to parse molecule for 3D Projection.")

    # Methodology Expander
    with st.expander("📚 Methodology & Cahn-Ingold-Prelog (CIP) Rules"):
        st.markdown("""
        This analytical instrument utilizes the **RDKit** chemoinformatics engine to evaluate stereochemical configurations.
        
        **Stereochemistry Logic:**
        1.  **Prioritization:** Atoms surrounding a chiral center are ranked by atomic number (CIP sequence rules).
        2.  **Projection:** The molecule is oriented such that the lowest priority group points away from the observer.
        3.  **Classification:**
            -   **Rectus (R):** Clockwise sequence (High → Low priority).
            -   **Sinister (S):** Counter-clockwise sequence.
            
        **Lipinski Screening:** Evaluates the 'Drug-likeness' of the spatial complex based on Molecular Weight, Hydrophobicity (LogP), and Hydrogen Bonding capacity.
        """)

    # Download Report
    report = f"REPORT: {res['name']}\nSMILES: {res['smiles']}\nFormula: {res['formula']}\nChiral Centers: {res['num_chiral']}"
    st.download_button("📜 Download Analytical Report", report, f"{res['name']}_analysis.txt", use_container_width=True)

