import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ScrollView, TextInput,
  Alert, RefreshControl, Dimensions, Linking, ActivityIndicator, Animated, Platform, Modal, Image
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons, MaterialCommunityIcons, Feather, FontAwesome5 } from '@expo/vector-icons';
import { CameraView, useCameraPermissions } from 'expo-camera';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'https://www.zurixsciences.com/api';
const { width, height } = Dimensions.get('window');
const api = axios.create({ baseURL: API_URL, timeout: 10000 });

// ========== CONSTANTS ==========
const WHATSAPP_SWITZERLAND = '+41791234567';
const WHATSAPP_ORDER = '+85212345678'; // For orders

const CRYPTO_WALLETS = {
  USDT: { address: 'TXqHLk8gZ9nKMYhW5v2xPjR3sBfE7cNmD1', network: 'TRC20' },
  BTC: { address: 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh', network: 'Bitcoin' },
  XMR: { address: '48daf1rG3hE1Txapk3URrHBLmJPP4xLMrN7ZPZQPqHJZRc8Yfzh8CrSVxvnULQcXhT8PTMW9mWNpLsNCXnP8W1oY1PF3nK', network: 'Monero' },
  SOL: { address: '7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU', network: 'Solana' },
};

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

const openWhatsApp = (number, message) => {
  const url = `https://wa.me/${number}?text=${encodeURIComponent(message)}`;
  openURL(url);
};

// ========== MOCK PROTOCOLS ==========
const MOCK_PROTOCOLS = [
  {
    id: '1',
    title: 'BPC-157 Recovery Protocol',
    description: 'A comprehensive healing protocol designed to accelerate tissue repair and reduce inflammation.',
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
    description: 'Advanced protocol for deep tissue healing and muscle recovery.',
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
    description: 'Synergistic growth hormone secretagogue protocol for enhanced recovery.',
    category: 'Advanced',
    price: 9.99,
    duration_weeks: 12,
    products_needed: ['CJC-1295 DAC 2mg', 'Ipamorelin 5mg', 'Bacteriostatic Water'],
    dosage_instructions: 'CJC-1295: 2mg weekly. Ipamorelin: 200-300mcg 2-3x daily',
    frequency: 'CJC-1295 weekly, Ipamorelin before meals/bedtime',
    expected_results: 'Better sleep, increased lean mass, improved recovery',
    side_effects: 'Water retention, tingling, increased hunger',
    storage_tips: 'Store peptides separately. Keep refrigerated',
    contraindications: 'Not for diabetics or those with pituitary disorders'
  },
  {
    id: '4',
    title: 'Epithalon Anti-Aging',
    description: 'Telomerase activation protocol for cellular rejuvenation and longevity.',
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
    description: 'Melanogenesis stimulation protocol for enhanced tanning response.',
    category: 'Basic',
    price: 4.99,
    duration_weeks: 4,
    products_needed: ['Melanotan II 10mg', 'Bacteriostatic Water'],
    dosage_instructions: 'Start with 0.25mg, gradually increase to 0.5-1mg daily',
    frequency: 'Daily, preferably before UV exposure',
    expected_results: 'Noticeable tan within 1-2 weeks',
    side_effects: 'Nausea, facial flushing, darkening of moles',
    storage_tips: 'Protect from light. Refrigerate reconstituted solution',
    contraindications: 'History of melanoma or skin cancer'
  },
  {
    id: '6',
    title: 'Semax Cognitive Enhancement',
    description: 'Neuroprotective peptide protocol for cognitive enhancement and focus.',
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
  crypto: {
    BTC: '#f7931a',
    USDT: '#26a17b',
    XMR: '#ff6600',
    SOL: '#9945ff',
  }
};

// ========== HOME SCREEN ==========
function HomeScreen({ goTo, cartCount }) {
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
      setStats({ products: prods.data.length || 49, protocols: protocolCount, scans: hist.length });
    } catch (e) { console.log(e); }
    setLoading(false);
    Animated.timing(fadeAnim, { toValue: 1, duration: 500, useNativeDriver: true }).start();
  }, [fadeAnim]);

  useEffect(() => { load(); }, [load]);

  const refresh = async () => { setRefreshing(true); await load(); setRefreshing(false); };

  const quickActions = [
    { title: 'Shop Products', subtitle: 'Browse & order peptides', iconName: 'cart', tab: 'Shop', gradient: T.gradient3 },
    { title: 'Verify Product', subtitle: 'Scan QR or enter code', iconName: 'shield-checkmark', tab: 'Verify', gradient: T.gradient1 },
    { title: 'Research Protocols', subtitle: 'Premium dosage guides', iconName: 'flask', tab: 'Protocols', gradient: T.gradient2 },
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
    <ScrollView style={styles.screen} contentContainerStyle={{ paddingBottom: 24 }}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor={T.primary} />}
      showsVerticalScrollIndicator={false}>
      <Animated.View style={{ opacity: fadeAnim }}>
        {/* Hero Section */}
        <LinearGradient colors={['#1e3a8a', '#3b82f6', '#7c3aed']} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }} style={styles.heroContainer}>
          <View style={styles.heroContent}>
            <View style={styles.heroBadge}>
              <Ionicons name="diamond" size={12} color={T.white} />
              <Text style={styles.heroBadgeText}>PREMIUM RESEARCH</Text>
            </View>
            <Text style={styles.heroTitle}>Zurix Sciences</Text>
            <Text style={styles.heroSubtitle}>Peptide verification & research protocols</Text>
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
            <TouchableOpacity key={index} style={styles.actionCard} onPress={() => goTo(action.tab)} activeOpacity={0.7}>
              <LinearGradient colors={[action.gradient[0] + '15', action.gradient[1] + '08']} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }} style={styles.actionCardGradient}>
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
            <LinearGradient colors={['#f59e0b20', '#f59e0b08']} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }} style={styles.infoBannerGradient}>
              <Ionicons name="warning" size={24} color={T.warning} />
              <Text style={styles.infoBannerText}>FOR RESEARCH USE ONLY - Not for human consumption.</Text>
            </LinearGradient>
          </View>
        </View>

        {/* Website Link */}
        <View style={styles.section}>
          <TouchableOpacity style={styles.websiteCard} onPress={() => openURL('https://www.zurixsciences.com')} activeOpacity={0.8}>
            <View style={styles.websiteCardInner}>
              <Ionicons name="globe-outline" size={24} color={T.primary} />
              <View style={{ flex: 1, marginLeft: 14 }}>
                <Text style={styles.websiteCardTitle}>Visit Our Website</Text>
                <Text style={styles.websiteCardUrl}>www.zurixsciences.com</Text>
              </View>
              <Feather name="external-link" size={18} color={T.textMuted} />
            </View>
          </TouchableOpacity>
        </View>
      </Animated.View>
    </ScrollView>
  );
}

