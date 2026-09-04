"""
Sequence comparison and protein-impact helpers (from genomics notebook).

@author: Preston Mackert
"""

# ------------------------------------------------------------------------------------- #
# libraries
# ------------------------------------------------------------------------------------- #

from __future__ import annotations
import re
from pathlib import Path
from typing import Any

# ------------------------------------------------------------------------------------- #
# set up data vectors that will be needed throughout the application
# ------------------------------------------------------------------------------------- #

# directory containing raw data files
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

CODON_TABLE = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}

REFERENCE_PRESETS = {
    # --- Oncology focus (8) ---
    "egfr_exon19": {
        "id": "egfr_exon19",
        "label": "EGFR",
        "file": "egfr_exon19_reference.fasta",
        "sample_file": "egfr_exon19_del_sample.fasta",
        "research_areas": ["oncology"],
        "context": "A small stretch of the EGFR gene (exon 19), the most frequent activating mutations in non-small cell lung cancer.",
    },
    "brca1": {
        "id": "brca1",
        "label": "BRCA1",
        "file": "brca1_snippet_reference.fasta",
        "sample_file": "brca1_snippet_frameshift.fasta",
        "research_areas": ["oncology"],
        "context": "A small stretch of BRCA1. Inherited mutations in this gene raise the risk of developing breast, ovarian, prostate, and pancreatic cancers.",
    },
    "btk_c481": {
        "id": "btk_c481",
        "label": "BTK",
        "file": "btk_c481_reference.fasta",
        "sample_file": "btk_c481s_sample.fasta",
        "research_areas": ["oncology"],
        "context": "A small stretch of BTK modeling the C481 site. In CLL, the C481S missense change is a common resistance mutation after covalent BTK inhibitors; non-covalent inhibitors such as pirtobrutinib can still bind.",
    },
    "kras_g12c": {
        "id": "kras_g12c",
        "label": "KRAS",
        "file": "kras_g12_reference.fasta",
        "sample_file": "kras_g12c_sample.fasta",
        "research_areas": ["oncology"],
        "context": "A small stretch of KRAS modeling codon 12. The G12C missense (Gly→Cys) was long considered “undruggable”; covalent G12C inhibitors are a recent precision-oncology breakthrough in NSCLC.",
    },
    "braf_v600e": {
        "id": "braf_v600e",
        "label": "BRAF",
        "file": "braf_v600_reference.fasta",
        "sample_file": "braf_v600e_sample.fasta",
        "research_areas": ["oncology"],
        "context": "A small stretch of BRAF modeling V600. The V600E missense (Val→Glu) activates MAPK signaling and is a classic biomarker for BRAF inhibitors in melanoma, colorectal cancer, and NSCLC.",
    },
    "esr1_y537s": {
        "id": "esr1_y537s",
        "label": "ESR1",
        "file": "esr1_y537_reference.fasta",
        "sample_file": "esr1_y537s_sample.fasta",
        "research_areas": ["oncology"],
        "context": "A small stretch of ESR1 modeling the ligand-binding region. Y537S and related ESR1 mutations drive resistance to aromatase inhibitors in ER+ breast cancer; oral SERDs such as elacestrant target this setting.",
    },
    "ret_m918t": {
        "id": "ret_m918t",
        "label": "RET",
        "file": "ret_m918_reference.fasta",
        "sample_file": "ret_m918t_sample.fasta",
        "research_areas": ["oncology"],
        "context": "A small stretch of RET modeling M918. M918T is a frequent activating mutation in medullary thyroid cancer; selective RET inhibitors (selpercatinib, pralsetinib) are recent precision therapies for RET-driven cancers.",
    },
    "ntrk_fusion": {
        "id": "ntrk_fusion",
        "label": "NTRK",
        "file": "ntrk_fusion_reference.fasta",
        "sample_file": "ntrk_fusion_sample.fasta",
        "research_areas": ["oncology"],
        "context": "A simplified NTRK region with an in-frame insertion standing in for a kinase fusion junction. NTRK fusions are rare but tumor-agnostic; TRK inhibitors such as repotrectinib are recent options for NTRK+ solid tumors.",
    },
    # --- Rare Mendelian Disease (8) ---
    "cftr_f508del": {
        "id": "cftr_f508del",
        "label": "CFTR",
        "file": "cftr_f508del_reference.fasta",
        "sample_file": "cftr_f508del_sample.fasta",
        "research_areas": ["rare_disease"],
        "context": "A small stretch of CFTR modeling the F508 codon. F508del is the most common cystic-fibrosis allele — an in-frame 3 bp deletion that misfolds CFTR; modulator therapies (e.g. elexacaftor/tezacaftor/ivacaftor) target this genotype class.",
    },
    "cftr_g551d": {
        "id": "cftr_g551d",
        "label": "CFTR",
        "file": "cftr_g551d_reference.fasta",
        "sample_file": "cftr_g551d_sample.fasta",
        "research_areas": ["rare_disease"],
        "context": "A CFTR gating-mutation teaching example (Gly→Asp). G551D was among the first alleles shown to respond to ivacaftor (Kalydeco), opening the door to genotype-guided CF modulators.",
    },
    "hbb_e6v": {
        "id": "hbb_e6v",
        "label": "HBB",
        "file": "hbb_e6v_reference.fasta",
        "sample_file": "hbb_e6v_sample.fasta",
        "research_areas": ["rare_disease"],
        "context": "A small stretch of HBB modeling the classic sickle-cell missense (Glu→Val). This single change polymerizes hemoglobin under low oxygen; gene therapies and disease-modifying drugs now target this pathway.",
    },
    "pah_r408w": {
        "id": "pah_r408w",
        "label": "PAH",
        "file": "pah_r408w_reference.fasta",
        "sample_file": "pah_r408w_sample.fasta",
        "research_areas": ["rare_disease"],
        "context": "A PAH missense teaching example (Arg→Trp) used in phenylketonuria (PKU). Confirming the genotype guides diet, sapropterin responsiveness workups, and enzyme/substitution strategies.",
    },
    "gba_n370s": {
        "id": "gba_n370s",
        "label": "GBA",
        "file": "gba_n370s_reference.fasta",
        "sample_file": "gba_n370s_sample.fasta",
        "research_areas": ["rare_disease"],
        "context": "A GBA missense teaching example (Asn→Ser) associated with Gaucher disease type 1. Enzyme-replacement and substrate-reduction therapies are genotype-informed options.",
    },
    "hexa_1278ins": {
        "id": "hexa_1278ins",
        "label": "HEXA",
        "file": "hexa_1278ins_reference.fasta",
        "sample_file": "hexa_1278ins_sample.fasta",
        "research_areas": ["rare_disease"],
        "context": "A HEXA frameshift insertion teaching example modeled on the common Ashkenazi Tay–Sachs allele. Loss of hexosaminidase A leads to GM2 ganglioside storage; carrier screening is a classic reproductive-genetics use case.",
    },
    "smn1_ex7del": {
        "id": "smn1_ex7del",
        "label": "SMN1",
        "file": "smn1_ex7del_reference.fasta",
        "sample_file": "smn1_ex7del_sample.fasta",
        "research_areas": ["rare_disease"],
        "context": "A simplified SMN1 exon-7 deletion stand-in for spinal muscular atrophy (SMA). Homozygous loss of SMN1 is the usual SMA genotype; SMN-directed therapies (nusinersen, onasemnogene, risdiplam) transformed outcomes.",
    },
    "dmd_frameshift": {
        "id": "dmd_frameshift",
        "label": "DMD",
        "file": "dmd_frameshift_reference.fasta",
        "sample_file": "dmd_frameshift_sample.fasta",
        "research_areas": ["rare_disease"],
        "context": "A DMD out-of-frame deletion teaching example. Frameshifting dystrophin mutations typically cause Duchenne muscular dystrophy; reading-frame rules also explain milder Becker phenotypes and exon-skipping strategies.",
    },
    # --- Cardiology (8) ---
    "myh7_r403q": {
        "id": "myh7_r403q",
        "label": "MYH7",
        "file": "myh7_r403q_reference.fasta",
        "sample_file": "myh7_r403q_sample.fasta",
        "research_areas": ["cardiology"],
        "context": "A MYH7 missense teaching example (Arg→Gln) linked to hypertrophic cardiomyopathy. Identifying a sarcomere variant can trigger cascade screening and ICD risk discussion in relatives.",
    },
    "mybpc3_trunc": {
        "id": "mybpc3_trunc",
        "label": "MYBPC3",
        "file": "mybpc3_trunc_reference.fasta",
        "sample_file": "mybpc3_trunc_sample.fasta",
        "research_areas": ["cardiology"],
        "context": "A MYBPC3 frameshift teaching example. Truncating MYBPC3 alleles are among the most common genetic causes of hypertrophic cardiomyopathy.",
    },
    "kcnq1_a341v": {
        "id": "kcnq1_a341v",
        "label": "KCNQ1",
        "file": "kcnq1_a341v_reference.fasta",
        "sample_file": "kcnq1_a341v_sample.fasta",
        "research_areas": ["cardiology"],
        "context": "A KCNQ1 missense teaching example used for long-QT syndrome type 1 education. Genotype can influence beta-blocker choice, exercise advice, and who else in the family needs ECGs.",
    },
    "scn5a_e1784k": {
        "id": "scn5a_e1784k",
        "label": "SCN5A",
        "file": "scn5a_e1784k_reference.fasta",
        "sample_file": "scn5a_e1784k_sample.fasta",
        "research_areas": ["cardiology"],
        "context": "An SCN5A missense teaching example spanning LQT3 / overlap arrhythmia phenotypes. Sodium-channel variants can change drug choices (e.g. avoiding sodium-channel blockers in Brugada-pattern risk).",
    },
    "ldlr_w66x": {
        "id": "ldlr_w66x",
        "label": "LDLR",
        "file": "ldlr_w66x_reference.fasta",
        "sample_file": "ldlr_w66x_sample.fasta",
        "research_areas": ["cardiology"],
        "context": "An LDLR nonsense teaching example for familial hypercholesterolemia. A molecular diagnosis supports aggressive LDL lowering and cascade lipid screening of relatives.",
    },
    "pkp2_c796r": {
        "id": "pkp2_c796r",
        "label": "PKP2",
        "file": "pkp2_c796r_reference.fasta",
        "sample_file": "pkp2_c796r_sample.fasta",
        "research_areas": ["cardiology"],
        "context": "A PKP2 missense teaching example associated with arrhythmogenic cardiomyopathy. Desmosomal variants prompt imaging, arrhythmia surveillance, and family evaluation.",
    },
    "tnnt2_r92q": {
        "id": "tnnt2_r92q",
        "label": "TNNT2",
        "file": "tnnt2_r92q_reference.fasta",
        "sample_file": "tnnt2_r92q_sample.fasta",
        "research_areas": ["cardiology"],
        "context": "A TNNT2 missense teaching example in the thin-filament cardiomyopathy gene set. Troponin variants can present with hypertrophy or restrictive features and inform sudden-death risk counseling.",
    },
    "lmna_r482w": {
        "id": "lmna_r482w",
        "label": "LMNA",
        "file": "lmna_r482w_reference.fasta",
        "sample_file": "lmna_r482w_sample.fasta",
        "research_areas": ["cardiology"],
        "context": "An LMNA missense teaching example. Lamin A/C cardiomyopathy often warrants earlier consideration of conduction disease and defibrillator therapy than sarcomere HCM alone.",
    },
    # --- Neurology (8) ---
    "scn1a_r377x": {
        "id": "scn1a_r377x",
        "label": "SCN1A",
        "file": "scn1a_r377x_reference.fasta",
        "sample_file": "scn1a_r377x_sample.fasta",
        "research_areas": ["neurology"],
        "context": "An SCN1A nonsense teaching example for Dravet-spectrum epilepsy. Genotype steers away from sodium-channel blockers and toward therapies better suited to SCN1A-related epilepsy.",
    },
    "mecp2_r106w": {
        "id": "mecp2_r106w",
        "label": "MECP2",
        "file": "mecp2_r106w_reference.fasta",
        "sample_file": "mecp2_r106w_sample.fasta",
        "research_areas": ["neurology"],
        "context": "A MECP2 missense teaching example for Rett syndrome. A molecular diagnosis ends long diagnostic odysseys and opens gene-informed trial eligibility.",
    },
    "sod1_a4v": {
        "id": "sod1_a4v",
        "label": "SOD1",
        "file": "sod1_a4v_reference.fasta",
        "sample_file": "sod1_a4v_sample.fasta",
        "research_areas": ["neurology"],
        "context": "A SOD1 missense teaching example used in familial ALS education. SOD1-targeted antisense approaches (e.g. tofersen) are genotype-specific therapy examples.",
    },
    "smn1_sma": {
        "id": "smn1_sma",
        "label": "SMN1",
        "file": "smn1_sma_reference.fasta",
        "sample_file": "smn1_sma_sample.fasta",
        "research_areas": ["neurology"],
        "context": "An SMN1 deletion teaching example for spinal muscular atrophy from the neurology clinic perspective — same gene logic as rare-disease SMA, emphasizing early treatment windows.",
    },
    "gaa_d645e": {
        "id": "gaa_d645e",
        "label": "GAA",
        "file": "gaa_d645e_reference.fasta",
        "sample_file": "gaa_d645e_sample.fasta",
        "research_areas": ["neurology"],
        "context": "A GAA missense teaching example for Pompe disease (acid maltase deficiency). Confirming GAA deficiency / genotype guides enzyme-replacement therapy.",
    },
    "htt_cag": {
        "id": "htt_cag",
        "label": "HTT",
        "file": "htt_cag_reference.fasta",
        "sample_file": "htt_cag_sample.fasta",
        "research_areas": ["neurology"],
        "context": "A simplified HTT CAG-expansion stand-in for Huntington disease. Repeat-length education cases show how in-frame insertions of glutamine codons drive a toxic protein.",
    },
    "app_v717i": {
        "id": "app_v717i",
        "label": "APP",
        "file": "app_v717i_reference.fasta",
        "sample_file": "app_v717i_sample.fasta",
        "research_areas": ["neurology"],
        "context": "An APP missense teaching example (London mutation style) for autosomal-dominant Alzheimer disease. Rare amyloid-pathway variants explain early-onset familial dementia pedigrees.",
    },
    "dmd_exon45": {
        "id": "dmd_exon45",
        "label": "DMD",
        "file": "dmd_exon45_reference.fasta",
        "sample_file": "dmd_exon45_sample.fasta",
        "research_areas": ["neurology"],
        "context": "An in-frame DMD exon-deletion teaching example. Frame rules distinguish Duchenne vs Becker and motivate exon-skipping / micro-dystrophin gene-therapy discussions.",
    },
    # --- Pharmacogenetics (8) ---
    "cyp2c19_star2": {
        "id": "cyp2c19_star2",
        "label": "CYP2C19",
        "file": "cyp2c19_star2_reference.fasta",
        "sample_file": "cyp2c19_star2_sample.fasta",
        "research_areas": ["pharmacogenetics"],
        "context": "A CYP2C19 loss-of-function teaching stand-in (*2 class). Poor clopidogrel activation raises guidance to consider alternative antiplatelets after PCI.",
    },
    "cyp2d6_star4": {
        "id": "cyp2d6_star4",
        "label": "CYP2D6",
        "file": "cyp2d6_star4_reference.fasta",
        "sample_file": "cyp2d6_star4_sample.fasta",
        "research_areas": ["pharmacogenetics"],
        "context": "A CYP2D6 loss-of-function teaching stand-in (*4 class). Activity score changes dosing or drug choice for many antidepressants, opioids, and other CYP2D6 substrates.",
    },
    "tpmt_star3c": {
        "id": "tpmt_star3c",
        "label": "TPMT",
        "file": "tpmt_star3c_reference.fasta",
        "sample_file": "tpmt_star3c_sample.fasta",
        "research_areas": ["pharmacogenetics"],
        "context": "A TPMT missense teaching example. Low TPMT activity means thiopurines (azathioprine, 6-MP) can cause life-threatening myelosuppression unless doses are reduced or avoided.",
    },
    "vkorc1_d36y": {
        "id": "vkorc1_d36y",
        "label": "VKORC1",
        "file": "vkorc1_d36y_reference.fasta",
        "sample_file": "vkorc1_d36y_sample.fasta",
        "research_areas": ["pharmacogenetics"],
        "context": "A VKORC1 coding-change teaching stand-in for warfarin sensitivity. Combined with CYP2C9, VKORC1 genotype helps explain large differences in weekly warfarin dose.",
    },
    "dpyd_star2a": {
        "id": "dpyd_star2a",
        "label": "DPYD",
        "file": "dpyd_star2a_reference.fasta",
        "sample_file": "dpyd_star2a_sample.fasta",
        "research_areas": ["pharmacogenetics"],
        "context": "A DPYD deletion/splice teaching stand-in (*2A class). DPD deficiency predisposes to severe fluoropyrimidine (5-FU / capecitabine) toxicity.",
    },
    "slco1b1_v174a": {
        "id": "slco1b1_v174a",
        "label": "SLCO1B1",
        "file": "slco1b1_v174a_reference.fasta",
        "sample_file": "slco1b1_v174a_sample.fasta",
        "research_areas": ["pharmacogenetics"],
        "context": "An SLCO1B1 missense teaching example (Val→Ala) linked to simvastatin myopathy risk. Guidelines may recommend dose limits or alternative statins.",
    },
    "hlab_5701": {
        "id": "hlab_5701",
        "label": "HLA-B",
        "file": "hlab_5701_reference.fasta",
        "sample_file": "hlab_5701_sample.fasta",
        "research_areas": ["pharmacogenetics"],
        "context": "An HLA-B marker teaching stand-in for *57:01. This allele predicts abacavir hypersensitivity — a classic “do not give this drug” pharmacogenetic rule.",
    },
    "cyp3a5_star3": {
        "id": "cyp3a5_star3",
        "label": "CYP3A5",
        "file": "cyp3a5_star3_reference.fasta",
        "sample_file": "cyp3a5_star3_sample.fasta",
        "research_areas": ["pharmacogenetics"],
        "context": "A CYP3A5 non-expressor teaching stand-in (*3 class). Tacrolimus dosing differs sharply between expressors and non-expressors after transplant.",
    },
    # --- Infectious Disease Genomics (8) ---
    "hiv_rt_k103n": {
        "id": "hiv_rt_k103n",
        "label": "HIV RT",
        "file": "hiv_rt_k103n_reference.fasta",
        "sample_file": "hiv_rt_k103n_sample.fasta",
        "research_areas": ["infectious"],
        "context": "An HIV reverse-transcriptase missense teaching example (Lys→Asn). K103N confers resistance to first-generation NNRTIs such as efavirenz.",
    },
    "hiv_rt_m184v": {
        "id": "hiv_rt_m184v",
        "label": "HIV RT",
        "file": "hiv_rt_m184v_reference.fasta",
        "sample_file": "hiv_rt_m184v_sample.fasta",
        "research_areas": ["infectious"],
        "context": "An HIV RT missense teaching example (Met→Val). M184V is selected by lamivudine/emtricitabine and is one of the most common NRTI resistance mutations.",
    },
    "tb_rpob_s531l": {
        "id": "tb_rpob_s531l",
        "label": "rpoB",
        "file": "tb_rpob_s531l_reference.fasta",
        "sample_file": "tb_rpob_s531l_sample.fasta",
        "research_areas": ["infectious"],
        "context": "A Mycobacterium tuberculosis rpoB missense teaching example. S531L-class changes are a major cause of rifampin resistance and drive MDR-TB regimen changes.",
    },
    "flu_na_h275y": {
        "id": "flu_na_h275y",
        "label": "NA",
        "file": "flu_na_h275y_reference.fasta",
        "sample_file": "flu_na_h275y_sample.fasta",
        "research_areas": ["infectious"],
        "context": "An influenza neuraminidase missense teaching example (His→Tyr). H275Y reduces oseltamivir susceptibility in H1N1 — a classic antiviral-resistance biomarker.",
    },
    "mrsa_mecA": {
        "id": "mrsa_mecA",
        "label": "mecA",
        "file": "mrsa_mecA_reference.fasta",
        "sample_file": "mrsa_mecA_sample.fasta",
        "research_areas": ["infectious"],
        "context": "A simplified mecA cassette insertion stand-in for MRSA. Acquisition of mecA encodes PBP2a and methicillin/oxacillin resistance.",
    },
    "hcv_ns5a_y93h": {
        "id": "hcv_ns5a_y93h",
        "label": "NS5A",
        "file": "hcv_ns5a_y93h_reference.fasta",
        "sample_file": "hcv_ns5a_y93h_sample.fasta",
        "research_areas": ["infectious"],
        "context": "An HCV NS5A missense teaching example (Tyr→His). Y93H can reduce susceptibility to some NS5A inhibitors and influences DAA regimen choice.",
    },
    "sars2_spike_n501y": {
        "id": "sars2_spike_n501y",
        "label": "S",
        "file": "sars2_spike_n501y_reference.fasta",
        "sample_file": "sars2_spike_n501y_sample.fasta",
        "research_areas": ["infectious"],
        "context": "A SARS-CoV-2 spike missense teaching example (Asn→Tyr). N501Y appeared in multiple variants of concern and illustrates how pathogen sequencing tracks transmission and immune escape.",
    },
    "hiv_pr_l90m": {
        "id": "hiv_pr_l90m",
        "label": "HIV PR",
        "file": "hiv_pr_l90m_reference.fasta",
        "sample_file": "hiv_pr_l90m_sample.fasta",
        "research_areas": ["infectious"],
        "context": "An HIV protease missense teaching example (Leu→Met). L90M contributes to resistance against several protease inhibitors and is read on standard HIV genotype reports.",
    },
    # --- Reproductive / Prenatal (8) ---
    "cftr_carrier": {
        "id": "cftr_carrier",
        "label": "CFTR",
        "file": "cftr_carrier_reference.fasta",
        "sample_file": "cftr_carrier_sample.fasta",
        "research_areas": ["reproductive"],
        "context": "A CFTR F508del teaching example framed for carrier screening. Finding one pathogenic allele prompts partner testing before or during pregnancy.",
    },
    "hbb_carrier": {
        "id": "hbb_carrier",
        "label": "HBB",
        "file": "hbb_carrier_reference.fasta",
        "sample_file": "hbb_carrier_sample.fasta",
        "research_areas": ["reproductive"],
        "context": "An HBB Glu→Val teaching example for sickle-cell carrier screening. Couples who are both carriers have a 25% chance of an affected child each pregnancy.",
    },
    "smn1_carrier": {
        "id": "smn1_carrier",
        "label": "SMN1",
        "file": "smn1_carrier_reference.fasta",
        "sample_file": "smn1_carrier_sample.fasta",
        "research_areas": ["reproductive"],
        "context": "An SMN1 deletion teaching example for SMA carrier screening — now a routine offering for people planning pregnancy in many guidelines.",
    },
    "hexa_carrier": {
        "id": "hexa_carrier",
        "label": "HEXA",
        "file": "hexa_carrier_reference.fasta",
        "sample_file": "hexa_carrier_sample.fasta",
        "research_areas": ["reproductive"],
        "context": "A HEXA frameshift teaching example for Tay–Sachs carrier screening, historically emphasized in Ashkenazi Jewish panels and now often part of broader carrier tests.",
    },
    "fmr1_cgg": {
        "id": "fmr1_cgg",
        "label": "FMR1",
        "file": "fmr1_cgg_reference.fasta",
        "sample_file": "fmr1_cgg_sample.fasta",
        "research_areas": ["reproductive"],
        "context": "A simplified FMR1 CGG-repeat expansion stand-in for fragile X. Premutation / full-mutation length classes change reproductive risk counseling and prenatal testing options.",
    },
    "f5_leiden": {
        "id": "f5_leiden",
        "label": "F5",
        "file": "f5_leiden_reference.fasta",
        "sample_file": "f5_leiden_sample.fasta",
        "research_areas": ["reproductive"],
        "context": "An F5 R506Q teaching example (Factor V Leiden). Thrombophilia genotype can inform VTE risk counseling around pregnancy, estrogen therapy, and surgery.",
    },
    "gjb2_35delg": {
        "id": "gjb2_35delg",
        "label": "GJB2",
        "file": "gjb2_35delg_reference.fasta",
        "sample_file": "gjb2_35delg_sample.fasta",
        "research_areas": ["reproductive"],
        "context": "A GJB2 single-base deletion teaching example. 35delG is a common cause of autosomal-recessive nonsyndromic hearing loss and appears on many carrier / newborn workups.",
    },
    "mthfr_c677t": {
        "id": "mthfr_c677t",
        "label": "MTHFR",
        "file": "mthfr_c677t_reference.fasta",
        "sample_file": "mthfr_c677t_sample.fasta",
        "research_areas": ["reproductive"],
        "context": "An MTHFR Ala→Val teaching stand-in for the common C677T variant. Used here to practice reading a frequent SNP — clinical utility is limited compared with true pathogenic carrier findings.",
    },
    # --- Immunology (8) ---
    "il2rg_r226c": {
        "id": "il2rg_r226c",
        "label": "IL2RG",
        "file": "il2rg_r226c_reference.fasta",
        "sample_file": "il2rg_r226c_sample.fasta",
        "research_areas": ["immunology"],
        "context": "An IL2RG missense teaching example for X-linked SCID. A molecular diagnosis routes infants toward urgent transplant or gene-therapy pathways.",
    },
    "ada_g216r": {
        "id": "ada_g216r",
        "label": "ADA",
        "file": "ada_g216r_reference.fasta",
        "sample_file": "ada_g216r_sample.fasta",
        "research_areas": ["immunology"],
        "context": "An ADA missense teaching example for adenosine-deaminase–deficient SCID. Enzyme replacement and gene therapy are genotype-linked options alongside transplant.",
    },
    "btk_r28c": {
        "id": "btk_r28c",
        "label": "BTK",
        "file": "btk_r28c_reference.fasta",
        "sample_file": "btk_r28c_sample.fasta",
        "research_areas": ["immunology"],
        "context": "A BTK missense teaching example for X-linked agammaglobulinemia (different clinical story from oncology BTK C481S). Loss of BTK blocks B-cell development; Ig replacement is foundational care.",
    },
    "was_trunc": {
        "id": "was_trunc",
        "label": "WAS",
        "file": "was_trunc_reference.fasta",
        "sample_file": "was_trunc_sample.fasta",
        "research_areas": ["immunology"],
        "context": "A WAS frameshift teaching example for Wiskott–Aldrich syndrome (eczema, thrombocytopenia, immune dysfunction). Genotype severity correlates with phenotype and transplant timing.",
    },
    "foxp3_r397w": {
        "id": "foxp3_r397w",
        "label": "FOXP3",
        "file": "foxp3_r397w_reference.fasta",
        "sample_file": "foxp3_r397w_sample.fasta",
        "research_areas": ["immunology"],
        "context": "A FOXP3 missense teaching example for IPEX syndrome (immune dysregulation, polyendocrinopathy, enteropathy, X-linked). Regulatory T-cell failure drives autoimmunity.",
    },
    "stat3_r382w": {
        "id": "stat3_r382w",
        "label": "STAT3",
        "file": "stat3_r382w_reference.fasta",
        "sample_file": "stat3_r382w_sample.fasta",
        "research_areas": ["immunology"],
        "context": "A STAT3 missense teaching example for autosomal-dominant hyper-IgE syndrome (Job syndrome). Genotype clarifies infection prophylaxis and complication surveillance.",
    },
    "hla_b_mismatch": {
        "id": "hla_b_mismatch",
        "label": "HLA-B",
        "file": "hla_b_mismatch_reference.fasta",
        "sample_file": "hla_b_mismatch_sample.fasta",
        "research_areas": ["immunology"],
        "context": "A simplified HLA-B coding mismatch teaching example. Transplant matching compares donor vs recipient HLA alleles — differences raise rejection and GVHD risk.",
    },
    "ciita_del": {
        "id": "ciita_del",
        "label": "CIITA",
        "file": "ciita_del_reference.fasta",
        "sample_file": "ciita_del_sample.fasta",
        "research_areas": ["immunology"],
        "context": "A CIITA in-frame deletion teaching example for MHC class II deficiency (bare lymphocyte syndrome type II). Without CIITA, HLA class II expression fails and CD4 help collapses.",
    },
}

