import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Modal,
  Alert
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, PROTOCOL_PRICES, CRYPTO_WALLETS } from '../constants/config';
import { getProtocols, savePurchasedProtocol, getPurchasedProtocols } from '../services/api';

const ProtocolsScreen = () => {
  const [protocols, setProtocols] = useState([]);
  const [purchased, setPurchased] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedProtocol, setSelectedProtocol] = useState(null);
  const [showPayment, setShowPayment] = useState(false);
  const [filter, setFilter] = useState('All');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [protocolsData, purchasedData] = await Promise.all([
        getProtocols(),
        getPurchasedProtocols()
      ]);
      setProtocols(protocolsData);
      setPurchased(purchasedData);
    } catch (error) {
      console.error('Error loading protocols:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleBuy = (protocol) => {
    if (purchased.includes(protocol.id)) {
      setSelectedProtocol(protocol);
      return;
    }
    setSelectedProtocol(protocol);
    setShowPayment(true);
  };

  const handlePaymentConfirm = async () => {
    if (!selectedProtocol) return;
    await savePurchasedProtocol(selectedProtocol.id);
    setPurchased(prev => [...prev, selectedProtocol.id]);
    setShowPayment(false);
    Alert.alert('Success', 'Protocol unlocked! You can now view the full details.');
  };

  const filteredProtocols = filter === 'All'
    ? protocols
    : protocols.filter(p => p.category === filter);

  const isPurchased = (id) => purchased.includes(id);

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.loadingText}>Loading protocols...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Filter Tabs */}
      <View style={styles.filterBar}>
        {['All', 'Basic', 'Advanced'].map((tab) => (
          <TouchableOpacity
            key={tab}
            style={[styles.filterTab, filter === tab && styles.filterTabActive]}
            onPress={() => setFilter(tab)}
          >
            <Text style={[styles.filterText, filter === tab && styles.filterTextActive]}>
              {tab}
            </Text>
            {tab !== 'All' && (
              <Text style={[styles.filterPrice, filter === tab && styles.filterTextActive]}>
                ${tab === 'Basic' ? '4.99' : '9.99'}
              </Text>
            )}
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        contentContainerStyle={styles.listContent}
      >
        {filteredProtocols.map((protocol) => (
          <TouchableOpacity
            key={protocol.id}
            style={styles.card}
            onPress={() => handleBuy(protocol)}
          >
            <View style={styles.cardHeader}>
              <View style={[
                styles.categoryBadge,
                { backgroundColor: protocol.category === 'Basic' ? COLORS.success + '20' : COLORS.primary + '20' }
              ]}>
                <Text style={[
                  styles.categoryText,
                  { color: protocol.category === 'Basic' ? COLORS.success : COLORS.primary }
                ]}>
                  {protocol.category}
                </Text>
              </View>
              {protocol.featured && (
                <Ionicons name="star" size={18} color="#f59e0b" />
              )}
              {isPurchased(protocol.id) && (
                <View style={styles.ownedBadge}>
                  <Ionicons name="checkmark-circle" size={16} color={COLORS.success} />
                  <Text style={styles.ownedText}>Owned</Text>
                </View>
              )}
            </View>

            <Text style={styles.cardTitle}>{protocol.title}</Text>
            <Text style={styles.cardDescription} numberOfLines={2}>
              {protocol.description}
            </Text>

            <View style={styles.cardMeta}>
              <View style={styles.metaItem}>
                <Ionicons name="time-outline" size={16} color={COLORS.textLight} />
                <Text style={styles.metaText}>{protocol.duration_weeks} weeks</Text>
              </View>
              <View style={styles.metaItem}>
                <Ionicons name="flask-outline" size={16} color={COLORS.textLight} />
                <Text style={styles.metaText}>{protocol.products_needed.length} products</Text>
              </View>
            </View>

            <View style={styles.cardFooter}>
              <Text style={styles.price}>
                {isPurchased(protocol.id) ? 'View Details' : `$${protocol.price.toFixed(2)}`}
              </Text>
              <Ionicons
                name={isPurchased(protocol.id) ? 'eye-outline' : 'lock-closed-outline'}
                size={20}
                color={isPurchased(protocol.id) ? COLORS.success : COLORS.primary}
              />
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Protocol Detail Modal */}
      <Modal visible={selectedProtocol !== null && !showPayment && isPurchased(selectedProtocol?.id)} animationType="slide" transparent>
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <ScrollView showsVerticalScrollIndicator={false}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>{selectedProtocol?.title}</Text>
                <TouchableOpacity onPress={() => setSelectedProtocol(null)}>
                  <Ionicons name="close-circle" size={28} color={COLORS.textLight} />
                </TouchableOpacity>
              </View>

              <Text style={styles.modalDescription}>{selectedProtocol?.description}</Text>

              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Dosage Instructions</Text>
                <Text style={styles.sectionText}>{selectedProtocol?.dosage_instructions}</Text>
              </View>

              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Frequency</Text>
                <Text style={styles.sectionText}>{selectedProtocol?.frequency}</Text>
              </View>

              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Expected Results</Text>
                <Text style={styles.sectionText}>{selectedProtocol?.expected_results}</Text>
              </View>

              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Products Needed</Text>
                {selectedProtocol?.products_needed.map((product, i) => (
                  <View key={i} style={styles.productItem}>
                    <Ionicons name="flask" size={16} color={COLORS.primary} />
                    <Text style={styles.productText}>{product}</Text>
                  </View>
                ))}
              </View>

              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Reconstitution Guide</Text>
                <Text style={styles.sectionText}>{selectedProtocol?.reconstitution_guide}</Text>
              </View>

              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Side Effects</Text>
                <Text style={styles.sectionText}>{selectedProtocol?.side_effects}</Text>
              </View>

              <View style={[styles.section, styles.warningSection]}>
                <Text style={styles.warningSectionTitle}>Contraindications</Text>
                <Text style={styles.sectionText}>{selectedProtocol?.contraindications}</Text>
              </View>

              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Storage Tips</Text>
                <Text style={styles.sectionText}>{selectedProtocol?.storage_tips}</Text>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* Payment Modal */}
      <Modal visible={showPayment} animationType="slide" transparent>
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Unlock Protocol</Text>
              <TouchableOpacity onPress={() => { setShowPayment(false); setSelectedProtocol(null); }}>
                <Ionicons name="close-circle" size={28} color={COLORS.textLight} />
              </TouchableOpacity>
            </View>

            <Text style={styles.paymentProtocolName}>{selectedProtocol?.title}</Text>
            <Text style={styles.paymentPrice}>${selectedProtocol?.price.toFixed(2)}</Text>

            <Text style={styles.paymentLabel}>Send payment to one of these wallets:</Text>

            {Object.entries(CRYPTO_WALLETS).map(([coin, address]) => (
              <View key={coin} style={styles.walletItem}>
                <Text style={styles.walletCoin}>{coin}</Text>
                <Text style={styles.walletAddress} numberOfLines={1}>{address}</Text>
              </View>
            ))}

            <Text style={styles.paymentNote}>
              After sending payment, tap "I've Paid" below. Your representative will verify the transaction.
            </Text>

            <TouchableOpacity style={styles.paidButton} onPress={handlePaymentConfirm}>
              <Ionicons name="checkmark-circle" size={20} color={COLORS.white} />
              <Text style={styles.paidButtonText}>I've Paid - Unlock Protocol</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.cancelButton}
              onPress={() => { setShowPayment(false); setSelectedProtocol(null); }}
            >
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.light },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { fontSize: 16, color: COLORS.textLight },
  filterBar: { flexDirection: 'row', padding: 12, backgroundColor: COLORS.white, gap: 8 },
  filterTab: { flex: 1, paddingVertical: 10, borderRadius: 8, backgroundColor: COLORS.light, alignItems: 'center' },
  filterTabActive: { backgroundColor: COLORS.primary },
  filterText: { fontSize: 14, fontWeight: '600', color: COLORS.text },
  filterTextActive: { color: COLORS.white },
  filterPrice: { fontSize: 11, color: COLORS.textLight, marginTop: 2 },
  listContent: { padding: 16, paddingBottom: 32 },
  card: { backgroundColor: COLORS.white, borderRadius: 16, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.08, shadowRadius: 4, elevation: 2 },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 },
  categoryBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  categoryText: { fontSize: 12, fontWeight: '600' },
  ownedBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, marginLeft: 'auto' },
  ownedText: { fontSize: 12, color: COLORS.success, fontWeight: '600' },
  cardTitle: { fontSize: 17, fontWeight: 'bold', color: COLORS.dark, marginBottom: 6 },
  cardDescription: { fontSize: 13, color: COLORS.text, lineHeight: 19, marginBottom: 10 },
  cardMeta: { flexDirection: 'row', gap: 16, marginBottom: 12 },
  metaItem: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  metaText: { fontSize: 13, color: COLORS.textLight },
  cardFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingTop: 12, borderTopWidth: 1, borderTopColor: COLORS.light },
  price: { fontSize: 18, fontWeight: 'bold', color: COLORS.primary },
  modalContainer: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContent: { backgroundColor: COLORS.white, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, maxHeight: '85%' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  modalTitle: { fontSize: 20, fontWeight: 'bold', color: COLORS.dark, flex: 1 },
  modalDescription: { fontSize: 14, color: COLORS.text, lineHeight: 20, marginBottom: 20 },
  section: { marginBottom: 20 },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: COLORS.dark, marginBottom: 6 },
  sectionText: { fontSize: 14, color: COLORS.text, lineHeight: 20 },
  productItem: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 4 },
  productText: { fontSize: 14, color: COLORS.text },
  warningSection: { backgroundColor: COLORS.warning + '15', padding: 12, borderRadius: 8, borderLeftWidth: 3, borderLeftColor: COLORS.warning },
  warningSectionTitle: { fontSize: 16, fontWeight: 'bold', color: COLORS.dark, marginBottom: 6 },
  paymentProtocolName: { fontSize: 16, fontWeight: '600', color: COLORS.dark, textAlign: 'center', marginBottom: 4 },
  paymentPrice: { fontSize: 32, fontWeight: 'bold', color: COLORS.primary, textAlign: 'center', marginBottom: 20 },
  paymentLabel: { fontSize: 14, color: COLORS.text, marginBottom: 12 },
  walletItem: { backgroundColor: COLORS.light, padding: 12, borderRadius: 8, marginBottom: 8 },
  walletCoin: { fontSize: 14, fontWeight: 'bold', color: COLORS.dark, marginBottom: 4 },
  walletAddress: { fontSize: 11, color: COLORS.textLight, fontFamily: 'monospace' },
  paymentNote: { fontSize: 12, color: COLORS.textLight, textAlign: 'center', marginVertical: 16, lineHeight: 18 },
  paidButton: { backgroundColor: COLORS.success, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 16, borderRadius: 12, marginBottom: 8 },
  paidButtonText: { color: COLORS.white, fontSize: 16, fontWeight: '600' },
  cancelButton: { padding: 12, alignItems: 'center' },
  cancelButtonText: { color: COLORS.textLight, fontSize: 14 }
});

export default ProtocolsScreen;
