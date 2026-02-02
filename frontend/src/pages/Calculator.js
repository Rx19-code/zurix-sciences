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
      totalDoses: Math.floor(totalDoses)
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
                For 0.5mg dose: inject 0.1ml (20 total doses)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Calculator;