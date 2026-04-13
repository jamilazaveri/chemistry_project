import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import AllChem
import py3Dmol
from stmol import showmol

# --- 1. SET UP THE PAGE ---
st.set_page_config(
    page_title="Chiral Spotlight", 
    page_icon="🧬",
    layout="centered"
)

# --- 2. CUSTOM CSS STYLING ---
st.markdown("""
<style>
    /* Dark Theme & Beautiful Gradients */
    .stApp {
        background-color: #0E1117;
    }
    
    .student-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #334155;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        margin-bottom: 2rem;
        color: #e2e8f0;
    }
    .student-card h2 {
        margin-top: 0;
        color: #38bdf8;
        font-family: monospace;
        letter-spacing: 1px;
    }
    .student-details {
        font-size: 1.15em;
        line-height: 1.6;
    }
    .highlight-span {
        color: #fbbf24;
        font-weight: bold;
    }
    
    /* Center images */
    .stImage, svg {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. STUDENT DETAILS BOX ---
st.markdown("""
<div class="student-card">
    <h2>👨‍🔬 Student Details</h2>
    <div class="student-details">
        <strong>Name:</strong> <span class="highlight-span">Jamila Mustaali Zaveri</span><br>
        <strong>Registration Number:</strong> <span class="highlight-span">RA2511026050033</span><br>
        <strong>Class/Sec:</strong> AIML-A<br>
        <strong>Year/Sem:</strong> I / II
    </div>
</div>
""", unsafe_allow_html=True)

# --- 4. APP HEADER & INPUT ---
st.title("🔬 Chiral Spotlight")
st.write("A professional tool for analyzing stereocenters and displaying detailed 2D/3D chemical properties of any molecule.")

smiles_input = st.text_input(
    "Enter SMILES string 👇", 
    value="CCOC(=O)[C@H]1[C@H](O)[C@@H](OC)[C@H](N)[C@H](OC(C)=O)C1",
)

analyze_btn = st.button("🚀 Analyze Molecule", use_container_width=True)

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