CUSTOM_REFERENCE = {
    "id": "",
    "label": "Custom Reference",
    "research_areas": None,  # available for every research area
    "context": 'Use any reference sequence from a <a href="https://my.clevelandclinic.org/health/body/gene" target="_blank" rel="noopener noreferrer">gene</a>.',
}

RESEARCH_AREAS = [
    {
        "id": "oncology",
        "label": "Oncology",
        "description": (
            "Oncology is the study of cancer, which is a disease of the DNA. It starts when genetic mutations corrupt a single cell, causing it to divide "
            "uncontrollably and refuse to die when it should. We can sequence DNA to identify genetic mutations that are "
            "present and inform treatment decisions. If the cancer is in late stages, or if a "
            "<a href='https://massivebio.com/what-are-the-differences-between-solid-and-liquid-tumors/' target='_blank' rel='noopener noreferrer'>liquid cancer</a> "
            "is identified, DNA sequencing becomes invaluable."
        ),
    },
    {
        "id": "cardiology",
        "label": "Cardiology",
        "description": (
            "Gene sequencing is used in cardiology to identify mutations that can cause inherited heart conditions. "
            "It serves as a tool for early disease detection and to develop personalized treatment plans."
            "Sequencing results can influence real decisions: which medicines to use, whether an implantable defibrillator is appropriate, "
            "how aggressively to lower cholesterol, and who else in the family might need to be screened before they develop symptoms."
        ),
    },
    {
        "id": "immunology",
        "label": "Immunology",
        "description": (
            "The body's immune system is built to defend the body from infections, viruses, and bacteria. It has a strong genetic backbone. "
            "Sequencing can help diagnose primary immunodeficiencies, evaluate tumor microenvironments, and has become a gold standard "
            "for matching donors and recipients for organ and bone marrow transplants. A molecular diagnosis can also point toward specific "
            "treatments or curative pathways such as stem-cell transplant or gene therapy."
        ),
    },
    {
        "id": "infectious",
        "label": "Infectious Disease Genomics",
        "description": (
            "Infectious Disease Genomics utilizes DNA and RNA sequencing to decode the genetic makeup of pathogens and their human hosts. "
            "It maps the exact transmission pathways, detecting antimicrobial resistance. This accelerates the development of targeted vaccines "
            "and therapeutics. The DNA being read often belongs to the pathogen, not the patient. Sequencing HIV, tuberculosis, bacteria, "
            "or viruses can reveal resistance mutations and track outbreaks as they spread."
            "<br /><br />"
            "Clinicians use results to pick antivirals or antibiotics that still work, while public-health teams use "
            "related methods to understand transmission."
        ),
    },
    {
        "id": "neurology",
        "label": "Neurology",
        "description": (
            "Neurology studies the nervous system and its diseases. Panels and exomes that are sequenced can pinpoint the causes of "
            "epilepsy, neuromuscular disease, ataxia, ALS subtypes, and developmental disorders that look similar at the bedside but differ genetically."
            "For some diagnoses, the gene answer unlocks targeted therapy (for example SMA treatments) or steers families "
            "toward the right trials, prognosis, and reproductive planning."
        ),
    },
    {
        "id": "pharmacogenetics",
        "label": "Pharmacogenetics",
        "description": (
            "Pharmacogenetics studies how inherited genetic variations may influence an individual's response to medications. The main concerns of "
            "this dicipline are drug metabolism, safety, and efficacy. Variants in genes such as CYP2C19, CYP2D6, TPMT, and HLA-B can change how "
            "medicines are activated, cleared, or whether they trigger dangerous immune reactions."
            "Sequencing informs dosing and drug choice for blood thinners, antidepressants, pain medicines, HIV therapy, and more — aiming for the "
            "right drug and dose the first time."
        ),
    },
    {
        "id": "rare_disease",
        "label": "Rare Mendelian Disease",
        "description": (
            "Rare Mendelian diseases are genetic conditions caused by a mutation in a single gene, following classic laws of inheritance. "
            "The diseases are individually rare, but cumulatively affect millions of people worldwide. Conditions like cystic fibrosis, "
            "sickle cell disease, Duchenne muscular dystrophy, and thousands of metabolic disorders are included in this category. "
            "Sequencing can confirm a diagnosis that might otherwise take years of guesswork. Once the exact variant is known, care shifts " 
            "from generic symptom management to gene-informed options: disease-modifying drugs for specific CFTR variants, gene therapies for "
            "sickle cell or SMA, and clearer guidance for family members who may carry the same change."
        ),
    },
    {
        "id": "reproductive",
        "label": "Reproductive and Prenatal",
        "description": (
            "Gene sequencing is utilized across the reproductive journey to assess carrier risks before pregnancy, screen embryos during IVF, "
            "and to diagnose fetal anomalies. The goal is information people can act on — whether that means knowing a couple’s shared carrier risk, "
            "clarifying a finding in pregnancy, or explaining a genetic contribution to reproductive challenges."
        ),
    },
]


