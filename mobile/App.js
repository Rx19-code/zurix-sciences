import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView, TextInput,
  Alert, RefreshControl, Dimensions, Linking, ActivityIndicator, Animated, Platform, Modal
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons, MaterialCommunityIcons, Feather } from '@expo/vector-icons';
import { CameraView, useCameraPermissions } from 'expo-camera';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'https://zurixsciences.com/api';
const { width, height } = Dimensions.get('window');
const api = axios.create({ baseURL: API_URL, timeout: 10000 });

// Helper function to open URLs safely
const openURL = async (url) => {
  try {
    const supported = await Linking.canOpenURL(url);
    if (supported) {
      await Linking.openURL(url);
    } else {
      Alert.alert('Error', `Cannot open URL: ${url}`);
    }
  } catch (error) {
    Alert.alert('Error', 'Failed to open link. Please try again.');
  }
};

// ========== MOCK PROTOCOLS (Simulation) ==========
const MOCK_PROTOCOLS = [
  {
    id: '1',
    title: 'BPC-157 Recovery Protocol',
    description: 'A comprehensive healing protocol designed to accelerate tissue repair and reduce inflammation. Ideal for post-injury recovery and joint health optimization.',
    category: 'Basic',
    price: 4.99,
    duration_weeks: 4,
    products_needed: ['BPC-157 5mg', 'Bacteriostatic Water'],
    dosage_instructions: '250-500mcg subcutaneously, twice daily',
    frequency: 'Twice daily (morning and evening)',
    expected_results: 'Improved healing, reduced inflammation, better joint mobility within 2-4 weeks',
    side_effects: 'Minimal. Possible injection site irritation',
    storage_tips: 'Store reconstituted peptide at 2-8°C. Use within 30 days',
    contraindications: 'Not for use during pregnancy or breastfeeding'
  },
  {
    id: '2',
    title: 'TB-500 Tissue Repair',
    description: 'Advanced protocol for deep tissue healing and muscle recovery. Promotes cell migration and blood vessel formation for enhanced repair.',
    category: 'Advanced',
    price: 9.99,
    duration_weeks: 6,
    products_needed: ['TB-500 5mg', 'Bacteriostatic Water', 'Insulin Syringes'],
    dosage_instructions: '2.5mg twice weekly for loading phase, then 2.5mg weekly',
    frequency: 'Twice weekly (loading) then weekly (maintenance)',
    expected_results: 'Enhanced flexibility, accelerated healing, improved endurance',
    side_effects: 'Temporary head rush, fatigue during initial phase',
    storage_tips: 'Refrigerate after reconstitution. Protect from light',
    contraindications: 'Avoid if history of cancer or tumors'
  },
  {
    id: '3',
    title: 'CJC-1295 + Ipamorelin Stack',
    description: 'Synergistic growth hormone secretagogue protocol for enhanced recovery, improved sleep quality, and body composition optimization.',
    category: 'Advanced',
    price: 9.99,
    duration_weeks: 12,
    products_needed: ['CJC-1295 DAC 2mg', 'Ipamorelin 5mg', 'Bacteriostatic Water'],
    dosage_instructions: 'CJC-1295: 2mg weekly. Ipamorelin: 200-300mcg 2-3x daily',
    frequency: 'CJC-1295 weekly, Ipamorelin before meals/bedtime',
    expected_results: 'Better sleep, increased lean mass, improved recovery, anti-aging benefits',
    side_effects: 'Water retention, tingling, increased hunger',
    storage_tips: 'Store peptides separately. Keep refrigerated',
    contraindications: 'Not for diabetics or those with pituitary disorders'
  },
  {
    id: '4',
    title: 'Epithalon Anti-Aging',
    description: 'Telomerase activation protocol for cellular rejuvenation and longevity. Based on decades of research in aging science.',
    category: 'Advanced',
    price: 9.99,
    duration_weeks: 8,
    products_needed: ['Epithalon 10mg', 'Bacteriostatic Water'],
    dosage_instructions: '5-10mg daily for 10-20 days, cycle every 4-6 months',
    frequency: 'Daily injection for cycle duration',
    expected_results: 'Improved sleep patterns, enhanced skin elasticity, increased energy',
    side_effects: 'Generally well tolerated. Rare injection site reactions',
    storage_tips: 'Store lyophilized peptide at room temperature. Refrigerate after reconstitution',
    contraindications: 'Consult physician if on immunosuppressants'
  },
  {
    id: '5',
    title: 'Melanotan II Tanning',
    description: 'Melanogenesis stimulation protocol for enhanced tanning response and skin pigmentation with minimal UV exposure.',
    category: 'Basic',
    price: 4.99,
    duration_weeks: 4,
    products_needed: ['Melanotan II 10mg', 'Bacteriostatic Water'],
    dosage_instructions: 'Start with 0.25mg, gradually increase to 0.5-1mg daily',
    frequency: 'Daily, preferably before UV exposure',
    expected_results: 'Noticeable tan within 1-2 weeks, enhanced tanning response',
    side_effects: 'Nausea, facial flushing, increased libido, darkening of moles',
    storage_tips: 'Protect from light. Refrigerate reconstituted solution',
    contraindications: 'History of melanoma or skin cancer'
  },
  {
    id: '6',
    title: 'PT-141 Protocol',
    description: 'Research protocol for studying melanocortin receptor activation and related physiological responses.',
    category: 'Basic',
    price: 4.99,
    duration_weeks: 2,
    products_needed: ['PT-141 10mg', 'Bacteriostatic Water'],
    dosage_instructions: '1-2mg subcutaneously, as needed',
    frequency: 'As needed, not more than once every 72 hours',
    expected_results: 'Effects typically observed within 4-6 hours of administration',
    side_effects: 'Nausea, flushing, headache',
    storage_tips: 'Refrigerate after reconstitution. Use within 30 days',
    contraindications: 'Cardiovascular conditions, uncontrolled hypertension'
  },
  {
    id: '7',
    title: 'Semax Cognitive Enhancement',
    description: 'Neuroprotective peptide protocol for cognitive enhancement, focus improvement, and mental clarity optimization.',
    category: 'Basic',
    price: 4.99,
    duration_weeks: 4,
    products_needed: ['Semax 0.1% Nasal Spray'],
    dosage_instructions: '2-3 drops per nostril, 2-3 times daily',
    frequency: 'Morning and afternoon, avoid evening use',
    expected_results: 'Improved focus, better memory recall, enhanced mental clarity',
    side_effects: 'Mild nasal irritation, rare headache',
    storage_tips: 'Store at room temperature. Keep away from heat',
    contraindications: 'Seizure disorders, bipolar disorder'
  },
  {
    id: '8',
    title: 'GHK-Cu Skin Regeneration',
    description: 'Copper peptide protocol for skin rejuvenation, wound healing, and collagen synthesis stimulation.',
    category: 'Advanced',
    price: 9.99,
    duration_weeks: 8,
    products_needed: ['GHK-Cu 50mg', 'Bacteriostatic Water'],
    dosage_instructions: '1-2mg subcutaneously daily, or topical application',
    frequency: 'Daily application or injection',
    expected_results: 'Improved skin texture, reduced fine lines, better wound healing',
    side_effects: 'Minimal. Possible injection site discoloration',
    storage_tips: 'Store in cool, dark place. Refrigerate after reconstitution',
    contraindications: 'Copper sensitivity or Wilson\'s disease'
  }
];

