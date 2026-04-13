import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import AllChem
import py3Dmol
from stmol import showmol

# --- 1. SET UP THE PAGE ---
st.set_page_config(
    page_title="Virtual Chemistry Lab", 
    page_icon="☕",
    layout="centered"
)

# --- 2. CUSTOM CSS STYLING (COZY CHEMISTRY VIBES) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&family=Playfair+Display:ital,wght@0,600;1,600&display=swap');
    
    /* Cozy Coffee/Chemistry Background */
    .stApp {
        background: linear-gradient(135deg, #fdfbf7 0%, #f4eade 100%);
        color: #3e3328;
        font-family: 'Nunito', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #8b5e34 !important;
    }

    /* Floating Animation for Student Card */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); box-shadow: 0 15px 30px -5px rgba(139, 94, 52, 0.3); }
        100% { transform: translateY(0px); }
    }
    
    .student-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 20px;
        border: 2px solid #ebdeb3;
        box-shadow: 0 10px 25px -5px rgba(139, 94, 52, 0.15);
        margin-bottom: 2rem;
        color: #5c4731;
        animation: float 6s ease-in-out infinite;
    }
    .student-card h2 {
        margin-top: 0;
        color: #8b5e34 !important;
        letter-spacing: 0.5px;
        text-align: center;
    }
    .student-details {
        font-size: 1.15em;
        line-height: 1.6;
        text-align: center;
    }
    .highlight-span {
        color: #d18134;
        font-weight: 800;
        background: rgba(209, 129, 52, 0.15);
        padding: 2px 10px;
        border-radius: 12px;
    }
    
    /* Shiny Animated Button */
    @keyframes pulse-mocha {
      0% { box-shadow: 0 0 0 0 rgba(139, 94, 52, 0.6); }
      70% { box-shadow: 0 0 0 15px rgba(139, 94, 52, 0); }
      100% { box-shadow: 0 0 0 0 rgba(139, 94, 52, 0); }
    }
    
    /* Enhance buttons to look cute & cozy */
    .stButton>button {
        background: linear-gradient(135deg, #a67c52 0%, #8b5e34 100%);
        color: #ffffff;
        font-weight: bold;
        font-size: 1.1em;
        border-radius: 16px;
        border: none;
        padding: 10px;
        transition: all 0.3s ease;
        animation: pulse-mocha 2.5s infinite;
    }
    .stButton>button:hover {
        transform: scale(1.03) translateY(-2px);
        background: linear-gradient(135deg, #b88d61 0%, #a67c52 100%);
        color: white;
        animation: none;
        box-shadow: 0 8px 20px rgba(139, 94, 52, 0.4);
    }
    
    /* Soft inputs */
    .stTextInput>div>div>input {
        border-radius: 12px;
        border: 2px solid #ebdeb3;
        background-color: white;
        padding: 12px;
        color: #3e3328;
        font-family: monospace;
        letter-spacing: 0.5px;
    }
    .stTextInput>div>div>input:focus {
        border-color: #d18134;
        box-shadow: 0 0 12px rgba(209, 129, 52, 0.2);
    }
    
    /* Custom tabs for cozy ui */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px 12px 0 0;
        padding: 12px 24px;
        background-color: rgba(235, 222, 179, 0.3);
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #8b5e34 !important;
        color: white !important;
    }
    
    /* Center images */
    .stImage, svg {
        display: block;
        margin-left: auto;
        margin-right: auto;
        transition: transform 0.5s ease;
    }
    svg:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. STUDENT DETAILS BOX ---
st.markdown("""
<div class="student-card">
    <h2>🧪 Student Project Outline 🤎</h2>
    <div class="student-details">
        <strong>Name:</strong> <span class="highlight-span">Jamila Mustaali Zaveri</span><br>
        <strong>Registration Number:</strong> <span class="highlight-span">RA2511026050033</span><br>
        <strong>Class/Sec:</strong> <span class="highlight-span">AIML-A</span> • <strong>Year/Sem:</strong> <span class="highlight-span">I / II</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4. APP HEADER & INPUT ---
st.title("☕ Virtual Chemistry Lab")
st.markdown("##### *A cozy, interactive aesthetic analyzer for molecules & stereocenters.*")
st.markdown("---")

smiles_input = st.text_input(
    "✨ Paste your SMILES string here:", 
    value="FC(F)(F)C1=CC(N2C(=O)C[C@H](N)CC2=O)=NN1CC1=C(F)C=C(F)C=C1F",
)

analyze_btn = st.button("🪄 Sparkle & Analyze!", use_container_width=True)

# --- 5. MAIN LOGIC ---
if analyze_btn:
    if not smiles_input.strip():
        st.error("Please enter a valid SMILES string.")
    else:
        with st.spinner("Analyzing processing chemical properties..."):
            
            mol = Chem.MolFromSmiles(smiles_input.strip())
            
            if mol is None:
                st.error("❌ Invalid SMILES input. Please check your spelling and try again.")
            else:
                # Add hydrogens for accurate stereochemical assignment
                mol_with_h = Chem.AddHs(mol)
                Chem.AssignStereochemistry(mol_with_h, force=True, cleanIt=True)
                
                # Setup metrics
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
                        "Element": symbol, 
                        "Configuration": config
                    })
                
                # Analyze Achiral (sp3) Carbons
                achiral_sp3 = 0
                for atom in mol_with_h.GetAtoms():
                    if atom.GetAtomicNum() == 6 and atom.GetHybridization() == Chem.HybridizationType.SP3:
                        if atom.GetIdx() not in chiral_indices_h:
                            achiral_sp3 += 1

                st.success("✅ Analysis Complete!")
                st.balloons()

                # --- 6. DISPLAY TABS ---
                tab1, tab2, tab3 = st.tabs(["📊 Results", "🎨 2D Highlighted", "🔮 3D View"])
                
                # Tab 1: Stats
                with tab1:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Summary Statistics")
                        st.markdown(f"- **Total Chiral Centers:** `{num_chiral}`")
                        st.markdown(f"- **R Configuration:** `{R_count}`")
                        st.markdown(f"- **S Configuration:** `{S_count}`")
                        st.markdown(f"- **Unassigned:** `{unknown}`")
                        st.markdown(f"- **Achiral (sp3) Carbons:** `{achiral_sp3}`")

                    with col2:
                        st.subheader("Detailed Breakdown")
                        if results_data:
                            st.table(results_data)
                        else:
                            st.info("No chiral centers found in this molecule.")
                            
                # Tab 2: Beautiful 2D Diagram
                with tab2:
                    st.subheader("2D Representation")
                    Chem.AssignStereochemistry(mol, force=True, cleanIt=True)
                    chiral_centers_orig = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
                    highlight_atoms = [idx for idx, _ in chiral_centers_orig]
                    
                    try:
                        drawer = rdMolDraw2D.MolDraw2DSVG(600, 400)
                        opts = drawer.drawOptions()
                        opts.clearBackground = False
                        opts.highlightDefaultRenderer = rdMolDraw2D.DrawColour(0.2, 0.8, 0.2) # Green highlights
                        
                        drawer.DrawMolecule(mol, highlightAtoms=highlight_atoms)
                        drawer.FinishDrawing()
                        svg = drawer.GetDrawingText()
                        
                        st.markdown(f'<div style="text-align: center; border-radius: 10px; background: white; padding: 10px;">{svg}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        img = Draw.MolToImage(mol, highlightAtoms=highlight_atoms, size=(600, 400))
                        st.image(img, use_container_width=True)

                # Tab 3: Interactive 3D Model
                with tab3:
                    st.subheader("Interactive 3D Model")
                    try:
                        params = AllChem.ETKDGv3()
                        params.randomSeed = 42
                        res = AllChem.EmbedMolecule(mol_with_h, params)
                        if res == -1:
                            st.warning("Could not calculate 3D coordinates for this specific molecule.")
                        else:
                            AllChem.MMFFOptimizeMolecule(mol_with_h)
                            mb = Chem.MolToMolBlock(mol_with_h)
                            
                            view = py3Dmol.view(width=700, height=500)
                            view.addModel(mb, 'sdf')
                            view.setStyle({'stick': {}})
                            view.setBackgroundColor('#0e1117')
                            view.zoomTo()
                            
                            showmol(view, height=500, width=700)
                            st.caption("Pro-tip: Scroll to zoom, click and drag to rotate.")
                            
                    except Exception as e:
                        st.error(f"Error generating 3D view: {e}")
