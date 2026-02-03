import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS } from '../constants/config';
import { getProducts, getPurchasedProtocols } from '../services/api';

const HomeScreen = ({ navigation }) => {
  const [stats, setStats] = useState({
    totalProducts: 0,
    purchasedProtocols: 0,
    verifications: 0
  });
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const products = await getProducts();
      const purchased = await getPurchasedProtocols();
      
      setStats({
        totalProducts: products.length,
        purchasedProtocols: purchased.length,
        verifications: 0 // Will be updated from local storage
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadStats();
    setRefreshing(false);
  };

  const features = [
    {
      icon: 'qr-code-outline',
      title: 'Scan Product',
      description: 'Verify product authenticity',
      color: COLORS.primary,
      action: () => navigation.navigate('Scan')
    },
    {
      icon: 'book-outline',
      title: 'Browse Protocols',
      description: 'View peptide protocols',
      color: COLORS.success,
      action: () => navigation.navigate('Protocols')
    },
    {
      icon: 'time-outline',
      title: 'View History',
      description: 'Check scan history',
      color: COLORS.warning,
      action: () => navigation.navigate('History')
    }
  ];

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header Card */}
      <View style={styles.headerCard}>
        <Text style={styles.welcomeText}>Welcome to</Text>
        <Text style={styles.brandText}>Nexgen Sciences</Text>
        <Text style={styles.subtitleText}>Product Verification & Protocols</Text>
      </View>

      {/* Stats Cards */}
      <View style={styles.statsContainer}>
        <View style={[styles.statCard, { backgroundColor: COLORS.primary }]}>
          <Ionicons name="cube-outline" size={32} color={COLORS.white} />
          <Text style={styles.statNumber}>{stats.totalProducts}</Text>
          <Text style={styles.statLabel}>Products</Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: COLORS.success }]}>
          <Ionicons name="book-outline" size={32} color={COLORS.white} />
          <Text style={styles.statNumber}>{stats.purchasedProtocols}</Text>
          <Text style={styles.statLabel}>My Protocols</Text>
        </View>
      </View>

      {/* Features */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        {features.map((feature, index) => (
          <TouchableOpacity
            key={index}
            style={styles.featureCard}
            onPress={feature.action}
          >
            <View style={[styles.featureIcon, { backgroundColor: feature.color + '20' }]}>
              <Ionicons name={feature.icon} size={28} color={feature.color} />
            </View>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>{feature.title}</Text>
              <Text style={styles.featureDescription}>{feature.description}</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color={COLORS.textLight} />
          </TouchableOpacity>
        ))}
      </View>

      {/* Warning Banner */}
      <View style={styles.warningBanner}>
        <Ionicons name="warning-outline" size={24} color={COLORS.warning} />
        <Text style={styles.warningText}>
          FOR RESEARCH USE ONLY - Not for human consumption
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.light
  },
  headerCard: {
    backgroundColor: COLORS.primary,
    padding: 24,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24
  },
  welcomeText: {
    fontSize: 16,
    color: COLORS.white,
    opacity: 0.8
  },
  brandText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: COLORS.white,
    marginTop: 4
  },
  subtitleText: {
    fontSize: 14,
    color: COLORS.white,
    opacity: 0.8,
    marginTop: 4
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12
  },
  statCard: {
    flex: 1,
    padding: 20,
    borderRadius: 16,
    alignItems: 'center'
  },
  statNumber: {
    fontSize: 28,
    fontWeight: 'bold',
    color: COLORS.white,
    marginTop: 8
  },
  statLabel: {
    fontSize: 12,
    color: COLORS.white,
    marginTop: 4
  },
  section: {
    padding: 16
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.dark,
    marginBottom: 12
  },
  featureCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2
  },
  featureIcon: {
    width: 56,
    height: 56,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12
  },
  featureContent: {
    flex: 1
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.dark,
    marginBottom: 4
  },
  featureDescription: {
    fontSize: 14,
    color: COLORS.textLight
  },
  warningBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.warning + '20',
    padding: 16,
    margin: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.warning
  },
  warningText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.dark
  }
});

export default HomeScreen;
