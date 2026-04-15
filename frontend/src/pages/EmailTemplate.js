import React, { useState, useRef } from 'react';
import { Copy, Check, Mail } from 'lucide-react';

var ADMIN_PASSWORD = '';

function generateHTML(clientName, responseText) {
  var lines = responseText.split('\n').map(function(line) {
    return '<p style="margin:0 0 12px;font-size:15px;color:#374151;line-height:1.7;">' + line + '</p>';
  }).join('\n          ');

  return '<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0;padding:0;background-color:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:32px 16px;"><tr><td align="center"><table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);"><tr><td style="background:linear-gradient(135deg,#1e40af 0%,#2563eb 100%);padding:32px 40px;text-align:center;"><h1 style="margin:0;font-size:28px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">Zurix Sciences</h1><p style="margin:4px 0 0;font-size:12px;color:#93c5fd;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">Premium Research Compounds</p></td></tr><tr><td style="padding:40px;"><p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">Dear <span style="color:#1e40af;font-weight:600;">' + clientName + '</span>,</p><p style="margin:0 0 20px;font-size:15px;color:#374151;line-height:1.7;">Thank you for reaching out to Zurix Sciences. We appreciate your interest in our research-grade peptide products.</p><div style="background-color:#f8fafc;border-left:4px solid #2563eb;border-radius:0 8px 8px 0;padding:20px 24px;margin:24px 0;">' + lines + '</div><p style="margin:24px 0 20px;font-size:15px;color:#374151;line-height:1.7;">Should you have any further questions, please do not hesitate to contact us. We are available Monday through Friday, 9:00 - 18:00 (CET).</p><p style="margin:0 0 8px;font-size:15px;color:#374151;line-height:1.7;">Kind regards,</p></td></tr><tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #e5e7eb;margin:0;"/></td></tr><tr><td style="padding:28px 40px;"><p style="margin:0 0 2px;font-size:16px;font-weight:700;color:#1e3a5f;">Zurix Sciences</p><p style="margin:0 0 12px;font-size:12px;color:#6b7280;text-transform:uppercase;letter-spacing:0.5px;">Research Division</p><p style="margin:0 0 4px;font-size:13px;color:#374151;">&#9993; RxpeptidesHK@proton.me</p><p style="margin:0 0 4px;font-size:13px;color:#374151;">&#9830; Threema ID: <strong>2D9DAD9R</strong></p><p style="margin:0 0 4px;font-size:13px;color:#374151;">&#9906; Aeschenvorstadt 71, 4051 Basel, Switzerland</p><p style="margin:0;font-size:13px;"><a href="https://zurixsciences.com" style="color:#2563eb;text-decoration:none;font-weight:600;">zurixsciences.com</a></p></td></tr><tr><td style="background-color:#f8fafc;padding:20px 40px;text-align:center;border-top:1px solid #e5e7eb;"><p style="margin:0 0 4px;font-size:11px;color:#9ca3af;">This email and any attachments are confidential and intended solely for the addressee.</p><p style="margin:0;font-size:11px;color:#9ca3af;">All products are sold strictly for research purposes only. Not for human consumption.</p></td></tr></table></td></tr></table></body></html>';
}

export default function EmailTemplate() {
  var [password, setPassword] = useState('');
  var [authenticated, setAuthenticated] = useState(false);
  var [clientName, setClientName] = useState('');
  var [responseText, setResponseText] = useState('');
  var [copied, setCopied] = useState(false);
  var [showPreview, setShowPreview] = useState(false);
  var iframeRef = useRef(null);

  function handleAuth(e) {
    e.preventDefault();
    if (password === 'Rx050217!') {
      setAuthenticated(true);
    }
  }

  function handleGenerate() {
    if (!clientName.trim() || !responseText.trim()) return;
    setShowPreview(true);
    setTimeout(function() {
      if (iframeRef.current) {
        var doc = iframeRef.current.contentDocument;
        doc.open();
        doc.write(generateHTML(clientName, responseText));
        doc.close();
      }
    }, 100);
  }

  function handleCopy() {
    var html = generateHTML(clientName, responseText);
    navigator.clipboard.writeText(html).then(function() {
      setCopied(true);
      setTimeout(function() { setCopied(false); }, 2000);
    });
  }

  if (!authenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="bg-white rounded-xl shadow-sm border p-8 w-full max-w-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-4 text-center">Admin Access</h2>
          <form onSubmit={handleAuth}>
            <input
              type="password"
              value={password}
              onChange={function(e) { setPassword(e.target.value); }}
              placeholder="Password"
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-blue-500"
            />
            <button type="submit" className="w-full bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700">
              Enter
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4" data-testid="email-template-page">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Mail className="w-6 h-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Email Template Generator</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Form */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Client Name</label>
                <input
                  type="text"
                  value={clientName}
                  onChange={function(e) { setClientName(e.target.value); }}
                  placeholder="John Smith"
                  data-testid="client-name-input"
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Your Response</label>
                <textarea
                  value={responseText}
                  onChange={function(e) { setResponseText(e.target.value); }}
                  placeholder="Type your response to the client here..."
                  rows={10}
                  data-testid="response-textarea"
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleGenerate}
                  disabled={!clientName.trim() || !responseText.trim()}
                  data-testid="generate-btn"
                  className="flex-1 bg-blue-600 text-white font-semibold py-2.5 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-40"
                >
                  Generate Preview
                </button>
                {showPreview && (
                  <button
                    onClick={handleCopy}
                    data-testid="copy-html-btn"
                    className="flex items-center gap-2 bg-green-600 text-white font-semibold px-5 py-2.5 rounded-lg hover:bg-green-700 transition-colors"
                  >
                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    {copied ? 'Copied!' : 'Copy HTML'}
                  </button>
                )}
              </div>
              {showPreview && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-xs text-blue-700 leading-relaxed">
                    <strong>How to use in ProtonMail:</strong> Click "Copy HTML" above, then in ProtonMail composer click the <code className="bg-blue-100 px-1 rounded">&lt;/&gt;</code> button (bottom toolbar, inside "..."), paste the HTML and send.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Preview */}
          <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
            <div className="bg-gray-100 px-4 py-2 border-b">
              <span className="text-sm font-medium text-gray-600">Email Preview</span>
            </div>
            {showPreview ? (
              <iframe
                ref={iframeRef}
                title="Email Preview"
                className="w-full border-0"
                style={{ height: '600px' }}
              />
            ) : (
              <div className="flex items-center justify-center h-96 text-gray-400 text-sm">
                Fill in the form and click "Generate Preview"
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
