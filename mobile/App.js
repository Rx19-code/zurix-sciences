import React, { useState, useEffect } from 'react';
import { SafeAreaView, View, Text, TouchableOpacity, StyleSheet, ScrollView, TextInput, Alert, RefreshControl } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'https://zurixsciences.com/api';
const C = { primary: '#1e40af', success: '#10b981', warning: '#f59e0b', danger: '#ef4444', dark: '#1f2937', light: '#f3f4f6', white: '#fff', text: '#374151', muted: '#9ca3af' };

const api = axios.create({ baseURL: API_URL, timeout: 10000 });

// ===== HOME =====
function HomeScreen({ goTo }) {
  const [products, setProducts] = useState(0);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    try {
      const r = await api.get('/products');
      setProducts(r.data.length);
    } catch (e) { console.log(e); }
  };

  useEffect(() => { load(); }, []);

  return (
    <ScrollView style={s.page} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={async () => { setRefreshing(true); await load(); setRefreshing(false); }} />}>
      <View style={{ backgroundColor: C.primary, padding: 24, borderBottomLeftRadius: 24, borderBottomRightRadius: 24 }}>
        <Text style={{ color: C.white, fontSize: 16, opacity: 0.8 }}>Welcome to</Text>
        <Text style={{ color: C.white, fontSize: 30, fontWeight: 'bold', marginTop: 4 }}>Zurix Sciences</Text>
        <Text style={{ color: C.white, fontSize: 14, opacity: 0.8, marginTop: 4 }}>Product Verification & Protocols</Text>
      </View>
      <View style={{ flexDirection: 'row', padding: 16, gap: 12 }}>
        <View style={{ flex: 1, backgroundColor: C.primary, padding: 20, borderRadius: 16, alignItems: 'center' }}>
          <Text style={{ color: C.white, fontSize: 28, fontWeight: 'bold' }}>{products}</Text>
          <Text style={{ color: C.white, fontSize: 12 }}>Products</Text>
        </View>
        <View style={{ flex: 1, backgroundColor: C.success, padding: 20, borderRadius: 16, alignItems: 'center' }}>
          <Text style={{ color: C.white, fontSize: 28, fontWeight: 'bold' }}>10</Text>
          <Text style={{ color: C.white, fontSize: 12 }}>Protocols</Text>
        </View>
      </View>
      <View style={{ padding: 16 }}>
        <Text style={{ fontSize: 20, fontWeight: 'bold', color: C.dark, marginBottom: 12 }}>Quick Actions</Text>
        {[{ t: 'Verify Product', d: 'Scan QR or enter code', tab: 'Scan' }, { t: 'Browse Protocols', d: 'View peptide protocols', tab: 'Protocols' }, { t: 'View History', d: 'Check scan history', tab: 'History' }].map((f, i) => (
          <TouchableOpacity key={i} style={{ flexDirection: 'row', alignItems: 'center', backgroundColor: C.white, padding: 16, borderRadius: 12, marginBottom: 12, elevation: 2 }} onPress={() => goTo(f.tab)}>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 16, fontWeight: '600', color: C.dark }}>{f.t}</Text>
              <Text style={{ fontSize: 14, color: C.muted }}>{f.d}</Text>
            </View>
            <Text style={{ color: C.muted, fontSize: 20 }}>{'>'}</Text>
          </TouchableOpacity>
        ))}
      </View>
      <View style={{ flexDirection: 'row', alignItems: 'center', backgroundColor: C.warning + '20', padding: 16, margin: 16, borderRadius: 12, borderLeftWidth: 4, borderLeftColor: C.warning }}>
        <Text style={{ flex: 1, fontSize: 12, fontWeight: '600', color: C.dark }}>FOR RESEARCH USE ONLY - Not for human consumption</Text>
      </View>
    </ScrollView>
  );
}