// ========== SHOP SCREEN ==========
function ShopScreen({ cart, setCart }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('All');
  const [showCart, setShowCart] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [showTerms, setShowTerms] = useState(true);

  const loadProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Fetching products from:', API_URL + '/products');
      const response = await api.get('/products');
      console.log('Products response:', response.data?.length, 'items');
      if (response.data && response.data.length > 0) {
        setProducts(response.data);
      } else {
        setError('No products available');
      }
    } catch (err) {
      console.log('Products error:', err.message);
      setError('Failed to load products: ' + err.message);
    }
    setLoading(false);
  };

  useEffect(() => {
    // Check if user already accepted terms
    AsyncStorage.getItem('shop_terms_accepted').then(accepted => {
      if (accepted === 'true') {
        setAcceptedTerms(true);
        setShowTerms(false);
      }
    });
    
    // Load products
    loadProducts();
  }, []);

  const handleAcceptTerms = async () => {
    await AsyncStorage.setItem('shop_terms_accepted', 'true');
    setAcceptedTerms(true);
    setShowTerms(false);
  };

  const categories = ['All', ...new Set(products.map(p => p.category).filter(Boolean))];
  const filtered = filter === 'All' ? products : products.filter(p => p.category === filter);

  const addToCart = (product) => {
    const productId = product.id || product._id;
    const existing = cart.find(item => (item.id || item._id) === productId);
    if (existing) {
      setCart(cart.map(item => (item.id || item._id) === productId ? { ...item, qty: item.qty + 1 } : item));
    } else {
      setCart([...cart, { ...product, qty: 1 }]);
    }
    Alert.alert('Added!', `${product.name} added to cart`);
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => (item.id || item._id) !== productId));
  };

  const updateQty = (productId, delta) => {
    setCart(cart.map(item => {
      if ((item.id || item._id) === productId) {
        const newQty = item.qty + delta;
        return newQty > 0 ? { ...item, qty: newQty } : item;
      }
      return item;
    }).filter(item => item.qty > 0));
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
  const cartCount = cart.reduce((sum, item) => sum + item.qty, 0);

  const checkout = () => {
    if (cart.length === 0) {
      Alert.alert('Cart Empty', 'Add products to your cart first');
      return;
    }
    const items = cart.map(item => `• ${item.name} x${item.qty} - $${(item.price * item.qty).toFixed(2)}`).join('\n');
    const message = `🛒 *New Order Request - Zurix Sciences*\n\n${items}\n\n💰 *Total: $${cartTotal.toFixed(2)}*\n\n⚠️ FOR RESEARCH USE ONLY\n\nPlease confirm availability and payment details.`;
    openWhatsApp(WHATSAPP_ORDER, message);
  };

  // Terms Modal - Must accept before accessing shop
  if (showTerms && !acceptedTerms) {
    return (
      <View style={styles.screen}>
        <Modal visible={true} transparent animationType="fade">
          <View style={styles.modalOverlay}>
            <View style={styles.termsModal}>
              <View style={styles.termsHeader}>
                <Ionicons name="document-text" size={32} color={T.warning} />
                <Text style={styles.termsTitle}>Terms & Disclaimer</Text>
              </View>
              
              <ScrollView style={styles.termsContent}>
                <Text style={styles.termsHeading}>FOR RESEARCH USE ONLY</Text>
                <Text style={styles.termsText}>
                  By accessing this product catalog, you acknowledge and agree to the following terms:
                </Text>
                
                <Text style={styles.termsBullet}>
                  • All products listed are intended exclusively for laboratory research and scientific study purposes.
                </Text>
                <Text style={styles.termsBullet}>
                  • Products are NOT intended for human consumption, veterinary use, therapeutic applications, or diagnostic purposes.
                </Text>
                <Text style={styles.termsBullet}>
                  • You confirm that you are a qualified researcher, scientist, or are purchasing on behalf of a licensed research institution.
                </Text>
                <Text style={styles.termsBullet}>
                  • Zurix Sciences acts as a facilitator connecting researchers with authorized distributors. We do not sell products directly.
                </Text>
                <Text style={styles.termsBullet}>
                  • All inquiries are forwarded to our authorized representative who will handle your request.
                </Text>
                <Text style={styles.termsBullet}>
                  • You agree to comply with all applicable laws and regulations in your jurisdiction regarding the purchase and use of research materials.
                </Text>
                <Text style={styles.termsBullet}>
                  • You assume full responsibility for the proper handling, storage, and use of any products acquired.
                </Text>
                
                <Text style={[styles.termsText, { marginTop: 16, fontWeight: '600' }]}>
                  By clicking "I Agree & Continue", you confirm that you have read, understood, and agree to be bound by these terms.
                </Text>
              </ScrollView>

              <TouchableOpacity style={styles.acceptTermsBtn} onPress={handleAcceptTerms}>
                <LinearGradient colors={T.gradient1} style={styles.acceptTermsBtnGradient}>
                  <Ionicons name="checkmark-circle" size={20} color={T.white} />
                  <Text style={styles.acceptTermsBtnText}>I Agree & Continue</Text>
                </LinearGradient>
              </TouchableOpacity>
              
              <Text style={styles.termsFooter}>
                Continued access constitutes acceptance of these terms.
              </Text>
            </View>
          </View>
        </Modal>
      </View>
    );
  }

  if (loading) {
    return <View style={[styles.screen, styles.center]}><ActivityIndicator size="large" color={T.primary} /></View>;
  }

  return (
    <View style={styles.screen}>
      {/* Cart Modal */}
      <Modal visible={showCart} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.cartModal}>
            <View style={styles.cartModalHeader}>
              <Text style={styles.cartModalTitle}>Shopping Cart</Text>
              <TouchableOpacity onPress={() => setShowCart(false)}>
                <Ionicons name="close" size={24} color={T.text} />
              </TouchableOpacity>
            </View>
            
            <ScrollView style={styles.cartModalContent}>
              {cart.length === 0 ? (
                <View style={styles.emptyCart}>
                  <Ionicons name="cart-outline" size={48} color={T.textMuted} />
                  <Text style={styles.emptyCartText}>Your cart is empty</Text>
                </View>
              ) : (
                cart.map((item, i) => (
                  <View key={i} style={styles.cartItem}>
                    <View style={{ flex: 1 }}>
                      <Text style={styles.cartItemName}>{item.name}</Text>
                      <Text style={styles.cartItemPrice}>${item.price?.toFixed(2)} each</Text>
                    </View>
                    <View style={styles.cartItemQty}>
                      <TouchableOpacity onPress={() => updateQty(item.id || item._id, -1)} style={styles.qtyBtn}>
                        <Ionicons name="remove" size={18} color={T.text} />
                      </TouchableOpacity>
                      <Text style={styles.qtyText}>{item.qty}</Text>
                      <TouchableOpacity onPress={() => updateQty(item.id || item._id, 1)} style={styles.qtyBtn}>
                        <Ionicons name="add" size={18} color={T.text} />
                      </TouchableOpacity>
                    </View>
                    <TouchableOpacity onPress={() => removeFromCart(item.id || item._id)} style={styles.removeBtn}>
                      <Ionicons name="trash-outline" size={20} color={T.danger} />
                    </TouchableOpacity>
                  </View>
                ))
              )}
            </ScrollView>

            {cart.length > 0 && (
              <View style={styles.cartModalFooter}>
                <View style={styles.cartTotal}>
                  <Text style={styles.cartTotalLabel}>Total:</Text>
                  <Text style={styles.cartTotalValue}>${cartTotal.toFixed(2)}</Text>
                </View>
                <Text style={styles.cartDisclaimer}>
                  ⚠️ For research purposes only. You will be connected with our authorized representative.
                </Text>
                <TouchableOpacity style={styles.checkoutBtn} onPress={checkout}>
                  <LinearGradient colors={T.gradient3} style={styles.checkoutBtnGradient}>
                    <Ionicons name="logo-whatsapp" size={20} color={T.white} />
                    <Text style={styles.checkoutBtnText}>Contact Representative</Text>
                  </LinearGradient>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>
      </Modal>

      {/* Research Banner */}
      <View style={styles.researchBanner}>
        <Ionicons name="flask" size={16} color={T.warning} />
        <Text style={styles.researchBannerText}>Research Products Only • Contact Representative to Order</Text>
      </View>

      {/* Header with Cart Button */}
      <View style={styles.shopHeader}>
        <Text style={styles.shopTitle}>Product Catalog</Text>
        <TouchableOpacity style={styles.cartButton} onPress={() => setShowCart(true)}>
          <Ionicons name="cart" size={24} color={T.text} />
          {cartCount > 0 && (
            <View style={styles.cartBadge}>
              <Text style={styles.cartBadgeText}>{cartCount}</Text>
            </View>
          )}
        </TouchableOpacity>
      </View>

      {/* Filter */}
      {categories.length > 1 && (
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll} contentContainerStyle={{ paddingHorizontal: 16, gap: 8 }}>
          {categories.map(cat => (
            <TouchableOpacity key={cat} style={[styles.filterChip, filter === cat && styles.filterChipActive]} onPress={() => setFilter(cat)}>
              <Text style={[styles.filterChipText, filter === cat && styles.filterChipTextActive]}>{cat}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      )}

      {/* Products Grid */}
      <ScrollView style={{ flex: 1 }} contentContainerStyle={styles.productsGrid}>
        {loading ? (
          <View style={styles.emptyProducts}>
            <ActivityIndicator size="large" color={T.primary} />
            <Text style={styles.emptyProductsTitle}>Loading Products...</Text>
          </View>
        ) : error ? (
          <View style={styles.emptyProducts}>
            <Ionicons name="alert-circle-outline" size={48} color={T.danger} />
            <Text style={styles.emptyProductsTitle}>Error Loading Products</Text>
            <Text style={styles.emptyProductsText}>{error}</Text>
            <TouchableOpacity style={styles.retryBtn} onPress={loadProducts}>
              <Text style={styles.retryBtnText}>Retry</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.visitWebsiteBtn} onPress={() => openURL('https://www.zurixsciences.com')}>
              <Text style={styles.visitWebsiteBtnText}>Visit Website Instead</Text>
            </TouchableOpacity>
          </View>
        ) : filtered.length === 0 ? (
          <View style={styles.emptyProducts}>
            <Ionicons name="flask-outline" size={48} color={T.textMuted} />
            <Text style={styles.emptyProductsTitle}>No Products Available</Text>
            <Text style={styles.emptyProductsText}>Please check back later or visit our website</Text>
            <TouchableOpacity style={styles.visitWebsiteBtn} onPress={() => openURL('https://www.zurixsciences.com')}>
              <Text style={styles.visitWebsiteBtnText}>Visit Website</Text>
            </TouchableOpacity>
          </View>
        ) : (
          filtered.map((product, i) => (
            <View key={product.id || i} style={styles.productCard}>
              <View style={styles.productImagePlaceholder}>
                <Ionicons name="flask" size={32} color={T.primary} />
              </View>
              <View style={[styles.categoryBadge, { backgroundColor: T.primary + '20', alignSelf: 'flex-start' }]}>
                <Text style={[styles.categoryBadgeText, { color: T.primary }]}>{product.category}</Text>
              </View>
              <Text style={styles.productName} numberOfLines={2}>{product.name}</Text>
              <Text style={styles.productPurity}>Purity: {product.purity}</Text>
              <View style={styles.productFooter}>
                <Text style={styles.productPrice}>${product.price?.toFixed(2)}</Text>
                <TouchableOpacity style={styles.addToCartBtn} onPress={() => addToCart(product)}>
                  <Ionicons name="add" size={20} color={T.white} />
                </TouchableOpacity>
              </View>
            </View>
          ))
        )}
      </ScrollView>
    </View>
  );
}


// ========== VERIFY SCREEN (Anti-Fake Enhanced) ==========
function VerifyScreen() {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showScanner, setShowScanner] = useState(false);
  const [permission, requestPermission] = useCameraPermissions();
  const resultAnim = useRef(new Animated.Value(0)).current;
  const scannedRef = useRef(false);

  const verify = async (verifyCode) => {
    const c = (verifyCode || code).trim().toUpperCase();
    if (!c) { Alert.alert('Code Required', 'Please enter a verification code.'); return; }
    
    setLoading(true);
    setResult(null);
    resultAnim.setValue(0);
    
    try {
      const r = await api.post('/verify-product', { code: c });
      setResult(r.data);
      const hist = JSON.parse(await AsyncStorage.getItem('vh') || '[]');
      hist.unshift({ ...r.data, code: c, timestamp: new Date().toISOString() });
      await AsyncStorage.setItem('vh', JSON.stringify(hist.slice(0, 100)));
      Animated.spring(resultAnim, { toValue: 1, useNativeDriver: true }).start();
    } catch (e) {
      setResult({ success: false, message: 'Network error. Check your connection.' });
      Animated.spring(resultAnim, { toValue: 1, useNativeDriver: true }).start();
    }
    setLoading(false);
  };

  const handleBarCodeScanned = ({ data }) => {
    if (scannedRef.current) return;
    scannedRef.current = true;
    setShowScanner(false);
    setCode(data.toUpperCase());
    setTimeout(() => { verify(data); scannedRef.current = false; }, 500);
  };

  const openScanner = async () => {
    if (!permission?.granted) {
      const { granted } = await requestPermission();
      if (!granted) { Alert.alert('Permission Required', 'Camera access needed.'); return; }
    }
    scannedRef.current = false;
    setShowScanner(true);
  };

  const reportFake = () => {
    const message = `🚨 *COUNTERFEIT REPORT*\n\nCode: ${code}\nProduct: ${result?.product?.name || 'Unknown'}\nVerification Count: ${result?.verification_count || 'N/A'}\n\nI believe this product may be counterfeit.`;
    openWhatsApp(WHATSAPP_SWITZERLAND, message);
  };

  const getVerificationWarning = (count) => {
    if (!count || count <= 1) return null;
    if (count <= 3) return { level: 'warning', message: `This batch has been verified ${count} times. If you didn't perform all verifications, be cautious.` };
    return { level: 'danger', message: `⚠️ HIGH RISK: This batch was verified ${count} times! This may indicate a counterfeit product.` };
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.screenPadding}>
      {/* Scanner Modal */}
      <Modal visible={showScanner} animationType="slide" onRequestClose={() => setShowScanner(false)}>
        <View style={styles.scannerContainer}>
          <CameraView style={styles.camera} facing="back" barcodeScannerSettings={{ barcodeTypes: ['qr', 'code128', 'code39'] }} onBarcodeScanned={handleBarCodeScanned}>
            <View style={styles.scannerOverlay}>
              <View style={styles.scannerHeader}>
                <TouchableOpacity style={styles.scannerCloseBtn} onPress={() => setShowScanner(false)}>
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
              <Text style={styles.scannerHint}>Position the QR code within the frame</Text>
            </View>
          </CameraView>
        </View>
      </Modal>

      {/* Header */}
      <View style={styles.verifyHeader}>
        <LinearGradient colors={T.gradient1} style={styles.verifyIconGradient}>
          <Ionicons name="shield-checkmark" size={32} color={T.white} />
        </LinearGradient>
        <Text style={styles.verifyTitle}>Product Verification</Text>
        <Text style={styles.verifySubtitle}>Authenticate your Zurix Sciences product</Text>
      </View>

      {/* Scan Button */}
      <TouchableOpacity style={styles.scanQRButton} onPress={openScanner}>
        <LinearGradient colors={T.gradient2} style={styles.scanQRButtonGradient}>
          <Ionicons name="qr-code" size={24} color={T.white} />
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

      {/* Manual Input */}
      <View style={styles.inputSection}>
        <Text style={styles.inputLabel}>ENTER CODE MANUALLY</Text>
        <View style={styles.inputWrapper}>
          <Ionicons name="key-outline" size={20} color={T.textMuted} />
          <TextInput style={styles.input} placeholder="e.g. ZX-ZE101208" placeholderTextColor={T.textDim}
            value={code} onChangeText={t => { setCode(t.toUpperCase()); setResult(null); }} autoCapitalize="characters" />
          {code.length > 0 && (
            <TouchableOpacity onPress={() => { setCode(''); setResult(null); }}>
              <Ionicons name="close-circle" size={20} color={T.textMuted} />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Verify Button */}
      <TouchableOpacity style={[styles.verifyButton, loading && { opacity: 0.6 }]} onPress={() => verify()} disabled={loading}>
        <LinearGradient colors={T.gradient1} style={styles.verifyButtonGradient}>
          {loading ? <ActivityIndicator color={T.white} /> : (
            <>
              <Ionicons name="shield-checkmark" size={22} color={T.white} />
              <Text style={styles.verifyButtonText}>Verify Product</Text>
            </>
          )}
        </LinearGradient>
      </TouchableOpacity>

      {/* Sample Codes */}
      <View style={styles.sampleSection}>
        <Text style={styles.sampleLabel}>Try sample codes:</Text>
        <View style={styles.sampleCodesRow}>
          {['ZX-ZE101208', 'ZX-BP050823'].map((c, i) => (
            <TouchableOpacity key={i} style={styles.sampleCode} onPress={() => { setCode(c); setResult(null); }}>
              <Text style={styles.sampleCodeText}>{c}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Result */}
      {result && (
        <Animated.View style={[styles.resultContainer, { opacity: resultAnim }]}>
          <View style={[styles.resultCard, { borderLeftColor: result.success ? T.success : T.danger }]}>
            <View style={styles.resultHeader}>
              <View style={[styles.resultIcon, { backgroundColor: result.success ? T.successGlow : T.danger + '20' }]}>
                <Ionicons name={result.success ? "checkmark-circle" : "close-circle"} size={28} color={result.success ? T.success : T.danger} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={[styles.resultStatus, { color: result.success ? T.success : T.danger }]}>
                  {result.success ? 'VERIFIED ✓' : 'NOT VERIFIED'}
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
                ].map((item, i) => (
                  <View key={i} style={styles.resultRow}>
                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                      <Ionicons name={item.icon} size={16} color={T.textMuted} />
                      <Text style={styles.resultRowLabel}>{item.label}</Text>
                    </View>
                    <Text style={styles.resultRowValue}>{item.value || 'N/A'}</Text>
                  </View>
                ))}
              </View>
            )}

            {/* Anti-Fake Warning */}
            {result.verification_count > 1 && (
              <View style={[styles.antiFakeWarning, { backgroundColor: result.verification_count > 3 ? T.danger + '20' : T.warning + '20' }]}>
                <Ionicons name="alert-circle" size={24} color={result.verification_count > 3 ? T.danger : T.warning} />
                <View style={{ flex: 1 }}>
                  <Text style={[styles.antiFakeTitle, { color: result.verification_count > 3 ? T.danger : T.warning }]}>
                    {result.verification_count > 3 ? '⚠️ HIGH COUNTERFEIT RISK' : '⚠️ Multiple Verifications'}
                  </Text>
                  <Text style={styles.antiFakeText}>
                    This batch has been verified {result.verification_count} times.
                    {result.verification_count > 3 ? ' This is unusual and may indicate a counterfeit product.' : ' If these weren\'t all your verifications, be cautious.'}
                  </Text>
                </View>
              </View>
            )}

            {/* Report Button */}
            {result.verification_count > 3 && (
              <TouchableOpacity style={styles.reportBtn} onPress={reportFake}>
                <Ionicons name="flag" size={18} color={T.danger} />
                <Text style={styles.reportBtnText}>Report Suspected Counterfeit</Text>
              </TouchableOpacity>
            )}
          </View>
        </Animated.View>
      )}
    </ScrollView>
  );
}