# ------------------------------------------------------------------------------------- #
# application functions
# ------------------------------------------------------------------------------------- #

def list_research_areas() -> list[dict[str, str]]:
    """Research areas sorted alphabetically by label for the picker."""
    return sorted(
        (
            {"id": area["id"], "label": area["label"], "description": area["description"]}
            for area in RESEARCH_AREAS
        ),
        key=lambda area: area["label"].lower(),
    )


def parse_sequence_text(raw: str) -> tuple[str, str]:
    """Parse FASTA or raw DNA text into (header, sequence)."""
    text = raw.strip()
    if not text:
        raise ValueError("Empty sequence input.")

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines[0].startswith(">"):
        header = lines[0].lstrip(">")
        sequence = "".join(line.upper() for line in lines[1:])
    else:
        header = "uploaded_sequence"
        sequence = "".join(lines).upper()

    sequence = "".join(ch for ch in sequence if ch.isalpha())
    if not sequence:
        raise ValueError("No DNA bases found in input.")
    return header, sequence


def read_fasta(path: Path) -> tuple[str, str]:
    return parse_sequence_text(path.read_text())


def find_local_indels(ref: str, alt: str) -> list[dict[str, Any]]:
    """Find simple indels when sequences differ in length (educational, not full aligner)."""
    events: list[dict[str, Any]] = []
    i = j = 0
    while i < len(ref) and j < len(alt):
        if ref[i] == alt[j]:
            i += 1
            j += 1
            continue

        for size in range(1, min(30, len(ref) - i + 1)):
            lookahead = min(6, len(alt) - j)
            if ref[i + size : i + size + lookahead] == alt[j : j + lookahead]:
                events.append(
                    {
                        "type": "deletion",
                        "ref_start": i,
                        "alt_start": j,
                        "deleted_bases": ref[i : i + size],
                        "length": size,
                    }
                )
                i += size
                break
        else:
            for size in range(1, min(30, len(alt) - j + 1)):
                lookahead = min(6, len(ref) - i)
                if alt[j + size : j + size + lookahead] == ref[i : i + lookahead]:
                    events.append(
                        {
                            "type": "insertion",
                            "ref_start": i,
                            "alt_start": j,
                            "inserted_bases": alt[j : j + size],
                            "length": size,
                        }
                    )
                    j += size
                    break
            else:
                events.append(
                    {
                        "type": "mismatch",
                        "ref_pos": i,
                        "alt_pos": j,
                        "ref_base": ref[i],
                        "alt_base": alt[j],
                    }
                )
                i += 1
                j += 1

    if i < len(ref):
        events.append(
            {
                "type": "deletion",
                "ref_start": i,
                "alt_start": j,
                "deleted_bases": ref[i:],
                "length": len(ref) - i,
            }
        )
    if j < len(alt):
        events.append(
            {
                "type": "insertion",
                "ref_start": i,
                "alt_start": j,
                "inserted_bases": alt[j:],
                "length": len(alt) - j,
            }
        )

    return events


def translate(dna: str) -> str:
    """Translate DNA from first ATG through first stop codon."""
    dna = dna.upper()
    start = dna.find("ATG")
    if start == -1:
        start = 0
    protein: list[str] = []
    for i in range(start, len(dna), 3):
        codon = dna[i : i + 3]
        if len(codon) < 3:
            protein.append("?")
            continue
        aa = CODON_TABLE.get(codon, "X")
        protein.append(aa)
        if aa == "*":
            break
    return "".join(protein)


def protein_alignment(ref_protein: str, alt_protein: str) -> dict[str, str]:
    width = max(len(ref_protein), len(alt_protein))
    ref = ref_protein.ljust(width, "-")
    alt = alt_protein.ljust(width, "-")
    marks = "".join("|" if r == a else " " for r, a in zip(ref, alt))
    return {"reference": ref, "marks": marks, "alternate": alt}


def build_sequence_spans(ref: str, alt: str, events: list[dict[str, Any]]) -> dict[str, list[dict]]:
    """Annotate reference and sample sequences with anomaly spans for UI highlighting."""
    ref_marks = ["match"] * len(ref)
    alt_marks = ["match"] * len(alt)

    for event in events:
        etype = event["type"]
        if etype == "deletion":
            start = event["ref_start"]
            end = start + event["length"]
            for pos in range(start, min(end, len(ref))):
                ref_marks[pos] = "deletion"
            if event["alt_start"] < len(alt):
                alt_marks[event["alt_start"]] = "deletion-edge"
        elif etype == "insertion":
            start = event["alt_start"]
            end = start + event["length"]
            for pos in range(start, min(end, len(alt))):
                alt_marks[pos] = "insertion"
            if event["ref_start"] < len(ref):
                ref_marks[event["ref_start"]] = "insertion-edge"
        elif etype == "mismatch":
            if event["ref_pos"] < len(ref):
                ref_marks[event["ref_pos"]] = "mismatch"
            if event["alt_pos"] < len(alt):
                alt_marks[event["alt_pos"]] = "mismatch"

    def collapse(sequence: str, marks: list[str]) -> list[dict]:
        if not sequence:
            return []
        spans: list[dict] = []
        current = marks[0]
        start = 0
        for idx in range(1, len(marks)):
            if marks[idx] != current:
                spans.append({"text": sequence[start:idx], "kind": current, "start": start})
                current = marks[idx]
                start = idx
        spans.append({"text": sequence[start:], "kind": current, "start": start})
        return spans

    return {"reference": collapse(ref, ref_marks), "sample": collapse(alt, alt_marks)}


def interpret_impact(
    events: list[dict[str, Any]],
    length_delta: int,
    ref_protein: str,
    alt_protein: str,
    preset_id: str | None = None,
) -> list[dict[str, str]]:
    """Produce teaching-oriented clinical notes from detected anomalies."""
    notes: list[dict[str, str]] = []
    deletions = [e for e in events if e["type"] == "deletion"]
    insertions = [e for e in events if e["type"] == "insertion"]
    mismatches = [e for e in events if e["type"] == "mismatch"]

    if not events:
        notes.append(
            {
                "severity": "info",
                "title": "No sequence differences",
                "detail": "Sample matches the reference over the compared region.",
            }
        )
        return notes

    for deletion in deletions:
        in_frame = deletion["length"] % 3 == 0
        notes.append(
            {
                "severity": "critical" if in_frame else "warning",
                "title": f"Deletion · {deletion['length']} bp @ ref {deletion['ref_start']}",
                "detail": (
                    f"Deleted bases: {deletion['deleted_bases']}. "
                    + (
                        "In-frame deletion (length ÷ 3) — amino acids removed but reading frame preserved."
                        if in_frame
                        else "Out-of-frame deletion — likely frameshift downstream, altering every codon after the break."
                    )
                ),
            }
        )

    for insertion in insertions:
        frameshift = insertion["length"] % 3 != 0
        notes.append(
            {
                "severity": "critical" if frameshift else "warning",
                "title": f"Insertion · {insertion['length']} bp @ ref {insertion['ref_start']}",
                "detail": (
                    f"Inserted bases: {insertion['inserted_bases']}. "
                    + (
                        "Frameshift insertion — alters every downstream codon and often truncates the protein."
                        if frameshift
                        else "In-frame insertion — adds amino acids without shifting the reading frame."
                    )
                ),
            }
        )

    if mismatches:
        notes.append(
            {
                "severity": "warning",
                "title": f"{len(mismatches)} base mismatch(es)",
                "detail": (
                    "Point substitutions detected. A missense change swaps one amino acid; impact depends on "
                    "the gene, residue, and clinical context."
                ),
            }
        )

    if abs(length_delta) % 3 != 0 and length_delta != 0:
        notes.append(
            {
                "severity": "critical",
                "title": "Frameshift indicated by length delta",
                "detail": f"Net length change of {length_delta:+d} bp is not divisible by 3.",
            }
        )

    premature_stop = "*" in alt_protein and (
        "*" not in ref_protein or alt_protein.index("*") < ref_protein.index("*")
        if "*" in ref_protein
        else True
    )
    if premature_stop and "*" in alt_protein:
        stop_at = alt_protein.index("*")
        notes.append(
            {
                "severity": "critical",
                "title": f"Premature stop codon at AA {stop_at + 1}",
                "detail": (
                    f"Sample protein truncated ({len(alt_protein)} aa incl. stop vs {len(ref_protein)} aa reference). "
                    "Premature stops often mean loss of function; clinical meaning depends on the gene."
                ),
            }
        )

    if preset_id == "egfr_exon19" and any(
        e["type"] == "deletion" and e["length"] % 3 == 0 for e in deletions
    ):
        notes.append(
            {
                "severity": "actionable",
                "title": "Matches EGFR exon 19 teaching pattern",
                "detail": "In-frame exon 19 deletion pattern consistent with TKI-sensitizing biomarker education case.",
            }
        )
    if preset_id == "brca1" and ("*" in alt_protein or any(e["type"] == "insertion" for e in insertions)):
        notes.append(
            {
                "severity": "actionable",
                "title": "Matches BRCA1 frameshift teaching pattern",
                "detail": "Frameshift / premature stop pattern consistent with HRD education case (Part 3 of the notebook).",
            }
        )

    if preset_id == "btk_c481" and mismatches:
        notes.append(
            {
                "severity": "actionable",
                "title": "Matches BTK C481S teaching pattern (CLL)",
                "detail": (
                    "Missense change at the modeled C481 codon (Cys→Ser). "
                    "C481S is a common resistance mutation after covalent BTK inhibitors "
                    "(e.g. ibrutinib). Non-covalent BTK inhibitors such as pirtobrutinib "
                    "(Jaypirca) remain active against C481-mutant BTK and are used in "
                    "relapsed/refractory CLL/SLL after prior covalent BTK-inhibitor therapy."
                ),
            }
        )

    if preset_id == "kras_g12c" and mismatches:
        notes.append(
            {
                "severity": "actionable",
                "title": "Matches KRAS G12C teaching pattern",
                "detail": (
                    "Missense change at the modeled codon 12 (Gly→Cys). "
                    "KRAS G12C covalent inhibitors (sotorasib, adagrasib) were among the first "
                    "approved drugs to directly target mutant KRAS in NSCLC."
                ),
            }
        )

    if preset_id == "braf_v600e" and mismatches:
        notes.append(
            {
                "severity": "actionable",
                "title": "Matches BRAF V600E teaching pattern",
                "detail": (
                    "Missense change at the modeled V600 codon (Val→Glu). "
                    "BRAF V600E activates MAPK signaling; BRAF inhibitors such as encorafenib "
                    "are used (often with a MEK inhibitor) in melanoma, colorectal cancer, and NSCLC."
                ),
            }
        )

    if preset_id == "esr1_y537s" and mismatches:
        notes.append(
            {
                "severity": "actionable",
                "title": "Matches ESR1 Y537S teaching pattern",
                "detail": (
                    "Missense change at the modeled Y537 codon (Tyr→Ser). "
                    "ESR1 ligand-binding-domain mutations drive resistance to aromatase inhibitors "
                    "in ER+/HER2− metastatic breast cancer; elacestrant (Orserdu) is an oral SERD "
                    "approved for ESR1-mutant disease after endocrine therapy."
                ),
            }
        )

    if preset_id == "ret_m918t" and mismatches:
        notes.append(
            {
                "severity": "actionable",
                "title": "Matches RET M918T teaching pattern",
                "detail": (
                    "Missense change at the modeled M918 codon (Met→Thr). "
                    "M918T is a common activating RET mutation in medullary thyroid cancer. "
                    "Selective RET inhibitors (selpercatinib, pralsetinib) are recent options "
                    "for RET-driven thyroid cancer and RET fusion–positive NSCLC."
                ),
            }
        )

    if preset_id == "ntrk_fusion" and any(e["type"] == "insertion" and e["length"] % 3 == 0 for e in insertions):
        notes.append(
            {
                "severity": "actionable",
                "title": "Matches NTRK fusion teaching pattern",
                "detail": (
                    "In-frame insertion used as a simplified stand-in for an NTRK kinase fusion. "
                    "NTRK fusions are uncommon but actionable across tumor types; next-generation "
                    "TRK inhibitors such as repotrectinib (Augtyro) are recent tumor-agnostic options."
                ),
            }
        )

    teaching = PRESET_TEACHING_NOTES.get(preset_id)
    if teaching and _preset_pattern_matched(preset_id, events, alt_protein):
        notes.append(
            {
                "severity": "actionable",
                "title": teaching["title"],
                "detail": teaching["detail"],
            }
        )

    return notes


