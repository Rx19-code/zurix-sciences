import React, { useState } from 'react';
import { SafeAreaView, View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import HomeScreen from './src/screens/HomeScreen';
import ScanScreen from './src/screens/ScanScreen';
import ProtocolsScreen from './src/screens/ProtocolsScreen';
import HistoryScreen from './src/screens/HistoryScreen';
import ProfileScreen from './src/screens/ProfileScreen';

const TABS = [
  { key: 'Home', label: 'Home', icon: 'H' },
  { key: 'Scan', label: 'Scan', icon: 'S' },
  { key: 'Protocols', label: 'Protocols', icon: 'P' },
  { key: 'History', label: 'History', icon: 'T' },
  { key: 'Profile', label: 'Profile', icon: 'U' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('Home');

  const renderScreen = () => {
    const nav = { navigate: (tab) => setActiveTab(tab) };
    switch (activeTab) {
      case 'Home': return <HomeScreen navigation={nav} />;
      case 'Scan': return <ScanScreen navigation={nav} />;
      case 'Protocols': return <ProtocolsScreen navigation={nav} />;
      case 'History': return <HistoryScreen navigation={nav} />;
      case 'Profile': return <ProfileScreen navigation={nav} />;
      default: return <HomeScreen navigation={nav} />;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      <View style={styles.header}>
        <Text style={styles.headerTitle}>
          {activeTab === 'Home' ? 'Zurix Sciences' : activeTab === 'Scan' ? 'Verify Product' : activeTab}
        </Text>
      </View>
      <View style={styles.content}>
        {renderScreen()}
      </View>
      <View style={styles.tabBar}>
        {TABS.map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={[styles.tab, activeTab === tab.key && styles.tabActive]}
            onPress={() => setActiveTab(tab.key)}
          >
            <Text style={[styles.tabIcon, activeTab === tab.key && styles.tabIconActive]}>
              {tab.icon}
            </Text>
            <Text style={[styles.tabLabel, activeTab === tab.key && styles.tabLabelActive]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1e40af' },
  header: {
    backgroundColor: '#1e40af',
    paddingTop: 10,
    paddingBottom: 14,
    paddingHorizontal: 20,
  },
  headerTitle: { color: '#fff', fontSize: 20, fontWeight: 'bold' },
  content: { flex: 1, backgroundColor: '#f3f4f6' },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    paddingBottom: 8,
    paddingTop: 8,
  },
  tab: { flex: 1, alignItems: 'center', paddingVertical: 4 },
  tabActive: {},
  tabIcon: { fontSize: 18, fontWeight: 'bold', color: '#9ca3af' },
  tabIconActive: { color: '#1e40af' },
  tabLabel: { fontSize: 10, color: '#9ca3af', marginTop: 2 },
  tabLabelActive: { color: '#1e40af', fontWeight: '600' },
});
