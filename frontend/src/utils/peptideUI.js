/**
 * Peptide UI (Unidades Internacionais / Insulin Units) helper.
 *
 * Standard assumption:
 *   - Reconstitution: 3 ml bacteriostatic water
 *   - Insulin syringe: 1 ml = 100 UI
 *
 * Formula: UI = (dose_mcg * 3) / vial_total_mcg * 100
 *
 * Edit VIAL_SIZES_MG below to match the vials you sell.
 */

// Default vial sizes per peptide (mg per vial)
export const VIAL_SIZES_MG = {
  'AOD-9604': 5,
  'CJC-1295': 5,
  'CJC-1295 DAC': 5,
  'Ipamorelin': 5,
  'BPC-157': 5,
  'TB-500': 10,
  'TB500': 10,
  'GHK-Cu': 100,        // mostly used topical (not converted to UI)
  'Tesamorelin': 10,
  'Sermorelin': 10,
  'Semaglutide': 5,
  'Tirzepatide': 10,
  'Retatrutide': 10,
  'Selank': 5,
  'Semax': 5,
  'PT-141': 10,
  'MOTS-c': 10,
  'NAD+': 500,
  'NAD': 500,
  '5-Amino-1MQ': 50,
  'Kisspeptin-10': 5,
  'Kisspeptin': 5,
  'Oxytocin': 5,
  'HGH Fragment 176-191': 10,
  'IGF-1 LR3': 1,
  'KPV': 10,
  'Thymosin Alpha': 5,
  'DSIP': 5,
  'AHK-Cu': 50,
  'SLU-PP-332': 0,      // tablet — no UI
  'Glutathione': 0,     // IV/oral — no UI
};

// Compounds that are NOT injectable peptides (no UI conversion)
const NON_PEPTIDES = new Set([
  'L-Carnitine', 'L-Carnitine Tartrate', 'Berberine', 'MCT Oil', 'DIM',
  'L-Theanine', '5-HTP', 'Yohimbine', 'Yohimbine HCl', 'Ashwagandha',
  'Dandelion Root Extract', 'Glutamine', 'Creatine', 'Vitamin D3',
  'Magnesium', 'Zinc', 'Fish Oil', 'Omega-3', 'Curcumin', 'Resveratrol',
  'Melatonin', 'CoQ10', 'NAC', 'Glycine',
]);

/**
 * Try to extract a numeric dose in mcg from a free-text dose string like:
 *   "300 mcg", "100 mcg PM", "250-300 mcg", "0.5 mg", "1 g"
 * Returns null if not parseable as mcg.
 */
function parseDoseMcg(dose) {
  if (!dose) return null;
  const s = String(dose).toLowerCase();
  // pick the first numeric token (or range start)
  const m = s.match(/(\d+(?:[.,]\d+)?)/);
  if (!m) return null;
  const num = parseFloat(m[1].replace(',', '.'));
  if (isNaN(num)) return null;

  if (s.includes('mcg')) return num;
  if (s.includes('mg')) return num * 1000;
  if (s.match(/\b\d+\s*g\b/) || s.match(/\bg\b/)) return null; // gram = supplement, skip
  return null;
}

/**
 * Compute UI for a given peptide name + dose string.
 * Returns {ui, vialMg} or null if not applicable.
 */
export function calculateUI(compoundName, doseStr, diluentMl = 3) {
  if (!compoundName) return null;
  // Strip parentheticals and trim
  const baseName = compoundName.replace(/\(.*?\)/g, '').trim();

  // Skip explicitly non-peptide compounds
  if (NON_PEPTIDES.has(baseName)) return null;

  // Skip topical, oral, tablet doses
  const d = (doseStr || '').toLowerCase();
  if (d.includes('topical') || d.includes('oral') || d.includes('tablet') || d.includes('capsule') || d.includes('tbsp') || d.includes('tsp')) return null;

  // Find matching vial — exact, then by prefix containing
  let vialMg = VIAL_SIZES_MG[baseName];
  if (vialMg === undefined) {
    const key = Object.keys(VIAL_SIZES_MG).find(k => baseName.toLowerCase().includes(k.toLowerCase()));
    vialMg = key ? VIAL_SIZES_MG[key] : undefined;
  }
  if (!vialMg || vialMg === 0) return null;

  const doseMcg = parseDoseMcg(doseStr);
  if (!doseMcg) return null;

  const vialMcg = vialMg * 1000;
  const ui = (doseMcg * diluentMl) / vialMcg * 100;
  // round to 1 decimal, drop .0 if whole
  const rounded = Math.round(ui * 10) / 10;
  return {
    ui: rounded,
    vialMg: vialMg,
    diluentMl: diluentMl,
  };
}
