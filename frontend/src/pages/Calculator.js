import React, { useState } from 'react';
import { Calculator as CalcIcon, Info } from 'lucide-react';

const Calculator = () => {
  const [vialMg, setVialMg] = useState('');
  const [waterMl, setWaterMl] = useState('');
  const [desiredDoseMg, setDesiredDoseMg] = useState('');
  const [result, setResult] = useState(null);

  const calculate = (e) => {
    e.preventDefault();

    const vialMgNum = parseFloat(vialMg);
    const waterMlNum = parseFloat(waterMl);
    const desiredDoseMgNum = parseFloat(desiredDoseMg);

    if (!vialMgNum || !waterMlNum || !desiredDoseMgNum) {
      alert('Please fill in all fields');
      return;
    }

    // Calculate concentration (mg/ml)
    const concentration = vialMgNum / waterMlNum;

    // Calculate ml needed for desired dose
    const mlNeeded = desiredDoseMgNum / concentration;

    // Calculate total doses
    const totalDoses = vialMgNum / desiredDoseMgNum;

    setResult({
      concentration: concentration.toFixed(2),
      mlNeeded: mlNeeded.toFixed(3),
      totalDoses: Math.floor(totalDoses),
      syringeUnits: (mlNeeded * 100).toFixed(1)
    });
  };

  const handleReset = () => {
    setVialMg('');
    setWaterMl('');
    setDesiredDoseMg('');
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gray-50" data-testid="calculator-page">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <CalcIcon className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4" data-testid="calculator-title">
            Dosage Calculator
          </h1>
          <p className="text-lg text-gray-600">
            Calculate concentration, dosage, and total doses for your research compounds
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Calculator Form */}
          <div className="bg-white rounded-xl shadow-sm p-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Enter Your Values</h2>
            <form onSubmit={calculate} className="space-y-6">
              {/* Vial Amount */}
              <div>
                <label htmlFor="vialMg" className="block text-sm font-medium text-gray-700 mb-2">
                  Amount in Vial (mg)
                </label>
                <input
                  type="number"
                  id="vialMg"
                  value={vialMg}
                  onChange={(e) => setVialMg(e.target.value)}
                  data-testid="vial-mg-input"
                  placeholder="e.g., 10"
                  step="any"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
                <p className="mt-1 text-xs text-gray-500">Total mg of compound in your vial</p>
              </div>

              {/* Water Amount */}
              <div>
                <label htmlFor="waterMl" className="block text-sm font-medium text-gray-700 mb-2">
                  Bacteriostatic Water (ml)
                </label>
                <input
                  type="number"
                  id="waterMl"
                  value={waterMl}
                  onChange={(e) => setWaterMl(e.target.value)}
                  data-testid="water-ml-input"
                  placeholder="e.g., 2"
                  step="any"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
                <p className="mt-1 text-xs text-gray-500">ml of water to reconstitute</p>
              </div>

              {/* Desired Dose */}
              <div>
                <label htmlFor="desiredDoseMg" className="block text-sm font-medium text-gray-700 mb-2">
                  Desired Dose (mg)
                </label>
                <input
                  type="number"
                  id="desiredDoseMg"
                  value={desiredDoseMg}
                  onChange={(e) => setDesiredDoseMg(e.target.value)}
                  data-testid="desired-dose-input"
                  placeholder="e.g., 0.5"
                  step="any"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
                <p className="mt-1 text-xs text-gray-500">mg per dose</p>
              </div>

              {/* Buttons */}
              <div className="flex space-x-4">
                <button
                  type="submit"
                  data-testid="calculate-button"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors"
                >
                  Calculate
                </button>
                <button
                  type="button"
                  onClick={handleReset}
                  data-testid="reset-button"
                  className="px-6 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-3 rounded-lg transition-colors"
                >
                  Reset
                </button>
              </div>
            </form>
          </div>

          {/* Results */}
          <div className="space-y-6">
            {result ? (
              <div className="bg-white rounded-xl shadow-sm p-8" data-testid="results-panel">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Results</h2>
                <div className="space-y-4">
                  <div className="bg-blue-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Concentration</p>
                    <p className="text-2xl font-bold text-blue-600" data-testid="concentration-result">
                      {result.concentration} mg/ml
                    </p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Volume Needed per Dose</p>
                    <p className="text-2xl font-bold text-green-600" data-testid="ml-needed-result">
                      {result.mlNeeded} ml
                    </p>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Total Doses</p>
                    <p className="text-2xl font-bold text-purple-600" data-testid="total-doses-result">
                      {result.totalDoses} doses
                    </p>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-4" data-testid="syringe-units-result">
                    <p className="text-sm text-gray-600 mb-1">Insulin Syringe (100 UI)</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {result.syringeUnits} UI
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Mark on a 100 UI syringe</p>
                  </div>
                  {/* Syringe Visual */}
                  <div className="bg-white border border-gray-200 rounded-lg p-5" data-testid="syringe-visual">
                    <p className="text-sm font-medium text-gray-700 mb-4">Insulin Syringe 100 UI - Draw to <span className="text-red-600 font-bold">{result.syringeUnits} UI</span></p>
                    <div className="flex justify-center">
                      <svg viewBox="0 0 380 60" className="w-full max-w-md h-16">
                        {/* Plunger handle */}
                        <rect x="2" y="18" width="6" height="24" rx="2" fill="#d1d5db" stroke="#9ca3af" strokeWidth="0.5" />
                        <rect x="8" y="22" width="4" height="16" rx="1" fill="#e5e7eb" stroke="#d1d5db" strokeWidth="0.5" />
                        
                        {/* Plunger rod */}
                        <rect x="12" y="27" width="40" height="6" rx="1" fill="#e5e7eb" stroke="#d1d5db" strokeWidth="0.5" />
                        
                        {/* Barrel bottom cap */}
                        <rect x="50" y="20" width="6" height="20" rx="2" fill="#e5e7eb" stroke="#d1d5db" strokeWidth="0.5" />
                        
                        {/* Barrel body */}
                        <rect x="56" y="18" width="260" height="24" rx="3" fill="white" stroke="#bbb" strokeWidth="1" />
                        
                        {/* Liquid fill - from left */}
                        {(() => {
                          const units = Math.min(parseFloat(result.syringeUnits), 100);
                          const fillWidth = (units / 100) * 258;
                          return (
                            <rect x="57" y="19" width={fillWidth} height="22" rx="2" fill="rgba(59, 130, 246, 0.2)" />
                          );
                        })()}
                        
                        {/* Scale markings - 100 at left, 0 at right */}
                        {[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100].map((mark) => {
                          const x = 56 + ((100 - mark) / 100) * 260;
                          return (
                            <g key={mark}>
                              <line x1={x} y1="18" x2={x} y2="26" stroke="#374151" strokeWidth="0.8" />
                              <line x1={x} y1="34" x2={x} y2="42" stroke="#374151" strokeWidth="0.8" />
                              <text x={x} y="52" fontSize="7" fill="#374151" fontWeight="bold" textAnchor="middle">{mark}</text>
                            </g>
                          );
                        })}
                        
                        {/* Minor ticks every 5 */}
                        {[5, 15, 25, 35, 45, 55, 65, 75, 85, 95].map((mark) => {
                          const x = 56 + ((100 - mark) / 100) * 260;
                          return (
                            <g key={mark}>
                              <line x1={x} y1="18" x2={x} y2="23" stroke="#9ca3af" strokeWidth="0.5" />
                              <line x1={x} y1="37" x2={x} y2="42" stroke="#9ca3af" strokeWidth="0.5" />
                            </g>
                          );
                        })}
                        
                        {/* Minor ticks every 2 */}
                        {Array.from({length: 50}, (_, i) => i * 2).filter(m => m % 5 !== 0).map((mark) => {
                          const x = 56 + ((100 - mark) / 100) * 260;
                          return (
                            <line key={mark} x1={x} y1="18" x2={x} y2="21" stroke="#d1d5db" strokeWidth="0.4" />
                          );
                        })}
                        
                        {/* Dose indicator - RED line */}
                        {(() => {
                          const units = Math.min(parseFloat(result.syringeUnits), 100);
                          const x = 56 + ((100 - units) / 100) * 260;
                          return (
                            <g>
                              <line x1={x} y1="14" x2={x} y2="46" stroke="#ef4444" strokeWidth="2" />
                              <polygon points={`${x - 4},14 ${x + 4},14 ${x},18`} fill="#ef4444" />
                            </g>
                          );
                        })()}
                        
                        {/* Barrel top cap */}
                        <rect x="316" y="22" width="8" height="16" rx="2" fill="#e5e7eb" stroke="#d1d5db" strokeWidth="0.5" />
                        
                        {/* Needle hub */}
                        <rect x="324" y="25" width="14" height="10" rx="2" fill="#333" />
                        
                        {/* Needle */}
                        <line x1="338" y1="30" x2="378" y2="30" stroke="#999" strokeWidth="1" />
                        <polygon points="378,29 378,31 380,30" fill="#999" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm p-8 text-center" data-testid="empty-results">
                <CalcIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">Enter values and click Calculate to see results</p>
              </div>
            )}

            {/* Info Panel */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <div className="flex items-start space-x-3">
                <Info className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-blue-900 mb-2">How to Use</h3>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>1. Enter the total mg in your vial</li>
                    <li>2. Enter ml of water for reconstitution</li>
                    <li>3. Enter your desired dose in mg</li>
                    <li>4. Get concentration, volume per dose, and total doses</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Example */}
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="font-semibold text-gray-900 mb-3">Example</h3>
              <p className="text-sm text-gray-600 mb-2">
                10mg vial + 2ml water = 5mg/ml concentration
              </p>
              <p className="text-sm text-gray-600">
                For 0.5mg dose: inject 0.1ml = <strong>10 UI</strong> on a 100 UI syringe (20 total doses)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Calculator;