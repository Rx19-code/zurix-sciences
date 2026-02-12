import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Modal,
  ScrollView,
  TextInput
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { Ionicons } from '@expo/vector-icons';
import { COLORS } from '../constants/config';
import { verifyScan, saveVerificationToLocal } from '../services/api';
import { getDeviceId } from '../utils/deviceId';

const ScanScreen = () => {
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);
  const [scanning, setScanning] = useState(true);
  const [manualCode, setManualCode] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleBarCodeScanned = async ({ data }) => {
    if (scanned) return;
    setScanned(true);
    setScanning(false);
    await verifyCode(data);
  };

  const verifyCode = async (code) => {
    setLoading(true);
    try {
      const deviceId = await getDeviceId();
      const response = await verifyScan(code, deviceId);
      setResult(response);

      if (response.success) {
        await saveVerificationToLocal({
          ...response,
          timestamp: new Date().toISOString(),
          code: code
        });
      }

      if (!response.success || response.warning) {
        Alert.alert(
          response.success ? 'Warning' : 'Verification Failed',
          response.warning || response.message
        );
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to verify product. Please check your internet connection.');
      console.error('Verification error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleManualVerify = () => {
    if (!manualCode.trim()) {
      Alert.alert('Error', 'Please enter a verification code');
      return;
    }
    verifyCode(manualCode.trim().toUpperCase());
  };

  const resetScan = () => {
    setScanned(false);
    setScanning(true);
    setResult(null);
    setManualCode('');
  };

  if (!permission) {
    return (
      <View style={styles.centerContainer}>
        <Text>Requesting camera permission...</Text>
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="camera-outline" size={64} color={COLORS.textLight} />
        <Text style={styles.noPermissionText}>No access to camera</Text>
        <Text style={styles.noPermissionSubtext}>Please grant camera permission</Text>
        <TouchableOpacity style={styles.grantButton} onPress={requestPermission}>
          <Text style={styles.grantButtonText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {scanning ? (
        <>
          <CameraView
            style={styles.camera}
            facing="back"
            barcodeScannerEnabled={true}
            barcodeScannerSettings={{ barcodeTypes: ['qr'] }}
            onBarcodeScanned={scanned ? undefined : handleBarCodeScanned}
          >
            <View style={styles.overlay}>
              <View style={styles.unfocusedContainer} />
              <View style={styles.middleContainer}>
                <View style={styles.unfocusedContainer} />
                <View style={styles.focusedContainer}>
                  <View style={[styles.corner, styles.topLeft]} />
                  <View style={[styles.corner, styles.topRight]} />
                  <View style={[styles.corner, styles.bottomLeft]} />
                  <View style={[styles.corner, styles.bottomRight]} />
                </View>
                <View style={styles.unfocusedContainer} />
              </View>
              <View style={styles.unfocusedContainer}>
                <Text style={styles.scanText}>Scan QR Code on product</Text>
              </View>
            </View>
          </CameraView>

          <View style={styles.manualEntry}>
            <Text style={styles.orText}>or enter code manually</Text>
            <View style={styles.inputContainer}>
              <TextInput
                style={styles.input}
                placeholder="Enter verification code"
                value={manualCode}
                onChangeText={setManualCode}
                autoCapitalize="characters"
                placeholderTextColor={COLORS.textLight}
              />
              <TouchableOpacity
                style={styles.verifyButton}
                onPress={handleManualVerify}
                disabled={loading}
              >
                <Text style={styles.verifyButtonText}>
                  {loading ? '...' : 'Verify'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </>
      ) : null}

      {/* Result Modal */}
      <Modal visible={result !== null} animationType="slide" transparent>
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <ScrollView showsVerticalScrollIndicator={false}>
              {result?.success ? (
                <>
                  <View style={[styles.resultIcon, { backgroundColor: COLORS.success + '20' }]}>
                    <Ionicons name="checkmark-circle" size={64} color={COLORS.success} />
                  </View>
                  <Text style={styles.resultTitle}>Product Authenticated</Text>
                  {result.product && (
                    <View style={styles.productInfo}>
                      <Text style={styles.productName}>{result.product.name}</Text>
                      <View style={styles.infoRow}>
                        <Text style={styles.infoLabel}>Batch:</Text>
                        <Text style={styles.infoValue}>{result.product.batch_number}</Text>
                      </View>
                      <View style={styles.infoRow}>
                        <Text style={styles.infoLabel}>Purity:</Text>
                        <Text style={styles.infoValue}>{result.product.purity}</Text>
                      </View>
                      <View style={styles.infoRow}>
                        <Text style={styles.infoLabel}>Expiry:</Text>
                        <Text style={styles.infoValue}>{result.product.expiry_date}</Text>
                      </View>
                      <View style={styles.infoRow}>
                        <Text style={styles.infoLabel}>Verifications:</Text>
                        <Text style={[styles.infoValue, result.verification_count > 5 && { color: COLORS.warning }]}>
                          {result.verification_count}x
                        </Text>
                      </View>
                    </View>
                  )}
                  {result.warning && (
                    <View style={styles.warningBox}>
                      <Ionicons name="warning" size={24} color={COLORS.warning} />
                      <Text style={styles.warningText}>{result.warning}</Text>
                    </View>
                  )}
                </>
              ) : (
                <>
                  <View style={[styles.resultIcon, { backgroundColor: COLORS.danger + '20' }]}>
                    <Ionicons name="close-circle" size={64} color={COLORS.danger} />
                  </View>
                  <Text style={[styles.resultTitle, { color: COLORS.danger }]}>Verification Failed</Text>
                  <Text style={styles.errorMessage}>{result?.message}</Text>
                </>
              )}
              <TouchableOpacity style={styles.closeButton} onPress={resetScan}>
                <Text style={styles.closeButtonText}>Scan Another Product</Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.dark },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 },
  camera: { flex: 1 },
  overlay: { flex: 1 },
  unfocusedContainer: { flex: 1, backgroundColor: 'rgba(0,0,0,0.7)', alignItems: 'center', justifyContent: 'center' },
  middleContainer: { flexDirection: 'row', flex: 1.5 },
  focusedContainer: { flex: 6 },
  corner: { position: 'absolute', width: 40, height: 40, borderColor: COLORS.white },
  topLeft: { top: 0, left: 0, borderTopWidth: 4, borderLeftWidth: 4 },
  topRight: { top: 0, right: 0, borderTopWidth: 4, borderRightWidth: 4 },
  bottomLeft: { bottom: 0, left: 0, borderBottomWidth: 4, borderLeftWidth: 4 },
  bottomRight: { bottom: 0, right: 0, borderBottomWidth: 4, borderRightWidth: 4 },
  scanText: { color: COLORS.white, fontSize: 16, fontWeight: '600', textAlign: 'center', marginTop: 20 },
  manualEntry: { backgroundColor: COLORS.white, padding: 20, borderTopLeftRadius: 20, borderTopRightRadius: 20 },
  orText: { textAlign: 'center', color: COLORS.textLight, marginBottom: 12, fontSize: 14 },
  inputContainer: { flexDirection: 'row', gap: 8 },
  input: { flex: 1, borderWidth: 1, borderColor: COLORS.textLight, borderRadius: 8, padding: 12, fontSize: 16, color: COLORS.dark },
  verifyButton: { backgroundColor: COLORS.primary, paddingHorizontal: 24, borderRadius: 8, justifyContent: 'center' },
  verifyButtonText: { color: COLORS.white, fontWeight: '600', fontSize: 16 },
  grantButton: { backgroundColor: COLORS.primary, paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8, marginTop: 16 },
  grantButtonText: { color: COLORS.white, fontWeight: '600', fontSize: 16 },
  noPermissionText: { fontSize: 18, fontWeight: '600', color: COLORS.dark, marginTop: 16 },
  noPermissionSubtext: { fontSize: 14, color: COLORS.textLight, marginTop: 8, textAlign: 'center' },
  modalContainer: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContent: { backgroundColor: COLORS.white, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, maxHeight: '80%' },
  resultIcon: { width: 100, height: 100, borderRadius: 50, alignItems: 'center', justifyContent: 'center', alignSelf: 'center', marginBottom: 16 },
  resultTitle: { fontSize: 24, fontWeight: 'bold', textAlign: 'center', color: COLORS.dark, marginBottom: 16 },
  productInfo: { backgroundColor: COLORS.light, padding: 16, borderRadius: 12, marginBottom: 16 },
  productName: { fontSize: 18, fontWeight: 'bold', color: COLORS.dark, marginBottom: 12 },
  infoRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  infoLabel: { fontSize: 14, color: COLORS.textLight },
  infoValue: { fontSize: 14, fontWeight: '600', color: COLORS.dark },
  warningBox: { flexDirection: 'row', backgroundColor: COLORS.warning + '20', padding: 12, borderRadius: 8, alignItems: 'center', marginBottom: 16 },
  warningText: { flex: 1, marginLeft: 12, fontSize: 14, color: COLORS.dark },
  errorMessage: { fontSize: 16, color: COLORS.text, textAlign: 'center', marginBottom: 24 },
  closeButton: { backgroundColor: COLORS.primary, padding: 16, borderRadius: 12, alignItems: 'center' },
  closeButtonText: { color: COLORS.white, fontSize: 16, fontWeight: '600' }
});

export default ScanScreen;
