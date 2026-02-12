import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS } from '../constants/config';
import { getLocalVerificationHistory } from '../services/api';

const HistoryScreen = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await getLocalVerificationHistory();
      setHistory(data);
    } catch (error) {
      console.error('Error loading history:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadHistory();
    setRefreshing(false);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      <View style={styles.cardLeft}>
        <View style={[
          styles.statusIcon,
          { backgroundColor: item.success ? COLORS.success + '20' : COLORS.danger + '20' }
        ]}>
          <Ionicons
            name={item.success ? 'checkmark-circle' : 'close-circle'}
            size={24}
            color={item.success ? COLORS.success : COLORS.danger}
          />
        </View>
      </View>
      <View style={styles.cardContent}>
        <Text style={styles.productName}>
          {item.product?.name || 'Unknown Product'}
        </Text>
        <Text style={styles.verificationCode}>{item.code}</Text>
        <Text style={styles.timestamp}>{formatDate(item.timestamp)}</Text>
        {item.product && (
          <View style={styles.detailsRow}>
            <Text style={styles.detailText}>Batch: {item.product.batch_number}</Text>
            <Text style={styles.detailText}>Purity: {item.product.purity}</Text>
          </View>
        )}
      </View>
      <View style={styles.cardRight}>
        <Text style={[
          styles.statusText,
          { color: item.success ? COLORS.success : COLORS.danger }
        ]}>
          {item.success ? 'Verified' : 'Failed'}
        </Text>
      </View>
    </View>
  );

  const renderEmpty = () => (
    <View style={styles.emptyContainer}>
      <Ionicons name="time-outline" size={64} color={COLORS.textLight} />
      <Text style={styles.emptyTitle}>No Verifications Yet</Text>
      <Text style={styles.emptyText}>
        Scan a product QR code or enter a verification code to see your history here.
      </Text>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.loadingText}>Loading history...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Stats Header */}
      <View style={styles.statsBar}>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{history.length}</Text>
          <Text style={styles.statLabel}>Total Scans</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={[styles.statNumber, { color: COLORS.success }]}>
            {history.filter(h => h.success).length}
          </Text>
          <Text style={styles.statLabel}>Verified</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={[styles.statNumber, { color: COLORS.danger }]}>
            {history.filter(h => !h.success).length}
          </Text>
          <Text style={styles.statLabel}>Failed</Text>
        </View>
      </View>

      <FlatList
        data={history}
        renderItem={renderItem}
        keyExtractor={(item, index) => `${item.code}-${index}`}
        contentContainerStyle={history.length === 0 ? styles.emptyList : styles.list}
        ListEmptyComponent={renderEmpty}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.light },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { fontSize: 16, color: COLORS.textLight },
  statsBar: {
    flexDirection: 'row',
    backgroundColor: COLORS.white,
    paddingVertical: 16,
    paddingHorizontal: 24,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: COLORS.light
  },
  statItem: { flex: 1, alignItems: 'center' },
  statNumber: { fontSize: 24, fontWeight: 'bold', color: COLORS.dark },
  statLabel: { fontSize: 12, color: COLORS.textLight, marginTop: 2 },
  statDivider: { width: 1, height: 32, backgroundColor: COLORS.light },
  list: { padding: 16, paddingBottom: 32 },
  emptyList: { flex: 1 },
  card: {
    flexDirection: 'row',
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 3,
    elevation: 1
  },
  cardLeft: { marginRight: 12, justifyContent: 'center' },
  statusIcon: { width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' },
  cardContent: { flex: 1 },
  productName: { fontSize: 15, fontWeight: '600', color: COLORS.dark, marginBottom: 2 },
  verificationCode: { fontSize: 12, fontFamily: 'monospace', color: COLORS.primary, marginBottom: 4 },
  timestamp: { fontSize: 11, color: COLORS.textLight, marginBottom: 4 },
  detailsRow: { flexDirection: 'row', gap: 12 },
  detailText: { fontSize: 11, color: COLORS.textLight },
  cardRight: { justifyContent: 'center' },
  statusText: { fontSize: 12, fontWeight: '600' },
  emptyContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 40 },
  emptyTitle: { fontSize: 20, fontWeight: 'bold', color: COLORS.dark, marginTop: 16, marginBottom: 8 },
  emptyText: { fontSize: 14, color: COLORS.textLight, textAlign: 'center', lineHeight: 20 }
});

export default HistoryScreen;