# ------------------------------------------------------------------------------------- #
# build up the teaching notes when a sequence is analyzed
# ------------------------------------------------------------------------------------- #

PRESET_TEACHING_NOTES: dict[str, dict[str, str]] = {
    "cftr_f508del": {
        "title": "Matches CFTR F508del teaching pattern",
        "detail": "In-frame 3 bp deletion at the modeled F508 codon — the most common cystic-fibrosis allele. CFTR modulators (e.g. elexacaftor/tezacaftor/ivacaftor) are genotype-directed therapies for this class.",
    },
    "cftr_g551d": {
        "title": "Matches CFTR G551D teaching pattern",
        "detail": "Missense change (Gly→Asp) at a classic CFTR gating codon. Ivacaftor was first approved for G551D and related gating mutations.",
    },
    "hbb_e6v": {
        "title": "Matches HBB sickle teaching pattern",
        "detail": "Missense change (Glu→Val) modeling the sickle-cell mutation in β-globin. Gene therapies and disease-modifying agents target this pathway.",
    },
    "pah_r408w": {
        "title": "Matches PAH R408W teaching pattern",
        "detail": "Missense change (Arg→Trp) used in PKU education. Genotype informs dietary management and sapropterin / enzyme-therapy discussions.",
    },
    "gba_n370s": {
        "title": "Matches GBA N370S teaching pattern",
        "detail": "Missense change (Asn→Ser) associated with Gaucher disease type 1. Enzyme-replacement and substrate-reduction therapies are options after confirmatory testing.",
    },
    "hexa_1278ins": {
        "title": "Matches HEXA 1278insTATC teaching pattern",
        "detail": "Frameshift insertion modeled on a common Tay–Sachs allele. Carrier screening and reproductive counseling are the usual next clinical steps.",
    },
    "smn1_ex7del": {
        "title": "Matches SMN1 exon-7 deletion teaching pattern",
        "detail": "Deletion stand-in for SMA. SMN-directed therapies (nusinersen, onasemnogene abeparvovec, risdiplam) depend on confirming SMN1 loss and SMN2 copy number.",
    },
    "dmd_frameshift": {
        "title": "Matches DMD frameshift teaching pattern",
        "detail": "Out-of-frame deletion pattern consistent with Duchenne muscular dystrophy education. Frame rules also motivate exon-skipping strategies.",
    },
    "myh7_r403q": {
        "title": "Matches MYH7 R403Q teaching pattern",
        "detail": "Missense change in a sarcomere gene linked to hypertrophic cardiomyopathy. Cascade family screening and sudden-death risk assessment follow a pathogenic finding.",
    },
    "mybpc3_trunc": {
        "title": "Matches MYBPC3 truncating teaching pattern",
        "detail": "Frameshift pattern in MYBPC3 — among the most common genetic causes of HCM. Relatives should be offered clinical and genetic evaluation.",
    },
    "kcnq1_a341v": {
        "title": "Matches KCNQ1 long-QT teaching pattern",
        "detail": "Missense change used for LQT1 education. Genotype can refine beta-blocker choice, activity advice, and who needs ECGs in the family.",
    },
    "scn5a_e1784k": {
        "title": "Matches SCN5A arrhythmia teaching pattern",
        "detail": "Missense change in the cardiac sodium channel spanning LQT3 / overlap phenotypes. Drug lists and device decisions often change with genotype.",
    },
    "ldlr_w66x": {
        "title": "Matches LDLR familial hypercholesterolemia teaching pattern",
        "detail": "Nonsense change truncating LDL receptor teaching protein. Supports aggressive LDL lowering and cascade lipid screening.",
    },
    "pkp2_c796r": {
        "title": "Matches PKP2 arrhythmogenic cardiomyopathy teaching pattern",
        "detail": "Missense change in a desmosomal gene. Triggers imaging, arrhythmia surveillance, and family evaluation for ARVC/ACM.",
    },
    "tnnt2_r92q": {
        "title": "Matches TNNT2 cardiomyopathy teaching pattern",
        "detail": "Missense change in cardiac troponin T — a thin-filament HCM/restrictive cardiomyopathy gene used in cascade screening education.",
    },
    "lmna_r482w": {
        "title": "Matches LMNA cardiomyopathy teaching pattern",
        "detail": "Missense change in lamin A/C. Laminopathies often warrant earlier conduction-disease and ICD discussions than sarcomere HCM alone.",
    },
    "scn1a_r377x": {
        "title": "Matches SCN1A Dravet teaching pattern",
        "detail": "Nonsense change in SCN1A. Dravet-spectrum care avoids sodium-channel blockers and uses genotype-informed antiseizure strategies.",
    },
    "mecp2_r106w": {
        "title": "Matches MECP2 Rett teaching pattern",
        "detail": "Missense change in MECP2. A molecular Rett diagnosis ends diagnostic odysseys and opens gene-informed trial pathways.",
    },
    "sod1_a4v": {
        "title": "Matches SOD1 ALS teaching pattern",
        "detail": "Missense change used in familial ALS education. SOD1-targeted antisense therapy (tofersen) is a genotype-specific example.",
    },
    "smn1_sma": {
        "title": "Matches SMN1 SMA teaching pattern",
        "detail": "Deletion stand-in for SMA from the neurology clinic perspective. Early SMN-directed therapy is time-critical.",
    },
    "gaa_d645e": {
        "title": "Matches GAA Pompe teaching pattern",
        "detail": "Missense change in acid α-glucosidase. Confirmed Pompe disease is treated with enzyme-replacement therapy.",
    },
    "htt_cag": {
        "title": "Matches HTT CAG-expansion teaching pattern",
        "detail": "In-frame CAG insertion stand-in for Huntington disease. Repeat length classes drive predictive testing and reproductive counseling.",
    },
    "app_v717i": {
        "title": "Matches APP familial Alzheimer teaching pattern",
        "detail": "Missense change in APP used for autosomal-dominant Alzheimer disease education in rare early-onset pedigrees.",
    },
    "dmd_exon45": {
        "title": "Matches DMD in-frame exon deletion teaching pattern",
        "detail": "In-frame deletion stand-in illustrating Becker-leaning frame rules and exon-skipping / gene-therapy discussions.",
    },
    "cyp2c19_star2": {
        "title": "Matches CYP2C19 loss-of-function teaching pattern",
        "detail": "Loss-of-function stand-in for CYP2C19*2-class alleles. Poor clopidogrel activation may prompt alternative antiplatelet therapy.",
    },
    "cyp2d6_star4": {
        "title": "Matches CYP2D6 loss-of-function teaching pattern",
        "detail": "Loss-of-function stand-in for CYP2D6*4-class alleles. Activity score changes dosing for many antidepressants and opioids.",
    },
    "tpmt_star3c": {
        "title": "Matches TPMT *3C teaching pattern",
        "detail": "Missense change reducing TPMT activity. Thiopurine doses must be reduced or avoided to prevent severe myelosuppression.",
    },
    "vkorc1_d36y": {
        "title": "Matches VKORC1 warfarin-sensitivity teaching pattern",
        "detail": "Coding-change stand-in for VKORC1 warfarin sensitivity. Helps explain large differences in weekly warfarin dose.",
    },
    "dpyd_star2a": {
        "title": "Matches DPYD *2A teaching pattern",
        "detail": "Deletion/splice stand-in for DPD deficiency. Fluoropyrimidine chemotherapy can be life-threatening without dose adjustment.",
    },
    "slco1b1_v174a": {
        "title": "Matches SLCO1B1 V174A teaching pattern",
        "detail": "Missense change linked to simvastatin myopathy risk. Guidelines may limit dose or prefer another statin.",
    },
    "hlab_5701": {
        "title": "Matches HLA-B*57:01 teaching pattern",
        "detail": "Marker stand-in for HLA-B*57:01. Abacavir is contraindicated when this allele is present.",
    },
    "cyp3a5_star3": {
        "title": "Matches CYP3A5 *3 teaching pattern",
        "detail": "Non-expressor stand-in for CYP3A5*3. Tacrolimus dosing differs sharply between expressors and non-expressors.",
    },
    "hiv_rt_k103n": {
        "title": "Matches HIV RT K103N teaching pattern",
        "detail": "Missense change conferring resistance to first-generation NNRTIs such as efavirenz — a classic HIV genotype finding.",
    },
    "hiv_rt_m184v": {
        "title": "Matches HIV RT M184V teaching pattern",
        "detail": "Missense change selected by lamivudine/emtricitabine and among the most common NRTI resistance mutations.",
    },
    "tb_rpob_s531l": {
        "title": "Matches TB rpoB rifampin-resistance teaching pattern",
        "detail": "Missense change in rpoB associated with rifampin resistance and MDR-TB regimen redesign.",
    },
    "flu_na_h275y": {
        "title": "Matches influenza NA H275Y teaching pattern",
        "detail": "Missense change reducing oseltamivir susceptibility in H1N1 — a classic antiviral-resistance biomarker.",
    },
    "mrsa_mecA": {
        "title": "Matches MRSA mecA teaching pattern",
        "detail": "Insertion stand-in for mecA acquisition encoding PBP2a and methicillin/oxacillin resistance.",
    },
    "hcv_ns5a_y93h": {
        "title": "Matches HCV NS5A Y93H teaching pattern",
        "detail": "Missense change that can reduce susceptibility to some NS5A inhibitors and influence DAA choice.",
    },
    "sars2_spike_n501y": {
        "title": "Matches SARS-CoV-2 spike N501Y teaching pattern",
        "detail": "Spike missense used to illustrate variant tracking and immune-escape surveillance in outbreak genomics.",
    },
    "hiv_pr_l90m": {
        "title": "Matches HIV protease L90M teaching pattern",
        "detail": "Missense change contributing to resistance against several protease inhibitors on standard HIV genotype reports.",
    },
    "cftr_carrier": {
        "title": "Matches CFTR carrier-screening teaching pattern",
        "detail": "F508del-style in-frame deletion framed for carrier screening. A positive result prompts partner testing.",
    },
    "hbb_carrier": {
        "title": "Matches HBB sickle-carrier teaching pattern",
        "detail": "Glu→Val change used in sickle-cell carrier counseling. Dual-carrier couples have a 25% risk of an affected child each pregnancy.",
    },
    "smn1_carrier": {
        "title": "Matches SMN1 carrier-screening teaching pattern",
        "detail": "SMN1 deletion stand-in for SMA carrier screening before or during pregnancy.",
    },
    "hexa_carrier": {
        "title": "Matches HEXA carrier-screening teaching pattern",
        "detail": "Frameshift insertion stand-in for Tay–Sachs carrier screening panels.",
    },
    "fmr1_cgg": {
        "title": "Matches FMR1 CGG-expansion teaching pattern",
        "detail": "CGG insertion stand-in for fragile X. Repeat-length class changes reproductive risk and prenatal testing options.",
    },
    "f5_leiden": {
        "title": "Matches Factor V Leiden teaching pattern",
        "detail": "Arg→Gln change modeling F5 Leiden. Informs VTE risk counseling around pregnancy and estrogen exposure.",
    },
    "gjb2_35delg": {
        "title": "Matches GJB2 35delG teaching pattern",
        "detail": "Single-base deletion modeling a common recessive hearing-loss allele used in carrier and newborn workups.",
    },
    "mthfr_c677t": {
        "title": "Matches MTHFR C677T teaching pattern",
        "detail": "Common Ala→Val SNP stand-in. Practice reading a frequent variant — clinical actionability is limited versus true pathogenic carrier findings.",
    },
    "il2rg_r226c": {
        "title": "Matches IL2RG X-SCID teaching pattern",
        "detail": "Missense change in the common γ-chain. X-linked SCID needs urgent transplant or gene-therapy pathways.",
    },
    "ada_g216r": {
        "title": "Matches ADA-SCID teaching pattern",
        "detail": "Missense change in adenosine deaminase. Enzyme replacement, gene therapy, and transplant are genotype-linked options.",
    },
    "btk_r28c": {
        "title": "Matches BTK XLA teaching pattern",
        "detail": "Missense change modeling X-linked agammaglobulinemia (not the oncology C481S story). Ig replacement is foundational care.",
    },
    "was_trunc": {
        "title": "Matches WAS truncating teaching pattern",
        "detail": "Frameshift pattern in Wiskott–Aldrich syndrome. Genotype severity correlates with phenotype and transplant timing.",
    },
    "foxp3_r397w": {
        "title": "Matches FOXP3 IPEX teaching pattern",
        "detail": "Missense change in FOXP3. Regulatory T-cell failure drives the IPEX autoimmune phenotype.",
    },
    "stat3_r382w": {
        "title": "Matches STAT3 hyper-IgE teaching pattern",
        "detail": "Missense change used for AD-HIES (Job syndrome) education — infection prophylaxis and complication surveillance follow genotype.",
    },
    "hla_b_mismatch": {
        "title": "Matches HLA-B mismatch teaching pattern",
        "detail": "Coding mismatch stand-in for transplant donor–recipient HLA comparison. Differences raise rejection and GVHD risk.",
    },
    "ciita_del": {
        "title": "Matches CIITA MHC II deficiency teaching pattern",
        "detail": "In-frame deletion stand-in for bare lymphocyte syndrome type II — without CIITA, HLA class II expression fails.",
    },
}