// ========== PROTOCOLS SCREEN (with Paywall) ==========
function ProtocolsScreen() {
  const [protocols, setProtocols] = useState([]);
  const [filter, setFilter] = useState('All');
  const [loading, setLoading] = useState(true);
  const [purchased, setPurchased] = useState([]);
  const [showPayment, setShowPayment] = useState(null);
  const [selectedCrypto, setSelectedCrypto] = useState('USDT');

  useEffect(() => {
    api.get('/protocols').then(r => {
      setProtocols(r.data?.length > 0 ? r.data : MOCK_PROTOCOLS);
      setLoading(false);
    }).catch(() => { setProtocols(MOCK_PROTOCOLS); setLoading(false); });
    
    AsyncStorage.getItem('purchased_protocols').then(data => {
      if (data) setPurchased(JSON.parse(data));
    });
  }, []);

  const filtered = filter === 'All' ? protocols : protocols.filter(p => p.category === filter);

  const isPurchased = (id) => purchased.includes(id);

  const handlePurchase = (protocol) => {
    setShowPayment(protocol);
  };

  const confirmPayment = async () => {
    const protocol = showPayment;
    const newPurchased = [...purchased, protocol.id];
    setPurchased(newPurchased);
    await AsyncStorage.setItem('purchased_protocols', JSON.stringify(newPurchased));
    setShowPayment(null);
    
    const message = `💳 *Protocol Purchase Confirmation*\n\nProtocol: ${protocol.title}\nPrice: $${protocol.price}\nPayment: ${selectedCrypto}\n\nPlease confirm my payment to activate access.`;
    openWhatsApp(WHATSAPP_SWITZERLAND, message);
  };

  const contactExpert = (protocol) => {
    const message = `👋 *Protocol Support Request*\n\nProtocol: ${protocol.title}\n\nI have questions about this protocol.`;
    openWhatsApp(WHATSAPP_SWITZERLAND, message);
  };

  if (loading) return <View style={[styles.screen, styles.center]}><ActivityIndicator size="large" color={T.primary} /></View>;

  return (
    <View style={styles.screen}>
      {/* Payment Modal */}
      <Modal visible={!!showPayment} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.paymentModal}>
            <View style={styles.paymentModalHeader}>
              <Text style={styles.paymentModalTitle}>Purchase Protocol</Text>
              <TouchableOpacity onPress={() => setShowPayment(null)}>
                <Ionicons name="close" size={24} color={T.text} />
              </TouchableOpacity>
            </View>

            {showPayment && (
              <>
                <Text style={styles.paymentProtocolName}>{showPayment.title}</Text>
                <Text style={styles.paymentPrice}>${showPayment.price?.toFixed(2)}</Text>

                <Text style={styles.paymentSectionTitle}>Select Cryptocurrency</Text>
                <View style={styles.cryptoOptions}>
                  {Object.keys(CRYPTO_WALLETS).map(crypto => (
                    <TouchableOpacity key={crypto} style={[styles.cryptoOption, selectedCrypto === crypto && styles.cryptoOptionActive]}
                      onPress={() => setSelectedCrypto(crypto)}>
                      <View style={[styles.cryptoDot, { backgroundColor: T.crypto[crypto] }]} />
                      <Text style={[styles.cryptoOptionText, selectedCrypto === crypto && styles.cryptoOptionTextActive]}>{crypto}</Text>
                    </TouchableOpacity>
                  ))}
                </View>

                <View style={styles.walletBox}>
                  <Text style={styles.walletLabel}>{selectedCrypto} Address ({CRYPTO_WALLETS[selectedCrypto].network})</Text>
                  <Text style={styles.walletAddress} selectable>{CRYPTO_WALLETS[selectedCrypto].address}</Text>
                </View>

                <Text style={styles.paymentInstructions}>
                  1. Send exactly ${showPayment.price?.toFixed(2)} in {selectedCrypto}{'\n'}
                  2. Click "I've Paid" to notify us{'\n'}
                  3. Access will be granted within 24h
                </Text>

                <TouchableOpacity style={styles.paidButton} onPress={confirmPayment}>
                  <LinearGradient colors={T.gradient3} style={styles.paidButtonGradient}>
                    <Ionicons name="checkmark-circle" size={20} color={T.white} />
                    <Text style={styles.paidButtonText}>I've Paid - Notify via WhatsApp</Text>
                  </LinearGradient>
                </TouchableOpacity>
              </>
            )}
          </View>
        </View>
      </Modal>

      {/* Header */}
      <View style={styles.protocolsHeader}>
        <Text style={styles.protocolsTitle}>Research Protocols</Text>
        <Text style={styles.protocolsSubtitle}>Premium dosage guides from experts</Text>
      </View>

      {/* Filter */}
      <View style={styles.filterContainer}>
        {['All', 'Basic', 'Advanced'].map(f => (
          <TouchableOpacity key={f} style={[styles.filterTab, filter === f && styles.filterTabActive]} onPress={() => setFilter(f)}>
            {filter === f && <LinearGradient colors={T.gradient1} style={StyleSheet.absoluteFill} />}
            <Text style={[styles.filterTabText, filter === f && styles.filterTabTextActive]}>{f}</Text>
            {f !== 'All' && <Text style={[styles.filterPrice, filter === f && styles.filterPriceActive]}>{f === 'Basic' ? '$4.99' : '$9.99'}</Text>}
          </TouchableOpacity>
        ))}
      </View>

      {/* Protocols List */}
      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16 }}>
        {filtered.map((protocol, index) => {
          const owned = isPurchased(protocol.id);
          return (
            <View key={protocol.id || index} style={styles.protocolCard}>
              <View style={styles.protocolCardHeader}>
                <View style={[styles.categoryBadge, { backgroundColor: protocol.category === 'Basic' ? T.success + '20' : T.secondary + '20' }]}>
                  <Text style={[styles.categoryBadgeText, { color: protocol.category === 'Basic' ? T.success : T.secondary }]}>{protocol.category}</Text>
                </View>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                  {!owned && <Ionicons name="lock-closed" size={16} color={T.textMuted} />}
                  <Text style={styles.protocolPrice}>${protocol.price?.toFixed(2)}</Text>
                </View>
              </View>

              <Text style={styles.protocolTitle}>{protocol.title}</Text>
              <Text style={styles.protocolDesc} numberOfLines={owned ? undefined : 2}>{protocol.description}</Text>

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

              {owned ? (
                <>
                  {/* Full Content */}
                  <View style={styles.protocolExpanded}>
                    {[
                      { title: 'Dosage Instructions', text: protocol.dosage_instructions, icon: 'medical' },
                      { title: 'Frequency', text: protocol.frequency, icon: 'refresh' },
                      { title: 'Expected Results', text: protocol.expected_results, icon: 'trending-up' },
                      { title: 'Side Effects', text: protocol.side_effects, icon: 'warning' },
                      { title: 'Storage Tips', text: protocol.storage_tips, icon: 'snow' },
                    ].map((item, i) => item.text && (
                      <View key={i} style={styles.protocolExpandedItem}>
                        <View style={styles.protocolExpandedHeader}>
                          <Ionicons name={item.icon} size={16} color={T.primary} />
                          <Text style={styles.protocolExpandedTitle}>{item.title}</Text>
                        </View>
                        <Text style={styles.protocolExpandedText}>{item.text}</Text>
                      </View>
                    ))}
                    
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
                  </View>

                  {/* Contact Expert Button */}
                  <TouchableOpacity style={styles.expertButton} onPress={() => contactExpert(protocol)}>
                    <Ionicons name="chatbubble-ellipses" size={18} color={T.success} />
                    <Text style={styles.expertButtonText}>Chat with Expert (WhatsApp)</Text>
                  </TouchableOpacity>
                </>
              ) : (
                /* Locked - Purchase Button */
                <TouchableOpacity style={styles.purchaseButton} onPress={() => handlePurchase(protocol)}>
                  <LinearGradient colors={T.gradient2} style={styles.purchaseButtonGradient}>
                    <Ionicons name="lock-open" size={18} color={T.white} />
                    <Text style={styles.purchaseButtonText}>Unlock Protocol - ${protocol.price?.toFixed(2)}</Text>
                  </LinearGradient>
                </TouchableOpacity>
              )}
            </View>
          );
        })}
      </ScrollView>
    </View>
  );
}