// ========== THEME ==========
const T = {
  bg: '#050810',
  bgSecondary: '#0c1221',
  card: '#111827',
  cardElevated: '#1a2235',
  cardBorder: '#1e293b',
  
  primary: '#3b82f6',
  primaryDark: '#2563eb',
  primaryGlow: '#3b82f620',
  
  secondary: '#8b5cf6',
  secondaryDark: '#7c3aed',
  
  success: '#10b981',
  successDim: '#065f46',
  successGlow: '#10b98120',
  
  warning: '#f59e0b',
  warningDim: '#92400e',
  
  danger: '#ef4444',
  dangerDim: '#7f1d1d',
  
  text: '#f8fafc',
  textSecondary: '#cbd5e1',
  textMuted: '#64748b',
  textDim: '#475569',
  
  white: '#ffffff',
  black: '#000000',
  
  gradient1: ['#1e40af', '#3b82f6'],
  gradient2: ['#7c3aed', '#a855f7'],
  gradient3: ['#059669', '#10b981'],
  gradientDark: ['#0f172a', '#1e293b'],
};

// ========== HOME SCREEN ==========
function HomeScreen({ goTo }) {
  const insets = useSafeAreaInsets();
  const [stats, setStats] = useState({ products: 0, protocols: 0, scans: 0 });
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const load = useCallback(async () => {
    try {
      const [prods, protos, hist] = await Promise.all([
        api.get('/products').catch(() => ({ data: [] })),
        api.get('/protocols').catch(() => ({ data: MOCK_PROTOCOLS })),
        AsyncStorage.getItem('vh').then(d => d ? JSON.parse(d) : []).catch(() => [])
      ]);
      const protocolCount = protos.data.length > 0 ? protos.data.length : MOCK_PROTOCOLS.length;
      setStats({ products: prods.data.length, protocols: protocolCount, scans: hist.length });
    } catch (e) { console.log(e); }
    setLoading(false);
    Animated.timing(fadeAnim, { toValue: 1, duration: 500, useNativeDriver: true }).start();
  }, [fadeAnim]);

  useEffect(() => { load(); }, [load]);

  const refresh = async () => { 
    setRefreshing(true); 
    await load(); 
    setRefreshing(false); 
  };

  const quickActions = [
    { 
      title: 'Verify Product', 
      subtitle: 'Scan QR or enter code', 
      iconName: 'shield-checkmark',
      tab: 'Scan',
      gradient: T.gradient1
    },
    { 
      title: 'Research Protocols', 
      subtitle: 'Browse dosage guides', 
      iconName: 'flask',
      tab: 'Protocols',
      gradient: T.gradient2
    },
    { 
      title: 'Scan History', 
      subtitle: 'View past verifications', 
      iconName: 'time',
      tab: 'History',
      gradient: T.gradient3
    },
  ];

  if (loading) {
    return (
      <View style={[styles.screen, styles.center]}>
        <ActivityIndicator size="large" color={T.primary} />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView 
      style={styles.screen} 
      contentContainerStyle={{ paddingBottom: 24 }}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor={T.primary} colors={[T.primary]} />
      }
      showsVerticalScrollIndicator={false}
    >
      <Animated.View style={{ opacity: fadeAnim }}>
        {/* Hero Section */}
        <LinearGradient
          colors={['#1e3a8a', '#3b82f6', '#7c3aed']}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.heroContainer}
        >
          <View style={styles.heroPattern}>
            {[...Array(6)].map((_, i) => (
              <View key={i} style={[styles.heroCircle, { 
                width: 100 + i * 40, 
                height: 100 + i * 40,
                opacity: 0.05 - i * 0.008,
                top: -20 - i * 15,
                right: -30 - i * 15,
              }]} />
            ))}
          </View>
          
          <View style={styles.heroContent}>
            <View style={styles.heroBadge}>
              <Ionicons name="diamond" size={12} color={T.white} />
              <Text style={styles.heroBadgeText}>PREMIUM RESEARCH</Text>
            </View>
            
            <Text style={styles.heroTitle}>Zurix Sciences</Text>
            <Text style={styles.heroSubtitle}>
              Peptide verification & research protocols at your fingertips
            </Text>
            
            <View style={styles.heroStatsRow}>
              <View style={styles.heroStat}>
                <Text style={styles.heroStatNumber}>{stats.products}</Text>
                <Text style={styles.heroStatLabel}>Products</Text>
              </View>
              <View style={styles.heroStatDivider} />
              <View style={styles.heroStat}>
                <Text style={styles.heroStatNumber}>{stats.protocols}</Text>
                <Text style={styles.heroStatLabel}>Protocols</Text>
              </View>
              <View style={styles.heroStatDivider} />
              <View style={styles.heroStat}>
                <Text style={styles.heroStatNumber}>{stats.scans}</Text>
                <Text style={styles.heroStatLabel}>Verified</Text>
              </View>
            </View>
          </View>
        </LinearGradient>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          
          {quickActions.map((action, index) => (
            <TouchableOpacity 
              key={index} 
              style={styles.actionCard}
              onPress={() => goTo(action.tab)}
              activeOpacity={0.7}
            >
              <LinearGradient
                colors={[action.gradient[0] + '15', action.gradient[1] + '08']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.actionCardGradient}
              >
                <View style={[styles.actionIconContainer, { backgroundColor: action.gradient[0] + '20' }]}>
                  <Ionicons name={action.iconName} size={26} color={action.gradient[1]} />
                </View>
                <View style={styles.actionTextContainer}>
                  <Text style={styles.actionTitle}>{action.title}</Text>
                  <Text style={styles.actionSubtitle}>{action.subtitle}</Text>
                </View>
                <Ionicons name="chevron-forward" size={20} color={T.textMuted} />
              </LinearGradient>
            </TouchableOpacity>
          ))}
        </View>

        {/* Info Banner */}
        <View style={styles.section}>
          <View style={styles.infoBanner}>
            <LinearGradient
              colors={['#f59e0b20', '#f59e0b08']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.infoBannerGradient}
            >
              <View style={styles.infoBannerIcon}>
                <Ionicons name="information-circle" size={24} color={T.warning} />
              </View>
              <Text style={styles.infoBannerText}>
                All products are intended for laboratory and research purposes only. Not for human consumption.
              </Text>
            </LinearGradient>
          </View>
        </View>

        {/* Website Link */}
        <View style={styles.section}>
          <TouchableOpacity 
            style={styles.websiteCard}
            onPress={() => openURL('https://zurixsciences.com')}
            activeOpacity={0.8}
          >
            <View style={styles.websiteCardInner}>
              <Ionicons name="globe-outline" size={24} color={T.primary} />
              <View style={{ flex: 1, marginLeft: 14 }}>
                <Text style={styles.websiteCardTitle}>Visit Our Website</Text>
                <Text style={styles.websiteCardUrl}>zurixsciences.com</Text>
              </View>
              <Feather name="external-link" size={18} color={T.textMuted} />
            </View>
          </TouchableOpacity>
        </View>
      </Animated.View>
    </ScrollView>
  );
}

