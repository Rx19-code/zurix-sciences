import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView, TextInput,
  Alert, RefreshControl, Dimensions, Linking, ActivityIndicator
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'https://zurixsciences.com/api';
const { width } = Dimensions.get('window');
const api = axios.create({ baseURL: API_URL, timeout: 10000 });

const P = {
  bg: '#0a0f1e',
  card: '#111827',
  cardLight: '#1a2235',
  accent: '#3b82f6',
  accentDark: '#2563eb',
  success: '#10b981',
  successDim: '#065f46',
  warning: '#f59e0b',
  danger: '#ef4444',
  dangerDim: '#7f1d1d',
  text: '#f1f5f9',
  textDim: '#94a3b8',
  textMuted: '#64748b',
  border: '#1e293b',
  white: '#ffffff',
  gradient1: '#1e40af',
  gradient2: '#7c3aed',
};

// ========== HOME ==========
function HomeScreen({ goTo }) {
  const [stats, setStats] = useState({ products: 0, protocols: 0, scans: 0 });
  const [refreshing, setRefreshing] = useState(false);
  const [featured, setFeatured] = useState([]);

  const load = useCallback(async () => {
    try {
      const [prods, protos, hist] = await Promise.all([
        api.get('/products').catch(() => ({ data: [] })),
        api.get('/protocols').catch(() => ({ data: [] })),
        AsyncStorage.getItem('vh').then(d => d ? JSON.parse(d) : []).catch(() => [])
      ]);
      setStats({ products: prods.data.length, protocols: protos.data.length, scans: hist.length });
      setFeatured(prods.data.filter(p => p.featured).slice(0, 3));
    } catch (e) { console.log(e); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const refresh = async () => { setRefreshing(true); await load(); setRefreshing(false); };

  return (
    <ScrollView style={s.screen} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor={P.accent} />}>
      <View style={s.heroCard}>
        <View style={s.heroGlow} />
        <Text style={s.heroSub}>Welcome to</Text>
        <Text style={s.heroTitle}>Zurix Sciences</Text>
        <Text style={s.heroParagraph}>Premium peptide research compounds verification & protocol platform</Text>
        <View style={s.heroStats}>
          <View style={s.heroStat}>
            <Text style={s.heroStatNum}>{stats.products}</Text>
            <Text style={s.heroStatLabel}>Products</Text>
          </View>
          <View style={[s.heroStatDiv]} />
          <View style={s.heroStat}>
            <Text style={s.heroStatNum}>{stats.protocols}</Text>
            <Text style={s.heroStatLabel}>Protocols</Text>
          </View>
          <View style={[s.heroStatDiv]} />
          <View style={s.heroStat}>
            <Text style={s.heroStatNum}>{stats.scans}</Text>
            <Text style={s.heroStatLabel}>Scans</Text>
          </View>
        </View>
      </View>

      <Text style={s.sectionTitle}>Quick Actions</Text>
      {[
        { t: 'Verify Product', d: 'Authenticate your research compounds', tab: 'Scan', color: P.accent, icon: '[QR]' },
        { t: 'Research Protocols', d: 'Browse peptide protocols & dosage guides', tab: 'Protocols', color: P.gradient2, icon: '[Rx]' },
        { t: 'Scan History', d: 'Review past verification results', tab: 'History', color: P.success, icon: '[H]' },
      ].map((f, i) => (
        <TouchableOpacity key={i} style={s.actionCard} onPress={() => goTo(f.tab)} activeOpacity={0.7}>
          <View style={[s.actionIcon, { backgroundColor: f.color + '20' }]}>
            <Text style={[s.actionIconText, { color: f.color }]}>{f.icon}</Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={s.actionTitle}>{f.t}</Text>
            <Text style={s.actionDesc}>{f.d}</Text>
          </View>
          <Text style={{ color: P.textMuted, fontSize: 18 }}>{'>'}</Text>
        </TouchableOpacity>
      ))}

      {featured.length > 0 && (
        <>
          <Text style={s.sectionTitle}>Featured Products</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ paddingHorizontal: 16, gap: 12 }}>
            {featured.map((p, i) => (
              <View key={i} style={s.featuredCard}>
                <View style={[s.catBadge, { backgroundColor: P.accent + '20' }]}>
                  <Text style={[s.catBadgeText, { color: P.accent }]}>{p.category}</Text>
                </View>
                <Text style={s.featuredName} numberOfLines={1}>{p.name}</Text>
                <Text style={s.featuredPrice}>${p.price?.toFixed(2)}</Text>
                <View style={s.featuredMeta}>
                  <Text style={s.featuredMetaText}>Purity: {p.purity}</Text>
                </View>
              </View>
            ))}
          </ScrollView>
        </>
      )}

      <View style={s.disclaimerBar}>
        <Text style={s.disclaimerIcon}>!</Text>
        <Text style={s.disclaimerText}>FOR RESEARCH USE ONLY - Not for human consumption, veterinary use, or diagnostic purposes.</Text>
      </View>
      <View style={{ height: 20 }} />
    </ScrollView>
  );
}