// ========== PROFILE SCREEN ==========
function ProfileScreen() {
  const [orderHistory, setOrderHistory] = useState([]);
  const [verifyHistory, setVerifyHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('orders');

  useEffect(() => {
    AsyncStorage.getItem('order_history').then(d => setOrderHistory(d ? JSON.parse(d) : []));
    AsyncStorage.getItem('vh').then(d => setVerifyHistory(d ? JSON.parse(d) : []));
  }, []);

  const clearAllData = () => {
    Alert.alert('Clear All Data', 'This will remove all local data including orders and verifications.', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Clear All', style: 'destructive', onPress: async () => {
        await AsyncStorage.multiRemove(['vh', 'order_history', 'purchased_protocols']);
        setOrderHistory([]);
        setVerifyHistory([]);
        Alert.alert('Done', 'All data cleared.');
      }}
    ]);
  };

  const menuItems = [
    { title: 'Visit Website', subtitle: 'www.zurixsciences.com', icon: 'globe-outline', color: T.primary, action: () => openURL('https://www.zurixsciences.com') },
    { title: 'Contact Support', subtitle: 'Switzerland WhatsApp', icon: 'logo-whatsapp', color: T.success, action: () => openWhatsApp(WHATSAPP_SWITZERLAND, 'Hello Zurix Sciences Support') },
    { title: 'Clear All Data', subtitle: 'Remove local data', icon: 'trash-outline', color: T.danger, action: clearAllData },
  ];

  const verifyStats = {
    total: verifyHistory.length,
    verified: verifyHistory.filter(h => h.success).length,
    failed: verifyHistory.filter(h => !h.success).length,
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.screenPadding}>
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

      {/* History Tabs */}
      <View style={styles.historyTabs}>
        <TouchableOpacity style={[styles.historyTab, activeTab === 'orders' && styles.historyTabActive]} onPress={() => setActiveTab('orders')}>
          <Ionicons name="receipt-outline" size={18} color={activeTab === 'orders' ? T.primary : T.textMuted} />
          <Text style={[styles.historyTabText, activeTab === 'orders' && styles.historyTabTextActive]}>Orders</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.historyTab, activeTab === 'verify' && styles.historyTabActive]} onPress={() => setActiveTab('verify')}>
          <Ionicons name="shield-checkmark-outline" size={18} color={activeTab === 'verify' ? T.primary : T.textMuted} />
          <Text style={[styles.historyTabText, activeTab === 'verify' && styles.historyTabTextActive]}>Verifications</Text>
        </TouchableOpacity>
      </View>

      {/* History Content */}
      {activeTab === 'verify' && (
        <>
          <View style={styles.statsContainer}>
            {[
              { label: 'Total', value: verifyStats.total, color: T.primary, icon: 'scan' },
              { label: 'Verified', value: verifyStats.verified, color: T.success, icon: 'checkmark-circle' },
              { label: 'Failed', value: verifyStats.failed, color: T.danger, icon: 'close-circle' },
            ].map((stat, i) => (
              <View key={i} style={styles.statCard}>
                <View style={[styles.statIconContainer, { backgroundColor: stat.color + '20' }]}>
                  <Ionicons name={stat.icon} size={18} color={stat.color} />
                </View>
                <Text style={[styles.statValue, { color: stat.color }]}>{stat.value}</Text>
                <Text style={styles.statLabel}>{stat.label}</Text>
              </View>
            ))}
          </View>

          {verifyHistory.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="time-outline" size={48} color={T.textMuted} />
              <Text style={styles.emptyTitle}>No Verifications Yet</Text>
            </View>
          ) : (
            verifyHistory.slice(0, 10).map((item, i) => (
              <View key={i} style={styles.historyCard}>
                <View style={[styles.historyStatusIndicator, { backgroundColor: item.success ? T.success : T.danger }]} />
                <View style={{ flex: 1 }}>
                  <Text style={styles.historyProductName}>{item.product?.name || 'Unknown'}</Text>
                  <Text style={styles.historyCode}>{item.code}</Text>
                  <Text style={styles.historyTime}>{new Date(item.timestamp).toLocaleString()}</Text>
                </View>
                <View style={[styles.historyStatusBadge, { backgroundColor: item.success ? T.successDim : T.dangerDim }]}>
                  <Text style={[styles.historyStatusText, { color: item.success ? T.success : T.danger }]}>{item.success ? 'OK' : 'FAIL'}</Text>
                </View>
              </View>
            ))
          )}
        </>
      )}

      {activeTab === 'orders' && (
        <View style={styles.emptyState}>
          <Ionicons name="receipt-outline" size={48} color={T.textMuted} />
          <Text style={styles.emptyTitle}>No Orders Yet</Text>
          <Text style={styles.emptyText}>Your order history will appear here</Text>
        </View>
      )}

      {/* Menu Items */}
      <View style={styles.menuSection}>
        <Text style={styles.menuSectionTitle}>Settings & Support</Text>
        {menuItems.map((item, i) => (
          <TouchableOpacity key={i} style={styles.menuItem} onPress={item.action}>
            <View style={[styles.menuIconContainer, { backgroundColor: item.color + '20' }]}>
              <Ionicons name={item.icon} size={20} color={item.color} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.menuItemTitle}>{item.title}</Text>
              <Text style={styles.menuItemSubtitle}>{item.subtitle}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={T.textMuted} />
          </TouchableOpacity>
        ))}
      </View>

      {/* Disclaimer */}
      <View style={styles.disclaimerCard}>
        <LinearGradient colors={['#f59e0b15', '#f59e0b08']} style={styles.disclaimerGradient}>
          <Ionicons name="warning" size={20} color={T.warning} />
          <Text style={styles.disclaimerText}>FOR RESEARCH USE ONLY - All products are intended for laboratory research only.</Text>
        </LinearGradient>
      </View>
    </ScrollView>
  );
}

