import streamlit as st
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import AllChem
import py3Dmol
from stmol import showmol

# --- 1. SET UP THE PAGE ---
st.set_page_config(
    page_title="Stereochemical Analyzer", 
    page_icon="🖋️",
    layout="centered"
)

# --- 2. CUSTOM CSS STYLING (DARK ACADEMIA) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap');
    
    /* Dark Academia Background */
    .stApp {
        background-color: #12100e;
        background-image: radial-gradient(circle at center, #1b1714 0%, #0a0807 100%);
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
    
    /* SVG border */
    .svg-container {
        border: 1px solid #cfab7a33;
        padding: 15px;
        background-color: #faf7f0; 
        border-radius: 2px;
    }
    
    /* Disable balloons or sparkles */
    
</style>
""", unsafe_allow_html=True)

# --- 3. STUDENT DETAILS BOX ---
st.markdown("""
<div class="student-card">
    <h2>Academic Project Portfolio</h2>
    <div class="student-details">
        <strong>Scholar:</strong> <span class="highlight-span">Jamila Mustaali Zaveri</span><br>
        <strong>Registration Protocol:</strong> <span class="highlight-span">RA2511026050033</span><br>
        <strong>Division:</strong> <span class="highlight-span">AIML-A</span> &nbsp;|&nbsp; <strong>Term:</strong> <span class="highlight-span">I / II</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4. APP HEADER & INPUT ---
st.title("Stereochemical Analyzer")
st.markdown("<p style='text-align: center; color: #8c7b64; font-size: 1.1em; margin-bottom: 30px;'>An analytical instrument to deduce structural chirality and R/S configurations via the PubChem archive.</p>", unsafe_allow_html=True)

# Selection for input type
search_type = st.radio("Query Paradigm Selection", ["Query by Chemical Nomenclature (PubChem)", "Query by SMILES String"])

if search_type == "Query by Chemical Nomenclature (PubChem)":
    query_input = st.text_input("Enter Standard IUPAC or Common Name:", value="Aspirin")
else:
    query_input = st.text_input("Enter SMILES Notation:", value="FC(F)(F)C1=CC(N2C(=O)C[C@H](N)CC2=O)=NN1CC1=C(F)C=C(F)C=C1F")

analyze_btn = st.button("Commence Analysis", use_container_width=True)

# --- 5. MAIN LOGIC ---
if analyze_btn:
    if not query_input.strip():
        st.error("Please provide a valid query.")
    else:
        with st.spinner("Consulting archives and synthesizing structural models..."):
            
            smiles_string = query_input.strip()
            compound_name = "Custom SMILES"
            
            # PubChem Search API integration
            if search_type == "Query by Chemical Nomenclature (PubChem)":
                try:
                    compounds = pcp.get_compounds(query_input.strip(), 'name')
                    if compounds:
                        # Grab the first match smiles
                        smiles_string = compounds[0].isomeric_smiles
                        compound_name = compounds[0].iupac_name or query_input.strip()
                        st.info(f"Successfully retrieved from PubChem Archive: **{compound_name.title()}** | Canonical SMILES: `{smiles_string}`")
                    else:
                        st.error("Compound not found within the PubChem archive. Please verify the nomenclature.")
                        smiles_string = None
                except Exception as e:
                    st.error("Failure accessing the PubChem Archive. Please ensure the term is a valid chemical or internet connection is active.")
                    smiles_string = None

            if smiles_string:
                mol = Chem.MolFromSmiles(smiles_string)
                
                if mol is None:
                    st.error("Synthesis Failed: The generated or provided SMILES string is invalid.")
                else:
                    mol_with_h = Chem.AddHs(mol)
                    Chem.AssignStereochemistry(mol_with_h, force=True, cleanIt=True)
                    
                    # Analyze chirality
                    chiral_centers = Chem.FindMolChiralCenters(mol_with_h, includeUnassigned=True)
                    num_chiral = len(chiral_centers)
                    R_count = S_count = unknown = 0
                    chiral_indices_h = []
                    results_data = []

                    for idx, config in chiral_centers:
                        atom = mol_with_h.GetAtomWithIdx(idx)
                        chiral_indices_h.append(idx)
                        symbol = atom.GetSymbol()
                        
                        if config == 'R': R_count += 1
                        elif config == 'S': S_count += 1
                        else: unknown += 1
                            
                        results_data.append({
                            "Atom Index": idx, 
                            "Atomic Species": symbol, 
                            "Configuration": config
                        })
                    
                    achiral_sp3 = 0
                    for atom in mol_with_h.GetAtoms():
                        if atom.GetAtomicNum() == 6 and atom.GetHybridization() == Chem.HybridizationType.SP3:
                            if atom.GetIdx() not in chiral_indices_h:
                                achiral_sp3 += 1

                    # --- 6. DISPLAY TABS ---
                    st.markdown("<br>", unsafe_allow_html=True)
                    tab1, tab2, tab3 = st.tabs(["Analytical Parameters", "2D Highlighting", "3D Projection"])
                    
                    with tab1:
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("### Structural Overview")
                            st.markdown(f"**Total Chiral Centers:** {num_chiral}")
                            st.markdown(f"**Rectus (R) Domains:** {R_count}")
                            st.markdown(f"**Sinister (S) Domains:** {S_count}")
                            st.markdown(f"**Indeterminate Arrays:** {unknown}")
                            st.markdown(f"**Achiral (sp³ hybridized) Carbons:** {achiral_sp3}")

                        with c2:
                            st.markdown("### Stereocenter Details")
                            if results_data:
                                st.table(results_data)
                            else:
                                st.write("Absence of structural chirality recognized within this framework.")
                                
                    with tab2:
                        Chem.AssignStereochemistry(mol, force=True, cleanIt=True)
                        chiral_centers_orig = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
                        highlight_atoms = [idx for idx, _ in chiral_centers_orig]
                        
                        try:
                            drawer = rdMolDraw2D.MolDraw2DSVG(600, 450)
                            opts = drawer.drawOptions()
                            # Pure white background for stark contrast so molecules remain clear
                            opts.clearBackground = True
                            # Gold highlights for dark academia feel
                            opts.highlightDefaultRenderer = rdMolDraw2D.DrawColour(0.81, 0.67, 0.48)
                            
                            drawer.DrawMolecule(mol, highlightAtoms=highlight_atoms)
                            drawer.FinishDrawing()
                            svg = drawer.GetDrawingText()
                            
                            st.markdown(f'<div class="svg-container" style="text-align: center;">{svg}</div>', unsafe_allow_html=True)
                        except Exception as e:
                            img = Draw.MolToImage(mol, highlightAtoms=highlight_atoms, size=(600, 450))
                            st.image(img, use_container_width=True)

                    with tab3:
                        try:
                            params = AllChem.ETKDGv3()
                            params.randomSeed = 42
                            res = AllChem.EmbedMolecule(mol_with_h, params)
                            if res == -1:
                                st.warning("3D coordinate synthesis unresolvable for this spatial complex.")
                            else:
                                AllChem.MMFFOptimizeMolecule(mol_with_h)
                                mb = Chem.MolToMolBlock(mol_with_h)
                                
                                view = py3Dmol.view(width=700, height=500)
                                view.addModel(mb, 'sdf')
                                view.setStyle({'stick': {}})
                                view.setBackgroundColor('#12100e')
                                view.zoomTo()
                                
                                showmol(view, height=500, width=700)
                                st.caption("Instruct: Scroll to magnify; Select and drag to alter structural rotation.")
                        except Exception as e:
                            st.error(f"Visual projection failure: {e}")