def _preset_pattern_matched(
    preset_id: str,
    events: list[dict[str, Any]],
    alt_protein: str,
) -> bool:
    """Whether the sample shows the expected event class for a teaching preset note."""
    if not events:
        return False
    deletions = [e for e in events if e["type"] == "deletion"]
    insertions = [e for e in events if e["type"] == "insertion"]
    mismatches = [e for e in events if e["type"] == "mismatch"]
    deletion_presets = {
        "cftr_f508del",
        "smn1_ex7del",
        "dmd_frameshift",
        "mybpc3_trunc",
        "smn1_sma",
        "dmd_exon45",
        "dpyd_star2a",
        "cftr_carrier",
        "smn1_carrier",
        "gjb2_35delg",
        "was_trunc",
        "ciita_del",
    }
    insertion_presets = {
        "hexa_1278ins",
        "htt_cag",
        "mrsa_mecA",
        "hexa_carrier",
        "fmr1_cgg",
    }
    stop_presets = {"ldlr_w66x", "scn1a_r377x", "cyp2c19_star2", "cyp2d6_star4", "cyp3a5_star3"}
    if preset_id in deletion_presets:
        return bool(deletions)
    if preset_id in insertion_presets:
        return bool(insertions)
    if preset_id in stop_presets:
        return "*" in alt_protein or bool(mismatches)
    # missense / substitution teaching cases (also accept rare indel calls from multi-base swaps)
    return bool(mismatches) or bool(events)


def summarize_notes_for_layperson(
    events: list[dict[str, Any]],
    length_delta: int,
    ref_protein: str,
    alt_protein: str,
    preset_id: str | None = None,
) -> str:
    """One extremely plain-language paragraph summarizing what the notes mean."""
    if not events:
        return (
            "The sample DNA looks the same as the reference in this short region. "
            "Nothing unusual jumped out in this comparison."
        )

    deletions = [e for e in events if e["type"] == "deletion"]
    insertions = [e for e in events if e["type"] == "insertion"]
    mismatches = [e for e in events if e["type"] == "mismatch"]
    parts: list[str] = []

    if deletions:
        sizes = ", ".join(str(e["length"]) for e in deletions)
        in_frame = all(e["length"] % 3 == 0 for e in deletions)
        if in_frame:
            parts.append(
                f"Some DNA letters are missing ({sizes} of them). "
                "The missing chunk is a multiple of 3, so the rest of the protein instructions can "
                "still be read in order."
            )
        else:
            parts.append(
                f"Some DNA letters are missing ({sizes} of them). "
                "The missing chunk throws off the 3-letter reading frame, so everything after it "
                "is damaged."
            )

    if insertions:
        sizes = ", ".join(str(e["length"]) for e in insertions)
        frameshift = any(e["length"] % 3 != 0 for e in insertions)
        if frameshift:
            parts.append(
                f"extra DNA letters were added (about {sizes}). "
                "This can scramble the protein recipe from that point on."
            )
        else:
            parts.append(
                f"extra DNA letters were added (about {sizes}), but the protein reading frame is kept intact."
            )

    if mismatches:
        n = len(mismatches)
        parts.append(
            f"{'One DNA letter was swapped' if n == 1 else f'{n} DNA letters were swapped'} "
            "for a different letter. This can change one building block of the protein "
            "(sometimes this is important, sometimes it isn't)."
        )

    premature_stop = "*" in alt_protein and (
        "*" not in ref_protein or alt_protein.index("*") < ref_protein.index("*")
    )
    if premature_stop:
        parts.append(
            "The sample’s protein also hits a stop sign early, so the finished protein is shorter "
            "than it should be — often meaning it no longer works properly."
        )

    preset_blurbs = {
        "egfr_exon19": (
            "This pattern matches a well-known lung-cancer change in EGFR that often means "
            "EGFR inhibitors (oral medications) may help."
        ),
        "brca1": (
            "This pattern matches a BRCA1-style break in a DNA-repair gene, which may be treated by "
            "PARP-inhibitor medicines."
        ),
        "btk_c481": (
            "This pattern matches a BTK change seen in chronic lymphocytic leukemia after older bruton "
            "tyrosine kinase inhibitors drugs stop working — a newer medicine like pirtobrutinib can be considered."
        ),
        "kras_g12c": (
            "This pattern matches KRAS G12C, a common lung-cancer switch that newer KRAS-targeted "
            "drugs were designed to hit."
        ),
        "braf_v600e": (
            "This pattern matches BRAF V600E, a growth-signal switch that BRAF-targeted medicines "
            "are meant to turn down."
        ),
        "esr1_y537s": (
            "This pattern matches an ESR1 change that can help breast-cancer cells ignore older "
            "hormone blockers — which is why drugs like elacestrant were developed."
        ),
        "ret_m918t": (
            "This pattern matches a RET switch that selective RET drugs were built to target."
        ),
        "ntrk_fusion": (
            "This pattern is a simplified stand-in for an NTRK fusion — a rare “mix-and-match” gene "
            "event that some tumor-agnostic TRK drugs can target."
        ),
        "cftr_f508del": "This matches the common cystic-fibrosis F508del change — medicines called CFTR modulators are built for genotypes like this.",
        "cftr_g551d": "This matches a CFTR gating change (like G551D) that ivacaftor was first approved to treat.",
        "hbb_e6v": "This matches the sickle-cell change in hemoglobin — one swapped letter that changes how red cells behave.",
        "pah_r408w": "This matches a PKU-related change in the PAH gene that guides diet and specialty medicine choices.",
        "gba_n370s": "This matches a Gaucher-disease–style change in GBA that enzyme or substrate-reduction therapies can address.",
        "hexa_1278ins": "This matches a Tay–Sachs–style break in HEXA — important for carrier screening and family planning.",
        "smn1_ex7del": "This matches an SMA-style loss of SMN1 — a gene answer that unlocked several SMN-directed treatments.",
        "dmd_frameshift": "This matches a Duchenne-style frameshift in dystrophin, where the reading-frame rules matter a lot.",
        "myh7_r403q": "This matches a hypertrophic-cardiomyopathy change in MYH7 that often leads to family heart screening.",
        "mybpc3_trunc": "This matches a truncating MYBPC3 change — another common genetic cause of thick-heart cardiomyopathy.",
        "kcnq1_a341v": "This matches a long-QT–style change in KCNQ1 that can change medicines, exercise advice, and family ECG checks.",
        "scn5a_e1784k": "This matches a cardiac sodium-channel change that can reshape arrhythmia drug and device decisions.",
        "ldlr_w66x": "This matches a familial hypercholesterolemia–style break in the LDL receptor gene.",
        "pkp2_c796r": "This matches a desmosome-gene change linked to arrhythmogenic cardiomyopathy family evaluation.",
        "tnnt2_r92q": "This matches a troponin-gene cardiomyopathy change used in cascade family screening education.",
        "lmna_r482w": "This matches a lamin A/C change — these cardiomyopathies often need earlier rhythm-device discussions.",
        "scn1a_r377x": "This matches an SCN1A epilepsy change (Dravet-spectrum) where some seizure medicines should be avoided.",
        "mecp2_r106w": "This matches a Rett-syndrome–style MECP2 change that can end a long diagnostic search.",
        "sod1_a4v": "This matches a familial ALS–style SOD1 change — an example where gene-targeted therapy exists.",
        "smn1_sma": "This matches SMA from the neurology clinic view — early SMN-directed treatment matters.",
        "gaa_d645e": "This matches a Pompe-disease–style GAA change treated with enzyme replacement.",
        "htt_cag": "This is a simplified Huntington CAG-expansion pattern — extra repeat letters that lengthen the protein.",
        "app_v717i": "This matches a rare familial Alzheimer–style APP change seen in some early-onset families.",
        "dmd_exon45": "This matches an in-frame dystrophin exon-loss pattern used to teach Becker vs Duchenne frame rules.",
        "cyp2c19_star2": "This matches a CYP2C19 “slow metabolizer” pattern that can change antiplatelet drug choice.",
        "cyp2d6_star4": "This matches a CYP2D6 loss-of-function pattern that changes dosing for many everyday medicines.",
        "tpmt_star3c": "This matches a TPMT change that makes usual thiopurine doses dangerously strong.",
        "vkorc1_d36y": "This matches a warfarin-sensitivity pattern — one reason people need very different weekly doses.",
        "dpyd_star2a": "This matches a DPD-deficiency pattern that can make 5-FU / capecitabine chemotherapy unsafe at standard doses.",
        "slco1b1_v174a": "This matches an SLCO1B1 change linked to higher simvastatin muscle-injury risk.",
        "hlab_5701": "This matches an HLA-B*57:01–style warning marker — abacavir should not be given when present.",
        "cyp3a5_star3": "This matches a CYP3A5 non-expressor pattern that changes tacrolimus dosing after transplant.",
        "hiv_rt_k103n": "This matches an HIV drug-resistance change that older NNRTI medicines may no longer cover.",
        "hiv_rt_m184v": "This matches a common HIV resistance change selected by lamivudine / emtricitabine.",
        "tb_rpob_s531l": "This matches a tuberculosis rifampin-resistance change that forces a different antibiotic plan.",
        "flu_na_h275y": "This matches a flu neuraminidase change that can blunt oseltamivir (Tamiflu).",
        "mrsa_mecA": "This matches an MRSA-style mecA acquisition — the bacteria picked up methicillin-resistance gear.",
        "hcv_ns5a_y93h": "This matches a hepatitis C NS5A resistance change that can alter which antiviral combo is used.",
        "sars2_spike_n501y": "This matches a SARS-CoV-2 spike change used to track variants during an outbreak.",
        "hiv_pr_l90m": "This matches an HIV protease-inhibitor resistance change seen on standard genotype reports.",
        "cftr_carrier": "This matches a cystic-fibrosis carrier finding — the next step is usually testing the partner.",
        "hbb_carrier": "This matches a sickle-cell carrier finding used in pregnancy and family-planning counseling.",
        "smn1_carrier": "This matches an SMA carrier-screening finding now offered to many people planning pregnancy.",
        "hexa_carrier": "This matches a Tay–Sachs carrier-screening finding.",
        "fmr1_cgg": "This is a simplified fragile-X repeat expansion — repeat length changes reproductive counseling.",
        "f5_leiden": "This matches Factor V Leiden, a clotting-risk variant discussed around pregnancy and estrogen therapy.",
        "gjb2_35delg": "This matches a common recessive hearing-loss allele used in carrier and newborn workups.",
        "mthfr_c677t": "This matches a very common MTHFR SNP — good practice reading a frequent change with limited actionability.",
        "il2rg_r226c": "This matches an X-linked SCID–style change that needs urgent immune-restoring treatment planning.",
        "ada_g216r": "This matches an ADA-SCID change where enzyme replacement or gene therapy may enter the conversation.",
        "btk_r28c": "This matches an X-linked agammaglobulinemia–style BTK change (different from cancer BTK C481S).",
        "was_trunc": "This matches a Wiskott–Aldrich frameshift used to teach severe combined immune/platelet disease.",
        "foxp3_r397w": "This matches an IPEX-style FOXP3 change — the immune system’s “brakes” fail.",
        "stat3_r382w": "This matches a hyper-IgE (Job) syndrome–style STAT3 change.",
        "hla_b_mismatch": "This matches a simplified transplant HLA mismatch — donor and recipient immune barcodes differ.",
        "ciita_del": "This matches an MHC class II deficiency pattern where helper-T immune signaling can’t start properly.",
    }
    if preset_id in preset_blurbs:
        parts.append(preset_blurbs[preset_id])

    if length_delta != 0 and abs(length_delta) % 3 != 0 and not any(
        e["type"] in ("deletion", "insertion") and e["length"] % 3 != 0 for e in events
    ):
        parts.append(
            "Overall, the sample is a different length in a way that can scramble the protein recipe."
        )

    return " ".join(parts)


# ------------------------------------------------------------------------------------- #
# define catalog of existing drugs that are used in the teaching examples
# ------------------------------------------------------------------------------------- #

# DrugBank is used to link molecule names, brand names link to DailyMed
DRUGBANK_BASE = "https://go.drugbank.com/drugs/"

def _dailymed(*, setid: str | None = None, query: str | None = None) -> str:
    """Stable FDA-label link (prefer setid; fall back to DailyMed search)."""
    if setid:
        return f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}"
    return (
        "https://dailymed.nlm.nih.gov/dailymed/search.cfm?labeltype=all&query="
        + (query or "")
    )


def _brand(name: str, *, setid: str | None = None) -> dict[str, str]:
    return {"name": name, "url": _dailymed(setid=setid, query=name)}