// ========== SCAN/VERIFY SCREEN ==========
function ScanScreen() {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showScanner, setShowScanner] = useState(false);
  const [permission, requestPermission] = useCameraPermissions();
  const inputRef = useRef(null);
  const resultAnim = useRef(new Animated.Value(0)).current;
  const scannedRef = useRef(false);

  const verify = async (verifyCode) => {
    const c = (verifyCode || code).trim().toUpperCase();
    if (!c) { 
      Alert.alert('Code Required', 'Please enter a verification code to continue.');
      return; 
    }
    
    setLoading(true);
    setResult(null);
    resultAnim.setValue(0);
    
    try {
      const r = await api.post('/verify-product', { code: c });
      setResult(r.data);
      
      // Save to history
      const hist = JSON.parse(await AsyncStorage.getItem('vh') || '[]');
      hist.unshift({ ...r.data, code: c, timestamp: new Date().toISOString() });
      await AsyncStorage.setItem('vh', JSON.stringify(hist.slice(0, 100)));
      
      Animated.spring(resultAnim, { toValue: 1, useNativeDriver: true }).start();
    } catch (e) {
      setResult({ success: false, message: 'Network error. Please check your connection and try again.' });
      Animated.spring(resultAnim, { toValue: 1, useNativeDriver: true }).start();
    }
    setLoading(false);
  };

  const handleBarCodeScanned = ({ type, data }) => {
    if (scannedRef.current) return;
    scannedRef.current = true;
    
    setShowScanner(false);
    setCode(data.toUpperCase());
    
    // Small delay then verify
    setTimeout(() => {
      verify(data);
      scannedRef.current = false;
    }, 500);
  };

  const openScanner = async () => {
    if (!permission?.granted) {
      const { granted } = await requestPermission();
      if (!granted) {
        Alert.alert('Permission Required', 'Camera access is needed to scan QR codes.');
        return;
      }
    }
    scannedRef.current = false;
    setShowScanner(true);
  };

  const sampleCodes = ['ZX-ZE101208', 'ZX-BP050823', 'ZX-SE030409'];

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.screenPadding} showsVerticalScrollIndicator={false}>
      {/* QR Scanner Modal */}
      <Modal visible={showScanner} animationType="slide" onRequestClose={() => setShowScanner(false)}>
        <View style={styles.scannerContainer}>
          <CameraView
            style={styles.camera}
            facing="back"
            barcodeScannerSettings={{
              barcodeTypes: ['qr', 'code128', 'code39', 'ean13', 'ean8'],
            }}
            onBarcodeScanned={handleBarCodeScanned}
          >
            <View style={styles.scannerOverlay}>
              <View style={styles.scannerHeader}>
                <TouchableOpacity 
                  style={styles.scannerCloseBtn} 
                  onPress={() => setShowScanner(false)}
                >
                  <Ionicons name="close" size={28} color={T.white} />
                </TouchableOpacity>
                <Text style={styles.scannerTitle}>Scan QR Code</Text>
                <View style={{ width: 44 }} />
              </View>
              
              <View style={styles.scannerFrame}>
                <View style={[styles.scannerCorner, styles.scannerCornerTL]} />
                <View style={[styles.scannerCorner, styles.scannerCornerTR]} />
                <View style={[styles.scannerCorner, styles.scannerCornerBL]} />
                <View style={[styles.scannerCorner, styles.scannerCornerBR]} />
              </View>
              
              <Text style={styles.scannerHint}>
                Position the QR code within the frame
              </Text>
            </View>
          </CameraView>
        </View>
      </Modal>

      {/* Header */}
      <View style={styles.verifyHeader}>
        <View style={styles.verifyIconContainer}>
          <LinearGradient colors={T.gradient1} style={styles.verifyIconGradient}>
            <Ionicons name="shield-checkmark" size={32} color={T.white} />
          </LinearGradient>
        </View>
        <Text style={styles.verifyTitle}>Product Verification</Text>
        <Text style={styles.verifySubtitle}>
          Scan QR code or enter verification code to authenticate your product
        </Text>
      </View>

      {/* Scan QR Button */}
      <TouchableOpacity 
        style={styles.scanQRButton}
        onPress={openScanner}
        activeOpacity={0.8}
      >
        <LinearGradient colors={T.gradient2} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }} style={styles.scanQRButtonGradient}>
          <Ionicons name="qr-code" size={24} color={T.white} style={{ marginRight: 12 }} />
          <Text style={styles.scanQRButtonText}>Scan QR Code</Text>
          <Ionicons name="camera" size={20} color={T.white} style={{ marginLeft: 'auto' }} />
        </LinearGradient>
      </TouchableOpacity>

      {/* Divider */}
      <View style={styles.dividerContainer}>
        <View style={styles.dividerLine} />
        <Text style={styles.dividerText}>OR</Text>
        <View style={styles.dividerLine} />
      </View>

      {/* Input Section */}
      <View style={styles.inputSection}>
        <Text style={styles.inputLabel}>ENTER CODE MANUALLY</Text>
        <View style={styles.inputWrapper}>
          <Ionicons name="key-outline" size={20} color={T.textMuted} style={styles.inputIcon} />
          <TextInput
            ref={inputRef}
            style={styles.input}
            placeholder="e.g. ZX-ZE101208"
            placeholderTextColor={T.textDim}
            value={code}
            onChangeText={t => { setCode(t.toUpperCase()); setResult(null); }}
            autoCapitalize="characters"
            autoCorrect={false}
          />
          {code.length > 0 && (
            <TouchableOpacity onPress={() => { setCode(''); setResult(null); }} style={styles.inputClear}>
              <Ionicons name="close-circle" size={20} color={T.textMuted} />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Verify Button */}
      <TouchableOpacity 
        style={[styles.verifyButton, loading && styles.verifyButtonDisabled]} 
        onPress={() => verify()} 
        disabled={loading}
        activeOpacity={0.8}
      >
        <LinearGradient colors={T.gradient1} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }} style={styles.verifyButtonGradient}>
          {loading ? (
            <ActivityIndicator color={T.white} size="small" />
          ) : (
            <>
              <Ionicons name="checkmark-shield" size={22} color={T.white} style={{ marginRight: 10 }} />
              <Text style={styles.verifyButtonText}>Verify Product</Text>
            </>
          )}
        </LinearGradient>
      </TouchableOpacity>

      {/* Sample Codes */}
      <View style={styles.sampleSection}>
        <Text style={styles.sampleLabel}>Try sample codes:</Text>
        <View style={styles.sampleCodesRow}>
          {sampleCodes.map((c, i) => (
            <TouchableOpacity 
              key={i} 
              style={styles.sampleCode}
              onPress={() => { setCode(c); setResult(null); }}
              activeOpacity={0.7}
            >
              <Text style={styles.sampleCodeText}>{c}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Result */}
      {result && (
        <Animated.View style={[styles.resultContainer, { 
          opacity: resultAnim,
          transform: [{ translateY: resultAnim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }]
        }]}>
          <View style={[styles.resultCard, { borderLeftColor: result.success ? T.success : T.danger }]}>
            <View style={styles.resultHeader}>
              <View style={[styles.resultIcon, { backgroundColor: result.success ? T.successGlow : T.danger + '20' }]}>
                <Ionicons 
                  name={result.success ? "checkmark-circle" : "close-circle"} 
                  size={28} 
                  color={result.success ? T.success : T.danger} 
                />
              </View>
              <View style={styles.resultHeaderText}>
                <Text style={[styles.resultStatus, { color: result.success ? T.success : T.danger }]}>
                  {result.success ? 'VERIFIED' : 'NOT VERIFIED'}
                </Text>
                <Text style={styles.resultMessage}>{result.message}</Text>
              </View>
            </View>

            {result.product && (
              <View style={styles.resultDetails}>
                {[
                  { icon: 'flask-outline', label: 'Product', value: result.product.name },
                  { icon: 'barcode-outline', label: 'Batch', value: result.product.batch_number },
                  { icon: 'diamond-outline', label: 'Purity', value: result.product.purity },
                  { icon: 'calendar-outline', label: 'Expiry', value: result.product.expiry_date },
                  { icon: 'folder-outline', label: 'Category', value: result.product.category },
                ].map((item, i) => (
                  <View key={i} style={styles.resultRow}>
                    <View style={styles.resultRowLeft}>
                      <Ionicons name={item.icon} size={16} color={T.textMuted} />
                      <Text style={styles.resultRowLabel}>{item.label}</Text>
                    </View>
                    <Text style={styles.resultRowValue}>{item.value || 'N/A'}</Text>
                  </View>
                ))}
                
                {result.verification_count > 3 && (
                  <View style={styles.warningBanner}>
                    <Ionicons name="warning" size={18} color={T.warning} />
                    <Text style={styles.warningText}>
                      This product has been verified {result.verification_count} times. 
                      Multiple verifications may indicate counterfeit risk.
                    </Text>
                  </View>
                )}
              </View>
            )}
          </View>
        </Animated.View>
      )}
      
      <View style={{ height: 24 }} />
    </ScrollView>
  );
}