// ========== MAIN APP ==========
function MainApp() {
  const insets = useSafeAreaInsets();
  const [activeTab, setActiveTab] = useState('Home');
  const [cart, setCart] = useState([]);

  const tabs = [
    { key: 'Home', label: 'Home', icon: 'home' },
    { key: 'Shop', label: 'Shop', icon: 'cart' },
    { key: 'Verify', label: 'Verify', icon: 'shield-checkmark' },
    { key: 'Protocols', label: 'Protocols', icon: 'flask' },
    { key: 'Profile', label: 'Profile', icon: 'person' },
  ];

  const cartCount = cart.reduce((sum, item) => sum + item.qty, 0);

  const renderScreen = () => {
    switch (activeTab) {
      case 'Home': return <HomeScreen goTo={setActiveTab} cartCount={cartCount} />;
      case 'Shop': return <ShopScreen cart={cart} setCart={setCart} />;
      case 'Verify': return <VerifyScreen />;
      case 'Protocols': return <ProtocolsScreen />;
      case 'Profile': return <ProfileScreen />;
      default: return <HomeScreen goTo={setActiveTab} />;
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: T.bg }]}>  
      <StatusBar style="light" />
      
      {/* Top Bar */}
      <View style={[styles.topBar, { paddingTop: insets.top + 12 }]}>
        <Text style={styles.topBarTitle}>{activeTab === 'Home' ? 'Zurix Sciences' : activeTab}</Text>
        {activeTab === 'Home' && (
          <View style={styles.topBarBadge}>
            <Ionicons name="diamond" size={12} color={T.primary} />
          </View>
        )}
      </View>

      {/* Content */}
      <View style={styles.content}>{renderScreen()}</View>

      {/* Bottom Navigation */}
      <View style={[styles.bottomNav, { paddingBottom: insets.bottom + 8 }]}>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.key;
          return (
            <TouchableOpacity key={tab.key} style={styles.bottomNavItem} onPress={() => setActiveTab(tab.key)}>
              <View style={[styles.bottomNavIconContainer, isActive && styles.bottomNavIconActive]}>
                <Ionicons name={isActive ? tab.icon : `${tab.icon}-outline`} size={22} color={isActive ? T.primary : T.textMuted} />
                {tab.key === 'Shop' && cartCount > 0 && (
                  <View style={styles.navCartBadge}>
                    <Text style={styles.navCartBadgeText}>{cartCount}</Text>
                  </View>
                )}
              </View>
              <Text style={[styles.bottomNavLabel, isActive && styles.bottomNavLabelActive]}>{tab.label}</Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <MainApp />
    </SafeAreaProvider>
  );
}