// ===== SCAN =====
function ScanScreen() {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const verify = async () => {
    if (!code.trim()) { Alert.alert('Error', 'Enter a code'); return; }
    setLoading(true);
    try {
      const r = await api.post('/verify-product', { code: code.trim().toUpperCase() });
      setResult(r.data);
      // Save to history
      const hist = JSON.parse(await AsyncStorage.getItem('vh') || '[]');
      hist.unshift({ ...r.data, code: code.trim().toUpperCase(), timestamp: new Date().toISOString() });
      await AsyncStorage.setItem('vh', JSON.stringify(hist.slice(0, 50)));
    } catch (e) { Alert.alert('Error', 'Network error'); }
    setLoading(false);
  };

  return (
    <ScrollView style={s.page} contentContainerStyle={{ padding: 16 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', color: C.dark, marginBottom: 8 }}>Verify Product</Text>
      <Text style={{ color: C.muted, marginBottom: 20 }}>Enter the verification code from your product</Text>
      <TextInput style={{ borderWidth: 1, borderColor: '#ddd', borderRadius: 12, padding: 16, fontSize: 18, fontFamily: 'monospace', backgroundColor: C.white, marginBottom: 12 }} placeholder="ZX-XXXXXXXX" value={code} onChangeText={t => setCode(t.toUpperCase())} autoCapitalize="characters" />
      <TouchableOpacity style={{ backgroundColor: C.primary, padding: 16, borderRadius: 12, alignItems: 'center', marginBottom: 16 }} onPress={verify} disabled={loading}>
        <Text style={{ color: C.white, fontSize: 16, fontWeight: '600' }}>{loading ? 'Verifying...' : 'Verify Product'}</Text>
      </TouchableOpacity>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
        {['ZX-ZE101208', 'ZX-BP050823', 'ZX-SE030409'].map(c => (
          <TouchableOpacity key={c} style={{ paddingHorizontal: 12, paddingVertical: 6, backgroundColor: C.primary + '15', borderRadius: 8 }} onPress={() => { setCode(c); setResult(null); }}>
            <Text style={{ fontFamily: 'monospace', fontSize: 12, color: C.primary }}>{c}</Text>
          </TouchableOpacity>
        ))}
      </View>
      {result && (
        <View style={{ backgroundColor: result.success ? C.success + '15' : C.danger + '15', padding: 20, borderRadius: 16, borderLeftWidth: 4, borderLeftColor: result.success ? C.success : C.danger }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold', color: result.success ? C.success : C.danger, marginBottom: 8 }}>{result.success ? 'Authenticated!' : 'Failed!'}</Text>
          <Text style={{ color: C.text, marginBottom: 8 }}>{result.message}</Text>
          {result.product && (
            <View>
              {[['Product', result.product.name], ['Batch', result.product.batch_number], ['Purity', result.product.purity], ['Expiry', result.product.expiry_date]].map(([k, v], i) => (
                <View key={i} style={{ flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 4 }}>
                  <Text style={{ color: C.muted }}>{k}:</Text>
                  <Text style={{ fontWeight: '600', color: C.dark }}>{v}</Text>
                </View>
              ))}
            </View>
          )}
        </View>
      )}
    </ScrollView>
  );
}

// ===== PROTOCOLS =====
function ProtocolsScreen() {
  const [protocols, setProtocols] = useState([]);
  const [filter, setFilter] = useState('All');
  const [selected, setSelected] = useState(null);

  useEffect(() => { api.get('/protocols').then(r => setProtocols(r.data)).catch(() => {}); }, []);

  const filtered = filter === 'All' ? protocols : protocols.filter(p => p.category === filter);

  return (
    <ScrollView style={s.page}>
      <View style={{ flexDirection: 'row', padding: 12, gap: 8 }}>
        {['All', 'Basic', 'Advanced'].map(f => (
          <TouchableOpacity key={f} style={{ flex: 1, paddingVertical: 10, borderRadius: 8, backgroundColor: filter === f ? C.primary : C.light, alignItems: 'center' }} onPress={() => setFilter(f)}>
            <Text style={{ fontWeight: '600', color: filter === f ? C.white : C.text }}>{f}</Text>
          </TouchableOpacity>
        ))}
      </View>
      <View style={{ padding: 16 }}>
        {filtered.map(p => (
          <TouchableOpacity key={p.id} style={{ backgroundColor: C.white, borderRadius: 16, padding: 16, marginBottom: 12, elevation: 2 }} onPress={() => setSelected(selected?.id === p.id ? null : p)}>
            <View style={{ flexDirection: 'row', marginBottom: 6 }}>
              <View style={{ paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, backgroundColor: p.category === 'Basic' ? C.success + '20' : C.primary + '20' }}>
                <Text style={{ fontSize: 12, fontWeight: '600', color: p.category === 'Basic' ? C.success : C.primary }}>{p.category}</Text>
              </View>
              {p.featured && <Text style={{ marginLeft: 8, color: '#f59e0b' }}>*</Text>}
            </View>
            <Text style={{ fontSize: 17, fontWeight: 'bold', color: C.dark, marginBottom: 6 }}>{p.title}</Text>
            <Text style={{ fontSize: 13, color: C.text, marginBottom: 8 }} numberOfLines={2}>{p.description}</Text>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', borderTopWidth: 1, borderTopColor: C.light, paddingTop: 10 }}>
              <Text style={{ fontSize: 18, fontWeight: 'bold', color: C.primary }}>${p.price.toFixed(2)}</Text>
              <Text style={{ color: C.muted }}>{p.duration_weeks} weeks</Text>
            </View>
            {selected?.id === p.id && (
              <View style={{ marginTop: 12, paddingTop: 12, borderTopWidth: 1, borderTopColor: C.light }}>
                <Text style={{ fontWeight: 'bold', color: C.dark, marginBottom: 4 }}>Dosage:</Text>
                <Text style={{ color: C.text, marginBottom: 8 }}>{p.dosage_instructions}</Text>
                <Text style={{ fontWeight: 'bold', color: C.dark, marginBottom: 4 }}>Frequency:</Text>
                <Text style={{ color: C.text, marginBottom: 8 }}>{p.frequency}</Text>
                <Text style={{ fontWeight: 'bold', color: C.dark, marginBottom: 4 }}>Expected Results:</Text>
                <Text style={{ color: C.text, marginBottom: 8 }}>{p.expected_results}</Text>
                <Text style={{ fontWeight: 'bold', color: C.dark, marginBottom: 4 }}>Products Needed:</Text>
                <Text style={{ color: C.text, marginBottom: 8 }}>{p.products_needed.join(', ')}</Text>
                <Text style={{ fontWeight: 'bold', color: C.dark, marginBottom: 4 }}>Side Effects:</Text>
                <Text style={{ color: C.text }}>{p.side_effects}</Text>
              </View>
            )}
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

// ===== HISTORY =====
function HistoryScreen() {
  const [history, setHistory] = useState([]);

  useEffect(() => { AsyncStorage.getItem('vh').then(d => setHistory(d ? JSON.parse(d) : [])).catch(() => {}); }, []);

  return (
    <ScrollView style={s.page} contentContainerStyle={{ padding: 16 }}>
      <View style={{ flexDirection: 'row', backgroundColor: C.white, borderRadius: 12, padding: 16, marginBottom: 16 }}>
        <View style={{ flex: 1, alignItems: 'center' }}><Text style={{ fontSize: 24, fontWeight: 'bold', color: C.dark }}>{history.length}</Text><Text style={{ color: C.muted, fontSize: 12 }}>Total</Text></View>
        <View style={{ flex: 1, alignItems: 'center' }}><Text style={{ fontSize: 24, fontWeight: 'bold', color: C.success }}>{history.filter(h => h.success).length}</Text><Text style={{ color: C.muted, fontSize: 12 }}>Verified</Text></View>
        <View style={{ flex: 1, alignItems: 'center' }}><Text style={{ fontSize: 24, fontWeight: 'bold', color: C.danger }}>{history.filter(h => !h.success).length}</Text><Text style={{ color: C.muted, fontSize: 12 }}>Failed</Text></View>
      </View>
      {history.length === 0 ? (
        <View style={{ alignItems: 'center', paddingVertical: 60 }}>
          <Text style={{ fontSize: 20, fontWeight: 'bold', color: C.dark, marginBottom: 8 }}>No Verifications Yet</Text>
          <Text style={{ color: C.muted, textAlign: 'center' }}>Verify a product to see history here</Text>
        </View>
      ) : history.map((h, i) => (
        <View key={i} style={{ flexDirection: 'row', backgroundColor: C.white, borderRadius: 12, padding: 14, marginBottom: 8, elevation: 1 }}>
          <View style={{ width: 40, height: 40, borderRadius: 20, backgroundColor: h.success ? C.success + '20' : C.danger + '20', alignItems: 'center', justifyContent: 'center', marginRight: 12 }}>
            <Text style={{ color: h.success ? C.success : C.danger, fontWeight: 'bold' }}>{h.success ? 'V' : 'X'}</Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={{ fontWeight: '600', color: C.dark }}>{h.product?.name || 'Unknown'}</Text>
            <Text style={{ fontFamily: 'monospace', fontSize: 11, color: C.primary }}>{h.code}</Text>
            <Text style={{ fontSize: 11, color: C.muted }}>{new Date(h.timestamp).toLocaleString()}</Text>
          </View>
        </View>
      ))}
    </ScrollView>
  );
}

// ===== PROFILE =====
function ProfileScreen() {
  const clearHistory = () => {
    Alert.alert('Clear History', 'Remove all verification history?', [
      { text: 'Cancel' },
      { text: 'Clear', style: 'destructive', onPress: () => AsyncStorage.removeItem('vh') }
    ]);
  };

  return (
    <ScrollView style={s.page} contentContainerStyle={{ padding: 16 }}>
      <View style={{ backgroundColor: C.primary, borderRadius: 20, padding: 24, alignItems: 'center', marginBottom: 16 }}>
        <View style={{ width: 70, height: 70, borderRadius: 35, backgroundColor: 'rgba(255,255,255,0.2)', alignItems: 'center', justifyContent: 'center', marginBottom: 12 }}>
          <Text style={{ color: C.white, fontSize: 28, fontWeight: 'bold' }}>Z</Text>
        </View>
        <Text style={{ color: C.white, fontSize: 22, fontWeight: 'bold' }}>Zurix Sciences</Text>
        <Text style={{ color: 'rgba(255,255,255,0.7)', fontSize: 13 }}>Version 1.0.0</Text>
      </View>
      {[{ t: 'Visit Website', d: 'zurixsciences.com' }, { t: 'Contact Support', d: 'Chat via WhatsApp' }, { t: 'Clear History', d: 'Remove verification data', action: clearHistory }].map((item, i) => (
        <TouchableOpacity key={i} style={{ flexDirection: 'row', alignItems: 'center', backgroundColor: C.white, padding: 14, borderRadius: 12, marginBottom: 8, elevation: 1 }} onPress={item.action || (() => {})}>
          <View style={{ flex: 1 }}>
            <Text style={{ fontSize: 15, fontWeight: '600', color: C.dark }}>{item.t}</Text>
            <Text style={{ fontSize: 12, color: C.muted }}>{item.d}</Text>
          </View>
          <Text style={{ color: C.muted }}>{'>'}</Text>
        </TouchableOpacity>
      ))}
      <View style={{ backgroundColor: C.white, borderRadius: 12, padding: 16, marginTop: 8, marginBottom: 16 }}>
        <Text style={{ fontWeight: 'bold', color: C.dark, marginBottom: 8 }}>About</Text>
        <Text style={{ color: C.text, fontSize: 13, lineHeight: 19 }}>Zurix Sciences app for product verification and peptide research protocols.</Text>
      </View>
      <View style={{ flexDirection: 'row', backgroundColor: C.warning + '15', padding: 12, borderRadius: 10, gap: 10 }}>
        <Text style={{ flex: 1, fontSize: 11, fontWeight: '600', color: C.dark }}>FOR RESEARCH USE ONLY - Not for human consumption</Text>
      </View>
    </ScrollView>
  );
}

// ===== MAIN APP =====
export default function App() {
  const [tab, setTab] = useState('Home');

  const screen = () => {
    switch (tab) {
      case 'Home': return <HomeScreen goTo={setTab} />;
      case 'Scan': return <ScanScreen />;
      case 'Protocols': return <ProtocolsScreen />;
      case 'History': return <HistoryScreen />;
      case 'Profile': return <ProfileScreen />;
    }
  };

  const tabs = [
    { k: 'Home', l: 'Home' }, { k: 'Scan', l: 'Verify' },
    { k: 'Protocols', l: 'Protocols' }, { k: 'History', l: 'History' },
    { k: 'Profile', l: 'Profile' }
  ];

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: C.primary }}>
      <StatusBar style="light" />
      <View style={{ backgroundColor: C.primary, paddingTop: 8, paddingBottom: 12, paddingHorizontal: 20 }}>
        <Text style={{ color: C.white, fontSize: 18, fontWeight: 'bold' }}>
          {tab === 'Home' ? 'Zurix Sciences' : tab === 'Scan' ? 'Verify Product' : tab}
        </Text>
      </View>
      <View style={{ flex: 1, backgroundColor: C.light }}>{screen()}</View>
      <View style={{ flexDirection: 'row', backgroundColor: C.white, borderTopWidth: 1, borderTopColor: '#e5e7eb', paddingVertical: 8 }}>
        {tabs.map(t => (
          <TouchableOpacity key={t.k} style={{ flex: 1, alignItems: 'center', paddingVertical: 4 }} onPress={() => setTab(t.k)}>
            <Text style={{ fontSize: 11, fontWeight: tab === t.k ? '700' : '400', color: tab === t.k ? C.primary : C.muted }}>{t.l}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({ page: { flex: 1, backgroundColor: C.light } });