// ========== PROTOCOLS SCREEN ==========
function ProtocolsScreen() {
  const [protocols, setProtocols] = useState([]);
  const [filter, setFilter] = useState('All');
  const [expanded, setExpanded] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/protocols')
      .then(r => { 
        // Use API data if available, otherwise use mock data
        const data = r.data && r.data.length > 0 ? r.data : MOCK_PROTOCOLS;
        setProtocols(data); 
        setLoading(false); 
      })
      .catch(() => {
        // On error, use mock data
        setProtocols(MOCK_PROTOCOLS);
        setLoading(false);
      });
  }, []);

  const filtered = filter === 'All' ? protocols : protocols.filter(p => p.category === filter);

  if (loading) {
    return (
      <View style={[styles.screen, styles.center]}>
        <ActivityIndicator size="large" color={T.primary} />
        <Text style={styles.loadingText}>Loading protocols...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.screen} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.protocolsHeader}>
        <Text style={styles.protocolsTitle}>Research Protocols</Text>
        <Text style={styles.protocolsSubtitle}>Browse peptide research protocols and dosage guides</Text>
      </View>

      {/* Filter Tabs */}
      <View style={styles.filterContainer}>
        {['All', 'Basic', 'Advanced'].map(f => (
          <TouchableOpacity 
            key={f} 
            style={[styles.filterTab, filter === f && styles.filterTabActive]}
            onPress={() => setFilter(f)}
            activeOpacity={0.7}
          >
            {filter === f && (
              <LinearGradient colors={T.gradient1} style={StyleSheet.absoluteFill} />
            )}
            <Text style={[styles.filterTabText, filter === f && styles.filterTabTextActive]}>{f}</Text>
            {f !== 'All' && (
              <Text style={[styles.filterPrice, filter === f && styles.filterPriceActive]}>
                {f === 'Basic' ? '$4.99' : '$9.99'}
              </Text>
            )}
          </TouchableOpacity>
        ))}
      </View>

      {/* Protocols List */}
      <View style={styles.protocolsList}>
        {filtered.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="flask-outline" size={48} color={T.textMuted} />
            <Text style={styles.emptyTitle}>No Protocols Found</Text>
            <Text style={styles.emptyText}>Try selecting a different category</Text>
          </View>
        ) : (
          filtered.map((protocol, index) => (
            <TouchableOpacity 
              key={protocol.id || index}
              style={styles.protocolCard}
              onPress={() => setExpanded(expanded === protocol.id ? null : protocol.id)}
              activeOpacity={0.8}
            >
              <View style={styles.protocolCardHeader}>
                <View style={[styles.categoryBadge, { 
                  backgroundColor: protocol.category === 'Basic' ? T.success + '20' : T.secondary + '20' 
                }]}>
                  <Text style={[styles.categoryBadgeText, { 
                    color: protocol.category === 'Basic' ? T.success : T.secondary 
                  }]}>
                    {protocol.category}
                  </Text>
                </View>
                <Text style={styles.protocolPrice}>${protocol.price?.toFixed(2)}</Text>
              </View>
              
              <Text style={styles.protocolTitle}>{protocol.title}</Text>
              <Text style={styles.protocolDesc} numberOfLines={expanded === protocol.id ? undefined : 2}>
                {protocol.description}
              </Text>
              
              <View style={styles.protocolMeta}>
                <View style={styles.protocolMetaItem}>
                  <Ionicons name="time-outline" size={14} color={T.textMuted} />
                  <Text style={styles.protocolMetaText}>{protocol.duration_weeks} weeks</Text>
                </View>
                <View style={styles.protocolMetaItem}>
                  <Ionicons name="flask-outline" size={14} color={T.textMuted} />
                  <Text style={styles.protocolMetaText}>{protocol.products_needed?.length || 0} products</Text>
                </View>
              </View>

              {expanded === protocol.id && (
                <View style={styles.protocolExpanded}>
                  {[
                    { title: 'Dosage Instructions', text: protocol.dosage_instructions, icon: 'medical' },
                    { title: 'Frequency', text: protocol.frequency, icon: 'refresh' },
                    { title: 'Expected Results', text: protocol.expected_results, icon: 'trending-up' },
                    { title: 'Side Effects', text: protocol.side_effects, icon: 'warning' },
                    { title: 'Storage Tips', text: protocol.storage_tips, icon: 'snow' },
                  ].map((item, i) => item.text ? (
                    <View key={i} style={styles.protocolExpandedItem}>
                      <View style={styles.protocolExpandedHeader}>
                        <Ionicons name={item.icon} size={16} color={T.primary} />
                        <Text style={styles.protocolExpandedTitle}>{item.title}</Text>
                      </View>
                      <Text style={styles.protocolExpandedText}>{item.text}</Text>
                    </View>
                  ) : null)}
                  
                  {protocol.products_needed?.length > 0 && (
                    <View style={styles.protocolExpandedItem}>
                      <View style={styles.protocolExpandedHeader}>
                        <Ionicons name="list" size={16} color={T.primary} />
                        <Text style={styles.protocolExpandedTitle}>Products Needed</Text>
                      </View>
                      {protocol.products_needed.map((prod, i) => (
                        <View key={i} style={styles.productNeededItem}>
                          <View style={styles.productNeededDot} />
                          <Text style={styles.protocolExpandedText}>{prod}</Text>
                        </View>
                      ))}
                    </View>
                  )}

                  {protocol.contraindications && (
                    <View style={styles.warningBanner}>
                      <Ionicons name="warning" size={18} color={T.warning} />
                      <Text style={styles.warningText}>
                        Contraindications: {protocol.contraindications}
                      </Text>
                    </View>
                  )}
                </View>
              )}
              
              <View style={styles.protocolExpandHint}>
                <Ionicons 
                  name={expanded === protocol.id ? "chevron-up" : "chevron-down"} 
                  size={18} 
                  color={T.textMuted} 
                />
                <Text style={styles.protocolExpandHintText}>
                  {expanded === protocol.id ? 'Collapse' : 'View details'}
                </Text>
              </View>
            </TouchableOpacity>
          ))
        )}
      </View>
      
      <View style={{ height: 24 }} />
    </ScrollView>
  );
}