DRUG_CATALOG = {
    # --- Oncology ---
    "osimertinib": {
        "name": "Osimertinib",
        "drugbank_id": "DB09330",
        "drug_class": "3rd-generation EGFR tyrosine kinase inhibitor (TKI)",
        "brands": [_brand("Tagrisso", setid="5e81b4a7-b971-45e1-9c31-29cea8c87ce7")],
    },
    "erlotinib": {
        "name": "Erlotinib",
        "drugbank_id": "DB00530",
        "drug_class": "1st-generation EGFR tyrosine kinase inhibitor (TKI)",
        "brands": [_brand("Tarceva", setid="5783976b-0862-44e5-9b19-0f41d236d5c3")],
    },
    "gefitinib": {
        "name": "Gefitinib",
        "drugbank_id": "DB00317",
        "drug_class": "1st-generation EGFR tyrosine kinase inhibitor (TKI)",
        "brands": [_brand("Iressa", setid="827d60e8-7e07-41b7-c28b-49ef1c4a5a41")],
    },
    "olaparib": {
        "name": "Olaparib",
        "drugbank_id": "DB09074",
        "drug_class": "PARP inhibitor",
        "brands": [_brand("Lynparza", setid="741ff3e3-dc1a-45a6-84e5-2481b27131aa")],
    },
    "rucaparib": {
        "name": "Rucaparib",
        "drugbank_id": "DB12332",
        "drug_class": "PARP inhibitor",
        "brands": [_brand("Rubraca", setid="0295d202-1cfe-7659-e063-6294a90a476e")],
    },
    "niraparib": {
        "name": "Niraparib",
        "drugbank_id": "DB11793",
        "drug_class": "PARP inhibitor",
        "brands": [_brand("Zejula", setid="b7f675e2-159c-490c-b6f4-3f16d9492b7d")],
    },
    "pirtobrutinib": {
        "name": "Pirtobrutinib",
        "drugbank_id": "DB17472",
        "drug_class": "Non-covalent (reversible) BTK inhibitor",
        "brands": [_brand("Jaypirca", setid="bd551845-0878-49a4-860f-839b83f6b801")],
    },
    "sotorasib": {
        "name": "Sotorasib",
        "drugbank_id": "DB15569",
        "drug_class": "KRAS G12C inhibitor",
        "brands": [_brand("Lumakras", setid="c80a362c-7ac3-4894-a076-0691e68ef8c1")],
    },
    "adagrasib": {
        "name": "Adagrasib",
        "drugbank_id": "DB15568",
        "drug_class": "KRAS G12C inhibitor",
        "brands": [_brand("Krazati", setid="0b8bf078-34c2-4f45-9012-38a8ac082b01")],
    },
    "encorafenib": {
        "name": "Encorafenib",
        "drugbank_id": "DB11967",
        "drug_class": "BRAF kinase inhibitor",
        "brands": [_brand("Braftovi", setid="235dfc38-0f0b-4037-b501-7a9f4294740c")],
    },
    "elacestrant": {
        "name": "Elacestrant",
        "drugbank_id": "DB06374",
        "drug_class": "Oral selective estrogen receptor degrader (SERD)",
        "brands": [_brand("Orserdu", setid="aa66ae5c-2bd2-4444-8178-b55651e054ef")],
    },
    "selpercatinib": {
        "name": "Selpercatinib",
        "drugbank_id": "DB15685",
        "drug_class": "Selective RET kinase inhibitor",
        "brands": [_brand("Retevmo", setid="7fa848ba-a59c-4144-9f52-64d090f4d828")],
    },
    "pralsetinib": {
        "name": "Pralsetinib",
        "drugbank_id": "DB15822",
        "drug_class": "Selective RET kinase inhibitor",
        "brands": [_brand("Gavreto", setid="59984249-e3ff-4f97-8d7a-c1a905d604a8")],
    },
    "repotrectinib": {
        "name": "Repotrectinib",
        "drugbank_id": "DB16826",
        "drug_class": "ROS1 / TRK tyrosine kinase inhibitor",
        "brands": [_brand("Augtyro", setid="fb526827-40ba-4462-94cf-179ae3b0cb8a")],
    },
    # --- Rare Mendelian ---
    "ivacaftor": {
        "name": "Ivacaftor",
        "drugbank_id": "DB08820",
        "drug_class": "CFTR potentiator",
        "brands": [_brand("Kalydeco", setid="0ab0c9f8-3eee-4e0f-9f3f-c1e16aaffe25")],
    },
    "elexacaftor_tezacaftor_ivacaftor": {
        "name": "Elexacaftor / tezacaftor / ivacaftor",
        "drugbank_id": "DB15444",
        "drug_class": "CFTR corrector / potentiator combination",
        "brands": [_brand("Trikafta", setid="f354423a-85c2-41c3-a9db-0f3aee135d8d")],
    },
    "hydroxyurea": {
        "name": "Hydroxyurea",
        "drugbank_id": "DB01008",
        "drug_class": "Ribonucleotide reductase inhibitor (sickle-cell disease-modifying)",
        "brands": [_brand("Hydrea"), _brand("Droxia")],
    },
    "voxelotor": {
        "name": "Voxelotor",
        "drugbank_id": "DB14989",
        "drug_class": "Hemoglobin S polymerization inhibitor",
        "brands": [_brand("Oxbryta")],
    },
    "sapropterin": {
        "name": "Sapropterin",
        "drugbank_id": "DB00360",
        "drug_class": "Synthetic BH4 cofactor (PKU)",
        "brands": [_brand("Kuvan")],
    },
    "imiglucerase": {
        "name": "Imiglucerase",
        "drugbank_id": "DB00053",
        "drug_class": "Enzyme replacement therapy (Gaucher disease)",
        "brands": [_brand("Cerezyme")],
    },
    "eliglustat": {
        "name": "Eliglustat",
        "drugbank_id": "DB09051",
        "drug_class": "Glucosylceramide synthase inhibitor (Gaucher)",
        "brands": [_brand("Cerdelga")],
    },
    "nusinersen": {
        "name": "Nusinersen",
        "drugbank_id": "DB13161",
        "drug_class": "SMN2-directed antisense oligonucleotide",
        "brands": [_brand("Spinraza")],
    },
    "risdiplam": {
        "name": "Risdiplam",
        "drugbank_id": "DB15305",
        "drug_class": "SMN2 splicing modifier",
        "brands": [_brand("Evrysdi", setid="eceb9a99-7191-4be5-87c3-0102707cf98e")],
    },
    "onasemnogene": {
        "name": "Onasemnogene abeparvovec",
        "drugbank_id": "DB15599",
        "drug_class": "AAV9 SMN1 gene therapy",
        "brands": [_brand("Zolgensma")],
    },
    "eteplirsen": {
        "name": "Eteplirsen",
        "drugbank_id": "DB06014",
        "drug_class": "DMD exon-51 skipping antisense oligonucleotide",
        "brands": [_brand("Exondys 51")],
    },
    "delandistrogene": {
        "name": "Delandistrogene moxeparvovec",
        "drugbank_id": "DB16798",
        "drug_class": "AAV rh74 micro-dystrophin gene therapy",
        "brands": [_brand("Elevidys")],
    },
    # --- Cardiology ---
    "mavacamten": {
        "name": "Mavacamten",
        "drugbank_id": "DB14924",
        "drug_class": "Cardiac myosin inhibitor (obstructive HCM)",
        "brands": [_brand("Camzyos")],
    },
    "metoprolol": {
        "name": "Metoprolol",
        "drugbank_id": "DB00264",
        "drug_class": "Beta-1 selective adrenergic blocker",
        "brands": [_brand("Lopressor"), _brand("Toprol-XL")],
    },
    "nadolol": {
        "name": "Nadolol",
        "drugbank_id": "DB01203",
        "drug_class": "Nonselective beta blocker (long-QT / arrhythmia)",
        "brands": [_brand("Corgard")],
    },
    "mexiletine": {
        "name": "Mexiletine",
        "drugbank_id": "DB00379",
        "drug_class": "Class Ib sodium-channel blocker (LQT3)",
        "brands": [_brand("Mexitil")],
    },
    "evolocumab": {
        "name": "Evolocumab",
        "drugbank_id": "DB09303",
        "drug_class": "PCSK9 inhibitor (familial hypercholesterolemia)",
        "brands": [_brand("Repatha")],
    },
    "rosuvastatin": {
        "name": "Rosuvastatin",
        "drugbank_id": "DB01098",
        "drug_class": "HMG-CoA reductase inhibitor (statin)",
        "brands": [_brand("Crestor")],
    },
    "sotalol": {
        "name": "Sotalol",
        "drugbank_id": "DB00489",
        "drug_class": "Class III antiarrhythmic / beta blocker",
        "brands": [_brand("Betapace")],
    },
    # --- Neurology ---
    "fenfluramine": {
        "name": "Fenfluramine",
        "drugbank_id": "DB04571",
        "drug_class": "Serotonin-releasing antiseizure medicine (Dravet)",
        "brands": [_brand("Fintepla")],
    },
    "cannabidiol": {
        "name": "Cannabidiol",
        "drugbank_id": "DB09061",
        "drug_class": "Antiseizure medicine (Dravet / LGS)",
        "brands": [_brand("Epidiolex")],
    },
    "trofinetide": {
        "name": "Trofinetide",
        "drugbank_id": "DB16640",
        "drug_class": "Synthetic IGF-1 tripeptide analog (Rett syndrome)",
        "brands": [_brand("Daybue")],
    },
    "tofersen": {
        "name": "Tofersen",
        "drugbank_id": "DB14790",
        "drug_class": "SOD1-directed antisense oligonucleotide (ALS)",
        "brands": [_brand("Qalsody")],
    },
    "alglucosidase": {
        "name": "Alglucosidase alfa",
        "drugbank_id": "DB01272",
        "drug_class": "Enzyme replacement therapy (Pompe disease)",
        "brands": [_brand("Lumizyme"), _brand("Myozyme")],
    },
    "deutetrabenazine": {
        "name": "Deutetrabenazine",
        "drugbank_id": "DB12278",
        "drug_class": "VMAT2 inhibitor (Huntington chorea)",
        "brands": [_brand("Austedo")],
    },
    "lecanemab": {
        "name": "Lecanemab",
        "drugbank_id": "DB14580",
        "drug_class": "Anti-amyloid monoclonal antibody (Alzheimer disease)",
        "brands": [_brand("Leqembi")],
    },
    # --- Pharmacogenetics (often alternatives / dose-guided drugs) ---
    "prasugrel": {
        "name": "Prasugrel",
        "drugbank_id": "DB06209",
        "drug_class": "P2Y12 inhibitor (clopidogrel alternative)",
        "brands": [_brand("Effient")],
    },
    "ticagrelor": {
        "name": "Ticagrelor",
        "drugbank_id": "DB08816",
        "drug_class": "P2Y12 inhibitor (clopidogrel alternative)",
        "brands": [_brand("Brilinta")],
    },
    "azathioprine": {
        "name": "Azathioprine",
        "drugbank_id": "DB00993",
        "drug_class": "Thiopurine immunosuppressant (TPMT-guided dosing)",
        "brands": [_brand("Imuran")],
    },
    "warfarin": {
        "name": "Warfarin",
        "drugbank_id": "DB00682",
        "drug_class": "Vitamin K antagonist (VKORC1/CYP2C9-guided dosing)",
        "brands": [_brand("Coumadin")],
    },
    "fluorouracil": {
        "name": "Fluorouracil",
        "drugbank_id": "DB00544",
        "drug_class": "Fluoropyrimidine antimetabolite (DPYD-guided)",
        "brands": [_brand("Adrucil")],
    },
    "capecitabine": {
        "name": "Capecitabine",
        "drugbank_id": "DB01101",
        "drug_class": "Oral fluoropyrimidine prodrug (DPYD-guided)",
        "brands": [_brand("Xeloda")],
    },
    "pravastatin": {
        "name": "Pravastatin",
        "drugbank_id": "DB00175",
        "drug_class": "Statin alternative when SLCO1B1 risk is high",
        "brands": [_brand("Pravachol")],
    },
    "dolutegravir": {
        "name": "Dolutegravir",
        "drugbank_id": "DB08930",
        "drug_class": "HIV integrase strand-transfer inhibitor",
        "brands": [_brand("Tivicay")],
    },
    "tacrolimus": {
        "name": "Tacrolimus",
        "drugbank_id": "DB00864",
        "drug_class": "Calcineurin inhibitor (CYP3A5-guided dosing)",
        "brands": [_brand("Prograf")],
    },
    # --- Infectious disease ---
    "bedaquiline": {
        "name": "Bedaquiline",
        "drugbank_id": "DB08903",
        "drug_class": "Diarylquinoline antimycobacterial (MDR-TB)",
        "brands": [_brand("Sirturo")],
    },
    "linezolid": {
        "name": "Linezolid",
        "drugbank_id": "DB00601",
        "drug_class": "Oxazolidinone antibiotic",
        "brands": [_brand("Zyvox")],
    },
    "zanamivir": {
        "name": "Zanamivir",
        "drugbank_id": "DB00558",
        "drug_class": "Neuraminidase inhibitor (oseltamivir alternative)",
        "brands": [_brand("Relenza")],
    },
    "baloxavir": {
        "name": "Baloxavir marboxil",
        "drugbank_id": "DB13997",
        "drug_class": "Cap-dependent endonuclease inhibitor (influenza)",
        "brands": [_brand("Xofluza")],
    },
    "vancomycin": {
        "name": "Vancomycin",
        "drugbank_id": "DB00512",
        "drug_class": "Glycopeptide antibiotic (MRSA)",
        "brands": [_brand("Vancocin")],
    },
    "sofosbuvir_velpatasvir_voxilaprevir": {
        "name": "Sofosbuvir / velpatasvir / voxilaprevir",
        "drugbank_id": "DB08934",
        "drug_class": "HCV NS5B / NS5A / protease inhibitor combination",
        "brands": [_brand("Vosevi")],
    },
    "nirmatrelvir_ritonavir": {
        "name": "Nirmatrelvir / ritonavir",
        "drugbank_id": "DB15661",
        "drug_class": "SARS-CoV-2 main protease inhibitor (+ booster)",
        "brands": [_brand("Paxlovid")],
    },
    "darunavir": {
        "name": "Darunavir",
        "drugbank_id": "DB01264",
        "drug_class": "HIV protease inhibitor",
        "brands": [_brand("Prezista")],
    },
    # --- Reproductive ---
    "enoxaparin": {
        "name": "Enoxaparin",
        "drugbank_id": "DB01225",
        "drug_class": "Low-molecular-weight heparin",
        "brands": [_brand("Lovenox")],
    },
    "folic_acid": {
        "name": "Folic acid",
        "drugbank_id": "DB00158",
        "drug_class": "B-vitamin cofactor (preconception / pregnancy support)",
        "brands": [_brand("Folic Acid")],
    },
    # --- Immunology ---
    "elapegademase": {
        "name": "Elapegademase",
        "drugbank_id": "DB14712",
        "drug_class": "Recombinant ADA enzyme replacement (ADA-SCID)",
        "brands": [_brand("Revcovi")],
    },
    "immune_globulin": {
        "name": "Immune globulin (human)",
        "drugbank_id": "DB00028",
        "drug_class": "Replacement immunoglobulin (antibody deficiency)",
        "brands": [_brand("Gamunex-C"), _brand("Privigen")],
    },
    "sirolimus": {
        "name": "Sirolimus",
        "drugbank_id": "DB00877",
        "drug_class": "mTOR inhibitor (immune dysregulation / transplant)",
        "brands": [_brand("Rapamune")],
    },
    "mycophenolate": {
        "name": "Mycophenolate mofetil",
        "drugbank_id": "DB00688",
        "drug_class": "Antimetabolite immunosuppressant (transplant)",
        "brands": [_brand("CellCept")],
    },
}

# ------------------------------------------------------------------------------------- #
# build up the UI components after sequence is analyzed
# ------------------------------------------------------------------------------------- #

def _drug_card(key: str, biomarker: str, evidence: str) -> dict[str, Any]:
    drug = DRUG_CATALOG[key]
    return {
        "name": drug["name"],
        "drug_class": drug["drug_class"],
        "drugbank_id": drug["drugbank_id"],
        "drugbank_url": f"{DRUGBANK_BASE}{drug['drugbank_id']}",
        "brands": drug["brands"],
        "biomarker": biomarker,
        "evidence": evidence,
    }


def _events_of(events: list[dict[str, Any]], kind: str) -> bool:
    return any(e["type"] == kind for e in events)

