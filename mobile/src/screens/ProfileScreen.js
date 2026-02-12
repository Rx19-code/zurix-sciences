import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Linking
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS } from '../constants/config';
import { getPurchasedProtocols, getLocalVerificationHistory } from '../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getDeviceId } from '../utils/deviceId';

const ProfileScreen = () => {
  const [stats, setStats] = useState({
    verifications: 0,
    purchased: 0,
    deviceId: ''
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const [purchased, history, deviceId] = await Promise.all([
        getPurchasedProtocols(),
        getLocalVerificationHistory(),
        getDeviceId()
      ]);
      setStats({
        verifications: history.length,
        purchased: purchased.length,
        deviceId
      });
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  const handleClearHistory = () => {
    Alert.alert(
      'Clear History',
      'This will remove all local verification history. This cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            await AsyncStorage.removeItem('verification_history');
            setStats(prev => ({ ...prev, verifications: 0 }));
            Alert.alert('Done', 'Verification history cleared.');
          }
        }
      ]
    );
  };

  const handleContactSupport = () => {
    const message = encodeURIComponent('Hello, I need support with the Zurix Sciences app.');
    Linking.openURL(`https://wa.me/85212345678?text=${message}`);
  };

  const handleVisitWebsite = () => {
    Linking.openURL('https://zurixsciences.com');
  };

  const menuItems = [
    {
      icon: 'globe-outline',
      title: 'Visit Website',
      subtitle: 'zurixsciences.com',
      action: handleVisitWebsite,
      color: COLORS.primary
    },
    {
      icon: 'chatbubble-outline',
      title: 'Contact Support',
      subtitle: 'Chat via WhatsApp',
      action: handleContactSupport,
      color: COLORS.success
    },
    {
      icon: 'trash-outline',
      title: 'Clear History',
      subtitle: 'Remove local verification data',
      action: handleClearHistory,
      color: COLORS.danger
    }
  ];

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <Ionicons name="flask" size={40} color={COLORS.white} />
        </View>
        <Text style={styles.appName}>Zurix Sciences</Text>
        <Text style={styles.appVersion}>Version 1.0.0</Text>
      </View>

      {/* Stats */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Ionicons name="scan-outline" size={28} color={COLORS.primary} />
          <Text style={styles.statNumber}>{stats.verifications}</Text>
          <Text style={styles.statLabel}>Scans</Text>
        </View>
        <View style={styles.statCard}>
          <Ionicons name="book-outline" size={28} color={COLORS.success} />
          <Text style={styles.statNumber}>{stats.purchased}</Text>
          <Text style={styles.statLabel}>Protocols</Text>
        </View>
      </View>

      {/* Device ID */}
      <View style={styles.deviceSection}>
        <Text style={styles.deviceLabel}>Device ID</Text>
        <Text style={styles.deviceId} numberOfLines={1}>{stats.deviceId}</Text>
      </View>

      {/* Menu */}
      <View style={styles.menuSection}>
        {menuItems.map((item, index) => (
          <TouchableOpacity
            key={index}
            style={styles.menuItem}
            onPress={item.action}
          >
            <View style={[styles.menuIcon, { backgroundColor: item.color + '15' }]}>
              <Ionicons name={item.icon} size={22} color={item.color} />
            </View>
            <View style={styles.menuContent}>
              <Text style={styles.menuTitle}>{item.title}</Text>
              <Text style={styles.menuSubtitle}>{item.subtitle}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={COLORS.textLight} />
          </TouchableOpacity>
        ))}
      </View>

      {/* About */}
      <View style={styles.aboutSection}>
        <Text style={styles.aboutTitle}>About</Text>
        <Text style={styles.aboutText}>
          Zurix Sciences mobile app for product verification and peptide research protocols.
          Scan QR codes to verify product authenticity and access research protocols.
        </Text>
      </View>

      {/* Warning */}
      <View style={styles.warningBanner}>
        <Ionicons name="warning-outline" size={20} color={COLORS.warning} />
        <Text style={styles.warningText}>
          FOR RESEARCH USE ONLY - Not for human consumption
        </Text>
      </View>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.light },
  header: {
    backgroundColor: COLORS.primary,
    paddingTop: 20,
    paddingBottom: 30,
    alignItems: 'center',
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24
  },
  avatarContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12
  },
  appName: { fontSize: 22, fontWeight: 'bold', color: COLORS.white },
  appVersion: { fontSize: 13, color: 'rgba(255,255,255,0.7)', marginTop: 4 },
  statsContainer: { flexDirection: 'row', padding: 16, gap: 12 },
  statCard: {
    flex: 1,
    backgroundColor: COLORS.white,
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 3,
    elevation: 1
  },
  statNumber: { fontSize: 24, fontWeight: 'bold', color: COLORS.dark, marginTop: 6 },
  statLabel: { fontSize: 12, color: COLORS.textLight, marginTop: 2 },
  deviceSection: {
    backgroundColor: COLORS.white,
    marginHorizontal: 16,
    borderRadius: 12,
    padding: 14,
    marginBottom: 16
  },
  deviceLabel: { fontSize: 12, color: COLORS.textLight, marginBottom: 4 },
  deviceId: { fontSize: 12, fontFamily: 'monospace', color: COLORS.text },
  menuSection: { marginHorizontal: 16, marginBottom: 16 },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    padding: 14,
    borderRadius: 12,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 2,
    elevation: 1
  },
  menuIcon: { width: 40, height: 40, borderRadius: 10, alignItems: 'center', justifyContent: 'center', marginRight: 12 },
  menuContent: { flex: 1 },
  menuTitle: { fontSize: 15, fontWeight: '600', color: COLORS.dark },
  menuSubtitle: { fontSize: 12, color: COLORS.textLight, marginTop: 2 },
  aboutSection: {
    backgroundColor: COLORS.white,
    marginHorizontal: 16,
    borderRadius: 12,
    padding: 16,
    marginBottom: 16
  },
  aboutTitle: { fontSize: 16, fontWeight: 'bold', color: COLORS.dark, marginBottom: 8 },
  aboutText: { fontSize: 13, color: COLORS.text, lineHeight: 19 },
  warningBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.warning + '15',
    marginHorizontal: 16,
    padding: 12,
    borderRadius: 10,
    gap: 10
  },
  warningText: { flex: 1, fontSize: 11, fontWeight: '600', color: COLORS.dark }
});

export default ProfileScreen;