// ========== HISTORY SCREEN ==========
function HistoryScreen() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    AsyncStorage.getItem('vh')
      .then(d => { setHistory(d ? JSON.parse(d) : []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const stats = {
    total: history.length,
    verified: history.filter(h => h.success).length,
    failed: history.filter(h => !h.success).length,
  };

  if (loading) {
    return (
      <View style={[styles.screen, styles.center]}>
        <ActivityIndicator size="large" color={T.primary} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.screenPadding} showsVerticalScrollIndicator={false}>
      {/* Stats Cards */}
      <View style={styles.statsContainer}>
        {[
          { label: 'Total Scans', value: stats.total, color: T.primary, icon: 'scan' },
          { label: 'Verified', value: stats.verified, color: T.success, icon: 'checkmark-circle' },
          { label: 'Failed', value: stats.failed, color: T.danger, icon: 'close-circle' },
        ].map((stat, i) => (
          <View key={i} style={styles.statCard}>
            <View style={[styles.statIconContainer, { backgroundColor: stat.color + '20' }]}>
              <Ionicons name={stat.icon} size={20} color={stat.color} />
            </View>
            <Text style={[styles.statValue, { color: stat.color }]}>{stat.value}</Text>
            <Text style={styles.statLabel}>{stat.label}</Text>
          </View>
        ))}
      </View>

      {/* History List */}
      {history.length === 0 ? (
        <View style={styles.emptyState}>
          <View style={styles.emptyIconContainer}>
            <Ionicons name="time-outline" size={48} color={T.textMuted} />
          </View>
          <Text style={styles.emptyTitle}>No History Yet</Text>
          <Text style={styles.emptyText}>Your verification history will appear here</Text>
        </View>
      ) : (
        <View style={styles.historyList}>
          <Text style={styles.historyListTitle}>Recent Verifications</Text>
          {history.map((item, i) => (
            <View key={i} style={styles.historyCard}>
              <View style={[styles.historyStatusIndicator, { 
                backgroundColor: item.success ? T.success : T.danger 
              }]} />
              <View style={styles.historyCardContent}>
                <Text style={styles.historyProductName}>
                  {item.product?.name || 'Unknown Product'}
                </Text>
                <View style={styles.historyCodeRow}>
                  <Ionicons name="key-outline" size={12} color={T.primary} />
                  <Text style={styles.historyCode}>{item.code}</Text>
                </View>
                <View style={styles.historyTimeRow}>
                  <Ionicons name="time-outline" size={12} color={T.textMuted} />
                  <Text style={styles.historyTime}>
                    {new Date(item.timestamp).toLocaleString()}
                  </Text>
                </View>
              </View>
              <View style={[styles.historyStatusBadge, {
                backgroundColor: item.success ? T.successDim : T.dangerDim
              }]}>
                <Text style={[styles.historyStatusText, {
                  color: item.success ? T.success : T.danger
                }]}>
                  {item.success ? 'OK' : 'FAIL'}
                </Text>
              </View>
            </View>
          ))}
        </View>
      )}
      
      <View style={{ height: 24 }} />
    </ScrollView>
  );
}

// ========== PROFILE SCREEN ==========
function ProfileScreen() {
  const clearHistory = () => {
    Alert.alert(
      'Clear History', 
      'This will remove all verification history from this device. This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Clear All', 
          style: 'destructive', 
          onPress: async () => {
            await AsyncStorage.removeItem('vh');
            Alert.alert('Done', 'Verification history has been cleared.');
          }
        }
      ]
    );
  };

  const menuItems = [
    { 
      title: 'Visit Website', 
      subtitle: 'zurixsciences.com', 
      icon: 'globe-outline',
      color: T.primary,
      action: () => Linking.openURL('https://zurixsciences.com')
    },
    { 
      title: 'Contact Support', 
      subtitle: 'Get help via WhatsApp', 
      icon: 'logo-whatsapp',
      color: T.success,
      action: () => Linking.openURL('https://wa.me/85212345678?text=Hello%20Zurix%20Sciences')
    },
    { 
      title: 'Clear Scan History', 
      subtitle: 'Remove local verification data', 
      icon: 'trash-outline',
      color: T.danger,
      action: clearHistory
    },
  ];

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.screenPadding} showsVerticalScrollIndicator={false}>
      {/* Profile Header */}
      <View style={styles.profileHeader}>
        <LinearGradient colors={T.gradient1} style={styles.profileAvatar}>
          <Text style={styles.profileAvatarText}>Z</Text>
        </LinearGradient>
        <Text style={styles.profileName}>Zurix Sciences</Text>
        <Text style={styles.profileTagline}>Premium Peptide Research</Text>
        <View style={styles.profileVersionBadge}>
          <Text style={styles.profileVersion}>v1.0.0</Text>
        </View>
      </View>

      {/* Menu Items */}
      <View style={styles.menuSection}>
        <Text style={styles.menuSectionTitle}>Settings & Support</Text>
        {menuItems.map((item, i) => (
          <TouchableOpacity 
            key={i} 
            style={styles.menuItem}
            onPress={item.action}
            activeOpacity={0.7}
          >
            <View style={[styles.menuIconContainer, { backgroundColor: item.color + '20' }]}>
              <Ionicons name={item.icon} size={20} color={item.color} />
            </View>
            <View style={styles.menuTextContainer}>
              <Text style={styles.menuItemTitle}>{item.title}</Text>
              <Text style={styles.menuItemSubtitle}>{item.subtitle}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={T.textMuted} />
          </TouchableOpacity>
        ))}
      </View>

      {/* About Section */}
      <View style={styles.aboutCard}>
        <View style={styles.aboutHeader}>
          <Ionicons name="information-circle" size={20} color={T.primary} />
          <Text style={styles.aboutTitle}>About</Text>
        </View>
        <Text style={styles.aboutText}>
          Zurix Sciences mobile application for product verification and peptide research protocols. 
          Scan product QR codes or enter verification codes to confirm product authenticity.
        </Text>
      </View>

      {/* Disclaimer */}
      <View style={styles.disclaimerCard}>
        <LinearGradient colors={['#f59e0b15', '#f59e0b08']} style={styles.disclaimerGradient}>
          <Ionicons name="warning" size={20} color={T.warning} />
          <Text style={styles.disclaimerText}>
            FOR RESEARCH USE ONLY - All products are intended for laboratory and research applications only. 
            Not for human consumption, veterinary use, or diagnostic purposes.
          </Text>
        </LinearGradient>
      </View>
      
      <View style={{ height: 24 }} />
    </ScrollView>
  );
}