def suggest_treatments(
    events: list[dict[str, Any]],
    length_delta: int,
    ref_protein: str,
    alt_protein: str,
    preset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Map detected alterations to teaching-level treatment cards (any research area)."""
    cards: list[dict[str, Any]] = []
    if not events:
        return cards

    in_frame_deletion = any(
        e["type"] == "deletion" and e["length"] % 3 == 0 for e in events
    )
    frameshift = (
        any(e["type"] in ("deletion", "insertion") and e["length"] % 3 != 0 for e in events)
        or (length_delta != 0 and abs(length_delta) % 3 != 0)
    )
    premature_stop = "*" in alt_protein and (
        "*" not in ref_protein or alt_protein.index("*") < ref_protein.index("*")
    )
    mismatch = _events_of(events, "mismatch")
    deletion = _events_of(events, "deletion")
    insertion = _events_of(events, "insertion")

    def add(keys: tuple[str, ...] | list[str], biomarker: str, evidence: str) -> None:
        cards.extend(_drug_card(key, biomarker, evidence) for key in keys)

    # --- Cancer ---
    if in_frame_deletion and preset_id in (None, "egfr_exon19"):
        add(
            ("osimertinib", "erlotinib", "gefitinib"),
            "EGFR exon 19 in-frame deletion (TKI-sensitizing)",
            "OncoKB Level 1 (NSCLC)",
        )
    if (frameshift or premature_stop) and preset_id in (None, "brca1"):
        add(
            ("olaparib", "rucaparib", "niraparib"),
            "BRCA1 loss-of-function (truncating / frameshift → HRD)",
            "OncoKB Level 1 (breast / ovarian / prostate)",
        )
    if preset_id == "btk_c481" and mismatch:
        add(("pirtobrutinib",), "BTK C481S (CLL/SLL; covalent BTK-inhibitor resistance)", "FDA-approved (after prior covalent BTKi)")
    if preset_id == "kras_g12c" and mismatch:
        add(("sotorasib", "adagrasib"), "KRAS G12C (NSCLC)", "FDA-approved (KRAS G12C–mutated NSCLC)")
    if preset_id == "braf_v600e" and mismatch:
        add(("encorafenib",), "BRAF V600E (melanoma / CRC / NSCLC)", "FDA-approved (often + MEK inhibitor)")
    if preset_id == "esr1_y537s" and mismatch:
        add(("elacestrant",), "ESR1 Y537S (ER+/HER2− mBC)", "FDA-approved (after endocrine therapy)")
    if preset_id == "ret_m918t" and mismatch:
        add(("selpercatinib", "pralsetinib"), "RET M918T (MTC / RET-driven tumors)", "FDA-approved (RET-altered cancers)")
    if preset_id == "ntrk_fusion" and any(e["type"] == "insertion" and e["length"] % 3 == 0 for e in events):
        add(("repotrectinib",), "NTRK gene fusion (tumor-agnostic)", "FDA-approved (NTRK+ solid tumors)")

    # --- Rare Mendelian ---
    if preset_id == "cftr_f508del" and deletion:
        add(
            ("elexacaftor_tezacaftor_ivacaftor", "ivacaftor"),
            "CFTR F508del (cystic fibrosis)",
            "FDA-approved CFTR modulators (genotype-directed)",
        )
    if preset_id == "cftr_g551d" and mismatch:
        add(("ivacaftor",), "CFTR G551D gating mutation", "FDA-approved (ivacaftor for gating mutations)")
    if preset_id == "hbb_e6v" and mismatch:
        add(("hydroxyurea", "voxelotor"), "HBB Glu→Val (sickle cell disease)", "Disease-modifying therapies for sickle cell disease")
    if preset_id == "pah_r408w" and mismatch:
        add(("sapropterin",), "PAH missense (phenylketonuria)", "BH4-responsive PKU consideration after testing")
    if preset_id == "gba_n370s" and mismatch:
        add(("imiglucerase", "eliglustat"), "GBA N370S (Gaucher disease type 1)", "Enzyme replacement / substrate reduction")
    if preset_id in ("smn1_ex7del", "smn1_sma") and deletion:
        add(
            ("nusinersen", "risdiplam", "onasemnogene"),
            "SMN1 loss (spinal muscular atrophy)",
            "FDA-approved SMN-directed SMA therapies",
        )
    if preset_id in ("dmd_frameshift", "dmd_exon45") and deletion:
        add(
            ("eteplirsen", "delandistrogene"),
            "DMD exon deletion / frameshift (Duchenne / Becker spectrum)",
            "Exon-skipping / micro-dystrophin gene therapy (eligibility is exon-specific)",
        )

    # --- Cardiology ---
    if preset_id in ("myh7_r403q", "mybpc3_trunc", "tnnt2_r92q") and (mismatch or frameshift or deletion):
        add(("mavacamten", "metoprolol"), "Sarcomere cardiomyopathy variant (HCM teaching case)", "Myosin inhibitor (obstructive HCM) + beta-blocker supportive care")
    if preset_id == "kcnq1_a341v" and mismatch:
        add(("nadolol", "metoprolol"), "KCNQ1 long-QT syndrome type 1", "Guideline-directed beta blockade for LQT1")
    if preset_id == "scn5a_e1784k" and mismatch:
        add(("mexiletine",), "SCN5A arrhythmia overlap (LQT3 teaching case)", "Late sodium-current block used in LQT3 care pathways")
    if preset_id == "ldlr_w66x" and (mismatch or premature_stop):
        add(("evolocumab", "rosuvastatin"), "LDLR loss-of-function (familial hypercholesterolemia)", "High-intensity LDL lowering + PCSK9 inhibition")
    if preset_id == "pkp2_c796r" and mismatch:
        add(("sotalol", "metoprolol"), "PKP2 arrhythmogenic cardiomyopathy", "Antiarrhythmic / beta-blocker supportive management")
    if preset_id == "lmna_r482w" and mismatch:
        add(("metoprolol",), "LMNA cardiomyopathy", "Rate/rhythm supportive care; device therapy often dominates decision-making")

    # --- Neurology ---
    if preset_id == "scn1a_r377x" and (mismatch or premature_stop):
        add(("fenfluramine", "cannabidiol"), "SCN1A Dravet-spectrum epilepsy", "FDA-approved options for Dravet; avoid sodium-channel blockers")
    if preset_id == "mecp2_r106w" and mismatch:
        add(("trofinetide",), "MECP2 Rett syndrome", "FDA-approved (Rett syndrome)")
    if preset_id == "sod1_a4v" and mismatch:
        add(("tofersen",), "SOD1-ALS", "FDA-approved SOD1 antisense oligonucleotide")
    if preset_id == "gaa_d645e" and mismatch:
        add(("alglucosidase",), "GAA Pompe disease", "Enzyme replacement therapy")
    if preset_id == "htt_cag" and insertion:
        add(("deutetrabenazine",), "HTT CAG expansion (Huntington disease)", "Symptomatic therapy for chorea")
    if preset_id == "app_v717i" and mismatch:
        add(("lecanemab",), "APP familial Alzheimer teaching case", "Anti-amyloid immunotherapy (broader AD indication; genotype informs counseling)")

    # --- Pharmacogenetics ---
    if preset_id == "cyp2c19_star2" and (mismatch or premature_stop):
        add(("prasugrel", "ticagrelor"), "CYP2C19 loss-of-function (*2-class stand-in)", "CPIC: consider alternative to clopidogrel after PCI")
    if preset_id == "tpmt_star3c" and mismatch:
        add(("azathioprine",), "TPMT reduced-activity allele", "CPIC: drastically reduce or avoid usual thiopurine doses")
    if preset_id == "vkorc1_d36y" and mismatch:
        add(("warfarin",), "VKORC1 warfarin-sensitivity stand-in", "CPIC/FDA: lower starting dose considerations")
    if preset_id == "dpyd_star2a" and deletion:
        add(("fluorouracil", "capecitabine"), "DPYD *2A-class deficiency stand-in", "CPIC: avoid or deeply reduce fluoropyrimidines")
    if preset_id == "slco1b1_v174a" and mismatch:
        add(("pravastatin", "rosuvastatin"), "SLCO1B1 V174A (simvastatin myopathy risk)", "CPIC: limit simvastatin dose or choose another statin")
    if preset_id == "hlab_5701" and mismatch:
        add(("dolutegravir",), "HLA-B*57:01 stand-in (abacavir hypersensitivity risk)", "Avoid abacavir; use alternate ART backbone")
    if preset_id == "cyp3a5_star3" and (mismatch or premature_stop):
        add(("tacrolimus",), "CYP3A5 non-expressor (*3-class stand-in)", "CPIC: expressor status changes tacrolimus dose requirements")

    # --- Infectious disease ---
    if preset_id == "hiv_rt_k103n" and mismatch:
        add(("dolutegravir",), "HIV RT K103N (NNRTI resistance)", "Prefer integrase-based ART; avoid efavirenz-class NNRTIs")
    if preset_id == "hiv_rt_m184v" and mismatch:
        add(("dolutegravir",), "HIV RT M184V (NRTI resistance)", "Modern INSTI-based regimens remain cornerstone options")
    if preset_id == "tb_rpob_s531l" and mismatch:
        add(("bedaquiline", "linezolid"), "M. tuberculosis rpoB (rifampin resistance)", "MDR-TB regimen components when rifampin fails")
    if preset_id == "flu_na_h275y" and mismatch:
        add(("zanamivir", "baloxavir"), "Influenza NA H275Y (oseltamivir reduced susceptibility)", "Alternate antivirals when H275Y is present")
    if preset_id == "mrsa_mecA" and insertion:
        add(("vancomycin", "linezolid"), "mecA-positive MRSA", "Anti-MRSA agents (not beta-lactamase–stable penicillins alone)")
    if preset_id == "hcv_ns5a_y93h" and mismatch:
        add(("sofosbuvir_velpatasvir_voxilaprevir",), "HCV NS5A Y93H resistance-associated substitution", "Salvage DAA combination used after NS5A failure")
    if preset_id == "sars2_spike_n501y" and mismatch:
        add(("nirmatrelvir_ritonavir",), "SARS-CoV-2 spike variant teaching case", "Oral antiviral for high-risk COVID-19 (not mutation-specific)")
    if preset_id == "hiv_pr_l90m" and mismatch:
        add(("darunavir",), "HIV protease L90M", "Boosted darunavir often retained; older PI options may fail")

    # --- Reproductive ---
    # Most carrier findings are counseling / partner-testing, not a drug for the carrier.
    if preset_id == "f5_leiden" and mismatch:
        add(("enoxaparin",), "Factor V Leiden (thrombophilia)", "LMWH considered in selected high-risk pregnancy / VTE settings")
    if preset_id == "mthfr_c677t" and mismatch:
        add(("folic_acid",), "MTHFR common variant (limited actionability)", "Standard preconception folic acid — not a targeted genotype drug")
    # cftr_carrier, hbb_carrier, smn1_carrier, hexa_carrier, fmr1_cgg, gjb2: counseling-focused

    # --- Immunology ---
    if preset_id == "il2rg_r226c" and mismatch:
        add(("immune_globulin",), "IL2RG X-SCID", "Supportive Ig while arranging definitive cellular / gene therapy")
    if preset_id == "ada_g216r" and mismatch:
        add(("elapegademase", "immune_globulin"), "ADA-SCID", "Enzyme replacement bridge to transplant / gene therapy")
    if preset_id == "btk_r28c" and mismatch:
        add(("immune_globulin",), "BTK X-linked agammaglobulinemia", "Lifelong immunoglobulin replacement")
    if preset_id == "was_trunc" and (deletion or frameshift):
        add(("immune_globulin",), "WAS truncating variant (Wiskott–Aldrich)", "Ig replacement / infection prophylaxis pending definitive therapy")
    if preset_id == "foxp3_r397w" and mismatch:
        add(("sirolimus", "immune_globulin"), "FOXP3 IPEX syndrome", "Immune modulation bridge to hematopoietic transplant")
    if preset_id == "stat3_r382w" and mismatch:
        add(("immune_globulin",), "STAT3 hyper-IgE syndrome", "Supportive Ig / antimicrobial prophylaxis")
    if preset_id == "hla_b_mismatch" and mismatch:
        add(("tacrolimus", "mycophenolate"), "HLA mismatch (transplant teaching case)", "Calcineurin inhibitor + antimetabolite immunosuppression")
    if preset_id == "ciita_del" and deletion:
        add(("immune_globulin",), "CIITA MHC class II deficiency", "Supportive care / transplant evaluation")

    # De-duplicate by molecule name while preserving order
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for card in cards:
        if card["name"] in seen:
            continue
        seen.add(card["name"])
        unique.append(card)
    return unique


# ------------------------------------------------------------------------------------- #
# have examples of indications for each of the teaching examples
# ------------------------------------------------------------------------------------- #

PRESET_INDICATIONS: dict[str, dict[str, str]] = {
    # Cancer
    "egfr_exon19": {
        "label": "Non-small cell lung cancer",
        "category": "Cancer",
        "detail": "EGFR exon 19 deletions are a common driver in lung adenocarcinoma.",
    },
    "brca1": {
        "label": "Breast / ovarian cancer (hereditary)",
        "category": "Cancer",
        "detail": "BRCA1 loss-of-function raises breast, ovarian, prostate, and pancreatic cancer risk.",
    },
    "btk_c481": {
        "label": "Chronic lymphocytic leukemia",
        "category": "Cancer",
        "detail": "BTK C481S emerges as resistance during covalent BTK-inhibitor therapy in CLL/SLL.",
    },
    "kras_g12c": {
        "label": "Non-small cell lung cancer",
        "category": "Cancer",
        "detail": "KRAS G12C also appears in colorectal and pancreatic cancer.",
    },
    "braf_v600e": {
        "label": "Melanoma / colorectal cancer",
        "category": "Cancer",
        "detail": "BRAF V600E drives melanoma, colorectal cancer, thyroid cancer, and some NSCLC.",
    },
    "esr1_y537s": {
        "label": "ER-positive metastatic breast cancer",
        "category": "Cancer",
        "detail": "ESR1 mutations arise as endocrine-therapy resistance in ER+/HER2− disease.",
    },
    "ret_m918t": {
        "label": "Medullary thyroid cancer",
        "category": "Cancer",
        "detail": "RET M918T is the hallmark somatic/germline driver in MEN2B-associated MTC.",
    },
    "ntrk_fusion": {
        "label": "NTRK fusion–positive solid tumors",
        "category": "Cancer",
        "detail": "Tumor-agnostic: the fusion matters more than the organ of origin.",
    },
    # Rare Mendelian
    "cftr_f508del": {
        "label": "Cystic fibrosis",
        "category": "Rare Mendelian disease",
        "detail": "F508del is the most common CF-causing allele worldwide.",
    },
    "cftr_g551d": {
        "label": "Cystic fibrosis (gating mutation)",
        "category": "Rare Mendelian disease",
        "detail": "G551D-class alleles let CFTR reach the surface but not open properly.",
    },
    "hbb_e6v": {
        "label": "Sickle cell disease",
        "category": "Rare Mendelian disease",
        "detail": "Glu→Val in β-globin causes hemoglobin to polymerize under low oxygen.",
    },
    "pah_r408w": {
        "label": "Phenylketonuria (PKU)",
        "category": "Rare Mendelian disease",
        "detail": "PAH deficiency causes phenylalanine buildup and neurologic injury if untreated.",
    },
    "gba_n370s": {
        "label": "Gaucher disease type 1",
        "category": "Rare Mendelian disease",
        "detail": "Glucocerebrosidase deficiency; also a Parkinson disease risk factor.",
    },
    "hexa_1278ins": {
        "label": "Tay–Sachs disease",
        "category": "Rare Mendelian disease",
        "detail": "Hexosaminidase A loss causes GM2 ganglioside storage in neurons.",
    },
    "smn1_ex7del": {
        "label": "Spinal muscular atrophy",
        "category": "Rare Mendelian disease",
        "detail": "Homozygous SMN1 exon-7 loss is the usual SMA genotype.",
    },
    "dmd_frameshift": {
        "label": "Duchenne muscular dystrophy",
        "category": "Rare Mendelian disease",
        "detail": "Out-of-frame dystrophin deletions typically cause the severe Duchenne phenotype.",
    },
    # Cardiology
    "myh7_r403q": {
        "label": "Hypertrophic cardiomyopathy",
        "category": "Cardiology",
        "detail": "MYH7 sarcomere variants are a leading inherited cause of HCM.",
    },
    "mybpc3_trunc": {
        "label": "Hypertrophic cardiomyopathy",
        "category": "Cardiology",
        "detail": "Truncating MYBPC3 alleles are among the most common HCM genotypes.",
    },
    "kcnq1_a341v": {
        "label": "Long QT syndrome type 1",
        "category": "Cardiology",
        "detail": "KCNQ1 loss slows cardiac repolarization and raises arrhythmia risk.",
    },
    "scn5a_e1784k": {
        "label": "Long QT type 3 / Brugada overlap",
        "category": "Cardiology",
        "detail": "SCN5A overlap syndromes can present with both LQT3 and Brugada features.",
    },
    "ldlr_w66x": {
        "label": "Familial hypercholesterolemia",
        "category": "Cardiology",
        "detail": "LDL receptor loss causes lifelong elevated LDL and early coronary disease.",
    },
    "pkp2_c796r": {
        "label": "Arrhythmogenic cardiomyopathy",
        "category": "Cardiology",
        "detail": "PKP2 desmosome variants are the most common ARVC/ACM cause.",
    },
    "tnnt2_r92q": {
        "label": "Hypertrophic / restrictive cardiomyopathy",
        "category": "Cardiology",
        "detail": "TNNT2 variants can cause modest hypertrophy with high arrhythmia risk.",
    },
    "lmna_r482w": {
        "label": "Laminopathy (cardiomyopathy / lipodystrophy)",
        "category": "Cardiology",
        "detail": "LMNA disease often combines conduction block with dilated cardiomyopathy.",
    },
    # Neurology
    "scn1a_r377x": {
        "label": "Dravet syndrome (epilepsy)",
        "category": "Neurology",
        "detail": "SCN1A loss-of-function causes severe early-onset epileptic encephalopathy.",
    },
    "mecp2_r106w": {
        "label": "Rett syndrome",
        "category": "Neurology",
        "detail": "MECP2 variants cause developmental regression, mostly in girls.",
    },
    "sod1_a4v": {
        "label": "Familial ALS",
        "category": "Neurology",
        "detail": "SOD1 A4V is associated with rapidly progressive familial ALS.",
    },
    "smn1_sma": {
        "label": "Spinal muscular atrophy",
        "category": "Neurology",
        "detail": "Motor-neuron loss from SMN protein deficiency; SMN2 copy number modifies severity.",
    },
    "gaa_d645e": {
        "label": "Pompe disease",
        "category": "Neurology",
        "detail": "Acid α-glucosidase deficiency causes glycogen storage myopathy and cardiomyopathy.",
    },
    "htt_cag": {
        "label": "Huntington disease",
        "category": "Neurology",
        "detail": "Expanded CAG repeats produce a toxic polyglutamine huntingtin protein.",
    },
    "app_v717i": {
        "label": "Early-onset familial Alzheimer disease",
        "category": "Neurology",
        "detail": "APP variants shift amyloid processing toward aggregation-prone peptides.",
    },
    "dmd_exon45": {
        "label": "Becker muscular dystrophy (in-frame)",
        "category": "Neurology",
        "detail": "In-frame dystrophin deletions produce a shortened but partly working protein.",
    },
    # Pharmacogenetics
    "cyp2c19_star2": {
        "label": "Clopidogrel poor response",
        "category": "Pharmacogenetics",
        "detail": "Reduced activation of clopidogrel raises stent thrombosis risk after PCI.",
    },
    "cyp2d6_star4": {
        "label": "Altered metabolism of CYP2D6 drugs",
        "category": "Pharmacogenetics",
        "detail": "Affects codeine, tamoxifen, many antidepressants and antipsychotics.",
    },
    "tpmt_star3c": {
        "label": "Thiopurine toxicity risk",
        "category": "Pharmacogenetics",
        "detail": "Low TPMT activity can cause life-threatening myelosuppression.",
    },
    "vkorc1_d36y": {
        "label": "Warfarin dose sensitivity",
        "category": "Pharmacogenetics",
        "detail": "VKORC1 genotype (with CYP2C9) explains much of warfarin dose variability.",
    },
    "dpyd_star2a": {
        "label": "Fluoropyrimidine toxicity risk",
        "category": "Pharmacogenetics",
        "detail": "DPD deficiency causes severe 5-FU / capecitabine toxicity at standard doses.",
    },
    "slco1b1_v174a": {
        "label": "Statin-associated myopathy risk",
        "category": "Pharmacogenetics",
        "detail": "Reduced hepatic uptake raises simvastatin muscle-injury risk.",
    },
    "hlab_5701": {
        "label": "Abacavir hypersensitivity risk",
        "category": "Pharmacogenetics",
        "detail": "HLA-B*57:01 carriers can have a severe systemic reaction to abacavir.",
    },
    "cyp3a5_star3": {
        "label": "Tacrolimus dose requirement",
        "category": "Pharmacogenetics",
        "detail": "Expressor status changes the tacrolimus dose needed after transplant.",
    },
    # Infectious disease
    "hiv_rt_k103n": {
        "label": "HIV — NNRTI resistance",
        "category": "Infectious disease",
        "detail": "Confers high-level resistance to efavirenz and nevirapine.",
    },
    "hiv_rt_m184v": {
        "label": "HIV — NRTI resistance",
        "category": "Infectious disease",
        "detail": "Selected by lamivudine/emtricitabine; also reduces viral fitness.",
    },
    "tb_rpob_s531l": {
        "label": "Rifampin-resistant / MDR tuberculosis",
        "category": "Infectious disease",
        "detail": "rpoB changes are the main molecular marker for rifampin resistance.",
    },
    "flu_na_h275y": {
        "label": "Oseltamivir-resistant influenza",
        "category": "Infectious disease",
        "detail": "H275Y reduces oseltamivir binding in H1N1 neuraminidase.",
    },
    "mrsa_mecA": {
        "label": "Methicillin-resistant S. aureus (MRSA)",
        "category": "Infectious disease",
        "detail": "mecA encodes PBP2a, which beta-lactams cannot inhibit.",
    },
    "hcv_ns5a_y93h": {
        "label": "Hepatitis C — NS5A inhibitor resistance",
        "category": "Infectious disease",
        "detail": "Y93H is a resistance-associated substitution affecting DAA choice.",
    },
    "sars2_spike_n501y": {
        "label": "COVID-19 variant surveillance",
        "category": "Infectious disease",
        "detail": "N501Y increased receptor binding in several variants of concern.",
    },
    "hiv_pr_l90m": {
        "label": "HIV — protease inhibitor resistance",
        "category": "Infectious disease",
        "detail": "Contributes to cross-resistance across several protease inhibitors.",
    },
    # Reproductive / prenatal
    "cftr_carrier": {
        "label": "Cystic fibrosis carrier status",
        "category": "Reproductive / prenatal",
        "detail": "Carriers are healthy; risk applies when both partners carry a variant.",
    },
    "hbb_carrier": {
        "label": "Sickle cell trait / carrier status",
        "category": "Reproductive / prenatal",
        "detail": "Two carrier parents have a 25% chance of an affected child per pregnancy.",
    },
    "smn1_carrier": {
        "label": "SMA carrier status",
        "category": "Reproductive / prenatal",
        "detail": "SMN1 carrier screening is offered routinely before or during pregnancy.",
    },
    "hexa_carrier": {
        "label": "Tay–Sachs carrier status",
        "category": "Reproductive / prenatal",
        "detail": "Historically emphasized in Ashkenazi Jewish screening panels.",
    },
    "fmr1_cgg": {
        "label": "Fragile X syndrome",
        "category": "Reproductive / prenatal",
        "detail": "Premutation carriers can expand to a full mutation in the next generation.",
    },
    "f5_leiden": {
        "label": "Inherited thrombophilia (VTE risk)",
        "category": "Reproductive / prenatal",
        "detail": "Raises clot risk with pregnancy, estrogen therapy, and immobility.",
    },
    "gjb2_35delg": {
        "label": "Nonsyndromic hearing loss",
        "category": "Reproductive / prenatal",
        "detail": "GJB2 (connexin 26) is the most common recessive deafness gene.",
    },
    "mthfr_c677t": {
        "label": "Common metabolic variant (low actionability)",
        "category": "Reproductive / prenatal",
        "detail": "Very common polymorphism; routine testing is not generally recommended.",
    },
    # Immunology
    "il2rg_r226c": {
        "label": "X-linked severe combined immunodeficiency",
        "category": "Immunology",
        "detail": "Common γ-chain loss blocks T- and NK-cell development — a pediatric emergency.",
    },
    "ada_g216r": {
        "label": "ADA-deficient SCID",
        "category": "Immunology",
        "detail": "Toxic metabolites destroy developing lymphocytes.",
    },
    "btk_r28c": {
        "label": "X-linked agammaglobulinemia",
        "category": "Immunology",
        "detail": "BTK loss halts B-cell maturation, leaving patients without antibodies.",
    },
    "was_trunc": {
        "label": "Wiskott–Aldrich syndrome",
        "category": "Immunology",
        "detail": "Eczema, small platelets with bleeding, and immune deficiency.",
    },
    "foxp3_r397w": {
        "label": "IPEX syndrome",
        "category": "Immunology",
        "detail": "Regulatory T-cell failure causes early severe multi-organ autoimmunity.",
    },
    "stat3_r382w": {
        "label": "Hyper-IgE (Job) syndrome",
        "category": "Immunology",
        "detail": "Recurrent skin/lung infections with very high IgE and connective-tissue findings.",
    },
    "hla_b_mismatch": {
        "label": "Transplant rejection / GVHD risk",
        "category": "Immunology",
        "detail": "Donor–recipient HLA mismatch drives alloimmune complications.",
    },
    "ciita_del": {
        "label": "MHC class II deficiency",
        "category": "Immunology",
        "detail": "Bare lymphocyte syndrome type II — CD4 T cells cannot be activated.",
    },
}

INDICATION_SLUG_OVERRIDES = {
    "egfr_exon19": "lung-cancer",
    "brca1": "breast-cancer",
    "btk_c481": "chronic-lymphocytic-leukemia",
    "kras_g12c": "lung-cancer",
    "braf_v600e": "melanoma",
    "esr1_y537s": "breast-cancer",
    "ret_m918t": "medullary-thyroid-cancer",
    "ntrk_fusion": "ntrk-fusion-solid-tumor",
}


def indication_for(preset_id: str | None) -> dict[str, str] | None:
    """Potential disease context for a teaching preset (None for custom references)."""
    if not preset_id:
        return None
    indication = PRESET_INDICATIONS.get(preset_id)
    if not indication:
        return None
    slug = INDICATION_SLUG_OVERRIDES.get(preset_id)
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "-", indication["label"].lower()).strip("-")
    return {**indication, "slug": slug}


def analyze_pair(
    ref_header: str,
    ref_seq: str,
    sample_header: str,
    sample_seq: str,
    preset_id: str | None = None,
) -> dict[str, Any]:
    events = find_local_indels(ref_seq, sample_seq)
    ref_protein = translate(ref_seq)
    sample_protein = translate(sample_seq)
    length_delta = len(sample_seq) - len(ref_seq)

    return {
        "reference": {
            "header": ref_header,
            "sequence": ref_seq,
            "length": len(ref_seq),
            "protein": ref_protein,
            "protein_length": len(ref_protein.rstrip("*")),
        },
        "sample": {
            "header": sample_header,
            "sequence": sample_seq,
            "length": len(sample_seq),
            "protein": sample_protein,
            "protein_length": len(sample_protein.rstrip("*")),
        },
        "length_delta": length_delta,
        "events": events,
        "spans": build_sequence_spans(ref_seq, sample_seq, events),
        "protein_alignment": protein_alignment(ref_protein, sample_protein),
        "in_frame_length_change": length_delta % 3 == 0,
        "notes": interpret_impact(events, length_delta, ref_protein, sample_protein, preset_id),
        "notes_summary": summarize_notes_for_layperson(
            events, length_delta, ref_protein, sample_protein, preset_id
        ),
        "treatments": suggest_treatments(events, length_delta, ref_protein, sample_protein, preset_id),
        "indication": indication_for(preset_id),
        "preset_id": preset_id,
    }


def load_preset_reference(preset_id: str) -> tuple[str, str, str]:
    if preset_id not in REFERENCE_PRESETS:
        raise ValueError(f"Unknown reference preset: {preset_id}")
    preset = REFERENCE_PRESETS[preset_id]
    header, sequence = read_fasta(DATA_DIR / preset["file"])
    return header, sequence, preset_id


def load_preset_sample(preset_id: str) -> tuple[str, str]:
    if preset_id not in REFERENCE_PRESETS:
        raise ValueError(f"Unknown sample preset: {preset_id}")
    preset = REFERENCE_PRESETS[preset_id]
    return read_fasta(DATA_DIR / preset["sample_file"])


def list_presets() -> list[dict[str, Any]]:
    teaching = [
        {
            "id": p["id"],
            "label": p["label"],
            "context": p["context"],
            "research_areas": list(p["research_areas"]),
        }
        for p in REFERENCE_PRESETS.values()
    ]
    return [
        {
            "id": CUSTOM_REFERENCE["id"],
            "label": CUSTOM_REFERENCE["label"],
            "context": CUSTOM_REFERENCE["context"],
            "research_areas": CUSTOM_REFERENCE["research_areas"],
        },
        *teaching,
    ]