// ========== STYLES ==========
const styles = StyleSheet.create({
  container: { flex: 1 },
  screen: { flex: 1, backgroundColor: T.bg },
  screenPadding: { padding: 16 },
  center: { justifyContent: 'center', alignItems: 'center' },
  loadingText: { color: T.textMuted, marginTop: 12, fontSize: 14 },

  // Top Bar
  topBar: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingBottom: 14, backgroundColor: T.bg, borderBottomWidth: 1, borderBottomColor: T.cardBorder },
  topBarTitle: { fontSize: 20, fontWeight: '700', color: T.text },
  topBarBadge: { backgroundColor: T.primaryGlow, padding: 6, borderRadius: 8 },
  content: { flex: 1 },

  // Bottom Nav
  bottomNav: { flexDirection: 'row', backgroundColor: T.card, borderTopWidth: 1, borderTopColor: T.cardBorder, paddingTop: 8 },
  bottomNavItem: { flex: 1, alignItems: 'center', gap: 4 },
  bottomNavIconContainer: { padding: 6, borderRadius: 12, position: 'relative' },
  bottomNavIconActive: { backgroundColor: T.primaryGlow },
  bottomNavLabel: { fontSize: 11, fontWeight: '500', color: T.textMuted },
  bottomNavLabelActive: { color: T.primary, fontWeight: '600' },
  navCartBadge: { position: 'absolute', top: -2, right: -2, backgroundColor: T.danger, borderRadius: 10, minWidth: 16, height: 16, alignItems: 'center', justifyContent: 'center' },
  navCartBadgeText: { color: T.white, fontSize: 10, fontWeight: '700' },

  // Hero
  heroContainer: { margin: 16, borderRadius: 24, overflow: 'hidden' },
  heroContent: { padding: 24 },
  heroBadge: { flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start', backgroundColor: 'rgba(255,255,255,0.15)', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, gap: 6, marginBottom: 12 },
  heroBadgeText: { color: T.white, fontSize: 10, fontWeight: '700', letterSpacing: 1 },
  heroTitle: { fontSize: 28, fontWeight: '800', color: T.white },
  heroSubtitle: { fontSize: 14, color: 'rgba(255,255,255,0.8)', marginTop: 8 },
  heroStatsRow: { flexDirection: 'row', backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: 16, padding: 16, marginTop: 20 },
  heroStat: { flex: 1, alignItems: 'center' },
  heroStatNumber: { fontSize: 24, fontWeight: '800', color: T.white },
  heroStatLabel: { fontSize: 11, color: 'rgba(255,255,255,0.7)', marginTop: 2 },
  heroStatDivider: { width: 1, backgroundColor: 'rgba(255,255,255,0.2)' },

  // Section
  section: { paddingHorizontal: 16, marginBottom: 8 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: T.text, marginBottom: 14 },

  // Action Cards
  actionCard: { marginBottom: 10, borderRadius: 16, overflow: 'hidden', borderWidth: 1, borderColor: T.cardBorder },
  actionCardGradient: { flexDirection: 'row', alignItems: 'center', padding: 16 },
  actionIconContainer: { width: 48, height: 48, borderRadius: 14, alignItems: 'center', justifyContent: 'center', marginRight: 14 },
  actionTextContainer: { flex: 1 },
  actionTitle: { fontSize: 16, fontWeight: '600', color: T.text },
  actionSubtitle: { fontSize: 13, color: T.textMuted, marginTop: 2 },

  // Info Banner
  infoBanner: { borderRadius: 14, overflow: 'hidden', borderWidth: 1, borderColor: T.warning + '30' },
  infoBannerGradient: { flexDirection: 'row', alignItems: 'center', padding: 14, gap: 12 },
  infoBannerText: { flex: 1, fontSize: 12, color: T.textSecondary },

  // Website Card
  websiteCard: { backgroundColor: T.card, borderRadius: 14, borderWidth: 1, borderColor: T.cardBorder },
  websiteCardInner: { flexDirection: 'row', alignItems: 'center', padding: 16 },
  websiteCardTitle: { fontSize: 15, fontWeight: '600', color: T.text },
  websiteCardUrl: { fontSize: 13, color: T.primary, marginTop: 2 },

  // Shop
  shopHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: T.cardBorder },
  shopTitle: { fontSize: 24, fontWeight: '700', color: T.text },
  cartButton: { position: 'relative', padding: 8 },
  cartBadge: { position: 'absolute', top: 0, right: 0, backgroundColor: T.danger, borderRadius: 10, minWidth: 18, height: 18, alignItems: 'center', justifyContent: 'center' },
  cartBadgeText: { color: T.white, fontSize: 11, fontWeight: '700' },
  filterScroll: { maxHeight: 50, marginVertical: 12 },
  filterChip: { paddingHorizontal: 16, paddingVertical: 8, backgroundColor: T.card, borderRadius: 20, borderWidth: 1, borderColor: T.cardBorder },
  filterChipActive: { backgroundColor: T.primary, borderColor: T.primary },
  filterChipText: { fontSize: 14, color: T.textMuted, fontWeight: '500' },
  filterChipTextActive: { color: T.white },
  productsGrid: { padding: 16, flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  productCard: { width: (width - 44) / 2, backgroundColor: T.card, borderRadius: 16, padding: 12, borderWidth: 1, borderColor: T.cardBorder },
  productImagePlaceholder: { height: 80, backgroundColor: T.cardElevated, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginBottom: 10 },
  productName: { fontSize: 14, fontWeight: '600', color: T.text, marginTop: 6, minHeight: 36 },
  productPurity: { fontSize: 12, color: T.textMuted, marginTop: 4 },
  productFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 10 },
  productPrice: { fontSize: 18, fontWeight: '700', color: T.primary },
  addToCartBtn: { backgroundColor: T.primary, width: 32, height: 32, borderRadius: 16, alignItems: 'center', justifyContent: 'center' },

  // Cart Modal
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.8)', justifyContent: 'flex-end' },
  cartModal: { backgroundColor: T.card, borderTopLeftRadius: 24, borderTopRightRadius: 24, maxHeight: height * 0.7 },
  cartModalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, borderBottomWidth: 1, borderBottomColor: T.cardBorder },
  cartModalTitle: { fontSize: 20, fontWeight: '700', color: T.text },
  cartModalContent: { padding: 16, maxHeight: height * 0.4 },
  emptyCart: { alignItems: 'center', paddingVertical: 40 },
  emptyCartText: { color: T.textMuted, marginTop: 12 },
  cartItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: T.cardElevated, borderRadius: 12, padding: 12, marginBottom: 8 },
  cartItemName: { fontSize: 14, fontWeight: '600', color: T.text },
  cartItemPrice: { fontSize: 12, color: T.textMuted, marginTop: 2 },
  cartItemQty: { flexDirection: 'row', alignItems: 'center', gap: 8, marginHorizontal: 12 },
  qtyBtn: { width: 28, height: 28, borderRadius: 14, backgroundColor: T.cardBorder, alignItems: 'center', justifyContent: 'center' },
  qtyText: { fontSize: 16, fontWeight: '600', color: T.text, minWidth: 24, textAlign: 'center' },
  removeBtn: { padding: 8 },
  cartModalFooter: { padding: 20, borderTopWidth: 1, borderTopColor: T.cardBorder },
  cartTotal: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 16 },
  cartTotalLabel: { fontSize: 16, color: T.textMuted },
  cartTotalValue: { fontSize: 20, fontWeight: '700', color: T.text },
  checkoutBtn: { borderRadius: 14, overflow: 'hidden' },
  checkoutBtnGradient: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 16, gap: 10 },
  checkoutBtnText: { fontSize: 16, fontWeight: '700', color: T.white },

  // Verify Screen
  verifyHeader: { alignItems: 'center', marginBottom: 24 },
  verifyIconGradient: { width: 72, height: 72, borderRadius: 20, alignItems: 'center', justifyContent: 'center', marginBottom: 16 },
  verifyTitle: { fontSize: 24, fontWeight: '700', color: T.text, marginBottom: 8 },
  verifySubtitle: { fontSize: 14, color: T.textMuted, textAlign: 'center' },
  scanQRButton: { borderRadius: 14, overflow: 'hidden', marginBottom: 20 },
  scanQRButtonGradient: { flexDirection: 'row', alignItems: 'center', paddingVertical: 18, paddingHorizontal: 20 },
  scanQRButtonText: { fontSize: 17, fontWeight: '700', color: T.white, marginLeft: 12 },
  dividerContainer: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  dividerLine: { flex: 1, height: 1, backgroundColor: T.cardBorder },
  dividerText: { color: T.textMuted, fontSize: 12, fontWeight: '600', paddingHorizontal: 16 },
  inputSection: { marginBottom: 20 },
  inputLabel: { fontSize: 12, fontWeight: '700', color: T.textMuted, letterSpacing: 1, marginBottom: 10 },
  inputWrapper: { flexDirection: 'row', alignItems: 'center', backgroundColor: T.card, borderRadius: 14, borderWidth: 1, borderColor: T.cardBorder, paddingHorizontal: 16, gap: 12 },
  input: { flex: 1, fontSize: 18, color: T.text, paddingVertical: 16, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
  verifyButton: { borderRadius: 14, overflow: 'hidden', marginBottom: 20 },
  verifyButtonGradient: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 16, gap: 10 },
  verifyButtonText: { fontSize: 16, fontWeight: '700', color: T.white },
  sampleSection: { marginBottom: 20 },
  sampleLabel: { fontSize: 13, color: T.textMuted, marginBottom: 10 },
  sampleCodesRow: { flexDirection: 'row', gap: 8 },
  sampleCode: { paddingHorizontal: 14, paddingVertical: 10, backgroundColor: T.primaryGlow, borderRadius: 10, borderWidth: 1, borderColor: T.primary + '30' },
  sampleCodeText: { fontSize: 13, fontWeight: '600', color: T.primary, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
  resultContainer: { marginTop: 8 },
  resultCard: { backgroundColor: T.card, borderRadius: 16, padding: 20, borderWidth: 1, borderColor: T.cardBorder, borderLeftWidth: 4 },
  resultHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
  resultIcon: { width: 48, height: 48, borderRadius: 14, alignItems: 'center', justifyContent: 'center', marginRight: 14 },
  resultStatus: { fontSize: 14, fontWeight: '800', letterSpacing: 1 },
  resultMessage: { fontSize: 13, color: T.textMuted, marginTop: 4 },
  resultDetails: { backgroundColor: T.cardElevated, borderRadius: 12, padding: 14 },
  resultRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: T.cardBorder },
  resultRowLabel: { fontSize: 13, color: T.textMuted },
  resultRowValue: { fontSize: 13, fontWeight: '600', color: T.text },
  antiFakeWarning: { flexDirection: 'row', padding: 14, borderRadius: 12, marginTop: 16, gap: 12 },
  antiFakeTitle: { fontSize: 14, fontWeight: '700', marginBottom: 4 },
  antiFakeText: { fontSize: 13, color: T.textSecondary, lineHeight: 18 },
  reportBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 14, borderRadius: 12, borderWidth: 1, borderColor: T.danger, marginTop: 12, gap: 8 },
  reportBtnText: { fontSize: 14, fontWeight: '600', color: T.danger },

  // Scanner
  scannerContainer: { flex: 1, backgroundColor: T.black },
  camera: { flex: 1 },
  scannerOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)' },
  scannerHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingTop: 60, paddingHorizontal: 20, paddingBottom: 20 },
  scannerCloseBtn: { width: 44, height: 44, borderRadius: 22, backgroundColor: 'rgba(255,255,255,0.2)', alignItems: 'center', justifyContent: 'center' },
  scannerTitle: { fontSize: 18, fontWeight: '700', color: T.white },
  scannerFrame: { width: 250, height: 250, alignSelf: 'center', marginTop: 40 },
  scannerCorner: { position: 'absolute', width: 40, height: 40, borderColor: T.primary },
  scannerCornerTL: { top: 0, left: 0, borderTopWidth: 4, borderLeftWidth: 4, borderTopLeftRadius: 12 },
  scannerCornerTR: { top: 0, right: 0, borderTopWidth: 4, borderRightWidth: 4, borderTopRightRadius: 12 },
  scannerCornerBL: { bottom: 0, left: 0, borderBottomWidth: 4, borderLeftWidth: 4, borderBottomLeftRadius: 12 },
  scannerCornerBR: { bottom: 0, right: 0, borderBottomWidth: 4, borderRightWidth: 4, borderBottomRightRadius: 12 },
  scannerHint: { color: T.white, fontSize: 14, textAlign: 'center', marginTop: 30, opacity: 0.8 },

  // Protocols
  protocolsHeader: { padding: 16, paddingBottom: 8 },
  protocolsTitle: { fontSize: 24, fontWeight: '700', color: T.text, marginBottom: 6 },
  protocolsSubtitle: { fontSize: 14, color: T.textMuted },
  filterContainer: { flexDirection: 'row', paddingHorizontal: 16, gap: 10, marginBottom: 16 },
  filterTab: { flex: 1, paddingVertical: 12, borderRadius: 12, backgroundColor: T.card, alignItems: 'center', borderWidth: 1, borderColor: T.cardBorder, overflow: 'hidden' },
  filterTabActive: { borderColor: T.primary },
  filterTabText: { fontSize: 14, fontWeight: '600', color: T.textMuted },
  filterTabTextActive: { color: T.white },
  filterPrice: { fontSize: 11, color: T.textDim, marginTop: 2 },
  filterPriceActive: { color: 'rgba(255,255,255,0.7)' },
  protocolCard: { backgroundColor: T.card, borderRadius: 16, padding: 18, marginBottom: 12, borderWidth: 1, borderColor: T.cardBorder },
  protocolCardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  categoryBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  categoryBadgeText: { fontSize: 11, fontWeight: '700' },
  protocolPrice: { fontSize: 18, fontWeight: '700', color: T.primary },
  protocolTitle: { fontSize: 17, fontWeight: '700', color: T.text, marginBottom: 6 },
  protocolDesc: { fontSize: 14, color: T.textMuted, lineHeight: 20 },
  protocolMeta: { flexDirection: 'row', gap: 16, marginTop: 12 },
  protocolMetaItem: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  protocolMetaText: { fontSize: 13, color: T.textMuted },
  protocolExpanded: { marginTop: 16, paddingTop: 16, borderTopWidth: 1, borderTopColor: T.cardBorder },
  protocolExpandedItem: { marginBottom: 16 },
  protocolExpandedHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 6 },
  protocolExpandedTitle: { fontSize: 13, fontWeight: '700', color: T.primary },
  protocolExpandedText: { fontSize: 13, color: T.textSecondary, lineHeight: 20 },
  productNeededItem: { flexDirection: 'row', alignItems: 'center', marginTop: 6, gap: 8 },
  productNeededDot: { width: 4, height: 4, borderRadius: 2, backgroundColor: T.primary },
  purchaseButton: { marginTop: 16, borderRadius: 12, overflow: 'hidden' },
  purchaseButtonGradient: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 14, gap: 8 },
  purchaseButtonText: { fontSize: 15, fontWeight: '700', color: T.white },
  expertButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 14, borderRadius: 12, borderWidth: 1, borderColor: T.success, marginTop: 16, gap: 8 },
  expertButtonText: { fontSize: 14, fontWeight: '600', color: T.success },

  // Payment Modal
  paymentModal: { backgroundColor: T.card, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 20, maxHeight: height * 0.85 },
  paymentModalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  paymentModalTitle: { fontSize: 20, fontWeight: '700', color: T.text },
  paymentProtocolName: { fontSize: 18, fontWeight: '600', color: T.text, textAlign: 'center' },
  paymentPrice: { fontSize: 32, fontWeight: '800', color: T.primary, textAlign: 'center', marginVertical: 16 },
  paymentSectionTitle: { fontSize: 14, fontWeight: '700', color: T.textMuted, marginBottom: 12 },
  cryptoOptions: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 20 },
  cryptoOption: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 10, backgroundColor: T.cardElevated, borderRadius: 12, borderWidth: 1, borderColor: T.cardBorder, gap: 8 },
  cryptoOptionActive: { borderColor: T.primary, backgroundColor: T.primaryGlow },
  cryptoDot: { width: 12, height: 12, borderRadius: 6 },
  cryptoOptionText: { fontSize: 14, fontWeight: '600', color: T.textMuted },
  cryptoOptionTextActive: { color: T.text },
  walletBox: { backgroundColor: T.cardElevated, borderRadius: 12, padding: 16, marginBottom: 16 },
  walletLabel: { fontSize: 12, color: T.textMuted, marginBottom: 8 },
  walletAddress: { fontSize: 12, color: T.text, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', lineHeight: 18 },
  paymentInstructions: { fontSize: 13, color: T.textMuted, lineHeight: 22, marginBottom: 20 },
  paidButton: { borderRadius: 14, overflow: 'hidden' },
  paidButtonGradient: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 16, gap: 10 },
  paidButtonText: { fontSize: 16, fontWeight: '700', color: T.white },

  // Profile
  profileHeader: { alignItems: 'center', backgroundColor: T.card, borderRadius: 24, padding: 28, marginBottom: 20, borderWidth: 1, borderColor: T.cardBorder },
  profileAvatar: { width: 80, height: 80, borderRadius: 24, alignItems: 'center', justifyContent: 'center', marginBottom: 16 },
  profileAvatarText: { fontSize: 32, fontWeight: '800', color: T.white },
  profileName: { fontSize: 22, fontWeight: '700', color: T.text, marginBottom: 4 },
  profileTagline: { fontSize: 14, color: T.textMuted, marginBottom: 12 },
  profileVersionBadge: { backgroundColor: T.cardElevated, paddingHorizontal: 14, paddingVertical: 6, borderRadius: 20 },
  profileVersion: { fontSize: 12, color: T.textMuted, fontWeight: '600' },
  historyTabs: { flexDirection: 'row', backgroundColor: T.card, borderRadius: 12, padding: 4, marginBottom: 16 },
  historyTab: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', paddingVertical: 12, borderRadius: 10, gap: 8 },
  historyTabActive: { backgroundColor: T.cardElevated },
  historyTabText: { fontSize: 14, fontWeight: '500', color: T.textMuted },
  historyTabTextActive: { color: T.primary, fontWeight: '600' },
  statsContainer: { flexDirection: 'row', gap: 10, marginBottom: 20 },
  statCard: { flex: 1, backgroundColor: T.card, borderRadius: 16, padding: 14, alignItems: 'center', borderWidth: 1, borderColor: T.cardBorder },
  statIconContainer: { width: 36, height: 36, borderRadius: 10, alignItems: 'center', justifyContent: 'center', marginBottom: 8 },
  statValue: { fontSize: 22, fontWeight: '800' },
  statLabel: { fontSize: 11, color: T.textMuted, marginTop: 4 },
  historyCard: { flexDirection: 'row', alignItems: 'center', backgroundColor: T.card, borderRadius: 14, padding: 14, marginBottom: 10, borderWidth: 1, borderColor: T.cardBorder },
  historyStatusIndicator: { width: 4, height: '100%', minHeight: 50, borderRadius: 2, marginRight: 14 },
  historyProductName: { fontSize: 15, fontWeight: '600', color: T.text, marginBottom: 4 },
  historyCode: { fontSize: 12, fontWeight: '600', color: T.primary, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace', marginBottom: 4 },
  historyTime: { fontSize: 12, color: T.textMuted },
  historyStatusBadge: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8 },
  historyStatusText: { fontSize: 11, fontWeight: '800' },
  menuSection: { marginTop: 8, marginBottom: 16 },
  menuSectionTitle: { fontSize: 16, fontWeight: '700', color: T.text, marginBottom: 14 },
  menuItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: T.card, borderRadius: 14, padding: 16, marginBottom: 10, borderWidth: 1, borderColor: T.cardBorder },
  menuIconContainer: { width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginRight: 14 },
  menuItemTitle: { fontSize: 15, fontWeight: '600', color: T.text },
  menuItemSubtitle: { fontSize: 13, color: T.textMuted, marginTop: 2 },
  emptyState: { alignItems: 'center', paddingVertical: 40 },
  emptyTitle: { fontSize: 18, fontWeight: '700', color: T.text, marginTop: 16 },
  emptyText: { fontSize: 14, color: T.textMuted, marginTop: 8 },
  disclaimerCard: { borderRadius: 14, overflow: 'hidden', marginTop: 8 },
  disclaimerGradient: { flexDirection: 'row', alignItems: 'flex-start', padding: 16, gap: 12, borderWidth: 1, borderColor: T.warning + '30', borderRadius: 14 },
  disclaimerText: { flex: 1, fontSize: 12, color: T.textSecondary, lineHeight: 18 },

  // Terms Modal
  termsModal: { backgroundColor: T.card, borderRadius: 24, margin: 20, maxHeight: height * 0.85, padding: 24 },
  termsHeader: { alignItems: 'center', marginBottom: 20 },
  termsTitle: { fontSize: 22, fontWeight: '700', color: T.text, marginTop: 12 },
  termsContent: { maxHeight: height * 0.45 },
  termsHeading: { fontSize: 16, fontWeight: '800', color: T.warning, marginBottom: 12, textAlign: 'center' },
  termsText: { fontSize: 14, color: T.textSecondary, lineHeight: 22, marginBottom: 12 },
  termsBullet: { fontSize: 13, color: T.textMuted, lineHeight: 20, marginBottom: 10, paddingLeft: 8 },
  acceptTermsBtn: { borderRadius: 14, overflow: 'hidden', marginTop: 20 },
  acceptTermsBtnGradient: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 16, gap: 10 },
  acceptTermsBtnText: { fontSize: 16, fontWeight: '700', color: T.white },
  termsFooter: { fontSize: 11, color: T.textDim, textAlign: 'center', marginTop: 12 },

  // Research Banner
  researchBanner: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: T.warning + '15', paddingVertical: 10, paddingHorizontal: 16, gap: 8 },
  researchBannerText: { fontSize: 12, color: T.warning, fontWeight: '600' },

  // Cart Disclaimer
  cartDisclaimer: { fontSize: 11, color: T.textMuted, textAlign: 'center', marginBottom: 12, lineHeight: 16 },

  // Empty Products
  emptyProducts: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: 60, paddingHorizontal: 20 },
  emptyProductsTitle: { fontSize: 18, fontWeight: '700', color: T.text, marginTop: 16 },
  emptyProductsText: { fontSize: 14, color: T.textMuted, marginTop: 8, textAlign: 'center' },
  visitWebsiteBtn: { marginTop: 20, paddingHorizontal: 24, paddingVertical: 12, backgroundColor: T.primary, borderRadius: 12 },
  visitWebsiteBtnText: { fontSize: 14, fontWeight: '600', color: T.white },
});