// ========== MAIN APP ==========
function MainApp() {
  const insets = useSafeAreaInsets();
  const [activeTab, setActiveTab] = useState('Home');

  const tabs = [
    { key: 'Home', label: 'Home', icon: 'home' },
    { key: 'Scan', label: 'Verify', icon: 'shield-checkmark' },
    { key: 'Protocols', label: 'Protocols', icon: 'flask' },
    { key: 'History', label: 'History', icon: 'time' },
    { key: 'Profile', label: 'Profile', icon: 'person' },
  ];

  const renderScreen = () => {
    switch (activeTab) {
      case 'Home': return <HomeScreen goTo={setActiveTab} />;
      case 'Scan': return <ScanScreen />;
      case 'Protocols': return <ProtocolsScreen />;
      case 'History': return <HistoryScreen />;
      case 'Profile': return <ProfileScreen />;
      default: return <HomeScreen goTo={setActiveTab} />;
    }
  };

  const getTitle = () => {
    switch (activeTab) {
      case 'Home': return 'Zurix Sciences';
      case 'Scan': return 'Verify Product';
      default: return activeTab;
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: T.bg }]}>
      <StatusBar style="light" />
      
      {/* Top Bar */}
      <View style={[styles.topBar, { paddingTop: insets.top + 12 }]}>
        <Text style={styles.topBarTitle}>{getTitle()}</Text>
        {activeTab === 'Home' && (
          <View style={styles.topBarBadge}>
            <Ionicons name="diamond" size={12} color={T.primary} />
          </View>
        )}
      </View>

      {/* Content */}
      <View style={styles.content}>
        {renderScreen()}
      </View>

      {/* Bottom Navigation */}
      <View style={[styles.bottomNav, { paddingBottom: insets.bottom + 8 }]}>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.key;
          return (
            <TouchableOpacity
              key={tab.key}
              style={styles.bottomNavItem}
              onPress={() => setActiveTab(tab.key)}
              activeOpacity={0.7}
            >
              <View style={[styles.bottomNavIconContainer, isActive && styles.bottomNavIconActive]}>
                <Ionicons 
                  name={isActive ? tab.icon : `${tab.icon}-outline`}
                  size={22} 
                  color={isActive ? T.primary : T.textMuted} 
                />
              </View>
              <Text style={[styles.bottomNavLabel, isActive && styles.bottomNavLabelActive]}>
                {tab.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

// ========== ROOT APP ==========
export default function App() {
  return (
    <SafeAreaProvider>
      <MainApp />
    </SafeAreaProvider>
  );
}

// ========== STYLES ==========
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  screen: {
    flex: 1,
    backgroundColor: T.bg,
  },
  screenPadding: {
    padding: 16,
  },
  center: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: T.textMuted,
    marginTop: 12,
    fontSize: 14,
  },

  // Top Bar
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingBottom: 14,
    backgroundColor: T.bg,
    borderBottomWidth: 1,
    borderBottomColor: T.cardBorder,
  },
  topBarTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: T.text,
    letterSpacing: 0.3,
  },
  topBarBadge: {
    backgroundColor: T.primaryGlow,
    padding: 6,
    borderRadius: 8,
  },

  // Content
  content: {
    flex: 1,
  },

  // Bottom Navigation
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: T.card,
    borderTopWidth: 1,
    borderTopColor: T.cardBorder,
    paddingTop: 8,
  },
  bottomNavItem: {
    flex: 1,
    alignItems: 'center',
    gap: 4,
  },
  bottomNavIconContainer: {
    padding: 6,
    borderRadius: 12,
  },
  bottomNavIconActive: {
    backgroundColor: T.primaryGlow,
  },
  bottomNavLabel: {
    fontSize: 11,
    fontWeight: '500',
    color: T.textMuted,
  },
  bottomNavLabelActive: {
    color: T.primary,
    fontWeight: '600',
  },

  // Hero Section
  heroContainer: {
    margin: 16,
    borderRadius: 24,
    overflow: 'hidden',
  },
  heroPattern: {
    ...StyleSheet.absoluteFillObject,
    overflow: 'hidden',
  },
  heroCircle: {
    position: 'absolute',
    borderRadius: 1000,
    backgroundColor: T.white,
  },
  heroContent: {
    padding: 24,
  },
  heroBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(255,255,255,0.15)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    gap: 6,
    marginBottom: 12,
  },
  heroBadgeText: {
    color: T.white,
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 1,
  },
  heroTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: T.white,
    letterSpacing: 0.5,
  },
  heroSubtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 8,
    lineHeight: 20,
  },
  heroStatsRow: {
    flexDirection: 'row',
    backgroundColor: 'rgba(0,0,0,0.2)',
    borderRadius: 16,
    padding: 16,
    marginTop: 20,
  },
  heroStat: {
    flex: 1,
    alignItems: 'center',
  },
  heroStatNumber: {
    fontSize: 24,
    fontWeight: '800',
    color: T.white,
  },
  heroStatLabel: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.7)',
    marginTop: 2,
  },
  heroStatDivider: {
    width: 1,
    backgroundColor: 'rgba(255,255,255,0.2)',
    marginHorizontal: 8,
  },

  // Section
  section: {
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: T.text,
    marginBottom: 14,
  },

  // Action Cards
  actionCard: {
    marginBottom: 10,
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: T.cardBorder,
  },
  actionCardGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: T.card,
  },
  actionIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  actionTextContainer: {
    flex: 1,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: T.text,
  },
  actionSubtitle: {
    fontSize: 13,
    color: T.textMuted,
    marginTop: 2,
  },

  // Info Banner
  infoBanner: {
    borderRadius: 14,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: T.warning + '30',
  },
  infoBannerGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
  },
  infoBannerIcon: {
    marginRight: 12,
  },
  infoBannerText: {
    flex: 1,
    fontSize: 12,
    color: T.textSecondary,
    lineHeight: 18,
  },

  // Website Card
  websiteCard: {
    backgroundColor: T.card,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: T.cardBorder,
  },
  websiteCardInner: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
  },
  websiteCardTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: T.text,
  },
  websiteCardUrl: {
    fontSize: 13,
    color: T.primary,
    marginTop: 2,
  },

  // Verify Screen
  verifyHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  verifyIconContainer: {
    marginBottom: 16,
  },
  verifyIconGradient: {
    width: 72,
    height: 72,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  verifyTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: T.text,
    marginBottom: 8,
  },
  verifySubtitle: {
    fontSize: 14,
    color: T.textMuted,
    textAlign: 'center',
    lineHeight: 20,
    paddingHorizontal: 16,
  },

  // Scan QR Button
  scanQRButton: {
    borderRadius: 14,
    overflow: 'hidden',
    marginBottom: 20,
  },
  scanQRButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 18,
    paddingHorizontal: 20,
  },
  scanQRButtonText: {
    fontSize: 17,
    fontWeight: '700',
    color: T.white,
  },

  // Divider
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: T.cardBorder,
  },
  dividerText: {
    color: T.textMuted,
    fontSize: 12,
    fontWeight: '600',
    paddingHorizontal: 16,
  },

  // Scanner
  scannerContainer: {
    flex: 1,
    backgroundColor: T.black,
  },
  camera: {
    flex: 1,
  },
  scannerOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  scannerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  scannerCloseBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  scannerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: T.white,
  },
  scannerFrame: {
    width: 250,
    height: 250,
    alignSelf: 'center',
    marginTop: 40,
  },
  scannerCorner: {
    position: 'absolute',
    width: 40,
    height: 40,
    borderColor: T.primary,
  },
  scannerCornerTL: {
    top: 0,
    left: 0,
    borderTopWidth: 4,
    borderLeftWidth: 4,
    borderTopLeftRadius: 12,
  },
  scannerCornerTR: {
    top: 0,
    right: 0,
    borderTopWidth: 4,
    borderRightWidth: 4,
    borderTopRightRadius: 12,
  },
  scannerCornerBL: {
    bottom: 0,
    left: 0,
    borderBottomWidth: 4,
    borderLeftWidth: 4,
    borderBottomLeftRadius: 12,
  },
  scannerCornerBR: {
    bottom: 0,
    right: 0,
    borderBottomWidth: 4,
    borderRightWidth: 4,
    borderBottomRightRadius: 12,
  },
  scannerHint: {
    color: T.white,
    fontSize: 14,
    textAlign: 'center',
    marginTop: 30,
    opacity: 0.8,
  },

  // Input Section
  inputSection: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: T.textMuted,
    letterSpacing: 1,
    marginBottom: 10,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: T.card,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: T.cardBorder,
    paddingHorizontal: 16,
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    fontSize: 18,
    color: T.text,
    paddingVertical: 16,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    letterSpacing: 1,
  },
  inputClear: {
    padding: 4,
  },

  // Verify Button
  verifyButton: {
    borderRadius: 14,
    overflow: 'hidden',
    marginBottom: 20,
  },
  verifyButtonDisabled: {
    opacity: 0.7,
  },
  verifyButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
  },
  verifyButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: T.white,
  },

  // Sample Codes
  sampleSection: {
    marginBottom: 20,
  },
  sampleLabel: {
    fontSize: 13,
    color: T.textMuted,
    marginBottom: 10,
  },
  sampleCodesRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  sampleCode: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    backgroundColor: T.primaryGlow,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: T.primary + '30',
  },
  sampleCodeText: {
    fontSize: 13,
    fontWeight: '600',
    color: T.primary,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },

  // Result
  resultContainer: {
    marginTop: 8,
  },
  resultCard: {
    backgroundColor: T.card,
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: T.cardBorder,
    borderLeftWidth: 4,
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  resultIcon: {
    width: 48,
    height: 48,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  resultHeaderText: {
    flex: 1,
  },
  resultStatus: {
    fontSize: 14,
    fontWeight: '800',
    letterSpacing: 1,
  },
  resultMessage: {
    fontSize: 13,
    color: T.textMuted,
    marginTop: 4,
  },
  resultDetails: {
    backgroundColor: T.cardElevated,
    borderRadius: 12,
    padding: 14,
  },
  resultRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: T.cardBorder,
  },
  resultRowLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  resultRowLabel: {
    fontSize: 13,
    color: T.textMuted,
  },
  resultRowValue: {
    fontSize: 13,
    fontWeight: '600',
    color: T.text,
  },

  // Warning Banner
  warningBanner: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: T.warning + '15',
    padding: 14,
    borderRadius: 10,
    marginTop: 12,
    gap: 10,
  },
  warningText: {
    flex: 1,
    fontSize: 12,
    color: T.textSecondary,
    lineHeight: 18,
  },

  // Protocols Screen
  protocolsHeader: {
    padding: 16,
    paddingBottom: 8,
  },
  protocolsTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: T.text,
    marginBottom: 6,
  },
  protocolsSubtitle: {
    fontSize: 14,
    color: T.textMuted,
    lineHeight: 20,
  },

  // Filter Tabs
  filterContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    gap: 10,
    marginBottom: 16,
  },
  filterTab: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: T.card,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: T.cardBorder,
    overflow: 'hidden',
  },
  filterTabActive: {
    borderColor: T.primary,
  },
  filterTabText: {
    fontSize: 14,
    fontWeight: '600',
    color: T.textMuted,
  },
  filterTabTextActive: {
    color: T.white,
  },
  filterPrice: {
    fontSize: 11,
    color: T.textDim,
    marginTop: 2,
  },
  filterPriceActive: {
    color: 'rgba(255,255,255,0.7)',
  },

  // Protocols List
  protocolsList: {
    paddingHorizontal: 16,
  },
  protocolCard: {
    backgroundColor: T.card,
    borderRadius: 16,
    padding: 18,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: T.cardBorder,
  },
  protocolCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  categoryBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  categoryBadgeText: {
    fontSize: 11,
    fontWeight: '700',
  },
  protocolPrice: {
    fontSize: 18,
    fontWeight: '700',
    color: T.primary,
  },
  protocolTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: T.text,
    marginBottom: 6,
  },
  protocolDesc: {
    fontSize: 14,
    color: T.textMuted,
    lineHeight: 20,
  },
  protocolMeta: {
    flexDirection: 'row',
    gap: 16,
    marginTop: 12,
  },
  protocolMetaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  protocolMetaText: {
    fontSize: 13,
    color: T.textMuted,
  },
  protocolExpanded: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: T.cardBorder,
  },
  protocolExpandedItem: {
    marginBottom: 16,
  },
  protocolExpandedHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 6,
  },
  protocolExpandedTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: T.primary,
  },
  protocolExpandedText: {
    fontSize: 13,
    color: T.textSecondary,
    lineHeight: 20,
  },
  productNeededItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 6,
    gap: 8,
  },
  productNeededDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: T.primary,
  },
  protocolExpandHint: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    marginTop: 12,
  },
  protocolExpandHintText: {
    fontSize: 12,
    color: T.textMuted,
  },

  // Empty State
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyIconContainer: {
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: T.text,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 14,
    color: T.textMuted,
    textAlign: 'center',
  },

  // Stats Container
  statsContainer: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    backgroundColor: T.card,
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: T.cardBorder,
  },
  statIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
  },
  statValue: {
    fontSize: 24,
    fontWeight: '800',
  },
  statLabel: {
    fontSize: 11,
    color: T.textMuted,
    marginTop: 4,
  },

  // History List
  historyList: {
    marginTop: 8,
  },
  historyListTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: T.text,
    marginBottom: 14,
  },
  historyCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: T.card,
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: T.cardBorder,
  },
  historyStatusIndicator: {
    width: 4,
    height: '100%',
    minHeight: 50,
    borderRadius: 2,
    marginRight: 14,
  },
  historyCardContent: {
    flex: 1,
  },
  historyProductName: {
    fontSize: 15,
    fontWeight: '600',
    color: T.text,
    marginBottom: 4,
  },
  historyCodeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 4,
  },
  historyCode: {
    fontSize: 12,
    fontWeight: '600',
    color: T.primary,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
  },
  historyTimeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  historyTime: {
    fontSize: 12,
    color: T.textMuted,
  },
  historyStatusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  historyStatusText: {
    fontSize: 11,
    fontWeight: '800',
  },

  // Profile Screen
  profileHeader: {
    alignItems: 'center',
    backgroundColor: T.card,
    borderRadius: 24,
    padding: 28,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: T.cardBorder,
  },
  profileAvatar: {
    width: 80,
    height: 80,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  profileAvatarText: {
    fontSize: 32,
    fontWeight: '800',
    color: T.white,
  },
  profileName: {
    fontSize: 22,
    fontWeight: '700',
    color: T.text,
    marginBottom: 4,
  },
  profileTagline: {
    fontSize: 14,
    color: T.textMuted,
    marginBottom: 12,
  },
  profileVersionBadge: {
    backgroundColor: T.cardElevated,
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 20,
  },
  profileVersion: {
    fontSize: 12,
    color: T.textMuted,
    fontWeight: '600',
  },

  // Menu Section
  menuSection: {
    marginBottom: 20,
  },
  menuSectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: T.text,
    marginBottom: 14,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: T.card,
    borderRadius: 14,
    padding: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: T.cardBorder,
  },
  menuIconContainer: {
    width: 44,
    height: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  menuTextContainer: {
    flex: 1,
  },
  menuItemTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: T.text,
  },
  menuItemSubtitle: {
    fontSize: 13,
    color: T.textMuted,
    marginTop: 2,
  },

  // About Card
  aboutCard: {
    backgroundColor: T.card,
    borderRadius: 16,
    padding: 18,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: T.cardBorder,
  },
  aboutHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 10,
  },
  aboutTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: T.text,
  },
  aboutText: {
    fontSize: 13,
    color: T.textMuted,
    lineHeight: 20,
  },

  // Disclaimer Card
  disclaimerCard: {
    borderRadius: 14,
    overflow: 'hidden',
  },
  disclaimerGradient: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 16,
    gap: 12,
    borderWidth: 1,
    borderColor: T.warning + '30',
    borderRadius: 14,
  },
  disclaimerText: {
    flex: 1,
    fontSize: 12,
    color: T.textSecondary,
    lineHeight: 18,
  },
});