// ========== SCAN / VERIFY ==========
function ScanScreen() {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const verify = async () => {
    const c = code.trim().toUpperCase();
    if (!c) { Alert.alert('Error', 'Enter a verification code'); return; }
    setLoading(true);
    setResult(null);
    try {
      const r = await api.post('/verify-product', { code: c });
      setResult(r.data);
      const hist = JSON.parse(await AsyncStorage.getItem('vh') || '[]');
      hist.unshift({ ...r.data, code: c, timestamp: new Date().toISOString() });
      await AsyncStorage.setItem('vh', JSON.stringify(hist.slice(0, 100)));
    } catch (e) {
      setResult({ success: false, message: 'Network error. Check your connection.' });
    }
    setLoading(false);
  };

  return (
    <ScrollView style={s.screen} contentContainerStyle={{ padding: 16 }}>
      <View style={s.verifyHeader}>
        <Text style={s.verifyTitle}>Product Verification</Text>
        <Text style={s.verifySubtitle}>Enter the unique code printed on your product label to confirm authenticity</Text>
      </View>

      <View style={s.inputGroup}>
        <Text style={s.inputLabel}>Verification Code</Text>
        <TextInput
          style={s.input}
          placeholder="Enter code (e.g. ZX-ZE101208)"
          placeholderTextColor={P.textMuted}
          value={code}
          onChangeText={t => { setCode(t.toUpperCase()); setResult(null); }}
          autoCapitalize="characters"
        />
      </View>

      <TouchableOpacity style={[s.primaryBtn, loading && { opacity: 0.6 }]} onPress={verify} disabled={loading} activeOpacity={0.8}>
        {loading ? <ActivityIndicator color={P.white} /> : <Text style={s.primaryBtnText}>Verify Product</Text>}
      </TouchableOpacity>

      <Text style={[s.inputLabel, { marginTop: 16, marginBottom: 8 }]}>Try a sample code:</Text>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
        {['ZX-ZE101208', 'ZX-BP050823', 'ZX-SE030409'].map(c => (
          <TouchableOpacity key={c} style={s.sampleCode} onPress={() => { setCode(c); setResult(null); }}>
            <Text style={s.sampleCodeText}>{c}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {result && (
        <View style={[s.resultCard, { borderLeftColor: result.success ? P.success : P.danger }]}>
          <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12 }}>
            <View style={[s.resultStatusDot, { backgroundColor: result.success ? P.success : P.danger }]} />
            <Text style={[s.resultStatus, { color: result.success ? P.success : P.danger }]}>
              {result.success ? 'AUTHENTICATED' : 'VERIFICATION FAILED'}
            </Text>
          </View>
          <Text style={s.resultMsg}>{result.message}</Text>
          {result.product && (
            <View style={s.resultDetails}>
              {[
                ['Product', result.product.name],
                ['Batch', result.product.batch_number],
                ['Purity', result.product.purity],
                ['Expiry', result.product.expiry_date],
                ['Category', result.product.category],
              ].map(([k, v], i) => (
                <View key={i} style={s.resultRow}>
                  <Text style={s.resultRowKey}>{k}</Text>
                  <Text style={s.resultRowVal}>{v}</Text>
                </View>
              ))}
              {result.verification_count > 3 && (
                <View style={[s.warningBox, { marginTop: 8 }]}>
                  <Text style={s.warningBoxText}>This product has been verified {result.verification_count} times. If you did not perform all verifications, this product may be counterfeit.</Text>
                </View>
              )}
            </View>
          )}
        </View>
      )}
      <View style={{ height: 20 }} />
    </ScrollView>
  );
}

// ========== PROTOCOLS ==========
function ProtocolsScreen() {
  const [protocols, setProtocols] = useState([]);
  const [filter, setFilter] = useState('All');
  const [expanded, setExpanded] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/protocols').then(r => { setProtocols(r.data); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const filtered = filter === 'All' ? protocols : protocols.filter(p => p.category === filter);

  if (loading) return <View style={[s.screen, { justifyContent: 'center', alignItems: 'center' }]}><ActivityIndicator size="large" color={P.accent} /></View>;

  return (
    <ScrollView style={s.screen}>
      <View style={{ padding: 16, paddingBottom: 8 }}>
        <Text style={{ color: P.textDim, fontSize: 14, marginBottom: 12 }}>Browse research protocols and dosage guides</Text>
      </View>
      <View style={{ flexDirection: 'row', paddingHorizontal: 16, gap: 8, marginBottom: 12 }}>
        {['All', 'Basic', 'Advanced'].map(f => (
          <TouchableOpacity key={f} style={[s.filterBtn, filter === f && s.filterBtnActive]} onPress={() => setFilter(f)}>
            <Text style={[s.filterBtnText, filter === f && s.filterBtnTextActive]}>{f}</Text>
            {f !== 'All' && <Text style={[s.filterPrice, filter === f && { color: P.white + '80' }]}>{f === 'Basic' ? '$4.99' : '$9.99'}</Text>}
          </TouchableOpacity>
        ))}
      </View>
      <View style={{ paddingHorizontal: 16, paddingBottom: 24 }}>
        {filtered.map(p => (
          <TouchableOpacity key={p.id} style={s.protoCard} onPress={() => setExpanded(expanded === p.id ? null : p.id)} activeOpacity={0.8}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 }}>
              <View style={[s.catBadge, { backgroundColor: p.category === 'Basic' ? P.success + '20' : P.gradient2 + '20' }]}>
                <Text style={[s.catBadgeText, { color: p.category === 'Basic' ? P.success : P.gradient2 }]}>{p.category}</Text>
              </View>
              <Text style={{ color: P.accent, fontWeight: 'bold', fontSize: 16 }}>${p.price?.toFixed(2)}</Text>
            </View>
            <Text style={s.protoTitle}>{p.title}</Text>
            <Text style={s.protoDesc} numberOfLines={expanded === p.id ? undefined : 2}>{p.description}</Text>
            <View style={{ flexDirection: 'row', gap: 16, marginTop: 8 }}>
              <Text style={s.protoMeta}>{p.duration_weeks} weeks</Text>
              <Text style={s.protoMeta}>{p.products_needed?.length || 0} products</Text>
            </View>
            {expanded === p.id && (
              <View style={s.protoExpanded}>
                {[
                  ['Dosage', p.dosage_instructions],
                  ['Frequency', p.frequency],
                  ['Expected Results', p.expected_results],
                  ['Side Effects', p.side_effects],
                  ['Storage', p.storage_tips],
                ].map(([title, text], i) => text ? (
                  <View key={i} style={{ marginBottom: 12 }}>
                    <Text style={s.protoExpandTitle}>{title}</Text>
                    <Text style={s.protoExpandText}>{text}</Text>
                  </View>
                ) : null)}
                {p.products_needed?.length > 0 && (
                  <View style={{ marginBottom: 12 }}>
                    <Text style={s.protoExpandTitle}>Products Needed</Text>
                    {p.products_needed.map((prod, i) => (
                      <Text key={i} style={[s.protoExpandText, { paddingLeft: 8 }]}>- {prod}</Text>
                    ))}
                  </View>
                )}
                {p.contraindications && (
                  <View style={s.warningBox}>
                    <Text style={s.warningBoxText}>Contraindications: {p.contraindications}</Text>
                  </View>
                )}
              </View>
            )}
            <Text style={{ color: P.textMuted, fontSize: 12, textAlign: 'center', marginTop: 8 }}>
              {expanded === p.id ? 'Tap to collapse' : 'Tap to view details'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

// ========== HISTORY ==========
function HistoryScreen() {
  const [history, setHistory] = useState([]);

  useEffect(() => { AsyncStorage.getItem('vh').then(d => setHistory(d ? JSON.parse(d) : [])).catch(() => {}); }, []);

  return (
    <ScrollView style={s.screen} contentContainerStyle={{ padding: 16 }}>
      <View style={s.statsRow}>
        {[
          { n: history.length, l: 'Total Scans', c: P.accent },
          { n: history.filter(h => h.success).length, l: 'Verified', c: P.success },
          { n: history.filter(h => !h.success).length, l: 'Failed', c: P.danger },
        ].map((st, i) => (
          <View key={i} style={s.statBox}>
            <Text style={[s.statBoxNum, { color: st.c }]}>{st.n}</Text>
            <Text style={s.statBoxLabel}>{st.l}</Text>
          </View>
        ))}
      </View>

      {history.length === 0 ? (
        <View style={s.emptyState}>
          <Text style={s.emptyIcon}>[ ]</Text>
          <Text style={s.emptyTitle}>No Verifications Yet</Text>
          <Text style={s.emptyText}>Verify a product to see your scan history here</Text>
        </View>
      ) : history.map((h, i) => (
        <View key={i} style={s.historyCard}>
          <View style={[s.historyDot, { backgroundColor: h.success ? P.success : P.danger }]} />
          <View style={{ flex: 1 }}>
            <Text style={s.historyName}>{h.product?.name || 'Unknown Product'}</Text>
            <Text style={s.historyCode}>{h.code}</Text>
            <Text style={s.historyTime}>{new Date(h.timestamp).toLocaleString()}</Text>
          </View>
          <View style={[s.historyBadge, { backgroundColor: h.success ? P.successDim : P.dangerDim }]}>
            <Text style={[s.historyBadgeText, { color: h.success ? P.success : P.danger }]}>{h.success ? 'OK' : 'FAIL'}</Text>
          </View>
        </View>
      ))}
      <View style={{ height: 20 }} />
    </ScrollView>
  );
}

// ========== PROFILE ==========
function ProfileScreen() {
  const clearHistory = () => {
    Alert.alert('Clear History', 'Remove all verification history? This cannot be undone.', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Clear', style: 'destructive', onPress: () => AsyncStorage.removeItem('vh').then(() => Alert.alert('Done', 'History cleared.')) }
    ]);
  };

  return (
    <ScrollView style={s.screen} contentContainerStyle={{ padding: 16 }}>
      <View style={s.profileHeader}>
        <View style={s.profileAvatar}>
          <Text style={s.profileAvatarText}>Z</Text>
        </View>
        <Text style={s.profileName}>Zurix Sciences</Text>
        <Text style={s.profileVersion}>v1.0.0 | Peptide Research Platform</Text>
      </View>

      <Text style={[s.sectionTitle, { paddingHorizontal: 0 }]}>Settings & Info</Text>

      {[
        { t: 'Visit Website', d: 'zurixsciences.com', color: P.accent, action: () => Linking.openURL('https://zurixsciences.com') },
        { t: 'Contact Support', d: 'Chat via WhatsApp', color: P.success, action: () => Linking.openURL('https://wa.me/85212345678?text=Hello%20Zurix%20Sciences') },
        { t: 'Clear Scan History', d: 'Remove local verification data', color: P.danger, action: clearHistory },
      ].map((item, i) => (
        <TouchableOpacity key={i} style={s.menuItem} onPress={item.action} activeOpacity={0.7}>
          <View style={[s.menuDot, { backgroundColor: item.color }]} />
          <View style={{ flex: 1 }}>
            <Text style={s.menuTitle}>{item.t}</Text>
            <Text style={s.menuDesc}>{item.d}</Text>
          </View>
          <Text style={{ color: P.textMuted }}>{'>'}</Text>
        </TouchableOpacity>
      ))}

      <View style={[s.card, { marginTop: 16 }]}>
        <Text style={{ color: P.text, fontWeight: 'bold', marginBottom: 8 }}>About</Text>
        <Text style={{ color: P.textDim, fontSize: 13, lineHeight: 20 }}>
          Zurix Sciences mobile application for product verification and peptide research protocols. 
          Scan product QR codes or enter verification codes to confirm product authenticity.
        </Text>
      </View>

      <View style={[s.disclaimerBar, { marginHorizontal: 0 }]}>
        <Text style={s.disclaimerIcon}>!</Text>
        <Text style={s.disclaimerText}>FOR RESEARCH USE ONLY - All products are intended for laboratory and research applications only.</Text>
      </View>
      <View style={{ height: 24 }} />
    </ScrollView>
  );
}

// ========== MAIN APP ==========
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
    { k: 'Home', l: 'Home', i: 'H' },
    { k: 'Scan', l: 'Verify', i: 'V' },
    { k: 'Protocols', l: 'Protocols', i: 'P' },
    { k: 'History', l: 'History', i: 'T' },
    { k: 'Profile', l: 'Profile', i: 'U' },
  ];

  return (
    <View style={{ flex: 1, backgroundColor: P.bg }}>
      <StatusBar style="light" />
      <View style={s.topBar}>
        <Text style={s.topBarTitle}>
          {tab === 'Home' ? 'Zurix Sciences' : tab === 'Scan' ? 'Verify Product' : tab}
        </Text>
      </View>
      <View style={{ flex: 1 }}>{screen()}</View>
      <View style={s.bottomBar}>
        {tabs.map(t => (
          <TouchableOpacity key={t.k} style={s.bottomTab} onPress={() => setTab(t.k)} activeOpacity={0.7}>
            <View style={[s.bottomTabDot, tab === t.k && s.bottomTabDotActive]} />
            <Text style={[s.bottomTabLabel, tab === t.k && s.bottomTabLabelActive]}>{t.l}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

// ========== STYLES ==========
const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: P.bg },
  topBar: { backgroundColor: P.bg, paddingTop: 50, paddingBottom: 12, paddingHorizontal: 20, borderBottomWidth: 1, borderBottomColor: P.border },
  topBarTitle: { color: P.white, fontSize: 20, fontWeight: '700', letterSpacing: 0.5 },
  bottomBar: { flexDirection: 'row', backgroundColor: P.card, borderTopWidth: 1, borderTopColor: P.border, paddingBottom: 28, paddingTop: 10 },
  bottomTab: { flex: 1, alignItems: 'center', gap: 4 },
  bottomTabDot: { width: 4, height: 4, borderRadius: 2, backgroundColor: 'transparent' },
  bottomTabDotActive: { backgroundColor: P.accent },
  bottomTabLabel: { fontSize: 11, color: P.textMuted, fontWeight: '500' },
  bottomTabLabelActive: { color: P.accent, fontWeight: '700' },

  heroCard: { margin: 16, borderRadius: 20, backgroundColor: P.gradient1, padding: 24, overflow: 'hidden' },
  heroGlow: { position: 'absolute', top: -40, right: -40, width: 160, height: 160, borderRadius: 80, backgroundColor: P.gradient2, opacity: 0.3 },
  heroSub: { color: P.white, opacity: 0.7, fontSize: 14 },
  heroTitle: { color: P.white, fontSize: 28, fontWeight: '800', marginTop: 4, letterSpacing: 0.5 },
  heroParagraph: { color: P.white, opacity: 0.8, fontSize: 13, lineHeight: 19, marginTop: 8 },
  heroStats: { flexDirection: 'row', marginTop: 20, backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: 12, padding: 14 },
  heroStat: { flex: 1, alignItems: 'center' },
  heroStatNum: { color: P.white, fontSize: 22, fontWeight: '800' },
  heroStatLabel: { color: P.white, opacity: 0.7, fontSize: 11, marginTop: 2 },
  heroStatDiv: { width: 1, backgroundColor: 'rgba(255,255,255,0.2)' },

  sectionTitle: { color: P.text, fontSize: 18, fontWeight: '700', paddingHorizontal: 16, marginTop: 20, marginBottom: 12 },

  actionCard: { flexDirection: 'row', alignItems: 'center', backgroundColor: P.card, marginHorizontal: 16, marginBottom: 10, borderRadius: 14, padding: 16, borderWidth: 1, borderColor: P.border },
  actionIcon: { width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginRight: 14 },
  actionIconText: { fontSize: 14, fontWeight: '800' },
  actionTitle: { color: P.text, fontSize: 15, fontWeight: '600' },
  actionDesc: { color: P.textMuted, fontSize: 12, marginTop: 2 },

  featuredCard: { width: width * 0.55, backgroundColor: P.card, borderRadius: 14, padding: 14, borderWidth: 1, borderColor: P.border },
  featuredName: { color: P.text, fontSize: 14, fontWeight: '600', marginTop: 8 },
  featuredPrice: { color: P.accent, fontSize: 18, fontWeight: '700', marginTop: 4 },
  featuredMeta: { marginTop: 6 },
  featuredMetaText: { color: P.textMuted, fontSize: 11 },

  catBadge: { paddingHorizontal: 10, paddingVertical: 3, borderRadius: 8, alignSelf: 'flex-start' },
  catBadgeText: { fontSize: 11, fontWeight: '700' },

  disclaimerBar: { flexDirection: 'row', alignItems: 'center', backgroundColor: P.warning + '12', marginHorizontal: 16, marginTop: 20, padding: 14, borderRadius: 12, borderLeftWidth: 3, borderLeftColor: P.warning },
  disclaimerIcon: { color: P.warning, fontWeight: '800', fontSize: 16, marginRight: 10, width: 22, height: 22, textAlign: 'center', lineHeight: 22, backgroundColor: P.warning + '25', borderRadius: 11, overflow: 'hidden' },
  disclaimerText: { flex: 1, color: P.textDim, fontSize: 11, lineHeight: 16 },

  card: { backgroundColor: P.card, borderRadius: 14, padding: 16, borderWidth: 1, borderColor: P.border },

  verifyHeader: { marginBottom: 20 },
  verifyTitle: { color: P.text, fontSize: 22, fontWeight: '700' },
  verifySubtitle: { color: P.textDim, fontSize: 14, marginTop: 6, lineHeight: 20 },
  inputGroup: { marginBottom: 16 },
  inputLabel: { color: P.textDim, fontSize: 13, fontWeight: '600', marginBottom: 6 },
  input: { backgroundColor: P.card, borderWidth: 1, borderColor: P.border, borderRadius: 12, padding: 16, fontSize: 18, color: P.text, fontFamily: 'monospace', letterSpacing: 1 },
  primaryBtn: { backgroundColor: P.accent, padding: 16, borderRadius: 12, alignItems: 'center' },
  primaryBtnText: { color: P.white, fontSize: 16, fontWeight: '700' },
  sampleCode: { paddingHorizontal: 14, paddingVertical: 8, backgroundColor: P.accent + '15', borderRadius: 8, borderWidth: 1, borderColor: P.accent + '30' },
  sampleCodeText: { fontFamily: 'monospace', fontSize: 12, color: P.accent, fontWeight: '600' },
  resultCard: { backgroundColor: P.card, borderRadius: 14, padding: 18, marginTop: 20, borderLeftWidth: 4, borderWidth: 1, borderColor: P.border },
  resultStatusDot: { width: 10, height: 10, borderRadius: 5, marginRight: 8 },
  resultStatus: { fontSize: 14, fontWeight: '800', letterSpacing: 1 },
  resultMsg: { color: P.textDim, fontSize: 13, marginBottom: 12 },
  resultDetails: { backgroundColor: P.cardLight, borderRadius: 10, padding: 12 },
  resultRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: P.border },
  resultRowKey: { color: P.textMuted, fontSize: 13 },
  resultRowVal: { color: P.text, fontWeight: '600', fontSize: 13 },

  filterBtn: { flex: 1, paddingVertical: 10, borderRadius: 10, backgroundColor: P.card, alignItems: 'center', borderWidth: 1, borderColor: P.border },
  filterBtnActive: { backgroundColor: P.accent, borderColor: P.accent },
  filterBtnText: { fontSize: 14, fontWeight: '600', color: P.textDim },
  filterBtnTextActive: { color: P.white },
  filterPrice: { fontSize: 11, color: P.textMuted, marginTop: 1 },

  protoCard: { backgroundColor: P.card, borderRadius: 14, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: P.border },
  protoTitle: { color: P.text, fontSize: 17, fontWeight: '700', marginBottom: 6 },
  protoDesc: { color: P.textDim, fontSize: 13, lineHeight: 19 },
  protoMeta: { color: P.textMuted, fontSize: 12 },
  protoExpanded: { marginTop: 14, paddingTop: 14, borderTopWidth: 1, borderTopColor: P.border },
  protoExpandTitle: { color: P.accent, fontSize: 13, fontWeight: '700', marginBottom: 4 },
  protoExpandText: { color: P.textDim, fontSize: 13, lineHeight: 19 },

  warningBox: { backgroundColor: P.warning + '12', padding: 12, borderRadius: 8, borderLeftWidth: 3, borderLeftColor: P.warning },
  warningBoxText: { color: P.textDim, fontSize: 12, lineHeight: 17 },

  statsRow: { flexDirection: 'row', gap: 10, marginBottom: 20 },
  statBox: { flex: 1, backgroundColor: P.card, borderRadius: 14, padding: 16, alignItems: 'center', borderWidth: 1, borderColor: P.border },
  statBoxNum: { fontSize: 24, fontWeight: '800' },
  statBoxLabel: { color: P.textMuted, fontSize: 11, marginTop: 4 },

  emptyState: { alignItems: 'center', paddingVertical: 60 },
  emptyIcon: { fontSize: 40, color: P.textMuted, marginBottom: 12 },
  emptyTitle: { color: P.text, fontSize: 18, fontWeight: '700', marginBottom: 6 },
  emptyText: { color: P.textMuted, fontSize: 14, textAlign: 'center' },

  historyCard: { flexDirection: 'row', alignItems: 'center', backgroundColor: P.card, borderRadius: 12, padding: 14, marginBottom: 8, borderWidth: 1, borderColor: P.border },
  historyDot: { width: 10, height: 10, borderRadius: 5, marginRight: 12 },
  historyName: { color: P.text, fontWeight: '600', fontSize: 14 },
  historyCode: { fontFamily: 'monospace', fontSize: 11, color: P.accent, marginTop: 2 },
  historyTime: { color: P.textMuted, fontSize: 11, marginTop: 2 },
  historyBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6 },
  historyBadgeText: { fontSize: 11, fontWeight: '800' },

  profileHeader: { backgroundColor: P.card, borderRadius: 20, padding: 28, alignItems: 'center', marginBottom: 8, borderWidth: 1, borderColor: P.border },
  profileAvatar: { width: 72, height: 72, borderRadius: 36, backgroundColor: P.accent, alignItems: 'center', justifyContent: 'center', marginBottom: 14 },
  profileAvatarText: { color: P.white, fontSize: 30, fontWeight: '800' },
  profileName: { color: P.text, fontSize: 22, fontWeight: '700' },
  profileVersion: { color: P.textMuted, fontSize: 12, marginTop: 4 },

  menuItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: P.card, padding: 16, borderRadius: 12, marginBottom: 8, borderWidth: 1, borderColor: P.border },
  menuDot: { width: 8, height: 8, borderRadius: 4, marginRight: 14 },
  menuTitle: { color: P.text, fontSize: 15, fontWeight: '600' },
  menuDesc: { color: P.textMuted, fontSize: 12, marginTop: 2 },
});
